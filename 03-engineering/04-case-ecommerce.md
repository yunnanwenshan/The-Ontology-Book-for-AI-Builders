# 阶段 3.4 · 实战案例：电商智能问答助手

> **一句话**：从 0 搭一个"促销活动问答"系统
> **目标**：2 小时做出能 demo 的完整系统

## 1. 一句话总结

**今天做完 5 件事**：
1. 写本体（50 行）
2. 写 SHACL 规则（30 行）
3. 填数据（30 行）
4. 写 3 个 SPARQL 查询
5. 接 Claude API + 简单聊天界面

## 2. 生活类比

```
本体    = 商品的"分类目录"     "iPhone 是 手机"
SHACL   = 商品的"上架规则"     "必须有价格"
数据    = 实际的"商品库存"     "5 台 iPhone"
SPARQL  = 查库存的"问法"      "还有几台 iPhone？"
聊天界面 = 用户的"购物界面"
```

## 3. 准备工作

```bash
# 启动 Fuseki（如果有上一节的 docker）
cd ~/ontology-hello && docker compose up -d

# 新建项目目录
mkdir -p ~/promo-bot && cd ~/promo-bot
mkdir -p data
```

## 4. 核心本体（50 行）

新建 `data/promo.owl.ttl`：

```turtle
@prefix ex: <http://shop.com/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# === 类定义 ===
ex:Product    a owl:Class ; rdfs:label "商品"@zh .
ex:Promotion  a owl:Class ; rdfs:label "促销活动"@zh .
ex:Discount   a owl:Class ; rdfs:label "折扣规则"@zh .
ex:Order      a owl:Class ; rdfs:label "订单"@zh .

# === 类层级 ===
ex:Electronics rdfs:subClassOf ex:Product .
ex:Phone       rdfs:subClassOf ex:Electronics .

# === 属性 ===
ex:hasPromotion rdfs:domain ex:Product ; rdfs:range ex:Promotion .
ex:discountRule rdfs:domain ex:Promotion ; rdfs:range ex:Discount .
ex:startDate    rdfs:domain ex:Promotion ; rdfs:range xsd:dateTime .
ex:endDate      rdfs:domain ex:Promotion ; rdfs:range xsd:dateTime .
ex:minAmount    rdfs:domain ex:Discount  ; rdfs:range xsd:decimal .
ex:discountAmt  rdfs:domain ex:Discount  ; rdfs:range xsd:decimal .

# === 约束：每个促销必须恰好有 1 个折扣规则 ===
ex:Promotion rdfs:subClassOf [
    a owl:Restriction ;
    owl:onProperty ex:discountRule ;
    owl:cardinality 1 ;
] .
```

## 5. SHACL 规则（30 行）

新建 `data/promo.shacl.ttl`：

```turtle
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix ex: <http://shop.com/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:PromotionShape
    a sh:NodeShape ;
    sh:targetClass ex:Promotion ;
    sh:property [
        sh:path ex:startDate ;
        sh:minCount 1 ;
        sh:datatype xsd:dateTime ;
    ] , [
        sh:path ex:endDate ;
        sh:minCount 1 ;
        sh:datatype xsd:dateTime ;
    ] , [
        sh:path ex:discountRule ;
        sh:minCount 1 ;
        sh:nodeKind sh:IRI ;
    ] .

ex:DiscountShape
    a sh:NodeShape ;
    sh:targetClass ex:Discount ;
    sh:property [
        sh:path ex:minAmount ;
        sh:minInclusive 0 ;
    ] , [
        sh:path ex:discountAmt ;
        sh:minInclusive 0 ;
    ] .
```

## 6. 业务数据（30 行）

新建 `data/promo-data.ttl`：

