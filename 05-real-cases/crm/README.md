# 实战案例 6 · CRM 本体

> **场景**：B2B 大客户销售，客户/联系人/线索/商机/活动/销售
> **难度 / 时间**：⭐⭐⭐ 高级 / 1.5 小时
> **谁在用**：销售 VP 看漏斗 / 销售问客户 / 开发者跑 crm-query.py

> **场景**：B2B 大客户销售，客户/联系人/线索/商机/活动/销售
> **目标**：让销售总监 1 秒回答 7 个每天问的问题
## 1. 业务问题

销售总监/VP 每天问：
- "销售漏斗什么样？"
- "赢率多少？"
- "各销售业绩？"
- "哪些大单还在谈？"
- "哪些线索来源转化高？"
- "客户行业分布？"
- "王经理最近在做什么？"

## 2. 跑 demo

```bash
cd ~/Documents/projects/ai/ontology/05-real-cases/crm
python3 crm-query.py
```

**真实输出**（已验证）：

```
数据校验：✅ 通过

Q1: 销售漏斗（各阶段商机数 + 金额）
  Lead           1 个  /  ¥400,000
  Qualified      2 个  /  ¥1,400,000
  Proposal       1 个  /  ¥600,000
  Negotiation    2 个  /  ¥3,500,000
  Won            1 个  /  ¥800,000
  Lost           1 个  /  ¥3,000,000

Q2: 赢率
  Won 1  /  Lost 1  /  赢率 50.0%

Q3: 各销售业绩（已成交）
  王经理  3 单  /  成交 ¥800,000
  李总监  3 单  /  成交 ¥0
  张主管  2 单  /  成交 ¥0

Q4: 100 万+ 仍未成交的商机
  海尔 ERP 升级  美的集团  ¥2,000,000  [Negotiation]  李总监
  美的 ERP       美的集团  ¥1,500,000  [Negotiation]  李总监
  华为云 CRM 续约  华为技术  ¥1,200,000  [Qualified]  王经理

Q5: 各线索来源转化
  Referral       总 2  /  转化 0
  Website        总 2  /  转化 0
  ...

Q6: 客户行业分布
  制造         1 客户  /  商机总 ¥3,500,000
  能源         1 客户  /  商机总 ¥3,000,000
  通信         1 客户  /  商机总 ¥1,200,000
  ...

Q7: 王经理最近 5 个活动
  2026-07-03T16:00:00  [Call]  需求确认  (华为云 CRM 续约)
  2026-07-01T11:00:00  [Meeting]  方案提交讨论  (上汽通用 CRM)
  ...
```

## 3. 业务价值

| 不用本体 | 用本体 |
|---------|--------|
| 翻 Salesforce / 飞书 CRM | 1 个 SPARQL 全出来 |
| 漏斗靠人工维护 | 自动实时算 |
| 业绩靠销售自报 | 数据说话 |
| 客户重复录入 | 实体关系清晰 |

## 4. SHACL 校验的关键规则

```turtle
# 商机金额必须 > 0
ex:OpportunityShape
    a sh:NodeShape ;
    sh:targetClass ex:Opportunity ;
    sh:property [
        sh:path ex:opportunityAmt ;
        sh:minExclusive 0 ;
    ] , [
        sh:path ex:opportunityStage ;
        sh:in ("Lead" "Qualified" "Proposal" "Negotiation" "Won" "Lost") ;
    ] .

# 客户公司规模
ex:AccountShape
    a sh:NodeShape ;
    sh:targetClass ex:Account ;
    sh:property [
        sh:path ex:accountSize ;
        sh:in ("SMB" "Mid" "Enterprise") ;
    ] .
```

## 5. 进阶练习

1. "本月新签的客户"
2. "本季度最长的销售周期"
3. "各线索来源转化率排行"
4. "王经理的所有商机"
5. "客户行业 × 销售交叉分析"
6. "本季度销售冠军是谁"

## 6. 跟 AI Agent 集成

```python
# 销售问："上汽通用最近进展？"
def ask(customer_name):
    return g.query(f"""
    PREFIX ex: <http://crm.com/>
    SELECT ?opp ?stage ?amt ?date WHERE {{
        ?c ex:customerName "{customer_name}" .
        ?o ex:opportunityForCustomer ?c ;
           ex:opportunityName ?opp ;
           ex:opportunityStage ?stage ;
           ex:opportunityAmt ?amt ;
           ex:opportunityCloseDate ?date .
    }} ORDER BY DESC(?date)
    """)
```

## 7. 实际场景拓展

可加：
- `ex:Contract`（合同管理）
- `ex:Quote`（报价单）
- `ex:Invoice`（发票）
- `ex:Commission`（销售提成）
- `ex:Territory`（区域）
- `ex:MarketingCampaign`（市场活动）

## 8. 文件清单

```
crm/
├── README.md
├── crm-query.py                  ← 7 个查询全跑通
└── data/
    ├── crm-ont.ttl              ← 本体（3 销售/3 产品/6 客户/4 联系人/5 公司/8 线索/8 商机/8 活动）
    ├── crm-shapes.ttl           ← SHACL 规则
    └── crm-data.ttl              ← 业务数据
```
