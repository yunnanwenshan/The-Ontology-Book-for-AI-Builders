"""CDC 一次性演示（4 轮跑完自动停）."""
import time
import sqlite3
import hashlib
import subprocess
import sys
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
WATCH_FILE = DATA_DIR / "shop.db"
MATERIALIZE_SCRIPT = Path(__file__).parent / "r2rml_materialize.py"


def file_md5(path):
    if not path.exists():
        return ""
    h = hashlib.md5()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def materialize():
    print("  触发物化...")
    r = subprocess.run([sys.executable, str(MATERIALIZE_SCRIPT)],
                       capture_output=True, text=True, timeout=30)
    if r.returncode == 0:
        for line in r.stdout.split("\n"):
            if "物化完成" in line or "物化订单数" in line or "孤儿" in line or "持久化" in line:
                print(f"    {line.strip()}")
    else:
        print(f"  ❌ 失败: {r.stderr[:200]}")


def order_count():
    conn = sqlite3.connect(WATCH_FILE)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM "order"')
    n = c.fetchone()[0]
    conn.close()
    return n


def add_new_order():
    conn = sqlite3.connect(WATCH_FILE)
    c = conn.cursor()
    order_id = c.execute('SELECT MAX(id) + 1 FROM "order"').fetchone()[0] or 1
    c.execute('INSERT INTO "order" VALUES (?, ?, ?, ?, ?)',
              (order_id, 4, '2026-07-09 14:00:00', 4999.00, 'Placed'))
    c.execute('INSERT INTO order_item VALUES (?, ?, ?, ?)',
              (order_id, 'IP001', 1, 4999.00))
    conn.commit()
    conn.close()
    return order_id


def main():
    print("=" * 70)
    print("  CDC 实时同步演示（4 轮自动停）")
    print("=" * 70)
    print(f"  监控: {WATCH_FILE.name}")
    print(f"  触发: 文件变化 → 自动物化")
    print()
    last_hash = file_md5(WATCH_FILE)
    print(f"  [Round 0] 初始订单数: {order_count()}")
    print(f"             初始 hash: {last_hash[:8]}")
    print()

    for round_num in [1, 2, 3, 4]:
        time.sleep(2)
        current_hash = file_md5(WATCH_FILE)

        if current_hash != last_hash:
            print(f"  [Round {round_num}] 🔔 检测到文件变化！")
            print(f"             旧 hash: {last_hash[:8]}")
            print(f"             新 hash: {current_hash[:8]}")
            last_hash = current_hash
            print(f"             订单数: {order_count()}")
            materialize()
        else:
            # 模拟 ERP 写入
            if round_num in [2, 4]:
                print(f"  [Round {round_num}] 📝 模拟 ERP 写入新订单...")
                new_id = add_new_order()
                print(f"             写入订单 O000000000{new_id}")
                # 下轮循环会自动检测到变化
            else:
                print(f"  [Round {round_num}] 监控中... 订单数: {order_count()}")

    print()
    print("=" * 70)
    print(f"  ✅ CDC 演示完成。最终订单数: {order_count()}")
    print("=" * 70)


if __name__ == "__main__":
    main()
