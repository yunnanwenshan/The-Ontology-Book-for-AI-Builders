"""端到端电商本体: 加载数据 + 3 个 SPARQL 查询."""
from rdflib import Graph
from rdflib.plugins.sparql import prepareQuery

g = Graph().parse("data/shop-data.ttl", format="turtle")
print(f"加载了 {len(g)} 条三元组\n")

# Q1: 所有订单按金额排序
q1 = prepareQuery("""
PREFIX ex: <http://example.com/shop#>
SELECT ?o ?amount WHERE {
    ?o a ex:Order ;
       ex:amount ?amount .
} ORDER BY DESC(?amount)
""")
print("Q1: 所有订单")
for row in g.query(q1):
    print(f"  {row.o.split('#')[-1]}  ¥{row.amount}")

# Q2: Alice 买过什么
q2 = prepareQuery("""
PREFIX ex: <http://example.com/shop#>
SELECT ?product ?price WHERE {
    ?order ex:customer ex:Alice ;
           ex:item ?product .
    ?product ex:price ?price .
}
""")
print("\nQ2: Alice 买过什么")
for row in g.query(q2):
    print(f"  {row.product.split('#')[-1]}  ¥{row.price}")

# Q3: VIP 客户
q3 = prepareQuery("""
PREFIX ex: <http://example.com/shop#>
SELECT ?name (SUM(?amount) AS ?total) WHERE {
    ?order ex:customer ?cust ;
           ex:amount ?amount .
    ?cust ex:name ?name .
} GROUP BY ?cust ?name
HAVING (SUM(?amount) > 5000)
""")
print("\nQ3: 消费超 5000 的客户")
for row in g.query(q3):
    print(f"  {row.name}  合计 ¥{row.total}")
