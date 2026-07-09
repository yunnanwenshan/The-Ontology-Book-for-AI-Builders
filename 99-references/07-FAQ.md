# 附录 E · 常见问题 FAQ

> 30 个小白最容易问的问题。

## 一、基础概念

### Q1. 本体和数据库表有什么区别？

**A**：表存"数据"，本体存"数据 + 含义"。

```
数据库：
  CREATE TABLE customer (id INT, name VARCHAR(50));
  → 只知道"有 customer 表，有 name 字段"

本体：
  ex:Customer a owl:Class ;
      rdfs:label "客户"@zh, "Customer"@en .
  → 知道"客户"是什么、有多语言名、属于哪一类概念
```

### Q2. 本体和 JSON Schema 有什么区别？

**A**：JSON Schema 校验结构，本体表达语义。

```
JSON Schema：
  → 检查"name 字段是字符串、必填"
  → 不说"name 是什么"

本体：
  → 说"name 是人类的标识符，有语言标签"
  → 可以跨数据源合并
```

### Q3. RDF 和图数据库（Neo4j）有什么区别？

**A**：RDF 是标准，图数据库是产品。

| RDF | 图数据库（Neo4j） |
|-----|-------------------|
| W3C 标准 | 私有协议（Cypher）|
| 互操作好 | 性能高 |
| 推理强 | 灵活 |
| 慢 | 快 |

**建议**：跨组织/标准场景用 RDF；高性能场景用图数据库。

### Q4. 我公司没"本体"，能不能用这套方法？

**A**：能。本体可以一步步建。

```
第一周：跑通最小 demo（看 03-engineering/01）
第二周：把一个核心业务用本体描述
第三周：让一个真实查询用 SPARQL
```

## 二、技术细节

### Q5. URI 怎么命名？

**A**：用稳定的业务键。

```
✅ 好的：
  http://shop.com/product/ISBN-978-7-...
  urn:uuid:f47ac10b-58cc-4372-a567-0e02b2c3d479

❌ 坏的：
  http://shop.com/order/12345      ← DB id 会变
  http://shop.com/product/1024     ← 1024 指代什么？
```

### Q6. 命名空间（prefix）怎么选？

**A**：用你的域名。

```turtle
@prefix shop: <http://shop.com/ont#> .
@prefix schema: <https://schema.org/> .  # 复用现成
```

**推荐**：核心本体用自己的，细节属性用 schema.org 等现成的。

### Q7. 什么时候用 RDFS，什么时候用 OWL？

**A**：看你需要"推理"多深。

| 场景 | 用什么 |
|------|--------|
| 简单类层级 | RDFS |
| 需要推理（如传递性） | OWL |
| 业务规则校验 | SHACL |
| 推理慢 / 不需要 | 全用 RDFS |

**经验**：80% 业务场景 RDFS 就够。

### Q8. OWL 推理很慢，怎么破？

**A**：分层用。

```
1. 设计阶段：用 OWL + 推理机（验证模型对）
2. 加载阶段：推理一次，存结果
3. 查询阶段：关掉推理，纯查 RDF
```

### Q9. SHACL 和 OWL 规则怎么选？

**A**：看目的。

| 目的 | 用什么 |
|------|--------|
| "订单必须有客户" | SHACL |
| "客户和用户是同一类" | OWL |
| "VIP 客户 = 消费超 10 万" | SHACL（用 SPARQL-based SHACL）|
| "人是动物" | OWL（推理）|

## 三、工程实战

### Q10. 怎么把 SQL 数据转 RDF？

**A**：三种方式。

| 方式 | 适合 |
|------|------|
| **R2RML（Ontop）** | 实时查询 SQL |
| **物化** | 小数据，准实时 |
| **CDC** | 大数据，变更捕获 |

详见 `03-engineering/01-hello-world.md`。

### Q11. Fuseki 太慢了怎么办？

**A**：换更快的。

| 工具 | 速度 | 适合 |
|------|------|------|
| **Fuseki** | 中 | 学习、原型 |
| **GraphDB** | 快 | 生产 |
| **Stardog** | 极快 | 大型项目 |
| **Oxigraph** | 极快 | Rust 应用 |

### Q12. 怎么监控本体层？

**A**：看 4 个指标。

```
1. SPARQL 查询延迟（P95 < 1s）
2. SHACL 校验通过率
3. 推理机响应时间
4. 三元组数量
```

### Q13. 数据更新怎么办？

**A**：三个策略。

| 策略 | 适合 | 延迟 |
|------|------|------|
| 物化+定时 ETL | 小数据 | 分钟级 |
| CDC（Debezium） | 中数据 | 秒级 |
| 实时查询 | 大数据 | 即时 |

## 四、跟 LLM 集成

### Q14. 怎么让 LLM 写 SPARQL？

**A**：不建议。**用模板化查询**。

```python
# ❌ 让 LLM 生成
sparql = llm.generate(f"用户问：{question}，生成 SPARQL")

# ✅ 模板化
QUERIES = {
    "top_customers": "SELECT ?name ...",
    "by_date": "SELECT ?order WHERE { ... }",
}
```

