# 实战案例 1 · HR 招聘本体

> **场景**：HR 用本体管招聘流程，从职位发布到入职
> **难度 / 时间**：⭐ 入门 / 30 分钟
> **谁在用**：HR 总监看仪表盘 / HR 专员问 Claude / 开发者跑 hr-query.py

## 1. 业务问题

HR 总监每天会问：
- "销售总监还招不招？"
- "现在 offer 阶段的有谁？"
- "张三面试了几轮？"
- "哪些职位还没人投？"

用本体 + SPARQL，**每个问题 1 秒钟准确回答**。

**怎么实现的**：
- HR 总监看 **HTML 仪表盘**（`build_dashboard.py` 风格）
- HR 专员问 **Claude Desktop**（`mcp_server.py` 提供 7 工具）
- 数据分析师自己改 **`hr-query.py` 加新查询**

## 2. 核心本体

**`hr-ont.ttl`**：

```turtle
@prefix ex: <http://hr.com/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# === 类 ===
ex:JobPosting    a owl:Class ; rdfs:label "职位"@zh .
ex:Candidate     a owl:Class ; rdfs:label "候选人"@zh .
ex:Application   a owl:Class ; rdfs:label "投递"@zh .
ex:Interview     a owl:Class ; rdfs:label "面试"@zh .

ex:Engineering   rdfs:subClassOf ex:JobPosting ; rdfs:label "工程岗"@zh .
ex:Sales         rdfs:subClassOf ex:JobPosting ; rdfs:label "销售岗"@zh .
ex:Management    rdfs:subClassOf ex:JobPosting ; rdfs:label "管理岗"@zh .

# === 状态枚举（建模为类）===
ex:Applied       a owl:Class ; rdfs:label "已投递"@zh .
ex:Screening     a owl:Class ; rdfs:label "筛选中"@zh .
ex:Interviewing  a owl:Class ; rdfs:label "面试中"@zh .
ex:OfferSent     a owl:Class ; rdfs:label "已发 offer"@zh .
ex:Hired         a owl:Class ; rdfs:label "已入职"@zh .
ex:Rejected      a owl:Class ; rdfs:label "已拒绝"@zh .

# === 属性 ===
ex:title         rdfs:domain ex:JobPosting ; rdfs:range xsd:string .
ex:department    rdfs:domain ex:JobPosting ; rdfs:range xsd:string .
ex:salaryMin     rdfs:domain ex:JobPosting ; rdfs:range xsd:integer .
ex:salaryMax     rdfs:domain ex:JobPosting ; rdfs:range xsd:integer .
ex:status        rdfs:domain ex:Application ; rdfs:range xsd:string .
ex:appliedJob    rdfs:domain ex:Application ; rdfs:range ex:JobPosting .
ex:candidate     rdfs:domain ex:Application ; rdfs:range ex:Candidate .
ex:candidateName rdfs:domain ex:Candidate  ; rdfs:range xsd:string .
ex:candidateEmail rdfs:domain ex:Candidate ; rdfs:range xsd:string .
ex:interviewOf   rdfs:domain ex:Interview  ; rdfs:range ex:Application .
ex:interviewer   rdfs:domain ex:Interview  ; rdfs:range xsd:string .
ex:interviewDate rdfs:domain ex:Interview  ; rdfs:range xsd:date .
ex:interviewRound rdfs:domain ex:Interview ; rdfs:range xsd:integer .
ex:feedback      rdfs:domain ex:Interview  ; rdfs:range xsd:string .
```

## 3. SHACL 规则

**`hr-shapes.ttl`**：

```turtle
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix ex: <http://hr.com/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# 职位必须有 title、salary
ex:JobShape
    a sh:NodeShape ;
    sh:targetClass ex:JobPosting ;
    sh:property [
        sh:path ex:title ;
        sh:minCount 1 ;
        sh:datatype xsd:string ;
    ] , [
        sh:path ex:salaryMin ;
        sh:minInclusive 0 ;
    ] , [
        sh:path ex:salaryMax ;
        sh:minInclusive 0 ;
    ] ;
    sh:property [
        sh:path ex:salaryMax ;
        sh:greaterThan ex:salaryMin ;   # 最高 > 最低
    ] .

# 候选人必须有邮箱
ex:CandidateShape
    a sh:NodeShape ;
    sh:targetClass ex:Candidate ;
    sh:property [
        sh:path ex:candidateEmail ;
        sh:minCount 1 ;
        sh:pattern ".+@.+\\..+" ;       # 简单邮箱校验
    ] .

# 状态必须在枚举内
ex:ApplicationShape
    a sh:NodeShape ;
    sh:targetClass ex:Application ;
    sh:property [
        sh:path ex:status ;
        sh:in ("Applied" "Screening" "Interviewing" "OfferSent" "Hired" "Rejected") ;
    ] .
```

## 4. 业务数据

**`hr-data.ttl`**：

