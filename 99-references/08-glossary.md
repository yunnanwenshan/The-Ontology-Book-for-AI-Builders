# 附录 F · 术语表

> 不懂就查这里。

| 术语 | 一句话 | 例子 |
|------|--------|------|
| **本体 (Ontology)** | 共享概念化的形式化说明 | "客户、订单、合同"及其关系 |
| **类 (Class)** | 一类事物的抽象 | `ex:Customer`（客户类）|
| **实例 (Instance)** | 具体的一个事物 | `ex:cust-001`（客户 001）|
| **属性 (Property)** | 类/实例的特征或关系 | `ex:hasOrder`（有订单）|
| **三元组 (Triple)** | RDF 的原子单位 | (主语, 谓语, 宾语) |
| **TBox** | 概念层（类、属性定义）| `ex:Customer a owl:Class` |
| **ABox** | 实例层（具体数据）| `ex:Alice a ex:Customer` |
| **RDF** | 资源描述框架 | W3C 标准 |
| **RDFS** | RDF Schema | `subClassOf`、`domain`、`range` |
| **OWL** | Web 本体语言 | 强逻辑，支持推理 |
| **SHACL** | 形状约束语言 | 业务规则校验 |
| **SPARQL** | RDF 查询语言 | 类似 SQL |
| **R2RML** | RDB to RDF 映射语言 | 把 SQL 变 RDF |
| **Turtle** | RDF 的一种语法 | `.ttl` 文件 |
| **URI / IRI** | 统一资源标识符 | `<http://example.com/x>` |
| **字面量 (Literal)** | 具体的值 | `"30"`、`"hello"@zh` |
| **空白节点 (Blank Node)** | 匿名节点 | `_:b1` |
| **前缀 (Prefix)** | 命名空间简写 | `@prefix ex: <http://example.com/>` |
| **推理机 (Reasoner)** | 自动推出新事实的程序 | Pellet、HermiT |
| **MCP** | Model Context Protocol | Agent 调用工具的标准 |
| **RAG** | Retrieval-Augmented Generation | 检索增强生成 |
| **GraphRAG** | RAG + 知识图谱 | 向量 + 图混合 |
| **schema.org** | 网页语义标记词汇表 | 行业标准 |
| **FOAF** | Friend of a Friend | 人 + 关系本体 |
| **SKOS** | 简单知识组织系统 | 分类、词表 |
| **PROV-O** | Provenance Ontology | 溯源本体 |
| **Dublin Core** | 元数据标准 | 题名、作者、日期 |
| **TTL (Terse RDF Triple Language)** | Turtle 缩写 | 常用格式 |
| **JSON-LD** | JSON 格式的 RDF | Web API 友好 |
| **Agent** | AI 智能体 | 能调工具的 LLM |
| **物化 (Materialization)** | 提前计算并存结果 | ETL 变 RDF |
| **CDC** | Change Data Capture | 捕获数据变更 |
| **Debezium** | 开源 CDC 工具 | 监听数据库变更 |
| **Wikidata** | 全球最大公共知识图谱 | 1 亿+ 实体 |
