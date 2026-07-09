"""Foundry Workshop 风格 HTML 仪表盘.

对齐 Palantir Foundry Workshop: 一个页面展示所有业务 Object.
- 顶部: KPI 卡片
- 中部: 订单全链路表格
- 底部: Action 历史时间线
"""
from pathlib import Path
from datetime import datetime
from rdflib import Graph, Namespace
from rdflib.plugins.sparql import prepareQuery
from rdflib.namespace import RDF, XSD

DATA_DIR = Path(__file__).parent / "data"
ont  = Graph().parse(str(DATA_DIR / "platform-ont.ttl"),    format="turtle")
data = Graph().parse(str(DATA_DIR / "platform-data.ttl"),   format="turtle")
# 加 namespace 让 SHACL 报告里 ex: 显示为 http://platform.com/
ex = Namespace("http://platform.com/")
g = ont + data
g.bind("ex", ex)

# === 取数据 ===
def get_kpis():
    kpis = {}
    q_rev = prepareQuery("""
    PREFIX ex: <http://platform.com/>
    SELECT (SUM(?amt) AS ?t) WHERE { ?inv a ex:Invoice ; ex:invoiceStatus "Paid" ; ex:invoiceAmount ?amt . }
    """)
    for r in g.query(q_rev):
        kpis["paid_total"] = float(r.t)
    q_pending = prepareQuery("""
    PREFIX ex: <http://platform.com/>
    SELECT (COUNT(?o) AS ?c) WHERE { ?o a ex:Order ; ex:orderStatus "Placed" . }
    """)
    for r in g.query(q_pending):
        kpis["pending"] = int(r.c)
    q_ship = prepareQuery("""
    PREFIX ex: <http://platform.com/>
    SELECT (COUNT(?o) AS ?c) WHERE { ?o a ex:Order ; ex:orderStatus "Shipped" . }
    """)
    for r in g.query(q_ship):
        kpis["shipping"] = int(r.c)
    q_risks = prepareQuery("""
    PREFIX ex: <http://platform.com/>
    SELECT (COUNT(?i) AS ?c) WHERE { ?i a ex:Invoice ; ex:invoiceStatus "Issued" . }
    """)
    for r in g.query(q_risks):
        kpis["risks"] = int(r.c)
    return kpis


def get_orders():
    q = prepareQuery("""
    PREFIX ex: <http://platform.com/>
    SELECT ?no ?customer ?total ?status ?date ?tracking ?shipStatus WHERE {
        ?o a ex:Order ;
           ex:orderNo ?no ;
           ex:orderTotalAmount ?total ;
           ex:orderStatus ?status ;
           ex:orderDate ?date ;
           ex:orderHasCustomer ?c .
        ?c ex:customerName ?customer .
        OPTIONAL {
            ?s ex:orderHasShipment ?o ;
              ex:shipmentTrackingNo ?tracking ;
              ex:shipmentStatus ?shipStatus .
        }
    } ORDER BY DESC(?date)
    """)
    return list(g.query(q))


def get_audit_log():
    q = prepareQuery("""
    PREFIX ex: <http://platform.com/>
    SELECT ?time ?emp ?result WHERE {
        { ?a a ex:ApproveOrder } UNION { ?a a ex:ReserveInventory } UNION
        { ?a a ex:CreateShipment } UNION { ?a a ex:AssignCustomer } .
        ?a ex:actionTime ?time ; ex:actionBy ?emp ; ex:actionResult ?result .
    } ORDER BY DESC(?time) LIMIT 10
    """)
    return list(g.query(q))


def get_object_types():
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
    return list(g.query(q))


def status_badge(s):
    colors = {
        "Placed":   "#9ca3af",
        "Paid":     "#3b82f6",
        "Shipped":  "#f59e0b",
        "Delivered": "#10b981",
        "Cancelled": "#ef4444",
    }
    bg = colors.get(s, "#6b7280")
    return f'<span class="badge" style="background:{bg}">{s}</span>'


