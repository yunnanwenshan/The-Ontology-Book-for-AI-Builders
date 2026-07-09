"""Palantir Foundry 风格本体平台演示.

对齐 Palantir Foundry 概念:
- Object Type + Property  -> RDF owl:Class + DatatypeProperty
- Link Type               -> RDF owl:ObjectProperty (有 owl:inverseOf)
- Action Type            -> 业务动作（如 ApproveOrder, ReserveInventory）
- Function               -> Python 函数（带副作用的实际业务逻辑）
- SHACL                  -> Object Validation
- SPARQL                 -> Object View / 仪表盘查询
"""
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import XSD
from rdflib.plugins.sparql import prepareQuery
from pyshacl import validate
from datetime import datetime
import json

EX = Namespace("http://platform.com/")

# ============================================================
# 1. 加载 Ontology + Data + Shapes
# ============================================================
ont    = Graph().parse("data/platform-ont.ttl",    format="turtle")
data   = Graph().parse("data/platform-data.ttl",   format="turtle")
shapes = Graph().parse("data/platform-shapes.ttl", format="turtle")
g = ont + data

print("=" * 60)
print("  Palantir Foundry 风格本体平台 Demo")
print("=" * 60)

# ============================================================
# 2. SHACL Object Validation（对应 Foundry 的 Object Validation）
# ============================================================
conforms, report_g, _ = validate(g, shacl_graph=shapes)
print(f"\n[1] SHACL 验证: {'✅ 所有 Object 有效' if conforms else '❌ 有 Object 不合规'}")

if not conforms:
    report_str = report_g.serialize(format="turtle")
    import re
    matches = re.findall(
        r'sh:focusNode\s+(\S+).*?sh:resultMessage\s+"([^"]+)"',
        report_str, re.DOTALL
    )
    for node, msg in matches:
        node_short = node.split("/")[-1] if "#" in node else node
        print(f"     ❌ {node_short}: {msg[:80]}")

# ============================================================
# 3. Object View（对应 Foundry Object Explorer）
# ============================================================
print(f"\n[2] Object 概览（Object Explorer）")
q = prepareQuery("""
PREFIX ex: <http://platform.com/>
SELECT ?type (COUNT(?o) AS ?cnt) WHERE {
    ?o a ?type .
    FILTER (
        ?type = ex:Employee || ?type = ex:Customer || ?type = ex:Product ||
        ?type = ex:Warehouse || ?type = ex:InventoryItem ||
        ?type = ex:Order || ?type = ex:OrderItem || ?type = ex:Shipment ||
        ?type = ex:Invoice || ?type = ex:Payment
    )
} GROUP BY ?type
""")
for r in g.query(q):
    type_name = r.type.split("/")[-1]
    print(f"     {type_name:<18} {r.cnt} 个")

# ============================================================
# 4. Link Type 关系图（对应 Foundry Graph View）
# ============================================================
print(f"\n[3] Link Type 关系图（节选）")
link_queries = [
    ("orderHasCustomer ↔ customerHasOrder", """
        PREFIX ex: <http://platform.com/>
        SELECT (COUNT(*) AS ?uses) WHERE { ?s ex:orderHasCustomer ?o } """),
    ("orderHasItem ↔ itemOfOrder", """
        PREFIX ex: <http://platform.com/>
        SELECT (COUNT(*) AS ?uses) WHERE { ?s ex:orderHasItem ?o } """),
    ("orderHasShipment ↔ shipmentOfOrder", """
        PREFIX ex: <http://platform.com/>
        SELECT (COUNT(*) AS ?uses) WHERE { ?s ex:orderHasShipment ?o } """),
    ("orderHasInvoice ↔ invoiceForOrder", """
        PREFIX ex: <http://platform.com/>
        SELECT (COUNT(*) AS ?uses) WHERE { ?s ex:orderHasInvoice ?o } """),
    ("orderHandledBy ↔ employeeHandlesOrder", """
        PREFIX ex: <http://platform.com/>
        SELECT (COUNT(*) AS ?uses) WHERE { ?s ex:orderHandledBy ?o } """),
]
for label, sq in link_queries:
    q = prepareQuery(sq)
    results = list(g.query(q))
    uses = int(results[0].uses) if results else 0
    print(f"     {label}  用了 {uses} 次")

# ============================================================
# 5. Function: 计算订单实际金额（对账用）
# ============================================================
def fn_calculate_order_total(order_uri: str) -> float:
    """对账 Function: 从 OrderItem 实际计算总金额."""
    order = URIRef(order_uri)
    bound_q = prepareQuery("""
    PREFIX ex: <http://platform.com/>
    SELECT (SUM(?qty * ?price) AS ?total) WHERE {
        ?item ex:orderHasItem ?o ;
              ex:itemQuantity ?qty ;
              ex:itemUnitPrice ?price .
    }
    """)
    result = list(g.query(bound_q, initBindings={'o': order}))
    return float(result[0].total) if result and result[0].total else 0.0