### Q15. 怎么防 SPARQL 注入？

**A**：3 招。

```python
# 1. 用模板（不要字符串拼接）
sparql = template.format(min=200)  # 自动转义

# 2. 用 SPARQLWrapper 的预处理
from SPARQLWrapper import SPARQLWrapper
sparql = SPARQLWrapper("...")
sparql.setQuery(...)
# 参数化查询

# 3. 加查询超时
# Fuseki config: ja:queryTimeout "5000"
```

### Q16. Agent 怎么知道有哪些"动作"？

**A**：工具定义 + 本体约束。

```python
TOOLS = [
    {
        "name": "query_orders",
        "description": "查询订单...支持日期范围、客户 ID、状态",
        "input_schema": {
            "type": "object",
            "properties": {
                "date_range": {"type": "string"},
                "customer_id": {"type": "string"},
            }
        }
    }
]
```

### Q17. 怎么把本体接 Claude Desktop？

**A**：用 MCP。详见 `03-engineering/02-architecture.md` 第 5 节。

### Q18. 怎么测 Agent 准确率？

**A**：建测试集。

```python
TEST_CASES = [
    ("哪些客户买过 iPhone？", "Alice, Bob"),
    ("3 月订单总额？", "15000"),
    ("VIP 客户？", "Alice"),
]
```

## 五、性能与扩展

### Q19. 多少数据量用 RDF？

**A**：10 亿三元组以下都 OK。

| 三元组数 | 工具 |
|----------|------|
| < 1 千万 | Fuseki |
| 1 千万 - 1 亿 | GraphDB / Stardog |
| > 1 亿 | 商业方案 + 分片 |

### Q20. 怎么优化 SPARQL 查询？

**A**：5 个技巧。

```sparql
# 1. 加 LIMIT
SELECT ?x WHERE { ... } LIMIT 100

# 2. 用具体类型
?x a ex:Customer  # 不用 ?x a ?type

# 3. 避免 OPTIONAL + FILTER 组合
# OPTIONAL + FILTER 会扫全表

# 4. 用命名图分片
# 5. 预计算常用聚合
# 比如每天跑一次"VIP 客户"CONSTRUCT
```

## 六、避坑

### Q21. 最容易踩的 3 个坑？

**A**：

1. **URI 用数据库 ID** → 改成业务键
2. **OWL 写业务规则** → 改用 SHACL
3. **让 LLM 自由生成 SPARQL** → 改用模板

### Q22. 我已经用了 RAG，怎么升级到本体？

**A**：3 步。

```
1. 把 RAG 找出的候选，扔到本体里验证
   → 提准确率
2. 把高频问题用 SPARQL 模板化
   → 降成本
3. 把业务规则用 SHACL 写
   → 加合规
```

### Q23. 本体要不要中文？

**A**：要。加多语言 label。

```turtle
ex:Contract rdfs:label "合同"@zh, "Contract"@en .
```

**LLM 读中文 label 推理更准**。

### Q24. 怎么让业务方也懂本体？

**A**：用图，不用文字。

```
1. 画一张类图（用 WebVOWL）
2. 给每个类加 1-2 个真实例子
3. 业务方只需懂"类"和"关系"
```

WebVOWL：http://vowl.visualdataweb.org/

### Q25. 团队没人会 OWL 怎么办？

**A**：3 个办法。

```
1. 用现成本体（schema.org、FOAF）— 80% 场景够用
2. 用低代码工具（TopBraid、PoolParty）— 鼠标点
3. 雇 1 个懂 OWL 的人 — 1 个人就能撑起
```

## 七、展望

### Q26. 本体会被 LLM 替代吗？

**A**：不会。**互补**。

```
LLM：模糊匹配、生成、对话
本体：精确事实、推理、约束
```

没有 LLM 的本体：不好用（要写 SPARQL）。
没有本体的 LLM：会胡说。

### Q27. 未来 3 年本体会怎么发展？

**A**：3 个趋势。

```
1. **GraphRAG 主流化**
   → 向量 + 图 混合检索
2. **本体自动构建**
   → LLM 帮你写 OWL
3. **本体即服务（Ontology-as-a-Service）**
   → 微软 Fabric IQ Ontology
   → Google Knowledge Catalog
```

### Q28. 应该学 SPARQL 还是 Cypher？

**A**：学 SPARQL。

```
SPARQL：标准、W3C、跨工具
Cypher：Neo4j 私有、性能好
```

**经验**：先 SPARQL，需要性能再换 Cypher。

### Q29. 用知识图谱还是向量数据库？

**A**：看你需要"事实"还是"相似度"。

| 你要 | 用 |
|------|----|
| "iPhone 15 多少钱"（事实）| 知识图谱 |
| "类似 iPhone 的手机"（相似）| 向量数据库 |
| "iPhone 15 适合什么场景"（综合）| 两者结合 |

### Q30. 我应该从哪里开始？

**A**：**跑通 demo**。

```bash
# 5 分钟
cd ~/onto-demo
docker compose up -d
open http://localhost:3030
```

看到界面了，再决定要不要深入。
