"""Palantir AIP 风格 MCP Server.

让 Claude Desktop / Claude Code 能直接调本体:
- 查 Object（SPARQL 查询）
- 改 Object（触发 Action）
- 跑 Function（对账 / 统计）

使用方式:
  1. pip install mcp
  2. 在 Claude Desktop 配置中:
     {
       "mcpServers": {
         "platform": {
           "command": "python3",
           "args": ["/path/to/this/mcp_server.py"]
         }
       }
     }
  3. 重启 Claude Desktop，问业务问题

对应 Palantir AIP: A.I.P. = AIP Logic → Foundry Ontology → Source Data
"""
import os
import json
from datetime import datetime
from pathlib import Path
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.plugins.sparql import prepareQuery
from rdflib.namespace import RDF, XSD

# 加载本体
DATA_DIR = Path(__file__).parent / "data"
ont  = Graph().parse(str(DATA_DIR / "platform-ont.ttl"),    format="turtle")
data = Graph().parse(str(DATA_DIR / "platform-data.ttl"),   format="turtle")
g = ont + data

EX = Namespace("http://platform.com/")

# ============================================================
# 工具 1: 查订单（Foundry Object View 风格）
# ============================================================
def tool_query_orders(
    customer_name: str = None,
    status: str = None,
    min_amount: float = None,
    limit: int = 10
) -> str:
    """查订单. 模拟 Palantir Object View 过滤.

    Args:
        customer_name: 按客户名过滤（可选）
        status: 按状态过滤（Placed/Paid/Shipped/Delivered/Cancelled）
        min_amount: 最低金额（可选）
        limit: 返回条数

    Returns:
        格式化的订单列表（Markdown）
    """
    filters = ["?o a ex:Order", "?o ex:orderNo ?no", "?o ex:orderTotalAmount ?amt",
               "?o ex:orderStatus ?st", "?o ex:orderDate ?d"]
    if customer_name:
        filters.append("?o ex:orderHasCustomer ?c")
        filters.append("?c ex:customerName ?cname")
        filters.append(f'FILTER (CONTAINS(?cname, "{customer_name}"))')
    if status:
        filters.append(f'FILTER (?st = "{status}")')
    if min_amount is not None:
        filters.append(f'FILTER (?amt >= {min_amount})')

    select_extra = "?cname" if customer_name else ""
    sparql = f"""
    PREFIX ex: <http://platform.com/>
    SELECT ?no ?st ?amt ?d {select_extra} WHERE {{
        {' . '.join(filters)}
    }} ORDER BY DESC(?d) LIMIT {limit}
    """
    q = prepareQuery(sparql)
    results = list(g.query(q))

    if not results:
        return f"❌ 没找到匹配的订单"

    lines = [f"找到 {len(results)} 个订单：\n"]
    lines.append("| 订单号 | 状态 | 金额 | 日期 |" + (" 客户 |" if customer_name else ""))
    lines.append("| --- | --- | --- | --- |" + (" --- |" if customer_name else ""))
    for row in results:
        d = row.asdict()
        no = d['no']
        st = d['st']
        amt = float(d['amt'])
        dt = str(d['d'])[:10]
        line = f"| {no} | {st} | ¥{amt:,.2f} | {dt} |"
        if customer_name:
            line += f" {d.get('cname', '-')} |"
        lines.append(line)
    return "\n".join(lines)


