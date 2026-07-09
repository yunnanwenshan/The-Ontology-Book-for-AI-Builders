"""客服本体: 6 个常见查询."""
from rdflib import Graph
from rdflib.plugins.sparql import prepareQuery
from pyshacl import validate

# 加载
ont  = Graph().parse("data/cs-ont.ttl",     format="turtle")
data = Graph().parse("data/cs-data.ttl",    format="turtle")
shapes = Graph().parse("data/cs-shapes.ttl", format="turtle")
g = ont + data

# SHACL 校验
conforms, _, _ = validate(g, shacl_graph=shapes)
print(f"数据校验：{'✅ 通过' if conforms else '❌ 失败'}\n")

# Q1: 客户最近订单
q1 = prepareQuery("""
PREFIX ex: <http://shop.com/>
SELECT ?order ?date ?amount ?status WHERE {
    ?order a ex:Order ;
           ex:customer ex:cust-001 ;
           ex:orderDate ?date ;
           ex:amount ?amount ;
           ex:status ?status .
} ORDER BY DESC(?date) LIMIT 3
""")
print("Q1: 客户 001 最近 3 个订单")
for r in g.query(q1):
    print(f"  {r.order.split('#')[-1]}  {r.date}  ¥{r.amount}  [{r.status}]")
print()

# Q2: 物流状态
q2 = prepareQuery("""
PREFIX ex: <http://shop.com/>
SELECT ?order ?tracking ?location ?updated WHERE {
    ?order a ex:Order ;
           ex:customer ex:cust-001 ;
           ex:status "Shipped" .
    ?ship a ex:Shipment ;
          ex:shipmentOf ?order ;
          ex:trackingNo ?tracking ;
          ex:currentLocation ?location ;
          ex:lastUpdate ?updated .
}
""")
print("Q2: 已发货订单的物流")
for r in g.query(q2):
    print(f"  {r.order.split('#')[-1]}  {r.tracking}  {r.location}  ({r.updated})")
print()

# Q3: 退货状态
q3 = prepareQuery("""
PREFIX ex: <http://shop.com/>
SELECT ?return ?order ?reason ?refundStatus WHERE {
    ?return a ex:Return ;
            ex:returnOf ?order ;
            ex:reason ?reason ;
            ex:refundStatus ?refundStatus ;
            ex:requestedBy ex:cust-001 .
}
""")
print("Q3: 客户 001 的退货")
for r in g.query(q3):
    d = r.asdict()
    r_id = d['return'].split('#')[-1]
    o_id = d['order'].split('#')[-1]
    print(f"  {r_id}  订单 {o_id}  原因 {d['reason']}  状态 {d['refundStatus']}")
print()

# Q4: 未处理的工单
q4 = prepareQuery("""
PREFIX ex: <http://shop.com/>
SELECT ?ticket ?subject ?priority WHERE {
    ?ticket a ex:Ticket ;
            ex:subject ?subject ;
            ex:priority ?priority ;
            ex:status "Open" .
} ORDER BY ?priority
""")
print("Q4: 未处理的工单（按优先级）")
priority_order = {"Critical": 1, "High": 2, "Medium": 3, "Low": 4}
results = list(g.query(q4))
results.sort(key=lambda r: priority_order.get(r.priority, 5))
for r in results:
    print(f"  [{r.priority}]  {r.ticket.split('#')[-1]}  {r.subject}")
print()

# Q5: 各状态的工单数
q5 = prepareQuery("""
PREFIX ex: <http://shop.com/>
SELECT ?status (COUNT(?t) AS ?cnt) WHERE {
    ?t a ex:Ticket ;
       ex:status ?status .
} GROUP BY ?status
""")
print("Q5: 工单状态分布")
for r in g.query(q5):
    print(f"  {r.status}: {r.cnt} 个")
print()

# Q6: 客户价值
q6 = prepareQuery("""
PREFIX ex: <http://shop.com/>
SELECT ?name (SUM(?amount) AS ?total) WHERE {
    ?order a ex:Order ;
           ex:customer ?cust ;
           ex:amount ?amount ;
           ex:status "Delivered" .
    ?cust ex:customerName ?name .
} GROUP BY ?cust ?name
ORDER BY DESC(?total)
""")
print("Q6: 已完成订单的客户消费")
for r in g.query(q6):
    print(f"  {r.name}  ¥{r.total}")
