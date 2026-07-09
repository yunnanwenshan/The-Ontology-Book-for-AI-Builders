"""医疗本体: 6 个常见查询（医院 HIS/CDSS 场景）."""
from rdflib import Graph
from rdflib.plugins.sparql import prepareQuery
from pyshacl import validate

ont  = Graph().parse("data/medical-ont.ttl",     format="turtle")
data = Graph().parse("data/medical-data.ttl",    format="turtle")
shapes = Graph().parse("data/medical-shapes.ttl", format="turtle")
g = ont + data

conforms, _, _ = validate(g, shacl_graph=shapes)
print(f"数据校验：{'✅ 通过' if conforms else '❌ 失败'}\n")

# Q1: P000001 患者的就诊历史
q1 = prepareQuery("""
PREFIX ex: <http://hospital.com/>
SELECT ?date ?doctor ?type ?complaint WHERE {
    { ?v a ex:OutpatientVisit } UNION { ?v a ex:EmergencyVisit } UNION { ?v a ex:InpatientVisit } .
    ?v ex:visitOf ex:p-001 ;
       ex:visitDate ?date ;
       ex:visitDoctor ?doc ;
       ex:visitType ?type ;
       ex:chiefComplaint ?complaint .
    ?doc ex:doctorName ?doctor .
} ORDER BY ?date
""")
print("Q1: 张三（P000001）的就诊历史")
for r in g.query(q1):
    print(f"  {r.date}  {r.doctor}  [{r.type}]  {r.complaint}")
print()

# Q2: 各诊断 ICD-10 编码的使用次数（流行病学统计）
q2 = prepareQuery("""
PREFIX ex: <http://hospital.com/>
SELECT ?icd ?name (COUNT(?dx) AS ?cnt) WHERE {
    ?dx a ex:Diagnosis ;
         ex:icdCode ?icd ;
         ex:diagnosisName ?name .
} GROUP BY ?icd ?name
ORDER BY DESC(?cnt)
""")
print("Q2: 各疾病诊断次数（按 ICD-10）")
for r in g.query(q2):
    print(f"  {r.icd}  {r.name}  {r.cnt} 次")
print()

# Q3: 7 月 8 日的就诊情况
q3 = prepareQuery("""
PREFIX ex: <http://hospital.com/>
SELECT ?dt ?patient ?doctor ?complaint WHERE {
    { ?v a ex:OutpatientVisit } UNION { ?v a ex:EmergencyVisit } UNION { ?v a ex:InpatientVisit } .
    ?v ex:visitDate ?dt ;
       ex:visitOf ?p ;
       ex:visitDoctor ?d ;
       ex:chiefComplaint ?complaint .
    ?p ex:patientName ?patient .
    ?d ex:doctorName ?doctor .
    FILTER (?dt >= "2026-07-08T00:00:00"^^xsd:dateTime && ?dt <= "2026-07-08T23:59:59"^^xsd:dateTime)
} ORDER BY ?dt
""")
print("Q3: 7 月 8 日所有就诊")
for r in g.query(q3):
    d = r.asdict()
    dt = d['dt']
    print(f"  {dt}  {d['patient']} ← {d['doctor']}  '{d['complaint']}'")
print()

# Q4: 各医生看的病人
q4 = prepareQuery("""
PREFIX ex: <http://hospital.com/>
SELECT ?doctor (COUNT(DISTINCT ?p) AS ?patientCount) (COUNT(?v) AS ?visitCount) WHERE {
    { ?v a ex:OutpatientVisit } UNION { ?v a ex:EmergencyVisit } UNION { ?v a ex:InpatientVisit } .
    ?v ex:visitDoctor ?d ; ex:visitOf ?p .
    ?d ex:doctorName ?doctor .
} GROUP BY ?d ?doctor
ORDER BY DESC(?visitCount)
""")
print("Q4: 各医生工作量")
for r in g.query(q4):
    print(f"  {r.doctor}  {r.patientCount} 病人  /  {r.visitCount} 次就诊")
print()

# Q5: 阿莫西林开给谁了
q5 = prepareQuery("""
PREFIX ex: <http://hospital.com/>
SELECT ?patient ?date ?dosage ?frequency WHERE {
    ?rx a ex:Prescription ; ex:drug ex:d-003 ;
         ex:prescribedTo ?v ;
         ex:dosage ?dosage ; ex:frequency ?frequency .
    ?v ex:visitOf ?p ; ex:visitDate ?date .
    ?p ex:patientName ?patient .
} ORDER BY ?date
""")
print("Q5: 阿莫西林开给谁了")
for r in g.query(q5):
    print(f"  {r.patient}  {r.date}  {r.dosage} {r.frequency}")
print()

# Q6: 各药品被开了多少次
q6 = prepareQuery("""
PREFIX ex: <http://hospital.com/>
SELECT ?drugName (COUNT(?rx) AS ?cnt) WHERE {
    ?rx a ex:Prescription ; ex:drug ?d .
    ?d ex:drugName ?drugName .
} GROUP BY ?d ?drugName
ORDER BY DESC(?cnt)
""")
print("Q6: 药品使用频率")
for r in g.query(q6):
    print(f"  {r.drugName}  {r.cnt} 次")
