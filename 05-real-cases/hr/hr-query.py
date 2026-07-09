"""HR 招聘本体: 6 个常见查询."""
from rdflib import Graph
from rdflib.plugins.sparql import prepareQuery
from pyshacl import validate

# 加载
ont  = Graph().parse("data/hr-ont.ttl",     format="turtle")
data = Graph().parse("data/hr-data.ttl",    format="turtle")
shapes = Graph().parse("data/hr-shapes.ttl", format="turtle")
g = ont + data

# SHACL 校验
conforms, _, _ = validate(g, shacl_graph=shapes, inference="rdfs")
print(f"数据校验：{'✅ 通过' if conforms else '❌ 失败'}\n")

# Q1: 销售总监还招不招？
q1 = prepareQuery("""
PREFIX ex: <http://hr.com/>
SELECT ?job WHERE {
    ?job a ex:Sales ;
         ex:title "销售总监" .
}
""")
print("Q1: 销售总监还招不招？")
jobs = list(g.query(q1))
print(f"  答案：{'是，还招' if jobs else '否，已关闭'}\n")

# Q2: Offer 阶段的有谁？
q2 = prepareQuery("""
PREFIX ex: <http://hr.com/>
SELECT ?name ?jobTitle WHERE {
    ?app ex:status "OfferSent" ;
         ex:candidate ?cand ;
         ex:appliedJob ?job .
    ?cand ex:candidateName ?name .
    ?job ex:title ?jobTitle .
}
""")
print("Q2: Offer 阶段的有谁？")
for r in g.query(q2):
    print(f"  {r.name}  →  {r.jobTitle}")
print()

# Q3: 张三面试了几轮？
q3 = prepareQuery("""
PREFIX ex: <http://hr.com/>
SELECT ?round ?date ?feedback WHERE {
    ?cand ex:candidateName "张三" .
    ?app ex:candidate ?cand .
    ?iv ex:interviewOf ?app ;
        ex:interviewRound ?round ;
        ex:interviewDate ?date ;
        ex:feedback ?feedback .
} ORDER BY ?round
""")
print("Q3: 张三的面试记录")
for r in g.query(q3):
    print(f"  Round {r.round}  {r.date}  {r.feedback}")
print()

# Q4: 哪些职位还没人投？
q4 = prepareQuery("""
PREFIX ex: <http://hr.com/>
SELECT ?title WHERE {
    ?job a ex:JobPosting ;
         ex:title ?title .
    FILTER NOT EXISTS { ?app ex:appliedJob ?job . }
}
""")
print("Q4: 还没人投的职位")
results = list(g.query(q4))
if results:
    for r in results:
        print(f"  {r.title}")
else:
    print("  （所有职位都有人投）")
print()

# Q5: 各状态的人数？
q5 = prepareQuery("""
PREFIX ex: <http://hr.com/>
SELECT ?status (COUNT(?app) AS ?cnt) WHERE {
    ?app ex:status ?status .
} GROUP BY ?status
ORDER BY DESC(?cnt)
""")
print("Q5: 各状态人数")
for r in g.query(q5):
    print(f"  {r.status}: {r.cnt} 人")
print()

# Q6: 简历/职位比
q6 = prepareQuery("""
PREFIX ex: <http://hr.com/>
SELECT (COUNT(?app) AS ?total_apps) (COUNT(DISTINCT ?job) AS ?total_jobs)
WHERE {
    ?app ex:appliedJob ?job .
}
""")
print("Q6: 简历统计")
for r in g.query(q6):
    total_a = int(r.total_apps)
    total_j = int(r.total_jobs)
    print(f"  共 {total_a} 份简历 / {total_j} 个职位")
    print(f"  平均每个职位 {total_a/total_j:.1f} 份")
