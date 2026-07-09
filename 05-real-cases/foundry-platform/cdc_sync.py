"""CDC 实时同步（Change Data Capture）.

对齐 Palantir Foundry 的 Pipeline Builder Stream Mode:
- 监控源数据文件变化
- 文件变化 → 触发物化
- 自动校验 → 持久化 → Dashboard 刷新

这模拟:
- ERP 导出新订单 → shop.db 变化 → 自动 RDF 化
- 不用手动跑 r2rml_materialize.py
"""
import time
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime
from rdflib import Graph
from rdflib.plugins.sparql import prepareQuery
import subprocess
import sys

DATA_DIR = Path(__file__).parent / "data"
WATCH_FILE = DATA_DIR / "shop.db"
ONTOLOGY = DATA_DIR / "platform-ont.ttl"
MATERIALIZE_SCRIPT = Path(__file__).parent / "r2rml_materialize.py"


def file_md5(path: Path) -> str:
    """计算文件 hash，看是否变化."""
    if not path.exists():
        return ""
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def materialize():
    """跑物化（实际工程用 subprocess 调 r2rml_materialize.py）."""
    print(f"  [{datetime.now().strftime('%H:%M:%S')}] 触发物化...")
    result = subprocess.run(
        [sys.executable, str(MATERIALIZE_SCRIPT)],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        # 提取关键输出
        for line in result.stdout.split("\n"):
            if "物化完成" in line or "物化订单数" in line or "孤儿" in line:
                print(f"     {line.strip()}")
    else:
        print(f"  ❌ 物化失败：{result.stderr[:200]}")


def quick_validate():
    """物化后快速校验（订单数 + SHACL）."""
    mat_file = DATA_DIR / "platform-data-mat.ttl"
    if not mat_file.exists():
        return

    g = Graph().parse(str(mat_file), format="turtle")

    # 订单数
    q = prepareQuery("""
    PREFIX ex: <http://platform.com/>
    SELECT (COUNT(?o) AS ?c) WHERE { ?o a ex:Order . }
    """)
    for r in g.query(q):
        print(f"     📦 物化订单数: {r.c}")

    # 孤儿
    q2 = prepareQuery("""
    PREFIX ex: <http://platform.com/>
    SELECT (COUNT(?item) AS ?c) WHERE {
        ?item a ex:OrderItem ; ex:orderHasItem ?o .
        FILTER NOT EXISTS { ?o a ex:Order . }
    }
    """)
    for r in g.query(q2):
        if int(r.c) > 0:
            print(f"     ⚠️  孤儿 OrderItem: {r.c}")


def modify_db():
    """模拟 ERP 写入新数据."""
    print(f"  [{datetime.now().strftime('%H:%M:%S')}] 📝 模拟新订单写入...")
    conn = sqlite3.connect(WATCH_FILE)
    c = conn.cursor()
    # 加一个新订单（order id 5）
    try:
        c.execute('INSERT INTO "order" VALUES (?, ?, ?, ?, ?)',
                  (5, 4, '2026-07-09 10:00:00', 4999.00, 'Placed'))
        # 加一个 OrderItem
        c.execute('INSERT INTO order_item VALUES (?, ?, ?, ?)',
                  (5, 'IP001', 1, 4999.00))
        conn.commit()
        print("     ✓ 写入订单 O0000000005 ¥4,999.00")
    except sqlite3.IntegrityError:
        print("     订单 5 已存在（重复触发）")
    finally:
        conn.close()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--once', action='store_true', help='跑 3 轮自动停')
    args = parser.parse_args()
    print("=" * 70)
    print("  CDC 实时同步演示（Foundry Pipeline Stream Mode 风格）")
    print("=" * 70)
    print(f"""
  监控文件: {WATCH_FILE.name}
  触发动作: 文件变化 → 自动跑 r2rml_materialize.py → 校验

  演示:
    1. 启动监控
    2. 3 秒后模拟 ERP 写入新订单
    3. 3 秒后再写一次
    4. Ctrl+C 停止

  （每个 round = 2 秒 sleep）
""")

    last_hash = file_md5(WATCH_FILE)
    print(f"  [启动] 文件初始 hash: {last_hash[:8]}...")
    print(f"          订单数: ", end="")
    conn = sqlite3.connect(WATCH_FILE)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM "order"')
    print(c.fetchone()[0])
    conn.close()

    round_num = 0
    try:
        while True:
            time.sleep(2)
            round_num += 1
            current_hash = file_md5(WATCH_FILE)

            if current_hash != last_hash:
                print(f"\n  [Round {round_num}] 🔔 文件变化检测！")
                print(f"     旧 hash: {last_hash[:8]}...")
                print(f"     新 hash: {current_hash[:8]}...")
                last_hash = current_hash
                materialize()
                quick_validate()
            else:
                # 模拟变更（每 3 轮修改一次）
                if round_num % 3 == 0:
                    print(f"\n  [Round {round_num}] 模拟写入新订单...")
                    modify_db()
                else:
                    conn = sqlite3.connect(WATCH_FILE)
                    c = conn.cursor()
                    c.execute('SELECT COUNT(*) FROM "order"')
                    cnt = c.fetchone()[0]
                    conn.close()
                    print(f"  [Round {round_num}] 监控中... 订单数: {cnt}")
    except KeyboardInterrupt:
        print(f"\n  [停止] CDC 监控已停止")


if __name__ == "__main__":
    main()
