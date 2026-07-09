# 实战案例 3 · 商品本体

> **场景**：电商 SPU/SKU + 多仓库库存 + 多价表
> **难度 / 时间**：⭐⭐ 中级 / 1 小时
> **谁在用**：运营经理看库存预警 / 采购问 Claude / 开发者跑 product-query.py

> **场景**：电商 SPU/SKU + 多仓库库存 + 多价表
> **目标**：让 AI 1 秒回答 6 个运营/采购每天问的问题
## 1. 业务问题

运营/采购每天问：
- "我们总库存值多少钱？"
- "哪些 SKU 要补货了？" ⚠️
- "上海仓和深圳仓各有多少？"
- "iPhone 15 有几个 SKU？"
- "现在有什么促销？"
- "Apple 和三星哪个卖得好？"

## 2. 跑 demo

```bash
cd ~/Documents/projects/ai/ontology/05-real-cases/product
python3 product-query.py
```

**真实输出**（已验证）：

```
数据校验：✅ 通过

Q1: 总库存金额（按零售价）
  ¥2,939,555.00

Q2: ⚠️ 库存预警（低于安全库存）
  iPad Pro 2TB  @ 上海主仓  现 0 / 安全 10
  iPhone 15 512G 白色  @ 上海主仓  现 5 / 安全 30
  Galaxy S24 512G  @ 深圳南头仓  现 15 / 安全 30

Q3: 各仓库库存
  上海主仓  5 个 SKU  /  共 405 件
  深圳南头仓  2 个 SKU  /  共 45 件

Q4: iPhone 15 下的所有 SKU
  iPhone 15 256G 黑色  (256G/黑色)
  iPhone 15 512G 白色  (512G/白色)

Q5: 当前有效的促销价
  iPhone 15 512G 白色  ¥8499.00  (2026-07-01 ~ 2026-07-31)

Q6: 品牌 SKU 分布
  Apple  2 SPU / 4 SKU  /  库存 235
  三星  1 SPU / 2 SKU  /  库存 215
```

## 3. 业务价值

| 不用本体 | 用本体 |
|---------|--------|
| 每天 5 张 Excel 透视 | 1 秒 SPARQL |
| 漏看要补货的 SKU | 自动预警（低于安全库存）|
| 多仓多价混乱 | 1 张图全关联 |
| 促销过期不提醒 | 1 个查询看哪些在售 |

## 4. SHACL 校验的关键规则

```turtle
# SKU 条形码必须合法
ex:SKUShape
    a sh:NodeShape ;
    sh:targetClass ex:SKU ;
    sh:property [
        sh:path ex:barcode ;
        sh:minCount 1 ;
        sh:pattern "^[0-9]{8,13}$" ;   # EAN-8/12/13
    ] .

# 价格必须 > 0，且类型只能是 4 种之一
ex:PriceShape
    a sh:NodeShape ;
    sh:targetClass ex:PriceList ;
    sh:property [
        sh:path ex:price ;
        sh:minExclusive 0 ;
    ] , [
        sh:path ex:priceType ;
        sh:in ("Retail" "Wholesale" "Promotional" "Member") ;
    ] .
```

## 5. 进阶练习

1. "8 月要补货的所有 SKU 清单"
2. "每仓库的库存金额"
3. "Promotional 价的 SKU 平均比 Retail 便宜多少"
4. "类目'手机'下的所有 SKU"
5. "哪些 SKU 还没在任何价表里？"
6. "销量前 3 的类目"

## 6. 实际场景拓展

`product-data.ttl` 换成你公司真实数据：
- 金蝶/管易/店小秘等 ERP 导出 → 转 RDF
- 加 `ex:Supplier` 实体（采购管理）
- 加 `ex:PurchaseOrder` 实体（采购单）

## 7. 跟 AI Agent 集成

```python
TOOLS = [{
    "name": "product_query",
    "description": "查询商品/库存/价格...",
    "input_schema": {
        "type": "object",
        "properties": {
            "query_name": {"enum": ["total_value", "low_stock", "warehouse_stats",
                                     "sku_by_spu", "active_promo", "brand_stats"]}
        }
    }
}]
```

## 8. 文件清单

```
product/
├── README.md
├── product-query.py                ← 6 个查询全跑通
└── data/
    ├── product-ont.ttl            ← 本体（3 品牌/3 类目/2 仓库/3 SPU/6 SKU/7 库存/6 价表）
    ├── product-shapes.ttl         ← SHACL 规则
    └── product-data.ttl            ← 业务数据
```