# ============================================================
# 工具 2: 查订单详情（Object View 单条）
# ============================================================
def tool_get_order_detail(order_no: str) -> str:
    """查订单的所有信息（含 Item/物流/发票/付款/Action 历史）.

    Args:
        order_no: 订单号（如 O0000000001）
    """
    q = prepareQuery("""
    PREFIX ex: <http://platform.com/>
    SELECT ?item ?product ?qty ?price ?shipment ?invoice ?paid ?action ?by ?result WHERE {
        ?o a ex:Order ; ex:orderNo ?no .
        FILTER (STR(?no) = ?orderNo)
        OPTIONAL {
            ?item ex:orderHasItem ?o ;
                  ex:orderItemForProduct ?product ;
                  ex:itemQuantity ?qty ;
                  ex:itemUnitPrice ?price .
        }
        OPTIONAL {
            ?shipment ex:orderHasShipment ?o ;
                      ex:shipmentTrackingNo ?trk ;
                      ex:shipmentStatus ?sst .
            BIND(CONCAT(STR(?trk), " [", STR(?sst), "]") AS ?shipment)
        }
        OPTIONAL {
            ?invoice ex:orderHasInvoice ?o ; ex:invoiceNo ?invNo ; ex:invoiceStatus ?invSt .
            BIND(CONCAT(STR(?invNo), " [", STR(?invSt), "]") AS ?invoice)
        }
        OPTIONAL {
            ?paid ex:paymentForInvoice ?i2 ; ex:paymentAmount ?pAmt .
            ?i2 ex:orderHasInvoice ?o .
            BIND(CONCAT("¥", STR(?pAmt)) AS ?paid)
        }
        OPTIONAL {
            ?action a ex:action ; ex:actionOnOrder ?o ; ex:actionBy ?by ; ex:actionResult ?result ; ex:actionTime ?t .
        }
    } ORDER BY ?t
    """)
    results = list(g.query(q, initBindings={'orderNo': Literal(order_no, datatype=XSD.string)}))

    if not results:
        return f"❌ 订单 {order_no} 不存在"

    out = [f"📋 订单 {order_no} 详情\n"]

    # 聚合所有行
    items = []
    shipments = set()
    invoices = set()
    payments = set()
    actions = []
    for r in results:
        d = r.asdict()
        if d.get('item'):
            items.append((str(d['item']).split('/')[-1],
                          str(d['product']).split('/')[-1],
                          int(d['qty']), float(d['price'])))
        if d.get('shipment'):
            shipments.add(d['shipment'])
        if d.get('invoice'):
            invoices.add(d['invoice'])
        if d.get('paid'):
            payments.add(d['paid'])
        if d.get('action'):
            actions.append((str(d['action']).split('/')[-1],
                            str(d['by']).split('/')[-1],
                            d['result'], str(d.get('t', ''))))

    if items:
        out.append("📦 商品：")
        for item, product, qty, price in items[:10]:
            out.append(f"   - {item} ({product}) x {qty} = ¥{price*qty:,.2f}")

    if shipments:
        out.append("\n🚚 物流：")
        for s in shipments:
            out.append(f"   - {s}")

    if invoices:
        out.append("\n🧾 发票：")
        for i in invoices:
            out.append(f"   - {i}")

    if payments:
        out.append("\n💰 付款：")
        for p in payments:
            out.append(f"   - {p}")

    if actions:
        out.append(f"\n📜 Action 历史（{len(actions)} 条）：")
        for act, by, result, t in actions[-5:]:
            ts = t[:19] if t else "?"
            out.append(f"   - {ts} {by} → {result}")

    return "\n".join(out)


