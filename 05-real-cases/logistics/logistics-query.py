"""物流本体: 7 个常见查询."""
from rdflib import Graph
from rdflib.plugins.sparql import prepareQuery
from pyshacl import validate
import re

ont  = Graph().parse("data/logistics-ont.ttl",     format="turtle")
data = Graph().parse("data/logistics-data.ttl",    format="turtle")
shapes = Graph().parse("data/logistics-shapes.ttl", format="turtle")
g = ont + data

conforms, _, _ = validate(g, shacl_graph=shapes)
print(f"数据校验：{'✅ 通过' if conforms else '❌ 失败'}\n")

# Q1: 运单 SF1234567890 的完整轨迹
q1 = prepareQuery("""
PREFIX ex: <http://logistics.com/>
SELECT ?time ?type ?location WHERE {
    ?s a ?vt ; ex:trackingNo "SF1234567890" .
    FILTER (?vt = ex:GroundShipment || ?vt = ex:AirShipment || ?vt = ex:SeaShipment)
    ?ev ex:eventOf ?s ;
        ex:eventTime ?time ;
        ex:eventType ?type ;
        ex:eventLocation ?location .
} ORDER BY ?time
""")
print("Q1: 运单 SF1234567890 的轨迹")
for r in g.query(q1):
    print(f"  {r.time}  [{r.type}]  {r.location}")
print()

# Q2: 运输中的运单
q2 = prepareQuery("""
PREFIX ex: <http://logistics.com/>
SELECT ?tracking ?customer ?city ?carrier WHERE {
    ?s a ?vt ;
       ex:trackingNo ?tracking ;
       ex:shipmentStatus ?status .
    FILTER (?vt = ex:GroundShipment || ?vt = ex:AirShipment || ?vt = ex:SeaShipment)
    FILTER (?status = "InTransit" || ?status = "PickedUp" || ?status = "OutForDelivery")
    ?s ex:shipmentOf ?o .
    ?o ex:orderCustomer ?c .
    ?c ex:customerName ?customer ; ex:customerAddress ?addr .
    ?s ex:shipmentCarrier ?car .
    ?car ex:carrierName ?carrier .
    BIND(STR(?addr) AS ?city)
} ORDER BY ?tracking
""")
print("Q2: 运输中的运单")
for r in g.query(q2):
    print(f"  {r.tracking}  {r.customer}  {r.carrier}")
print()

# Q3: 各承运商运单数
q3 = prepareQuery("""
PREFIX ex: <http://logistics.com/>
SELECT ?carrier (COUNT(?s) AS ?cnt) WHERE {
    ?s a ?vt ; ex:shipmentCarrier ?car .
    ?car ex:carrierName ?carrier .
    FILTER (?vt = ex:GroundShipment || ?vt = ex:AirShipment || ?vt = ex:SeaShipment)
} GROUP BY ?car ?carrier
ORDER BY DESC(?cnt)
""")
print("Q3: 各承运商运单数")
for r in g.query(q3):
    print(f"  {r.carrier}  {r.cnt} 单")
print()

# Q4: 延误的运单（实际到达 > 预计到达）
q4 = prepareQuery("""
PREFIX ex: <http://logistics.com/>
SELECT ?tracking ?customer ?eta ?actual WHERE {
    ?s a ?vt ;
       ex:trackingNo ?tracking ;
       ex:estimatedArrival ?eta ;
       ex:actualArrival ?actual .
    FILTER (?vt = ex:GroundShipment || ?vt = ex:AirShipment || ?vt = ex:SeaShipment)
    FILTER (?actual > ?eta)
    ?s ex:shipmentOf ?o .
    ?o ex:orderCustomer ?c .
    ?c ex:customerName ?customer .
}
""")
print("Q4: 延误的运单（实际 > 预计）")
for r in g.query(q4):
    print(f"  {r.tracking}  {r.customer}  预计 {r.eta}  实际 {r.actual}")
print()

# Q5: 异常统计
q5 = prepareQuery("""
PREFIX ex: <http://logistics.com/>
SELECT ?type (COUNT(?e) AS ?cnt) WHERE {
    ?e a ?vt ; ex:exceptionType ?type .
    FILTER (?vt = ex:DamageException || ?vt = ex:DelayException || ?vt = ex:LostException)
} GROUP BY ?type
ORDER BY DESC(?cnt)
""")
print("Q5: 异常类型分布")
for r in g.query(q5):
    print(f"  {r.type}  {r.cnt} 次")
print()

# Q6: 异常率（异常运单 / 总运单）
q6 = prepareQuery("""
PREFIX ex: <http://logistics.com/>
SELECT (COUNT(?s) AS ?exc_count) WHERE {
    ?s a ?vt ;
       ex:shipmentStatus "Exception" .
    FILTER (?vt = ex:GroundShipment || ?vt = ex:AirShipment || ?vt = ex:SeaShipment)
}
""")
print("Q6: 异常运单")
exc = 0
for r in g.query(q6):
    exc = int(r.exc_count)
print(f"  {exc} 异常 / 8 总运单 = {exc/8*100:.1f}%")
print()

# Q7: 各仓库出货量
q7 = prepareQuery("""
PREFIX ex: <http://logistics.com/>
SELECT ?warehouse (COUNT(?o) AS ?orders) (SUM(?weight) AS ?total_weight) WHERE {
    ?o a ex:Order ; ex:orderWarehouse ?wh ; ex:orderWeight ?weight .
    ?wh ex:warehouseName ?warehouse .
} GROUP BY ?wh ?warehouse
ORDER BY DESC(?orders)
""")
print("Q7: 各仓库出货量")
for r in g.query(q7):
    print(f"  {r.warehouse}  {r.orders} 单  /  共 {float(r.total_weight):.1f} kg")
