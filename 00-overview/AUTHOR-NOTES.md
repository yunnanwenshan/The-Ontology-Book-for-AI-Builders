# 作者手记 · The LLM Grounding Playbook

> **书名**：The LLM Grounding Playbook
> **中文副标题**：让 LLM 不胡说 — 7 个本体实战 + 1 个 Palantir 风格平台

我（作者）写这套教程的思路、踩过的坑、推荐路径。
不是"必须读"，但读完能少走 3 天弯路。

## 我怎么学的这套东西

```
2024.06  LLM 火了，我用它做客服
2024.09  发现 LLM 严重幻觉，问"订单状态"编一个不存在的
2024.10  调研 → 找到 Palantir Foundry 的 Ontology 概念
2024.11  开始读 W3C 规范，发现 RDF/SPARQL/SHACL
2024.12  第一次写 OWL 本体，踩了 3 个坑（详见后）
2025.01  做出第一个 HR 本体
2025.03  累计 7 个业务案例
2025.06  对齐 Palantir Foundry，加 MCP
2025.07  把所有跑通的代码整理成教程
```

## 我踩过的 5 个坑（小白能直接避免）

### 坑 1：把订单/客户/产品画成"独立表"

第一版我画了 3 个类：`Order` / `Customer` / `Product`，然后用 SQL 思路查。

错在哪？**本体不是表，是图**。

第二版改成：
```
Order ---has--> Customer
Order ---contains--> OrderItem ---refersTo--> Product
```

这样查"买了 iPhone 的客户" = `?order ex:contains ?item . ?item ex:refersTo ex:iPhone . ?order ex:has ?cust`。

**教训**：先画"关系"再画"实体"。

### 坑 2：用 OWL 写业务规则

我第一版用 `owl:Restriction` 写"订单至少 1 个商品"。能用，但**慢 + 难调试**。

换成 SHACL 后：
```turtle
ex:OrderShape
    a sh:NodeShape ;
    sh:property [ sh:path ex:contains ; sh:minCount 1 ] .
```

**快 10 倍 + 错误消息直接告诉你"哪个对象违规"**。

**教训**：OWL 用于分类推理，**SHACL 用于业务校验**。

### 坑 3：让 LLM 自由生成 SPARQL

我让 Claude 写 SPARQL 查客户订单。结果：10 个查询 4 个有语法错。

改成**模板化**后：
```python
QUERIES = {
    "by_customer": "SELECT ?o WHERE { ?o ex:has ?c . FILTER (?c = ?custId) }",
    "by_date": "SELECT ?o WHERE { ?o ex:date ?d . FILTER (?d > ?from) }",
}
# Agent 只选模板名 + 填参数
```

**教训**：Agent 不该直接写 SPARQL，**只该选模板**。

### 坑 4：把 ontology 文件当数据

我第一版把 ontology 和数据混在一个 `.ttl` 文件里。结果改 ontology 改 100 处。

分开：
- `*ont.ttl` = 本体（schema），基本不变
- `*data.ttl` = 数据，每天变

**教训**：schema 和 data 分文件，**版本控制分开**。

### 坑 5：忽略 OWL 推理

我以为只要写好 RDFS subClassOf 就够。错。

OWL 推理能推出"传**递性**"（A→B→C 自动出 A→C）和"等价性"（A owl:equivalentClass B）。

例子：
```turtle
ex:hasParent a owl:TransitiveProperty .
ex:Alice ex:hasParent ex:Bob .
ex:Bob   ex:hasParent ex:Charlie .
# 推理：ex:Alice ex:hasParent ex:Charlie
```

但**OWL 推理慢**——生产环境关掉推理，只在设计时用。

**教训**：OWL 推理是**设计工具**不是**运行工具**。

## 我推荐的学习顺序

```
第 1 周（10 小时）：
  Day 1-2: 04 demo（5 个跑通，看懂输出）
  Day 3-4: 02-实战指南（4 篇手把手）
  Day 5:   跑 2 个真实案例（推荐 HR + 财务）

第 2 周（10 小时）：
  Day 1-2: 7 个案例全跑一遍
  Day 3-4: Foundry 平台 6 脚本
  Day 5:   把其中一个案例改成你自己公司的数据

第 3 周（10 小时）：
  Day 1-2: 02-specs（速查手册）
  Day 3-4: ABAC 权限 + CDC 同步
  Day 5:   接 Claude Desktop 跑通 MCP
```

**别跳**。我试过跳，结果是后面 3 个坑才学到。

## 我推荐的项目"试点"流程

1. **挑 1 个最简单的业务场景**（推荐 HR 或 客服）
2. **跑通 demo**（30 分钟）
3. **改成你公司数据**（1-2 小时）
4. **加 1-2 个自己的查询**（30 分钟）
5. **给业务方演示**（30 分钟，让他们提需求）
6. **再加下一个场景**（重复 1-5）

**不要一上来就建企业级本体**——会死在 500 个类的维护上。

## 哪些场景**不要**用本体

我尝试过、但发现不合适的：

| 场景 | 原因 | 用什么 |
|------|------|--------|
| 短文本分类（垃圾邮件） | 实体少、关系少 | 正则 / 分类器 |
| 实时音视频 | 数据太密集 | 流处理 + 向量 |
| 探索性数据分析 | schema 还没定 | pandas / SQL |
| 简单 CRUD | 没"关系" | 数据库 |

**本体适合**：实体多、关系复杂、跨源、需要推理、要查证。

## 哪些场景**必须**用本体

| 场景 | 原因 |
|------|------|
| 跨系统数据整合 | 需要统一 schema |
| 合规审计 | 需要追溯"这个数据从哪来" |
| 复杂业务规则 | 规则超过 10 条就难维护 |
| AI 知识库 | LLM 幻觉，必须有事实锚点 |
| 多 Agent 协作 | Agent 需要共同世界模型 |

## 我没解决的 3 个问题（欢迎你接）

1. **千万级 Object 性能**：RDF 单机跑不了。换 Neptune / Blazegraph
2. **Workshop 拖拽 UI**：HTML 替代品。Foundry Workshop 是 React 应用，难复现
3. **多用户权限 UI**：代码层 ABAC 跑通，UI 登录还没接

## 给读者的 3 个建议

1. **跑通 > 看完**：先跑 demo，再回头看理论
2. **改一下 > 抄一下**：把 `people.csv` 换成你自己的，SPARQL 改成你的问题
3. **失败 > 不跑**：每个错误都是真问题（pyshacl 报错帮我找到 3 个 schema bug）

## 反馈

我写这套教程踩了很多坑，欢迎你：

- 提 Issue：哪里卡住 / 跑不通
- 提 PR：直接改文件
- 提问题：发我，我会加 FAQ

**最重要的是**：跑通你自己的第一个查询。

> 跑通 = 学会了。没跑通 = 没学会。