# ============================================================
# 工具 3: 订单履约 Dashboard（KPI）
# ============================================================
def tool_dashboard_kpi() -> str:
    """看业务 KPI（Foundry Quiver 风格）.

    Returns:
        4 个关键指标的格式化字符串
    """
    out = ["📊 订单履约 KPI\n"]

    q1 = prepareQuery("""
    PREFIX ex: <http://platform.com/>
    SELECT (SUM(?amt) AS ?total) WHERE {
        ?inv a ex:Invoice ; ex:invoiceStatus "Paid" ; ex:invoiceAmount ?amt .
    }
    """)
    for r in g.query(q1):
        out.append(f"💰 已付款发票总额：¥{float(r.total):,.2f}")

    q2 = prepareQuery("""
    PREFIX ex: <http://platform.com/>
    SELECT (COUNT(?o) AS ?cnt) WHERE { ?o a ex:Order ; ex:orderStatus "Placed" . }
    """)
    for r in g.query(q2):
        out.append(f"⏳ 待处理订单：{r.cnt} 个")

    q3 = prepareQuery("""
    PREFIX ex: <http://platform.com/>
    SELECT (COUNT(?o) AS ?cnt) WHERE { ?o a ex:Order ; ex:orderStatus "Shipped" . }
    """)
    for r in g.query(q3):
        out.append(f"🚚 运输中订单：{r.cnt} 个")

    q4 = prepareQuery("""
    PREFIX ex: <http://platform.com/>
    SELECT ?inv ?amt ?ord WHERE {
        ?inv a ex:Invoice ; ex:invoiceStatus "Issued" ; ex:invoiceAmount ?amt .
        ?inv ex:orderHasInvoice ?ord .
    }
    """)
    risks = list(g.query(q4))
    if risks:
        out.append(f"⚠️  风险（已开票未付款）：{len(risks)} 个订单")
        for inv, amt, ord in risks[:5]:
            inv_short = str(inv).split("/")[-1]
            ord_short = str(ord).split("/")[-1]
            out.append(f"   - {inv_short} (¥{float(amt):,.2f}) → 订单 {ord_short}")

    return "\n".join(out)


# ============================================================
# 工具 4: 订单对账（Function 风格）
# ============================================================
def tool_reconcile_orders() -> str:
    """对账：每个订单的声明金额 vs 从 OrderItem 算出的真实金额.

    Returns:
        有差异的订单列表
    """
    q = prepareQuery("""
    PREFIX ex: <http://platform.com/>
    SELECT ?no ?declared ?order WHERE {
        ?order a ex:Order ; ex:orderNo ?no ; ex:orderTotalAmount ?declared .
    }
    """)
    orders = list(g.query(q))

    issues = []
    for row in orders:
        d = row.asdict()
        no = d['no']
        order = d['order']
        declared = float(d['declared'])
        # 算实际
        q2 = prepareQuery("""
        PREFIX ex: <http://platform.com/>
        SELECT (SUM(?qty * ?price) AS ?actual) WHERE {
            ?item ex:orderHasItem ?o ; ex:itemQuantity ?qty ; ex:itemUnitPrice ?price .
            FILTER (?o = ?order)
        }
        """)
        result = list(g.query(q2, initBindings={'order': order}))
        actual = float(result[0].actual) if result and result[0].actual else 0.0
        diff = actual - declared
        if abs(diff) > 0.01:
            issues.append((no, declared, actual, diff))

    if not issues:
        return "✅ 所有订单金额对账一致"

    out = [f"⚠️  发现 {len(issues)} 个订单金额不一致：\n"]
    out.append("| 订单号 | 声明金额 | 实际金额 | 差异 |")
    out.append("| --- | --- | --- | --- |")
    for no, declared, actual, diff in issues:
        sign = "+" if diff > 0 else ""
        out.append(f"| {no} | ¥{declared:,.2f} | ¥{actual:,.2f} | {sign}¥{diff:,.2f} |")
    return "\n".join(out)