def build_html():
    kpis = get_kpis()
    orders = get_orders()
    logs = get_audit_log()
    obj_types = get_object_types()

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>Palantir Foundry 风格仪表盘</title>
<style>
  * {{ font-family: -apple-system, "Helvetica Neue", "PingFang SC", sans-serif; box-sizing: border-box; }}
  body {{ margin: 0; padding: 20px; background: #0f172a; color: #e2e8f0; }}
  h1 {{ color: #f8fafc; font-size: 24px; margin: 0 0 20px 0; }}
  h2 {{ color: #cbd5e1; font-size: 16px; margin: 30px 0 12px 0; text-transform: uppercase; letter-spacing: 1px; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; }}
  .kpi {{ background: #1e293b; padding: 20px; border-radius: 8px; border-left: 4px solid #3b82f6; }}
  .kpi .label {{ color: #94a3b8; font-size: 12px; text-transform: uppercase; }}
  .kpi .value {{ color: #f1f5f9; font-size: 28px; font-weight: 700; margin-top: 4px; }}
  .kpi .value.green {{ color: #10b981; }}
  .kpi .value.orange {{ color: #f59e0b; }}
  .kpi .value.red {{ color: #ef4444; }}
  table {{ width: 100%; border-collapse: collapse; background: #1e293b; border-radius: 8px; overflow: hidden; }}
  th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #334155; }}
  th {{ background: #334155; color: #cbd5e1; font-weight: 600; font-size: 12px; text-transform: uppercase; }}
  tr:hover {{ background: #334155; }}
  .badge {{ padding: 4px 10px; border-radius: 12px; color: white; font-size: 11px; font-weight: 600; }}
  .timeline {{ background: #1e293b; padding: 20px; border-radius: 8px; border-left: 3px solid #10b981; }}
  .timeline .entry {{ display: flex; padding: 8px 0; border-bottom: 1px solid #334155; }}
  .timeline .time {{ width: 200px; color: #94a3b8; font-family: monospace; font-size: 12px; }}
  .timeline .result {{ color: #f1f5f9; font-weight: 600; }}
  .footer {{ color: #64748b; text-align: center; margin-top: 40px; font-size: 12px; }}
  .stat-box {{ background: #1e293b; padding: 12px; border-radius: 6px; text-align: center; }}
  .stat-box .num {{ font-size: 22px; color: #f1f5f9; font-weight: 700; }}
  .stat-box .name {{ color: #94a3b8; font-size: 11px; text-transform: uppercase; }}
  .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }}
  .header .ts {{ color: #94a3b8; font-size: 12px; font-family: monospace; }}
</style>
</head>
<body>
<div class="header">
  <h1>📊 订单履约平台 (Foundry 风格)</h1>
  <div class="ts">生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
</div>

<h2>📈 KPI 概览</h2>
<div class="grid">
  <div class="kpi">
    <div class="label">💰 已付款发票总额</div>
    <div class="value green">¥{kpis.get('paid_total', 0):,.0f}</div>
  </div>
  <div class="kpi">
    <div class="label">⏳ 待处理订单</div>
    <div class="value orange">{kpis.get('pending', 0)} 个</div>
  </div>
  <div class="kpi">
    <div class="label">🚚 运输中订单</div>
    <div class="value orange">{kpis.get('shipping', 0)} 个</div>
  </div>
  <div class="kpi">
    <div class="label">⚠️ 风险发票</div>
    <div class="value red">{kpis.get('risks', 0)} 个</div>
  </div>
</div>

<h2>📦 Object Type 分布</h2>
<div class="grid">
"""
    for row in obj_types:
        tname = str(row.type).split("/")[-1]
        html += f"""
  <div class="stat-box">
    <div class="num">{row.cnt}</div>
    <div class="name">{tname}</div>
  </div>
"""

    html += """
</div>

<h2>📋 订单履约全链路</h2>
<table>
<thead>
<tr>
  <th>订单号</th>
  <th>客户</th>
  <th>金额</th>
  <th>订单状态</th>
  <th>物流状态</th>
  <th>物流单号</th>
  <th>日期</th>
</tr>
</thead>
<tbody>
"""
    for row in orders:
        d = row.asdict()
        tracking = d.get('tracking') or "—"
        ship = d.get('shipStatus') or "—"
        html += f"""
<tr>
  <td><code>{d['no']}</code></td>
  <td>{d['customer']}</td>
  <td>¥{float(d['total']):,.2f}</td>
  <td>{status_badge(d['status'])}</td>
  <td>{ship}</td>
  <td><code>{tracking}</code></td>
  <td>{str(d['date'])[:10]}</td>
</tr>"""
    html += """
</tbody>
</table>

<h2>📜 Action 历史</h2>
<div class="timeline">
"""
    for row in logs:
        d = row.asdict()
        emp = str(d['emp']).split("/")[-1]
        t = str(d['time'])[:19]
        html += f"""
  <div class="entry">
    <div class="time">{t}</div>
    <div class="result">{d['result']}</div>
    <div style="color:#94a3b8; margin-left:20px;">by {emp}</div>
  </div>"""
    html += """
</div>

<div class="footer">
  🎨 Palantir Foundry 风格仪表盘 · 由 RDF/rdflib + pyshacl + SPARQL 驱动
</div>

</body>
</html>
"""
    return html


def main():
    print("=" * 60)
    print("  生成 Foundry 风格 HTML 仪表盘")
    print("=" * 60)
    html = build_html()
    out = Path(__file__).parent / "dashboard.html"
    out.write_text(html, encoding="utf-8")
    size_kb = out.stat().st_size / 1024
    print(f"\n✅ 写入 {out}  ({size_kb:.1f} KB)")
    print("   用浏览器打开看效果")


if __name__ == "__main__":
    main()
