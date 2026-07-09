# The LLM Grounding Playbook

> **中文副标题**：让 LLM 不胡说 — 7 个本体实战 + 1 个 Palantir 风格平台
> **版本**：v1.0 · 2026-07

> **完整教程**：写给开发者的小白友好版
> **作者手记**：本教程基于 Palantir Foundry / AIP 工程化理念 + 8 个真实业务案例
> **目标读者**：开发者、架构师、数据治理工程师
> **配套代码**：~6000 行 Python + 12 个本体文件 + 6 个 Foundry 平台脚本

---

## 前言

> **作者建议**：先读  了解踩过的坑。
> **遇到错误**：查  的故障排查节。

## 目录

- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 

---

## 第 0 章 · 写在前面

### 这本书解决什么问题？

AI（特别是 LLM）是个会编故事的算命先生。
**本体**是给算命先生的一本"真经"。

这本书教你：

1. **哲学 2400 年的"分类学"** — 人类怎么给世界分类
2. **知识表示 60 年的演变** — 怎么让机器"懂"
3. **4 个核心规范** — RDF / RDFS / OWL / SHACL / SPARQL
4. **5 分钟跑通第一个 demo** — 不装 Docker，纯 Python
5. **7 个真实业务案例** — HR/客服/财务/商品/医疗/物流/CRM
6. **Palantir Foundry 风格企业平台** — Object/Action/Function + ABAC + CDC
7. **AIP / MCP 集成** — 让 LLM 调本体

### 谁应该读？

- ✅ **AI 应用开发者**：用 LLM 但被幻觉折磨
- ✅ **软件架构师**：设计数据中台、语义层
- ✅ **数据治理工程师**：统一跨系统 schema
- ✅ **技术负责人**：评估语义网 / 本体 / KG 技术栈

### 怎么读？

- **30 分钟版**：第 0-3 章 + 第 10 章
- **4 小时版**：第 4-8 章 + 跑 7 个案例中的 2 个
- **3 周系统学**：按顺序读 + 跑全部代码

---

## 第 1 章 · 哲学源流

> 2400 年里，人类一直在问同一个问题：**世界怎么分类？**

### 1.1 亚里士多德（前 384 - 前 322）· 范畴与定义

"狗是什么？" = 动物（属）+ 会叫、胎生、哺乳（种差）

**对今天的影响**：RDFS 的 `rdfs:subClassOf`。

### 1.2 莱布尼茨（1646 - 1716）· 通用语言

"能不能把所有人类知识都写进一套符号里？"

**对今天的影响**：URI（每个东西有唯一地址）+ RDF（每个事实有唯一表示）。

### 1.3 康德（1724 - 1804）· 范畴与判断

"人类认识世界前，已经有一些'先天框架'（时间、空间、因果）。"

**对今天的影响**：本体就是给 AI 的"先天框架"。

### 1.4 弗雷格（1848 - 1925）· 谓词逻辑

"发明了谓词逻辑（'所有人都会死，苏格拉底是人，所以苏格拉底会死'）。"

**对今天的影响**：OWL 的底层 = Description Logic（描述逻辑）。

### 1.5 1990s · 哲学进入工程

| 年 | 事件 | 影响 |
|---|---|---|
| 1991 | 第一次"ontology"协作定义 | 工程化起点 |
| 1993 | Gruber 写"本体是共享概念化的形式化说明" | **最常被引用的定义** |
| 1998 | Studer 加"显式" | 更严格 |
| 2001 | Noy & McGuinness 发 101 教程 | **工程师入门必读** |

### 1.6 Gruber 1993 的经典定义（人话版）

> **本体 = 把大家头脑里"我们怎么理解这个领域"这件事，写成机器能读的文档。**

拆开看：
- **"大家"** = 不是一个人的想法，是团队共识
- **"怎么理解"** = 抽象的概念（不是具体数据）
- **"写成"** = 用形式化语言（OWL）
- **"机器能读"** = AI 能用

---

## 第 2 章 · 知识表示

> 60 年里，人类怎么把"我知道的东西"写下来，让机器也能看。

### 2.1 60 年时间线

