"""R2RML 风格 SQL → RDF 物化.

对齐 Palantir Foundry 的 Pipeline Builder / Code Transforms:
- 从关系数据库 (SQLite) 读数据
- 物化成 RDF 三元组
- 加载到本体（与已有 ontology 合并）

这是生产环境的 ETL 入口: ERP/MySQL → RDF → Ontology → Agent.
"""
import sqlite3
from pathlib import Path
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, XSD

# === 准备测试数据库 ===
DB_PATH = Path(__file__).parent / "data" / "shop.db"

def setup_db():
    """建一个 SQLite 库模拟 ERP."""
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.executescript("""
    CREATE TABLE customer (id INT, name TEXT, tier TEXT, email TEXT);
    CREATE TABLE product (sku TEXT PRIMARY KEY, name TEXT, category TEXT, price REAL);
    CREATE TABLE "order" (id INT PRIMARY KEY, customer_id INT, order_date TEXT,
                         total_amount REAL, status TEXT);
    CREATE TABLE order_item (order_id INT, product_sku TEXT, qty INT, unit_price REAL);

    INSERT INTO customer VALUES (1, '华为技术', 'VIP', 'huawei@x.com');
    INSERT INTO customer VALUES (2, '字节跳动', 'VIP', 'bytedance@x.com');
    INSERT INTO customer VALUES (3, '美的集团', 'Standard', 'midea@x.com');
    INSERT INTO customer VALUES (4, '新客户甲', 'New', 'new@x.com');

    INSERT INTO product VALUES ('IP001', 'iPhone 15', '手机', 6999.00);
    INSERT INTO product VALUES ('IP002', 'iPad Pro', '平板', 8999.00);
    INSERT INTO product VALUES ('MAC01', 'MacBook Pro', '电脑', 15999.00);
    INSERT INTO product VALUES ('AP001', 'AirPods Pro', '耳机', 1999.00);

    INSERT INTO "order" VALUES (1, 1, '2026-07-01 10:00:00', 21997.00, 'Delivered');
    INSERT INTO "order" VALUES (2, 2, '2026-07-03 11:00:00', 8999.00, 'Shipped');
    INSERT INTO "order" VALUES (3, 3, '2026-07-05 15:00:00', 25997.00, 'Paid');
    INSERT INTO "order" VALUES (4, 4, '2026-07-08 09:00:00', 1999.00, 'Placed');

    INSERT INTO order_item VALUES (1, 'IP001', 2, 6999.00);
    INSERT INTO order_item VALUES (1, 'AP001', 4, 1999.00);
    INSERT INTO order_item VALUES (2, 'IP002', 1, 8999.00);
    INSERT INTO order_item VALUES (3, 'IP001', 2, 6999.00);
    INSERT INTO order_item VALUES (3, 'MAC01', 1, 15999.00);
    INSERT INTO order_item VALUES (4, 'AP001', 1, 1999.00);

    INSERT INTO order_item VALUES (99, 'IP001', 1, 6999.00);  -- 孤儿 item（订单 99 不存在）
    """)
    conn.commit()
    return conn


# === R2RML 映射（简化版，参考 W3C R2RML） ===
# 真实 R2RML 是 ttl 文件，这里用 Python dict 表达
MAPPINGS = {
    "Customer": {
        "table": "customer",
        "class": "ex:Customer",
        "subject_template": "http://platform.com/customer/{id}",
        "properties": [
            ("ex:customerName", "name", XSD.string),
            ("ex:customerTier", "tier", XSD.string),
            ("ex:customerEmail", "email", XSD.string),
        ]
    },
    "Product": {
        "table": "product",
        "class": "ex:Product",
        "subject_template": "http://platform.com/product/{sku}",
        "properties": [
            ("ex:productName", "name", XSD.string),
            ("ex:productCategory", "category", XSD.string),
            ("ex:productUnitPrice", "price", XSD.decimal),
        ]
    },
    "Order": {
        "table": "order",
        "class": "ex:Order",
        "subject_template": "http://platform.com/order/{id}",
        "properties": [
            ("ex:orderDate", "order_date", XSD.dateTime),
            ("ex:orderTotalAmount", "total_amount", XSD.decimal),
            ("ex:orderStatus", "status", XSD.string),
        ],
        "links": [
            ("ex:orderHasCustomer", "customer_id", "http://platform.com/customer/{customer_id}"),
        ]
    },
    "OrderItem": {
        "table": "order_item",
        "class": "ex:OrderItem",
        "subject_template": "http://platform.com/orderitem/{order_id}-{product_sku}",
        "properties": [
            ("ex:itemQuantity", "qty", XSD.integer),
            ("ex:itemUnitPrice", "unit_price", XSD.decimal),
        ],
        "links": [
            ("ex:orderHasItem", "order_id", "http://platform.com/order/{order_id}"),
            ("ex:orderItemForProduct", "product_sku", "http://platform.com/product/{product_sku}"),
        ]
    },
}