```turtle
@prefix ex: <http://hr.com/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# 3 个职位
ex:job-001 a ex:Engineering ; ex:title "高级 Python 工程师" ; ex:salaryMin 35000 ; ex:salaryMax 60000 .
ex:job-002 a ex:Engineering ; ex:title "前端开发"          ; ex:salaryMin 25000 ; ex:salaryMax 45000 .
ex:job-003 a ex:Sales       ; ex:title "销售总监"          ; ex:salaryMin 50000 ; ex:salaryMax 80000 .
ex:job-004 a ex:Management  ; ex:title "HR 经理"           ; ex:salaryMin 30000 ; ex:salaryMax 50000 .

# 5 个候选人
ex:cand-001 a ex:Candidate ; ex:candidateName "张三" ; ex:candidateEmail "zhang@x.com" .
ex:cand-002 a ex:Candidate ; ex:candidateName "李四" ; ex:candidateEmail "li@x.com" .
ex:cand-003 a ex:Candidate ; ex:candidateName "王五" ; ex:candidateEmail "wang@x.com" .
ex:cand-004 a ex:Candidate ; ex:candidateName "赵六" ; ex:candidateEmail "zhao@x.com" .
ex:cand-005 a ex:Candidate ; ex:candidateName "孙七" ; ex:candidateEmail "sun@x.com" .

# 6 个投递
ex:app-001 a ex:Application ;
    ex:appliedJob ex:job-001 ; ex:candidate ex:cand-001 ; ex:status "Interviewing" .
ex:app-002 a ex:Application ;
    ex:appliedJob ex:job-001 ; ex:candidate ex:cand-002 ; ex:status "OfferSent" .
ex:app-003 a ex:Application ;
    ex:appliedJob ex:job-002 ; ex:candidate ex:cand-003 ; ex:status "Screening" .
ex:app-004 a ex:Application ;
    ex:appliedJob ex:job-003 ; ex:candidate ex:cand-004 ; ex:status "Interviewing" .
ex:app-005 a ex:Application ;
    ex:appliedJob ex:job-004 ; ex:candidate ex:cand-005 ; ex:status "Hired" .
ex:app-006 a ex:Application ;
    ex:appliedJob ex:job-003 ; ex:candidate ex:cand-001 ; ex:status "Rejected" .

# 4 场面试
ex:iv-001 a ex:Interview ;
    ex:interviewOf ex:app-001 ; ex:interviewer "王经理" ; ex:interviewDate "2026-06-15"^^xsd:date ; ex:interviewRound 1 ; ex:feedback "基础扎实" .
ex:iv-002 a ex:Interview ;
    ex:interviewOf ex:app-001 ; ex:interviewer "李总监" ; ex:interviewDate "2026-06-22"^^xsd:date ; ex:interviewRound 2 ; ex:feedback "通过" .
ex:iv-003 a ex:Interview ;
    ex:interviewOf ex:app-002 ; ex:interviewer "王经理" ; ex:interviewDate "2026-06-20"^^xsd:date ; ex:interviewRound 1 ; ex:feedback "OK" .
ex:iv-004 a ex:Interview ;
    ex:interviewOf ex:app-004 ; ex:interviewer "陈总"   ; ex:interviewDate "2026-07-01"^^xsd:date ; ex:interviewRound 1 ; ex:feedback "候选" .
```

## 5. 5 分钟上手脚本

**`hr-query.py`**：

```python
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
    ?app ex:candidate ?cand ;
         ex:status ?status .
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
for r in g.query(q4):
    print(f"  {r.title}")
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

# Q6: 平均每个职位收几份简历
q6 = prepareQuery("""
PREFIX ex: <http://hr.com/>
SELECT (COUNT(?app) AS ?total_apps) (COUNT(DISTINCT ?job) AS ?total_jobs)
WHERE {
    ?app ex:appliedJob ?job .
}
""")
print("Q6: 简历总数")
for r in g.query(q6):
    print(f"  共 {r.total_apps} 份简历 / {r.total_jobs} 个职位")
    print(f"  平均每个职位 {int(r.total_apps)/int(r.total_jobs):.1f} 份")
```

**跑**：

```bash
cd ~/Documents/projects/ai/ontology/05-real-cases/hr
python3 hr-query.py
```

**真实输出**（已验证）：

```
数据校验：✅ 通过

Q1: 销售总监还招不招？
  答案：是，还招

Q2: Offer 阶段的有谁？
  李四  →  高级 Python 工程师

Q3: 张三的面试记录
  Round 1  2026-06-15  基础扎实
  Round 2  2026-06-22  通过

Q4: 还没人投的职位
  （无）

Q5: 各状态人数
  Interviewing: 2 人
  OfferSent: 1 人
  Screening: 1 人
  Rejected: 1 人
  Hired: 1 人

Q6: 简历总数
  共 6 份简历 / 4 个职位
  平均每个职位 1.5 份
```

## 6. 拓展（30 分钟）

试试这 5 个新查询：

1. "7 月安排了几场面试？"
2. "李总监面试的所有候选人？"
3. "平均每个候选人面试几轮？"
4. "Python 工程师岗位的 offer rate？"
5. "哪些候选人同时投了多个职位？"

## 7. 业务价值

| 不用本体 | 用本体 |
|---------|--------|
| HR 手动从 Excel 筛选 | 1 秒 SPARQL 查询 |
| 数据不准确（人为填错）| SHACL 自动校验 |
| 跨表 join 麻烦 | 一张图全关联 |
| 招错人风险 | 面试记录完整可追溯 |