```
1968  Quillian 发明语义网络（画图）
  ↓
1975  Minsky 框架理论（结构化）
  ↓
1985  KL-ONE（带推理的本体）
  ↓
1998  Tim Berners-Lee 提出语义网
  ↓
2004  RDF 成为 W3C 标准
  ↓
2004  OWL 1.0
  ↓
2009  OWL 2
  ↓
2011  SPARQL 1.0
  ↓
2017  SHACL
  ↓
2024  Anthropic 发布 MCP（让 Agent 调本体）
  ↓
2025  Palantir Foundry 模式成为企业数据中台主流
  ↓
2026  LLM + Ontology 重新成为热点
```

### 2.2 为什么 2025 年又火本体？

- LLM 幻觉严重 → 需要"事实核查层"
- 知识图谱 + 向量 = GraphRAG
- MCP 让 Agent 直接调本体
- **本体的角色变了**：从"独立知识库"变成"AI 的脚手架"

---

## 第 3 章 · AI 时代为什么需要本体

### 3.1 LLM 的三大"病"

#### 3.1.1 幻觉（Hallucination）

**症状**：模型一本正经说错信息。
**根因**：模型是概率机器，"什么像真的"≠"什么真"。
**本体怎么治**：LLM 不知道答案时，**先去本体查**。查到了就引用，没查到就说"我查不到"。

#### 3.1.2 数据孤岛

**症状**：销售数据在 MySQL，物流在 PostgreSQL，订单在 Oracle。
**本体怎么治**：用统一 schema 把不同表映射到同一组概念。

#### 3.1.3 黑盒

**症状**：模型答对了，但不知道为什么。
**本体怎么治**：每条结论附本体路径，审计可回放。

### 3.2 一张决策表

| 场景 | 需要本体？ | 为什么 |
|---|---|---|
| 通用聊天 | 不太需要 | 没有结构化数据 |
| 客服（订单查询） | 强烈需要 | 订单数据是结构化的、要准 |
| 文档问答 | 部分需要 | 文档为主，本体辅助 |
| 决策支持 | 极需要 | 不允许错 |
| 跨组织数据交换 | 极需要 | 双方需要共同 schema |
| 多 Agent 协作 | 强烈需要 | Agent 共享世界模型 |

### 3.3 决策树

```
你的数据有结构化 schema 吗？
  │
  ├── 否 → 用 RAG
  │
  └── 是
      ├── 准确率 95%+？→ 本体 + SPARQL
      └── 灵活为主？  → RAG / GraphRAG
```

---

## 第 4 章 · RDF：所有事实的最小单元

### 4.1 一句话

**RDF = 一切皆"主-谓-宾"三元组（Triple）**

### 4.2 第一个 RDF

```turtle
@prefix ex: <http://example.com/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

ex:Neo a ex:Hacker ;
    ex:realName "Thomas Anderson" ;
    ex:loves ex:Trinity .

ex:Trinity a ex:Hacker ;
    ex:loves ex:Neo .
```

读作：Neo 是一个 Hacker，他的真名是 Thomas Anderson，他爱 Trinity。

### 4.3 5 个最常用模式

1. `ex:Alice a ex:Person`（声明类型）
2. `ex:Alice ex:age 30`（数据属性）
3. `ex:Alice ex:knows ex:Bob`（对象关系）
4. `ex:Alice rdfs:label "Alice"@zh`（多语言标签）
5. `ex:Alice ex:birthday "1995-01-01"^^xsd:date`（带类型字面量）

### 4.4 5 分钟上手（Python）

```python
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF

g = Graph()
EX = Namespace("http://example.com/")

g.add((EX.Alice, RDF.type, EX.Person))
g.add((EX.Alice, EX.age, Literal(30)))
g.add((EX.Alice, EX.knows, EX.Bob))

print(g.serialize(format="turtle"))
```

**输出**：
```turtle
@prefix ns1: <http://example.com/> .

ns1:Alice a ns1:Person ;
    ns1:age 30 ;
    ns1:knows ns1:Bob .
```

---

## 第 5 章 · RDFS/OWL：让机器"懂"

### 5.1 RDFS：类层级

```turtle
ex:Hacker rdfs:subClassOf ex:Person .
ex:Tom a ex:Hacker .
# 推理机自动推出：Tom 是 Person
```

### 5.2 OWL：5 个类构造器

```turtle
# 交集
ex:EmployedStudent owl:equivalentClass [
    owl:intersectionOf (ex:Employee ex:Student)
] .

# 并集
ex:FamilyMember owl:equivalentClass [
    owl:unionOf (ex:Parent ex:Child ex:Spouse)
] .

# 全称量词
ex:Person rdfs:subClassOf [
    owl:onProperty ex:hasChild ;
    owl:allValuesFrom ex:Human
] .
```

