"""CRM 本体: 7 个常见查询（销售漏斗/客户管理场景）."""
from rdflib import Graph
from rdflib.plugins.sparql import prepareQuery
from pyshacl import validate

ont  = Graph().parse("data/crm-ont.ttl",     format="turtle")
data = Graph().parse("data/crm-data.ttl",    format="turtle")
shapes = Graph().parse("data/crm-shapes.ttl", format="turtle")
g = ont + data

conforms, _, _ = validate(g, shacl_graph=shapes)
print(f"数据校验：{'✅ 通过' if conforms else '❌ 失败'}\n")

# Q1: 销售漏斗（各阶段商机数）
q1 = prepareQuery("""
PREFIX ex: <http://crm.com/>
SELECT ?stage (COUNT(?o) AS ?cnt) (SUM(?amt) AS ?total) WHERE {
    ?o a ex:Opportunity ;
       ex:opportunityStage ?stage ;
       ex:opportunityAmt ?amt .
} GROUP BY ?stage
ORDER BY ?stage
""")
print("Q1: 销售漏斗（各阶段商机数 + 金额）")
stage_order = {"Lead": 1, "Qualified": 2, "Proposal": 3, "Negotiation": 4, "Won": 5, "Lost": 6}
results = list(g.query(q1))
results.sort(key=lambda r: stage_order.get(r.stage, 99))
for r in results:
    print(f"  {r.stage:<14} {r.cnt} 个  /  ¥{float(r.total):,.0f}")
print()

# Q2: 赢率（Won / (Won + Lost)）
q2 = prepareQuery("""
PREFIX ex: <http://crm.com/>
SELECT
    (SUM(?won) AS ?w) (SUM(?lost) AS ?l)
WHERE {
    {
        SELECT (1 AS ?won) (0 AS ?lost) WHERE {
            ?o a ex:Opportunity ; ex:opportunityStage "Won" .
        }
    } UNION {
        SELECT (0 AS ?won) (1 AS ?lost) WHERE {
            ?o a ex:Opportunity ; ex:opportunityStage "Lost" .
        }
    }
}
""")
print("Q2: 赢率")
won = lost = 0
for r in g.query(q2):
    won = int(r.w)
    lost = int(r.l)
total = won + lost
if total > 0:
    print(f"  Won {won}  /  Lost {lost}  /  赢率 {won/total*100:.1f}%")
else:
    print("  （无已结案商机）")
print()

# Q3: 各销售业绩
q3 = prepareQuery("""
PREFIX ex: <http://crm.com/>
SELECT ?rep (COUNT(?o) AS ?total_opp) WHERE {
    ?o a ex:Opportunity ; ex:opportunityRep ?r .
    ?r ex:repName ?rep .
} GROUP BY ?r ?rep
ORDER BY ?rep
""")
print("Q3: 各销售业绩（已成交）")
# Python 端分别统计
q3b = prepareQuery("""
PREFIX ex: <http://crm.com/>
SELECT ?rep (SUM(?amt) AS ?won_amt) WHERE {
    ?o a ex:Opportunity ; ex:opportunityRep ?r ;
       ex:opportunityStage "Won" ; ex:opportunityAmt ?amt .
    ?r ex:repName ?rep .
} GROUP BY ?r ?rep
""")
won_by_rep = {}
for r in g.query(q3b):
    won_by_rep[r.rep] = float(r.won_amt)
for r in g.query(q3):
    name = r.rep
    total = int(r.total_opp)
    won = won_by_rep.get(name, 0)
    print(f"  {name}  {total} 单  /  成交 ¥{won:,.0f}")
print()

# Q4: 高价值未成交商机
q4 = prepareQuery("""
PREFIX ex: <http://crm.com/>
SELECT ?opp ?customer ?amt ?stage ?rep WHERE {
    ?o a ex:Opportunity ;
       ex:opportunityName ?opp ;
       ex:opportunityAmt ?amt ;
       ex:opportunityStage ?stage .
    FILTER (?amt > 1000000)
    FILTER (?stage != "Won" && ?stage != "Lost")
    ?o ex:opportunityForCustomer ?c .
    ?c ex:customerName ?customer .
    ?o ex:opportunityRep ?r .
    ?r ex:repName ?rep .
} ORDER BY DESC(?amt)
""")
print("Q4: 100 万+ 仍未成交的商机")
for r in g.query(q4):
    print(f"  {r.opp}  {r.customer}  ¥{float(r.amt):,.0f}  [{r.stage}]  {r.rep}")
print()

# Q5: 各线索来源转化率
q5 = prepareQuery("""
PREFIX ex: <http://crm.com/>
SELECT ?source
       (COUNT(?l) AS ?total_leads)
       (SUM(?converted) AS ?converted)
WHERE {
    ?l a ?vt ; ex:leadSource ?source .
    FILTER (?vt = ex:NewLead || ?vt = ex:QualifiedLead || ?vt = ex:HotLead)
    OPTIONAL {
        ?l ex:leadStatus "Converted" .
        BIND(1 AS ?converted)
    }
} GROUP BY ?source
ORDER BY DESC(?total_leads)
""")
print("Q5: 各线索来源转化")
source_data = {}
for r in g.query(q5):
    name = r.source
    if name not in source_data:
        source_data[name] = {"total": 0, "converted": 0}
    source_data[name]["total"] += int(r.total_leads)
    if r.converted is not None:
        source_data[name]["converted"] += int(r.converted)
for name, d in sorted(source_data.items()):
    rate = d["converted"]/d["total"]*100 if d["total"] > 0 else 0
    print(f"  {name:<14} 总 {d['total']}  /  转化 {d['converted']}  /  率 {rate:.1f}%")
print()

# Q6: 客户行业分布 + 总价值
q6 = prepareQuery("""
PREFIX ex: <http://crm.com/>
SELECT ?industry (COUNT(DISTINCT ?c) AS ?customers) (SUM(?amt) AS ?total) WHERE {
    ?c ex:customerName ?name ; ex:industry ?industry .
    OPTIONAL {
        ?o a ex:Opportunity ; ex:opportunityForCustomer ?c ; ex:opportunityAmt ?amt .
    }
} GROUP BY ?industry
ORDER BY DESC(?total)
""")
print("Q6: 客户行业分布")
for r in g.query(q6):
    total = float(r.total) if r.total else 0
    print(f"  {r.industry:<10} {r.customers} 客户  /  商机总 ¥{total:,.0f}")
print()

# Q7: 王经理的最近 5 个活动
q7 = prepareQuery("""
PREFIX ex: <http://crm.com/>
SELECT ?date ?type ?subject ?opp WHERE {
    ?a a ex:Activity ;
       ex:activityBy ex:rep-001 ;
       ex:activityTime ?date ;
       ex:activityType ?type ;
       ex:activitySubject ?subject ;
       ex:activityOf ?o .
    ?o ex:opportunityName ?opp .
} ORDER BY DESC(?date) LIMIT 5
""")
print("Q7: 王经理最近 5 个活动")
for r in g.query(q7):
    print(f"  {r.date}  [{r.type}]  {r.subject}  ({r.opp})")
