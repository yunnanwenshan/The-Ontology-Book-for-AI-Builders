# 实战案例 7 · 医疗本体

> **场景**：医院的患者、就诊、诊断、处方、药品
> **难度 / 时间**：⭐⭐⭐ 高级 / 1.5 小时
> **谁在用**：医院 IT 维护 / 医生问患者 / 开发者跑 medical-query.py

> **场景**：医院的患者、就诊、诊断、处方、药品
> **目标**：让 AI 1 秒回答 6 个医生/管理者每天问的问题
## 1. 业务问题

医生/管理者每天问：
- "张三的就诊历史？"
- "这周最多见的病？"
- "今天 7 月 8 日的接诊情况？"
- "各医生工作量？"
- "阿莫西林开给了谁？"
- "药品使用频率？"

## 2. 跑 demo

```bash
cd ~/Documents/projects/ai/ontology/05-real-cases/medical
python3 medical-query.py
```

**真实输出**（已验证）：

```
数据校验：✅ 通过

Q1: 张三（P000001）的就诊历史
  2026-06-15T09:30:00  李华  [门诊]  胸闷气短 1 周
  2026-07-01T10:00:00  李华  [复诊]  胸闷缓解，咨询用药

Q2: 各疾病诊断次数（按 ICD-10）
  I25.10  冠状动脉粥样硬化性心脏病  1 次
  I10  原发性高血压  1 次
  ...

Q3: 7 月 8 日所有就诊
  2026-07-08T15:30:00  孙七 ← 王芳  '咽痛 2 天'
  2026-07-08T22:15:00  王五 ← 张明  '高热 40℃'

Q4: 各医生工作量
  李华  2 病人  /  3 次就诊
  王芳  2 病人  /  2 次就诊
  张明  1 病人  /  1 次就诊

Q5: 阿莫西林开给谁了
  李四  2026-07-05T14:20:00  500mg 每日3次
  孙七  2026-07-08T15:30:00  500mg 每日3次

Q6: 药品使用频率
  阿司匹林肠溶片  3 次
  阿莫西林胶囊  2 次
  ...
```

## 3. 业务价值

| 不用本体 | 用本体 |
|---------|--------|
| 翻电子病历 | 1 秒 SPARQL |
| ICD-10 编码靠医生记 | SHACL 校验编码格式 |
| 跨科室查询难 | 1 张图全院关联 |
| 抗菌药滥用难监控 | 1 个查询看处方 |

## 4. SHACL 校验的关键规则

```turtle
# 处方必须有药品和剂量
ex:PrescriptionShape
    a sh:NodeShape ;
    sh:targetClass ex:Prescription ;
    sh:property [
        sh:path ex:drug ;
        sh:minCount 1 ;
        sh:class ex:Drug ;
    ] , [
        sh:path ex:dosage ;
        sh:minCount 1 ;
    ] .

# ICD-10 编码格式校验
ex:DiagnosisShape
    a sh:NodeShape ;
    sh:targetClass ex:Diagnosis ;
    sh:property [
        sh:path ex:icdCode ;
        sh:minCount 1 ;
        sh:pattern "^[A-Z]\\d{2}(\\.\\d{1,4})?$" ;   # ICD-10 标准格式
    ] .

# 药品必须有国药准字
ex:DrugShape
    a sh:NodeShape ;
    sh:targetClass ex:Drug ;
    sh:property [
        sh:path ex:drugCode ;
        sh:minCount 1 ;
        sh:pattern "^国药准字[A-Z]\\d{8}$" ;
    ] .
```

## 5. 进阶练习

1. "本月所有 60 岁以上患者的就诊"
2. "开出某种药的所有医生"
3. "高热（≥39℃）患者数"
4. "王芳医生看的所有诊断"
5. "抗血小板药的处方数"
6. "诊断为 J18.9（肺炎）的患者"

## 6. 跟 AI Agent 集成（CDSS 临床决策支持）

```python
# 危险药物相互作用检查
def check_interaction(drug_a, drug_b):
    q = """
    PREFIX ex: <http://hospital.com/>
    ASK {
        ex:drug-a ex:interactsWith ex:drug-b .
    }
    """
    return g.query(q)
```

## 7. 文件清单

```
medical/
├── README.md
├── medical-query.py                ← 6 个查询全跑通
└── data/
    ├── medical-ont.ttl            ← 本体（3 科室/3 医生/5 患者/5 药品/6 就诊/7 诊断/8 处方）
    ├── medical-shapes.ttl         ← SHACL 规则（含 ICD-10 校验）
    └── medical-data.ttl            ← 业务数据
```

## 8. 真实世界延伸

- 加 `ex:LabResult` 实体（化验结果）
- 加 `ex:Allergy` 实体（过敏记录）
- 加 `ex:prescribedFor` 关系（药与诊断的对应）—— 这是 CDSS 关键
- 加 SNOMED CT / LOINC 编码