def run_mapping(conn, g, ex):
    """执行 R2RML 映射（简化版）."""
    cur = conn.cursor()
    total = 0
    for type_name, m in MAPPINGS.items():
        table = m['table']
        # SQL 关键字需要加引号
        if table == 'order':
            table_q = '"order"'
        else:
            table_q = table
        cur.execute(f"SELECT * FROM {table_q}")
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description]
        print(f"  [{type_name}] 读取 {len(rows)} 行")
        for row in rows:
            record = dict(zip(cols, row))
            # Subject
            subject_tpl = m["subject_template"]
            subject_uri = subject_tpl.format(**record)
            subject = URIRef(subject_uri)
            # rdf:type
            g.add((subject, RDF.type, URIRef(ex + m["class"].split(":")[1])))
            # DatatypeProperty
            for prop, col, dtype in m["properties"]:
                if record.get(col) is not None:
                    g.add((subject, URIRef(ex + prop.split(":")[1]),
                            Literal(record[col], datatype=dtype)))
            # ObjectProperty (link)
            for prop, col, target_tpl in m.get("links", []):
                if record.get(col) is not None:
                    target_uri = target_tpl.format(**record)
                    g.add((subject, URIRef(ex + prop.split(":")[1]),
                            URIRef(target_uri)))
            total += 1
    return total


def validate_after_materialization(g, ex):
    """物化后跑 SHACL 校验（看数据是否符合业务规则）."""
    shapes_path = Path(__file__).parent / "data" / "platform-shapes.ttl"
    if not shapes_path.exists():
        return True, "无 SHACL 文件"

    from pyshacl import validate
    shapes = Graph().parse(str(shapes_path), format="turtle")
    conforms, report_g, _ = validate(g, shacl_graph=shapes)
    return conforms, report_g.serialize(format="turtle")


def verify_queries(g, ex):
    """物化后跑 3 个验证查询（看数据是否正确）."""
    from rdflib.plugins.sparql import prepareQuery

    out = []
    # Q1: 总订单数
    q1 = prepareQuery("PREFIX ex: <http://platform.com/> SELECT (COUNT(?o) AS ?c) WHERE { ?o a ex:Order . }")
    for r in g.query(q1):
        out.append(f"  ✓ 物化订单数：{r.c}")

    # Q2: 每个客户的订单数
    q2 = prepareQuery("""
    PREFIX ex: <http://platform.com/>
    SELECT ?name (COUNT(?o) AS ?cnt) WHERE {
        ?o a ex:Order ; ex:orderHasCustomer ?c .
        ?c ex:customerName ?name .
    } GROUP BY ?c ?name
    """)
    out.append("  ✓ 客户订单分布：")
    for r in g.query(q2):
        out.append(f"      {r.name}  → {r.cnt} 单")

    # Q3: 孤儿 OrderItem（order 99 不存在）
    q3 = prepareQuery("""
    PREFIX ex: <http://platform.com/>
    SELECT ?item WHERE {
        ?item a ex:OrderItem ; ex:orderHasItem ?o .
        FILTER NOT EXISTS { ?o a ex:Order . }
    }
    """)
    orphans = list(g.query(q3))
    out.append(f"  ⚠️  孤儿 OrderItem（指向不存在的 Order）：{len(orphans)} 个")
    for r in orphans:
        out.append(f"      {r.item}")

    return "\n".join(out)


def main():
    print("=" * 60)
    print("  R2RML 物化：SQL → RDF（Foundry Pipeline Builder 风格）")
    print("=" * 60)

    # Step 1: 建测试库
    print("\n[1] 准备模拟 ERP（SQLite）")
    conn = setup_db()
    print(f"  ✓ 写入 {DB_PATH}")
    cur = conn.cursor()
    for t in ["customer", "product", '"order"', "order_item"]:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        cnt = cur.fetchone()[0]
        print(f"      {t:<15} {cnt} 行")

    # Step 2: 加载 ontology 模板
    print("\n[2] 加载 ontology 模板")
    ont_path = Path(__file__).parent / "data" / "platform-ont.ttl"
    ont = Graph().parse(str(ont_path), format="turtle")
    g = ont + Graph()  # 新图：本体 + 空白
    ex = Namespace("http://platform.com/")
    print(f"  ✓ 本体 {len(ont)} 条三元组")

    # Step 3: 跑 R2RML 映射
    print("\n[3] 跑 R2RML 映射")
    total = run_mapping(conn, g, ex)
    print(f"  ✓ 物化完成：{total} 个 Object 实例")

    # Step 4: 跑 SHACL 校验
    print("\n[4] SHACL Object Validation（看数据合规性）")
    conforms, report = validate_after_materialization(g, ex)
    if conforms:
        print(f"  ✅ 全部合规")
    else:
        report_str = report if isinstance(report, str) else report.decode()
        print(f"  ❌ 有违规：")
        import re
        for m in re.findall(r'sh:focusNode\s+(\S+).*?sh:resultMessage\s+"([^"]+)"', report_str, re.DOTALL):
            n = m[0].split("#")[-1] if "#" in m[0] else m[0]
            print(f"      - {n}: {m[1][:80]}")

    # Step 5: 跑验证查询
    print("\n[5] 物化后验证查询（Foundry Workshop 风格）")
    print(verify_queries(g, ex))

    # Step 6: 持久化
    output_path = Path(__file__).parent / "data" / "platform-data-mat.ttl"
    g.serialize(str(output_path), format="turtle")
    print(f"\n[6] 持久化：{output_path}")
    print(f"    三元组总数：{len(g)}")
    conn.close()

    print("\n" + "=" * 60)
    print("  ✅ 物化完成。可用 mcp_server.py 查这个图")
    print("=" * 60)


if __name__ == "__main__":
    main()