```turtle
@prefix ex: <http://shop.com/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# === 促销 1：618 全场满 200 减 50 ===
ex:promo-001 a ex:Promotion ;
    ex:startDate "2025-05-25T00:00:00"^^xsd:dateTime ;
    ex:endDate   "2025-06-18T23:59:59"^^xsd:dateTime ;
    ex:discountRule ex:disc-001 .

ex:disc-001 a ex:Discount ;
    ex:minAmount 200 ;
    ex:discountAmt 50 .

# === 促销 2：手机 9 折 ===
ex:promo-002 a ex:Promotion ;
    ex:startDate "2025-06-01T00:00:00"^^xsd:dateTime ;
    ex:endDate   "2025-06-30T23:59:59"^^xsd:dateTime ;
    ex:discountRule ex:disc-002 .

ex:disc-002 a ex:Discount ;
    ex:minAmount 0 ;
    ex:discountAmt 0.10 .   # 10% off

# === 商品 ===
ex:iphone-15 a ex:Phone ;
    ex:hasPromotion ex:promo-002 , ex:promo-001 .

ex:xiaomi-14 a ex:Phone ;
    ex:hasPromotion ex:promo-001 .

ex:ipad-pro a ex:Electronics ;
    ex:hasPromotion ex:promo-001 .
```

## 7. 一键校验 + 入库

### 7.1 校验 SHACL

新建 `validate.py`：

```python
from pyshacl import validate
from rdflib import Graph

shapes = Graph().parse("data/promo.shacl.ttl",  format="turtle")
data   = Graph().parse("data/promo-data.ttl", format="turtle")

conforms, report, _ = validate(data, shacl_graph=shapes, inference="rdfs")
print(f"通过？ {conforms}")
if not conforms:
    print(report if isinstance(report, str) else report.decode())
```

```bash
python3 validate.py
# 期望：True
```

### 7.2 上传到 Fuseki

```bash
# 创建 /promo dataset
curl -X POST http://admin:admin@localhost:3030/$/datasets \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "dbName=promo&dbType=tdb2"

# 上传数据
curl -X POST http://admin:admin@localhost:3030/promo/data \
    -H "Content-Type: text/turtle" \
    --data-binary @data/promo.owl.ttl

curl -X POST http://admin:admin@localhost:3030/promo/data \
    -H "Content-Type: text/turtle" \
    --data-binary @data/promo-data.ttl
```

## 8. 关键查询

### 8.1 "哪些商品参加满 200 减 50"

```sparql
PREFIX ex: <http://shop.com/>
SELECT ?product WHERE {
    ?product ex:hasPromotion ?promo .
    ?promo ex:discountRule ?disc .
    ?disc ex:minAmount 200 ;
           ex:discountAmt 50 .
}
```

### 8.2 "6 月手机有哪些活动"

```sparql
PREFIX ex: <http://shop.com/>
SELECT ?phone ?promo WHERE {
    ?phone a ex:Phone ;
           ex:hasPromotion ?promo .
    ?promo ex:startDate ?s ;
           ex:endDate ?e .
    FILTER (?s <= "2025-06-30T23:59:59"^^xsd:dateTime &&
            ?e >= "2025-06-01T00:00:00"^^xsd:dateTime)
}
```

### 8.3 "所有促销活动的折扣规则"

```sparql
PREFIX ex: <http://shop.com/>
SELECT ?promo ?min ?off WHERE {
    ?promo ex:discountRule ?disc .
    ?disc ex:minAmount ?min ;
           ex:discountAmt ?off .
}
```

## 9. 接入 Claude API

### 9.1 安装

```bash
pip install anthropic gradio
export ANTHROPIC_API_KEY="sk-ant-..."
```

### 9.2 写聊天界面

新建 `chatbot.py`：