# ============================================================
# 工具 5: Action - 审核订单
# ============================================================
def tool_approve_order(order_no: str, approver_emp_id: str) -> str:
    """Action: 审核订单（Placed → Paid），写 action 历史.

    Args:
        order_no: 订单号
        approver_emp_id: 审核人 ID（如 E0001）

    Returns:
        成功/失败消息
    """
    q = prepareQuery("""
    PREFIX ex: <http://platform.com/>
    SELECT ?o ?st WHERE {
        ?o a ex:Order ; ex:orderNo ?no .
        FILTER (STR(?no) = ?orderNo)
    }
    """)
    results = list(g.query(q, initBindings={'orderNo': Literal(order_no, datatype=XSD.string)}))
    if not results:
        return f"❌ 订单 {order_no} 不存在"

    order = results[0].o
    if str(results[0].st) != "Placed":
        return f"❌ 订单 {order_no} 状态 {results[0].st}，不能审核（仅 Placed 可审核）"

    # 找审核人
    q_emp = prepareQuery("""
    PREFIX ex: <http://platform.com/>
    SELECT ?emp WHERE {
        ?emp a ex:Employee ; ex:employeeId ?id .
        FILTER (STR(?id) = ?empId)
    }
    """)
    emp_results = list(g.query(q_emp, initBindings={'empId': Literal(approver_emp_id, datatype=XSD.string)}))
    if not emp_results:
        return f"❌ 审核人 {approver_emp_id} 不存在"
    approver = emp_results[0].emp

    # 改状态
    g.remove((order, EX.orderStatus, None))
    g.add((order, EX.orderStatus, Literal("Paid")))

    # 写 action 历史
    new_action = URIRef(f"http://platform.com/act-aip-{datetime.now().strftime('%H%M%S%f')}")
    g.add((new_action, RDF.type, EX.action))
    g.add((new_action, RDF.type, EX.ApproveOrder))
    g.add((new_action, EX.actionOnOrder, order))
    g.add((new_action, EX.actionBy, approver))
    g.add((new_action, EX.actionTime, Literal(datetime.now().isoformat(), datatype=XSD.dateTime)))
    g.add((new_action, EX.actionResult, Literal("Approved via AIP")))

    # 持久化
    g.serialize(str(DATA_DIR / "platform-data.ttl"), format="turtle")

    return f"✅ 订单 {order_no} 审核通过 (Placed → Paid)\n  审核人：{approver_emp_id}\n  Action: {str(new_action).split('/')[-1]}"


# ============================================================
# 工具 6: Action - 分配库存
# ============================================================
def tool_reserve_inventory(order_no: str, warehouse_emp_id: str) -> str:
    """Action: 分配库存. 检查每个 OrderItem 的产品在哪个仓库有库存,
    然后把 stockReservedQty 增加.

    Args:
        order_no: 订单号
        warehouse_emp_id: 仓库员工 ID
    """
    # 找订单
    q = prepareQuery("""
    PREFIX ex: <http://platform.com/>
    SELECT ?o WHERE { ?o a ex:Order ; ex:orderNo ?no . FILTER (STR(?no) = ?orderNo) }
    """)
    results = list(g.query(q, initBindings={'orderNo': Literal(order_no, datatype=XSD.string)}))
    if not results:
        return f"❌ 订单 {order_no} 不存在"
    order = results[0].o

    # 找该订单的所有 OrderItem
    q_items = prepareQuery("""
    PREFIX ex: <http://platform.com/>
    SELECT ?item ?product ?qty WHERE {
        ?item ex:orderHasItem ?o ; ex:orderItemForProduct ?product ; ex:itemQuantity ?qty .
    }
    """)
    items = list(g.query(q_items, initBindings={'o': order}))
    if not items:
        return f"❌ 订单 {order_no} 无 OrderItem"

    out = [f"📦 为订单 {order_no} 分配库存：\n"]
    all_ok = True
    for item, product, qty in items:
        # 找最近的有库存的 warehouse
        q_stock = prepareQuery("""
        PREFIX ex: <http://platform.com/>
        SELECT ?stock ?available WHERE {
            ?stock ex:stockOfProduct ?p ; ex:stockQuantity ?total ; ex:stockReservedQty ?reserved .
            BIND(?total - ?reserved AS ?available)
            FILTER (?p = ?product && ?available >= ?qty)
        }
        """)
        stock_results = list(g.query(q_stock, initBindings={'product': product, 'qty': qty}))
        if not stock_results:
            all_ok = False
            out.append(f"  ❌ 产品 {str(product).split('/')[-1]} 库存不足")
            continue

        stock = stock_results[0].stock
        old_reserved = list(g.objects(stock, EX.stockReservedQty))[0]
        g.remove((stock, EX.stockReservedQty, old_reserved))
        new_reserved = int(old_reserved) + int(qty)
        g.add((stock, EX.stockReservedQty, Literal(new_reserved, datatype=XSD.integer)))

        out.append(f"  ✅ {str(product).split('/')[-1]} x {qty}  ←  {str(stock).split('/')[-1]} (预留从 {old_reserved} → {new_reserved})")

    g.serialize(str(DATA_DIR / "platform-data.ttl"), format="turtle")
    out.append(f"\n{ '✅ 全部成功' if all_ok else '⚠️  部分失败'}")
    return "\n".join(out)


