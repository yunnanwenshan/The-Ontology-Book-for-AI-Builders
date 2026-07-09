# 实战案例 4 · 财务本体

> **场景**：电商公司的供应商合同 + 发票 + 付款 + 科目
> **难度 / 时间**：⭐⭐ 中级 / 1 小时
> **谁在用**：财务总监看 KPI / 会计问 Claude / 开发者跑 finance-query.py

> **场景**：电商公司的供应商合同 + 发票 + 付款 + 科目
> **目标**：让 AI 1 秒回答 6 个财务总监每天问的问题
## 1. 业务问题

财务总监（你）每天问：
- "7 月哪些合同到期？"
- "哪些发票还没付？"
- "本月付款总额？"
- "各供应商付款分布？"
- "超期未付的发票（风险）？"
- "各科目汇总？"

## 2. 跑 demo

```bash
cd ~/Documents/projects/ai/ontology/05-real-cases/finance
python3 finance-query.py
```

**真实输出**（已验证）：

```
数据校验：✅ 通过

Q1: 7 月到期的合同
  （无）

Q2: 未付款发票
  inv-004  北京广告公司  ¥30000.00  开票 2026-06-15

Q3: 7 月付款总额
  ¥0

Q4: 各供应商付款金额
  北京广告公司  ¥40000.00  (1 笔)
  上海物流有限公司  ¥35000.00  (2 笔)
  深圳软件服务商  ¥10000.00  (1 笔)

Q5: 风险：7 月前开票但未付
  inv-004  北京广告公司  ¥30000.00  2026-06-15

Q6: 各科目付款汇总
  1002  银行存款  ¥85000.00
```

## 3. 业务价值

| 不用本体 | 用本体 |
|---------|--------|
| 财务手工汇总（Excel 公式）| 1 秒 SPARQL |
| 漏看风险发票 | 自动监控超期 |
| 跨表 join 难 | 一张图全关联 |
| 合规靠人盯 | SHACL 自动校验（税号、合同号格式）|

## 4. SHACL 校验的合规规则（这条最重要）

```turtle
# 供应商必须有税号
ex:VendorShape
    a sh:NodeShape ;
    sh:targetClass ex:Vendor ;
    sh:property [
        sh:path ex:taxId ;
        sh:minCount 1 ;
        sh:pattern "^[0-9A-Z]{15,20}$" ;   # 中国税号 15-20 位
    ] .

# 合同号必须规范
ex:ContractShape
    a sh:NodeShape ;
    sh:targetClass ex:Contract ;
    sh:property [
        sh:path ex:contractNo ;
        sh:pattern "^C-\\d{4}-\\d{3}$" ;   # C-2026-001 格式
    ] .
```

## 5. 进阶练习

1. "8 月到期的合同"
2. "本月每个供应商各付了多少"
3. "所有'管理费用'科目的付款"
4. "合同金额 > 10 万的所有合同"
5. "付款用了哪些支付方式？各多少"
6. "北京广告公司所有未付发票"

## 6. 实际场景拓展

把 `finance-data.ttl` 换成你公司的真实数据：
- 金蝶导出 Excel → 转 CSV → `2-csv-to-rdf.py` 跑
- 4 个科目可以扩到 30+ 个
- 合同类型可以加 `ex:LeaseContract`（租赁合同）

## 7. 跟 AI Agent 集成

接 Anthropic Claude + MCP：

```python
# 让 Claude 直接调这 6 个查询
TOOLS = [{
    "name": "finance_query",
    "description": "查询合同、发票、付款、科目...",
    "input_schema": {
        "type": "object",
        "properties": {
            "query_name": {"enum": ["contracts_due", "unpaid_invoices", "monthly_payments",
                                     "vendor_payments", "overdue_invoices", "account_totals"]},
            "params": {"type": "object"}
        }
    }
}]
```

## 8. 文件清单

```
finance/
├── README.md
├── finance-query.py                ← 6 个查询全跑通
└── data/
    ├── finance-ont.ttl            ← 本体（4 科目/3 供应商/4 合同/5 发票/4 付款）
    ├── finance-shapes.ttl         ← SHACL 规则
    └── finance-data.ttl            ← 业务数据
```