### 5.3 OWL：5 个属性特征

```turtle
ex:ancestorOf a owl:TransitiveProperty .
ex:marriedTo a owl:SymmetricProperty .
ex:Male owl:disjointWith ex:Female .
ex:hasBirthday a owl:FunctionalProperty .
ex:hasParent owl:inverseOf ex:hasChild .
```

---

## 第 6 章 · SPARQL：本体的 SQL

### 6.1 5 个最常用模式

```sparql
# 1. 基本
SELECT ?x WHERE { ?x a ex:Class }

# 2. 过滤
SELECT ?x WHERE { ?x ex:age ?a . FILTER (?a > 18) }

# 3. 可选
SELECT ?x ?y WHERE { ?x a ex:Class . OPTIONAL { ?x ex:y ?y } }

# 4. 联合
SELECT ?x WHERE { { ?x a ex:A } UNION { ?x a ex:B } }

# 5. 路径
SELECT ?x WHERE { ex:Alice ex:knows+ ?x }
```

### 6.2 5 分钟上手：查 Wikidata

```python
from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
sparql.setReturnFormat(JSON)
sparql.setQuery("""
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>

SELECT ?film ?filmLabel WHERE {
  ?film wdt:P57 wd:Q25191 .    # 诺兰导演
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . }
} LIMIT 5
""")
for r in sparql.query().convert()["results"]["bindings"]:
    print(r["filmLabel"]["value"])
```

**输出**：
```
Inception
The Dark Knight
Interstellar
...
```

---

## 第 7 章 · SHACL：业务规则守门员

### 7.1 业务问题

OWL 偏"分类"（什么是订单），但不擅长"约束"（订单必须有客户）。

### 7.2 第一个 SHACL Shape

```turtle
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix ex: <http://example.com/> .

ex:OrderShape
    a sh:NodeShape ;
    sh:targetClass ex:Order ;
    sh:property [
        sh:path ex:customer ;
        sh:minCount 1 ;
        sh:class ex:Customer ;
    ] .
```

### 7.3 10 个最常用约束

| 约束 | 含义 |
|---|---|
| `sh:minCount N` | 至少 N 个值 |
| `sh:maxCount N` | 最多 N 个值 |
| `sh:datatype xsd:int` | 数据类型 |
| `sh:minInclusive N` | 最小值 |
| `sh:pattern "..."` | 正则 |
| `sh:in (...)` | 枚举 |
| `sh:class ex:X` | 必须是某类 |

---

## 第 8 章 · 5 分钟跑通第一个 demo

### 8.1 装环境

```bash
pip install rdflib pyshacl SPARQLWrapper
```

### 8.2 跑第一个 demo

```bash
cd ~/Documents/projects/ai/ontology/04-zero-install-demo
python3 examples/1-first-rdf.py
```

**输出**：
```
=== 你的第一个 RDF ===
  http://example.com/Alice -- ...knows --> ...Bob
  http://example.com/Alice -- ...type --> ...Person
  ...
共 4 条三元组
```

---

## 第 9 章 · 7 个真实业务案例

### 9.1 案例对照

| 案例 | 路径 | 适合 |
|---|---|---|
| **HR 招聘** |  | HR/招聘经理 |
| **客服** |  | 客服主管 |
| **财务** |  | 财务总监/会计 |
| **商品** |  | 电商运营/采购 |
| **医疗** |  | 医院 IT/医生 |
| **物流** |  | 物流经理/客服 |
| **CRM** |  | 销售总监/VP |

### 9.2 每个案例的结构

```
case-name/
├── README.md            ← 业务问题 + 跑法
├── case-query.py        ← 跑通的查询
└── data/
    ├── case-ont.ttl     ← 本体
    ├── case-shapes.ttl  ← SHACL 规则
    └── case-data.ttl    ← 业务数据
```

### 9.3 跑 HR 案例

```bash
cd ~/Documents/projects/ai/ontology/05-real-cases/hr
python3 hr-query.py
```

**输出**（节选）：
```
数据校验：✅ 通过

Q1: 销售总监还招不招？
  答案：是，还招

Q2: Offer 阶段的有谁？
  李四  →  高级 Python 工程师

Q4: 各状态人数
  Interviewing: 2 人
  OfferSent: 1 人
  ...
```