```python
import gradio as gr
import requests
import json
from anthropic import Anthropic

client = Anthropic()
ENDPOINT = "http://localhost:3030/promo/query"

# 模板化查询（避免 Agent 写错 SPARQL）
QUERIES = {
    "products_in_promotion": {
        "desc": "哪些商品参加指定促销活动",
        "sparql": """
            PREFIX ex: <http://shop.com/>
            SELECT ?product WHERE {
                ?product ex:hasPromotion ?promo .
                ?promo ex:discountRule ?disc .
                ?disc ex:minAmount {min} ;
                       ex:discountAmt {off} .
            }
        """
    },
    "phone_promos_in_range": {
        "desc": "某时间段内手机的促销",
        "sparql": """
            PREFIX ex: <http://shop.com/>
            SELECT ?phone ?promo WHERE {
                ?phone a ex:Phone ;
                       ex:hasPromotion ?promo .
                ?promo ex:startDate ?s ;
                       ex:endDate ?e .
                FILTER (?s <= "{end}"^^xsd:dateTime &&
                        ?e >= "{start}"^^xsd:dateTime)
            }
        """
    }
}

def run_ontology(query_template: str, params: dict) -> list:
    sparql = query_template.format(**params)
    resp = requests.get(ENDPOINT, params={"query": sparql, "format": "json"})
    return resp.json()["results"]["bindings"]

TOOLS = [{
    "name": "run_query",
    "description": "查询促销活动、商品、订单等结构化信息。\n可用查询：\n- products_in_promotion: 哪些商品参加指定促销（参数: min, off）\n- phone_promos_in_range: 某时间段手机的促销（参数: start, end）",
    "input_schema": {
        "type": "object",
        "properties": {
            "query_name": {"type": "string", "enum": list(QUERIES.keys())},
            "params": {"type": "object"}
        },
        "required": ["query_name", "params"]
    }
}]

def chat(message, history):
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2000,
        tools=TOOLS,
        messages=[{"role": "user", "content": message}]
    )

    # 处理 tool calls
    while response.stop_reason == "tool_use":
        tool = next(b for b in response.content if b.type == "tool_use")
        result = run_ontology(QUERIES[tool.input["query_name"]]["sparql"],
                              tool.input["params"])
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=2000,
            tools=TOOLS,
            messages=[
                {"role": "user", "content": message},
                {"role": "assistant", "content": response.content},
                {"role": "user",
                 "content": [{"type": "tool_result",
                              "tool_use_id": tool.id,
                              "content": json.dumps(result, ensure_ascii=False)}]}
            ]
        )

    return response.content[0].text

gr.ChatInterface(chat, title="促销活动问答助手").launch()
```

### 9.3 启动

```bash
python3 chatbot.py
```

浏览器打开 http://localhost:7860 即可。

## 10. 5 个测试问题

1. "哪些商品参加满 200 减 50？" → iPhone 15、小米 14、iPad Pro
2. "6 月手机有哪些活动？" → iPhone 15 有 2 个
3. "所有促销活动的折扣规则" → promo-001 和 promo-002
4. SHACL 校验故意改坏数据：end < start → 应报错
5. 加新促销：直接编辑 promo-data.ttl，上传，新查询立即可见

## 11. 完整文件结构

```
~/promo-bot/
├── data/
│   ├── promo.owl.ttl      ← 本体
│   ├── promo.shacl.ttl    ← 业务规则
│   └── promo-data.ttl     ← 业务数据
├── validate.py            ← SHACL 校验脚本
├── chatbot.py             ← 聊天界面
└── README.md
```

## 12. 速读建议

| 时间 | 看哪几节 |
|------|----------|
| 10 分钟 | 1-3、4-6（写本体+数据） |
| 20 分钟 | + 7-8（校验+查询） |
| 40 分钟 | + 9（接 Claude） |
| 60 分钟 | 跑通整个 demo |

## 13. 避坑提示

- ❌ **别忘了 `PREFIX`**：没前缀查询不到
- ❌ **别用错日期类型**：`^^xsd:dateTime` 不要漏
- ✅ **先测 SHACL**：上传前先 `python3 validate.py`
- ❌ **别让 Agent 自由生成 SPARQL**：用模板
- ✅ **工具描述要详细**：让 Agent 知道怎么用
- ❌ **别忘了 `ANTHROPIC_API_KEY`**：export 一下

## 参考文献

- Gradio. https://gradio.app/
- Anthropic Tool Use. https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/overview
- Apache Jena Fuseki. https://jena.apache.org/documentation/fuseki2/