print(f"\n[4] Function: 订单实际金额（重新计算）")
q = prepareQuery("PREFIX ex: <http://platform.com/> SELECT ?o ?no ?amt WHERE { ?o a ex:Order ; ex:orderNo ?no ; ex:orderTotalAmount ?amt . }")
for r in g.query(q):
    order_uri = r.o
    actual = fn_calculate_order_total(str(order_uri))
    declared = float(r.amt)
    diff = actual - declared
    status = "✅ 一致" if abs(diff) < 0.01 else f"❌ 差异 ¥{diff:.2f}"
    print(f"     {r.no}  声明 ¥{declared:>10,.2f}  /  实际 ¥{actual:>10,.2f}  {status}")

# ============================================================
# 6. Action: ApproveOrder（修改 Order 状态）
# ============================================================
def action_approve_order(order_uri: str, approver_emp: str) -> dict:
    """Action: 审核订单. 触发副作用: 改状态 + 写 action 历史."""
    order = URIRef(order_uri)
    approver = URIRef(approver_emp)
    # 校验：订单当前状态
    cur_status = list(g.query("""
    PREFIX ex: <http://platform.com/>
    SELECT ?s WHERE { ?o ex:orderStatus ?s . FILTER (?o = ?order) }
    """, initBindings={'order': order}))
    if not cur_status:
        return {"ok": False, "msg": "订单不存在"}
    if str(cur_status[0].s) != "Placed":
        return {"ok": False, "msg": f"状态 {cur_status[0].s} 不能审核"}

    # 副作用 1: 改状态
    g.remove((order, EX.orderStatus, None))
    g.add((order, EX.orderStatus, Literal("Paid")))

    # 副作用 2: 写 action 历史
    new_action = EX[f"act-new-{datetime.now().strftime('%H%M%S')}"]
    g.add((new_action, RDF.type, EX.action)) if False else None  # noqa
    from rdflib.namespace import RDF
    g.add((new_action, RDF.type, EX.action))
    g.add((new_action, RDF.type, EX.ApproveOrder))
    g.add((new_action, EX.actionOnOrder, order))
    g.add((new_action, EX.actionBy, approver))
    g.add((new_action, EX.actionTime, Literal(datetime.now().isoformat(), datatype=XSD.dateTime)))
    g.add((new_action, EX.actionResult, Literal("Approved")))

    return {"ok": True, "msg": "审核通过"}

print(f"\n[5] Action: ApproveOrder（试试审核 O0000000004）")
result = action_approve_order("http://platform.com/ord-004", "http://platform.com/emp-001")
print(f"     结果: {result}")

# ============================================================
# 7. Action: ReserveInventory（分配库存）
# ============================================================
def action_reserve_inventory(order_uri: str, warehouse_emp: str) -> dict:
    """Action: 分配库存. 校验每个 OrderItem 的产品在该仓库有足够库存."""
    order = URIRef(order_uri)
    approver = URIRef(warehouse_emp)
    # 找该订单的所有 OrderItem
    items = list(g.query("""
    PREFIX ex: <http://platform.com/>
    SELECT ?item ?product ?qty WHERE {
        ?item ex:orderHasItem ?o ;
               ex:orderItemForProduct ?product ;
               ex:itemQuantity ?qty .
        FILTER (?o = ?order)
    }
    """, initBindings={'order': order}))

    if not items:
        return {"ok": False, "msg": "订单无 OrderItem"}

    reservations = []
    for item, product, qty in items:
        # 找最近的库存
        stocks = list(g.query("""
        PREFIX ex: <http://platform.com/>
        SELECT ?stock ?available WHERE {
            ?stock ex:stockOfProduct ?p ;
                   ex:stockQuantity ?total ;
                   ex:stockReservedQty ?reserved .
            BIND(?total - ?reserved AS ?available)
            FILTER (?p = ?product && ?available >= ?qty)
        }
        """, initBindings={'product': product, 'qty': qty}))
        if not stocks:
            return {"ok": False, "msg": f"产品 {product.split('#')[-1]} 库存不足"}
        stock = stocks[0].stock
        # 副作用: 增加 stockReservedQty
        from rdflib.namespace import XSD
        old = list(g.objects(stock, EX.stockReservedQty))[0]
        g.remove((stock, EX.stockReservedQty, old))
        g.add((stock, EX.stockReservedQty, Literal(int(old) + int(qty), datatype=XSD.integer)))
        reservations.append((str(product), int(qty), str(stock)))

    return {"ok": True, "msg": "已预留", "details": reservations}