---

## 第 10 章 · Palantir Foundry 风格平台

### 10.1 架构对齐

| Palantir 概念 | 我们的实现 |
|---|---|
| Object Type | `owl:Class` (12 个) |
| Link Type | `ObjectProperty` + `owl:inverseOf` (5 个) |
| Property | `DatatypeProperty` (22 个) |
| Action Type | 子类 + Python 函数 (5 个) |
| Function | Python 函数 (2 个) |
| SHACL | Object Validation (7 个 Shape) |
| Pipeline Builder | R2RML 物化脚本 |
| Workshop | HTML 仪表盘 |
| AIP | MCP Server (7 工具) |

### 10.2 4 个工程模块

```bash
cd ~/Documents/projects/ai/ontology/05-real-cases/foundry-platform

# 1. 核心 9 section
python3 run_platform.py

# 2. AIP / MCP Server
python3 mcp_server.py

# 3. R2RML 物化（SQL → RDF）
python3 r2rml_materialize.py

# 4. HTML 仪表盘
python3 build_dashboard.py
```

### 10.3 端到端工程流程

```
ERP/MySQL
   ↓ r2rml_materialize.py
RDF Graph
   ↓ SHACL 验证
本体平台（4 个脚本）
   ├── run_platform.py
   ├── mcp_server.py → Claude Desktop
   └── build_dashboard.py → dashboard.html
```

---

## 第 11 章 · AIP / MCP：让 LLM 调本体

### 11.1 MCP Server

```bash
python3 mcp_server.py --mcp
```

**7 个 MCP 工具**：

| 工具 | 作用 |
|---|---|
| `query_orders` | 查订单 |
| `get_order_detail` | 订单详情 |
| `dashboard_kpi` | KPI |
| `reconcile_orders` | 对账 |
| `approve_order` | 审核订单 |
| `reserve_inventory` | 分配库存 |
| `assign_customer` | 分配客户 |

### 11.2 接入 Claude Desktop

`~/Library/Application Support/Claude/claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "platform": {
      "command": "python3",
      "args": ["/path/to/mcp_server.py", "--mcp"]
    }
  }
}
```

### 11.3 对话示例

用户：**"查华为的所有订单"**
Claude 调 `query_orders(customer_name="华为")` → 返回真实业务数据。

---

## 第 12 章 · 工程化进阶

### 12.1 ABAC 权限

`abac_security.py` 实现：

- 4 个敏感度等级（Public / Internal / Confidential / Restricted）
- 6 个用户角色
- 字段级过滤（销售看不到付款金额）
- 持久化到 `platform-ont-with-security.ttl`

**真实输出**：
```
王经理（销售部经理）→ 客户 ✅ 金额 ✅ 邮箱 ✅ 付款 🔒
李销售（销售员）    → 客户 ✅ 金额 ✅ 邮箱 🔒 付款 🔒
赵财务（财务总监）  → 客户 ✅ 金额 ✅ 邮箱 ✅ 付款 ✅
```

### 12.2 CDC 实时同步

`cdc_demo.py` 监控源数据文件，变化时自动物化：

```
[Round 2] 📝 模拟 ERP 写入新订单
           写入订单 O0000000006
[Round 3] 🔔 检测到文件变化！
           触发物化...
           ✓ 物化完成：19 个 Object 实例
```

### 12.3 HTML 仪表盘

`build_dashboard.py` 生成 Foundry Workshop 风格的暗色仪表盘：

- 4 个 KPI 卡
- 10 个 Object Type 分布
- 订单全链路表格
- Action 时间线

---

## 第 13 章 · 30 道实战作业

### Level 1（基础）

1. 写你的家庭本体（5 个人 + 关系网）
2. 把 CSV 转 RDF
3. 从 JSON 转 RDF
4. 找最贵的商品
5. 找 Bob 买过什么

### Level 2（进阶）

1. 用 SHACL 校验"金额 > 0"
2. 用 SHACL 校验手机号格式
3. 写 OWL 父子类推理
4. 跨属性校验
5. 建模"商品系统"（SPU/SKU/库存/价表）

### Level 3（实战）

1. "上个月销售额"
2. "VIP 客户"
3. "工单超时"
4. "补货预警"
5. "业绩排名"

