"""财务本体: 6 个常见查询（电商财务总监场景）."""
from rdflib import Graph
from rdflib.plugins.sparql import prepareQuery
from pyshacl import validate

ont  = Graph().parse("data/finance-ont.ttl",     format="turtle")
data = Graph().parse("data/finance-data.ttl",    format="turtle")
shapes = Graph().parse("data/finance-shapes.ttl", format="turtle")
g = ont + data

conforms, _, _ = validate(g, shacl_graph=shapes)
print(f"数据校验：{'✅ 通过' if conforms else '❌ 失败'}\n")

# Q1: 哪些合同本月到期？
q1 = prepareQuery("""
PREFIX ex: <http://finance.com/>
SELECT ?no ?vendor ?amt ?expiry WHERE {
    ?c a ex:Contract ;
       ex:contractNo ?no ;
       ex:vendor ?v ;
       ex:contractAmt ?amt ;
       ex:expiryDate ?expiry ;
       ex:status "Active" .
    ?v ex:vendorName ?vendor .
    FILTER (?expiry >= "2026-07-01"^^xsd:date &&
            ?expiry <= "2026-07-31"^^xsd:date)
}
""")
print("Q1: 7 月到期的合同")
results = list(g.query(q1))
if results:
    for r in results:
        print(f"  {r.no}  {r.vendor}  ¥{r.amt}  到期 {r.expiry}")
else:
    print("  （无）")
print()

# Q2: 哪些发票还没付？
q2 = prepareQuery("""
PREFIX ex: <http://finance.com/>
SELECT ?inv ?vendor ?amt ?due WHERE {
    ?inv a ex:Invoice ;
         ex:invoiceOf ?c ;
         ex:invoiceAmt ?amt ;
         ex:invoiceDate ?due .
    ?c ex:vendor ?v .
    ?v ex:vendorName ?vendor .
    FILTER NOT EXISTS { ?p ex:paymentOf ?inv . }
} ORDER BY ?due
""")
print("Q2: 未付款发票")
results = list(g.query(q2))
if results:
    for r in results:
        inv_id = r.inv.split('#')[-1]
        print(f"  {inv_id}  {r.vendor}  ¥{r.amt}  开票 {r.due}")
else:
    print("  （无）")
print()

# Q3: 本月付款总额
q3 = prepareQuery("""
PREFIX ex: <http://finance.com/>
SELECT (SUM(?amt) AS ?total) WHERE {
    ?p a ex:Payment ; ex:paymentAmt ?amt ;
       ex:paymentDate ?d .
    FILTER (?d >= "2026-07-01"^^xsd:date &&
            ?d <= "2026-07-31"^^xsd:date)
}
""")
print("Q3: 7 月付款总额")
for r in g.query(q3):
    val = r.total if r.total else 0
    print(f"  ¥{val}")
print()

# Q4: 各供应商付款分布
q4 = prepareQuery("""
PREFIX ex: <http://finance.com/>
SELECT ?vendor (SUM(?amt) AS ?total) (COUNT(?p) AS ?cnt) WHERE {
    ?p a ex:Payment ;
       ex:paymentOf ?inv ;
       ex:paymentAmt ?amt .
    ?inv ex:invoiceOf ?c .
    ?c ex:vendor ?v .
    ?v ex:vendorName ?vendor .
} GROUP BY ?v ?vendor
ORDER BY DESC(?total)
""")
print("Q4: 各供应商付款金额")
for r in g.query(q4):
    print(f"  {r.vendor}  ¥{r.total}  ({r.cnt} 笔)")
print()

# Q5: 风险：超期未付发票
q5 = prepareQuery("""
PREFIX ex: <http://finance.com/>
SELECT ?inv ?vendor ?amt ?invoiceDate WHERE {
    ?inv a ex:Invoice ;
         ex:invoiceOf ?c ;
         ex:invoiceAmt ?amt ;
         ex:invoiceDate ?invoiceDate .
    ?c ex:vendor ?v .
    ?v ex:vendorName ?vendor .
    FILTER (?invoiceDate < "2026-07-01"^^xsd:date)
    FILTER NOT EXISTS { ?p ex:paymentOf ?inv }
} ORDER BY ?invoiceDate
""")
print("Q5: 风险：7 月前开票但未付")
results = list(g.query(q5))
if results:
    for r in results:
        inv_id = r.inv.split('#')[-1]
        print(f"  {inv_id}  {r.vendor}  ¥{r.amt}  {r.invoiceDate}")
else:
    print("  （无）")
print()

# Q6: 科目汇总
q6 = prepareQuery("""
PREFIX ex: <http://finance.com/>
SELECT ?code ?name (SUM(?amt) AS ?total) WHERE {
    ?p a ex:Payment ; ex:paymentAmt ?amt ; ex:postedTo ?acc .
    ?acc ex:accountCode ?code ; ex:accountName ?name .
} GROUP BY ?acc ?code ?name
ORDER BY ?code
""")
print("Q6: 各科目付款汇总")
for r in g.query(q6):
    print(f"  {r.code}  {r.name}  ¥{r.total}")