# ============================================================
# 工具 7: 客户分配
# ============================================================
def tool_assign_customer(customer_name: str, sales_emp_id: str) -> str:
    """Action: 分配客户给销售.

    Args:
        customer_name: 客户名
        sales_emp_id: 销售员工 ID
    """
    q = prepareQuery("""
    PREFIX ex: <http://platform.com/>
    SELECT ?c ?emp WHERE {
        ?c ex:customerName ?cn .
        ?emp a ex:Employee ; ex:employeeId ?id .
        FILTER (CONTAINS(STR(?cn), ?custName) && STR(?id) = ?empId)
    }
    """)
    results = list(g.query(q, initBindings={'custName': Literal(customer_name), 'empId': Literal(sales_emp_id)}))
    if not results:
        return f"❌ 找不到客户 '{customer_name}' 或销售 {sales_emp_id}"

    cust, sales = results[0].c, results[0].emp
    g.add((cust, EX.customerAssignedTo, sales))

    # 写 action
    new_action = URIRef(f"http://platform.com/act-aip-{datetime.now().strftime('%H%M%S%f')}")
    g.add((new_action, RDF.type, EX.action))
    g.add((new_action, RDF.type, EX.AssignCustomer))
    g.add((new_action, EX.actionBy, sales))
    g.add((new_action, EX.actionTime, Literal(datetime.now().isoformat(), datatype=XSD.dateTime)))
    g.add((new_action, EX.actionResult, Literal(f"{customer_name} → {sales_emp_id}")))

    g.serialize(str(DATA_DIR / "platform-data.ttl"), format="turtle")
    return f"✅ 客户 {customer_name} 分配给销售 {sales_emp_id}"