---

## 附录 A · 资源与工具速查

### A.1 W3C 规范

| 规范 | 链接 |
|---|---|
| RDF 1.1 | https://www.w3.org/TR/rdf11-concepts/ |
| RDFS | https://www.w3.org/TR/rdf-schema/ |
| SPARQL 1.1 | https://www.w3.org/TR/sparql11-query/ |
| OWL 2 | https://www.w3.org/TR/owl2-overview/ |
| SHACL | https://www.w3.org/TR/shacl/ |
| R2RML | https://www.w3.org/TR/r2rml/ |

### A.2 Python 工具

| 库 | 装 |
|---|---|
| rdflib | `pip install rdflib` |
| pyshacl | `pip install pyshacl` |
| owlready2 | `pip install owlready2` |
| SPARQLWrapper | `pip install SPARQLWrapper` |
| mcp | `pip install mcp` |

### A.3 三元组库

| 工具 | 适合 |
|---|---|
| Apache Jena + Fuseki | 学习、原型 |
| GraphDB | 生产 |
| Stardog | 大型项目 |
| Oxigraph | 嵌入式 |

### A.4 编辑器

| 工具 | 网址 |
|---|---|
| Protégé | https://protege.stanford.edu/ |
| TopBraid Composer | https://www.topquadrant.com/ |
| WebVOWL | http://vowl.visualdataweb.org/ |

### A.5 公共数据源

| 源 | 数据 |
|---|---|
| Wikidata | https://www.wikidata.org/ |
| DBpedia | https://dbpedia.org/ |
| schema.org | https://schema.org/ |

---

## 附录 B · 常见陷阱与最佳实践

### B.1 七大常见陷阱

1. **过度建模**：200 个类，70% 永远不被用
2. **命名不一致**：`hasCustomer` / `hasCustomerRef` / `customerId`
3. **混淆 TBox 和 ABox**
4. **谓词方向混乱**（用 `owl:inverseOf`）
5. **闭世界假设搞反**（OWL 开世界，SHACL 闭世界）
6. **时间维度没处理**
7. **URI 不稳定**（用数据库 ID）

### B.2 十大最佳实践

1. 先用现成本体（schema.org / FOAF）
2. 单一来源原则
3. 从需求倒推
4. 用 Noy & McGuinness "七步法"
5. 版本化
6. 加多语言 label
7. 写测试用例
8. 性能与表达力平衡
9. 治理流程
10. 文档化

---

## 附录 C · 术语表

| 术语 | 一句话 |
|---|---|
| **本体 (Ontology)** | 共享概念化的形式化说明 |
| **类 (Class)** | 一类事物的抽象 |
| **实例 (Instance)** | 具体的一个事物 |
| **属性 (Property)** | 特征或关系 |
| **三元组 (Triple)** | RDF 的原子单位 |
| **TBox** | 概念层（类、属性定义）|
| **ABox** | 实例层（具体数据）|
| **RDF** | 资源描述框架 |
| **OWL** | Web 本体语言 |
| **SHACL** | 形状约束语言 |
| **SPARQL** | RDF 查询语言 |
| **ABAC** | 基于属性的访问控制 |
| **CDC** | 变更数据捕获 |
| **AIP** | AI Platform（Palantir）|
| **MCP** | Model Context Protocol |
| **GraphRAG** | RAG + 知识图谱 |

---

## 写在最后

2400 年前，亚里士多德问"狗是什么"。

今天，你用 RDF + OWL 写出了答案，让 AI 也能"懂"。

哲学 → 工程 → AI 应用：

```
亚里士多德     →    RDFS subClassOf
莱布尼茨       →    URI
康德          →    Ontology
弗雷格        →    OWL Description Logic
Gruber 1993   →    "共享概念化的形式化说明"
2004 W3C      →    RDF 成为标准
2017          →    SHACL
2024-11       →    MCP 协议
2025-2026     →    LLM + Ontology 主流
2026          →    你正在读这本书
```

**下一步**：

1. 跑通 8 个案例
2. 把数据接 MCP
3. 接入 Claude Desktop
4. 在你的公司试点
5. 写你自己的本体

**最后一句话**：

> **AI 没有本体 = 会说人话的算命先生**
> **AI 有了本体 = 看过病历的医生**

---

*本教程由 Hermes Agent 协作完成，代码全部真机验证。*