print(f"\n[6] Action: ReserveInventory（试给 ord-002 分配库存）")
result = action_reserve_inventory("http://platform.com/ord-002", "http://platform.com/emp-005")
print(f"     结果: {result}")

# ============================================================
# 8. Dashboard：跨 Object 的业务视图（Foundry Workshop 风格）
# ============================================================
print(f"\n[7] Dashboard: 订单履约全链路（Foundry Workshop 风格）")
q = prepareQuery("""
PREFIX ex: <http://platform.com/>
SELECT ?orderNo ?customer ?total ?orderStatus ?tracking ?shipStatus WHERE {
    ?o a ex:Order ;
       ex:orderNo ?orderNo ;
       ex:orderTotalAmount ?total ;
       ex:orderStatus ?orderStatus ;
       ex:orderHasCustomer ?c .
    ?c ex:customerName ?customer .
    OPTIONAL {
        ?s ex:orderHasShipment ?o .
        ?s ex:shipmentTrackingNo ?tracking ;
           ex:shipmentStatus ?shipStatus .
    }
} ORDER BY ?orderNo
""")
for r in g.query(q):
    o_no = r.orderNo
    cust = r.customer
    total = float(r.total)
    o_st = r.orderStatus
    tracking = r.tracking or "（无）"
    s_st = r.shipStatus or "（无）"
    print(f"     {o_no}  {cust:<10}  ¥{total:>10,.2f}  订单[{o_st:<10}]  物流[{s_st:<10}]  {tracking}")

# ============================================================
# 9. KPI 卡片（Foundry Quiver 风格）
# ============================================================
print(f"\n[8] KPI 卡片")
q_rev = prepareQuery("""
PREFIX ex: <http://platform.com/>
SELECT (SUM(?amt) AS ?total) WHERE {
    ?inv a ex:Invoice ; ex:invoiceStatus "Paid" ; ex:invoiceAmount ?amt .
}
""")
for r in g.query(q_rev):
    print(f"     💰 已付款发票总额: ¥{float(r.total):,.2f}")

q_aov = prepareQuery("""
PREFIX ex: <http://platform.com/>
SELECT (COUNT(?o) AS ?cnt) WHERE { ?o a ex:Order . FILTER EXISTS { ?o ex:orderStatus "Placed" } }
""")
for r in g.query(q_aov):
    print(f"     ⏳ 待处理订单: {r.cnt} 个")

q_ship = prepareQuery("""
PREFIX ex: <http://platform.com/>
SELECT (COUNT(?o) AS ?cnt) WHERE { ?o a ex:Order ; ex:orderStatus "Shipped" . }
""")
for r in g.query(q_ship):
    print(f"     🚚 运输中订单: {r.cnt} 个")

q_alert = prepareQuery("""
PREFIX ex: <http://platform.com/>
SELECT ?o WHERE {
    ?inv a ex:Invoice ; ex:invoiceStatus "Issued" ; ex:orderHasInvoice ?o .
    ?o ex:orderTotalAmount ?amt .
}
""")
alerts = list(g.query(q_alert))
print(f"     ⚠️  风险（已开票未付款）: {len(alerts)} 个订单")

# ============================================================
print(f"\n[9] Audit Log: 最近 10 个 Action")
# 10. Action 历史（Foundry Audit Log 风格）
q9 = prepareQuery("""
PREFIX ex: <http://platform.com/>
SELECT ?time ?order ?emp ?result WHERE {
    { ?a a ex:ApproveOrder } UNION { ?a a ex:ReserveInventory } UNION
    { ?a a ex:CreateShipment } UNION { ?a a ex:AssignCustomer } .
    ?a ex:actionTime ?time ; ex:actionBy ?emp ; ex:actionResult ?result .
    OPTIONAL { ?a ex:actionOnOrder ?orderNode }
    BIND(IF(BOUND(?orderNode), STRAFTER(STR(?orderNode), "/"), "-") AS ?order)
} ORDER BY DESC(?time) LIMIT 10
""")
for r in g.query(q9):
    d = r.asdict()
    order = d['order'].split("/")[-1] if d['order'] != '-' else '-'
    emp = d['emp'].split("/")[-1]
    print(f"     {d['time']}  {emp}  订单 {order}  → {d['result']}")

g.serialize("data/platform-data-updated.ttl", format="turtle")
print(f"[保存] data/platform-data-updated.ttl")
print("=" * 60)
print("  ✅ 演示完成")
print("=" * 60)