# ============================================================
# MCP Server 入口
# ============================================================
try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent

    app = Server("platform-aip")

    @app.list_tools()
    async def list_tools():
        return [
            Tool(
                name="query_orders",
                description="查订单。可按客户、状态、金额过滤。",
                input_schema={
                    "type": "object",
                    "properties": {
                        "customer_name": {"type": "string", "description": "客户名（模糊匹配）"},
                        "status": {"type": "string", "enum": ["Placed", "Paid", "Shipped", "Delivered", "Cancelled"]},
                        "min_amount": {"type": "number", "description": "最低金额"},
                        "limit": {"type": "integer", "default": 10, "description": "返回条数"}
                    }
                }
            ),
            Tool(
                name="get_order_detail",
                description="查订单完整信息（Item/物流/发票/付款/Action）",
                input_schema={
                    "type": "object",
                    "properties": {
                        "order_no": {"type": "string", "description": "订单号，如 O0000000001"}
                    },
                    "required": ["order_no"]
                }
            ),
            Tool(
                name="dashboard_kpi",
                description="看业务 KPI（已付款/待处理/运输中/风险）",
                input_schema={"type": "object", "properties": {}}
            ),
            Tool(
                name="reconcile_orders",
                description="对账：检查每个订单的金额是否和 OrderItem 一致",
                input_schema={"type": "object", "properties": {}}
            ),
            Tool(
                name="approve_order",
                description="Action: 审核订单（Placed → Paid），写 action 历史",
                input_schema={
                    "type": "object",
                    "properties": {
                        "order_no": {"type": "string"},
                        "approver_emp_id": {"type": "string", "description": "审核人 ID，如 E0001"}
                    },
                    "required": ["order_no", "approver_emp_id"]
                }
            ),
            Tool(
                name="reserve_inventory",
                description="Action: 分配库存（给订单预留库存）",
                input_schema={
                    "type": "object",
                    "properties": {
                        "order_no": {"type": "string"},
                        "warehouse_emp_id": {"type": "string"}
                    },
                    "required": ["order_no", "warehouse_emp_id"]
                }
            ),
            Tool(
                name="assign_customer",
                description="Action: 分配客户给销售",
                input_schema={
                    "type": "object",
                    "properties": {
                        "customer_name": {"type": "string"},
                        "sales_emp_id": {"type": "string"}
                    },
                    "required": ["customer_name", "sales_emp_id"]
                }
            ),
        ]

    @app.call_tool()
    async def call_tool(name: str, arguments: dict):
        if name == "query_orders":
            result = tool_query_orders(**arguments)
        elif name == "get_order_detail":
            result = tool_get_order_detail(**arguments)
        elif name == "dashboard_kpi":
            result = tool_dashboard_kpi()
        elif name == "reconcile_orders":
            result = tool_reconcile_orders()
        elif name == "approve_order":
            result = tool_approve_order(**arguments)
        elif name == "reserve_inventory":
            result = tool_reserve_inventory(**arguments)
        elif name == "assign_customer":
            result = tool_assign_customer(**arguments)
        else:
            result = f"❌ 未知工具: {name}"
        return [TextContent(type="text", text=result)]

    if __name__ == "__main__":
        import sys
        if "--mcp" in sys.argv:
            import asyncio
            from mcp.server.stdio import stdio_server
            async def main():
                async with stdio_server() as (read_stream, write_stream):
                    await app.run(read_stream, write_stream, app.create_initialization_options())
            asyncio.run(main())
        else:
            print("🚀 Palantir Foundry 风格 AIP（CLI 演示模式）")
            print("   加 --mcp 参数启动 MCP Server")
            print("=" * 60)
            print("\n[1] 查订单（customer=华为）")
            print(tool_query_orders(customer_name="华为", limit=5))
            print("\n[2] 订单详情")
            print(tool_get_order_detail("O0000000001"))
            print("\n[3] KPI")
            print(tool_dashboard_kpi())
            print("\n[4] 对账")
            print(tool_reconcile_orders())
            print("\n[5] 审核订单")
            print(tool_approve_order("O0000000004", "E0001"))
            print("\n[6] 分配库存")
            print(tool_reserve_inventory("O0000000002", "E0005"))
            print("\n[7] 客户分配")
            print(tool_assign_customer("美的", "E0001"))

except ImportError:
    # MCP 没装 → 退化为 CLI 演示
    if __name__ == "__main__":
        print("⚠️  mcp 库未装（pip install mcp），进入 CLI 演示模式")
        print("=" * 60)
        print("  Palantir AIP 风格本体平台（CLI 演示）")
        print("=" * 60)
        print("\n[示例 1] 查订单（customer=华为）")
        print(tool_query_orders(customer_name="华为", limit=5))
        print("\n[示例 2] 订单详情")
        print(tool_get_order_detail("O0000000001"))
        print("\n[示例 3] KPI")
        print(tool_dashboard_kpi())
        print("\n[示例 4] 对账")
        print(tool_reconcile_orders())
        print("\n[示例 5] 审核订单")
        print(tool_approve_order("O0000000004", "E0001"))
        print("\n[示例 6] 分配库存")
        print(tool_reserve_inventory("O0000000002", "E0005"))
        print("\n[示例 7] 客户分配")
        print(tool_assign_customer("美的", "E0001"))
