# 附录 A · 资源与工具速查

> 全部工具/书/网站，按"我应该用哪个"分类。

## A.1 编辑器（写本体用）

| 工具 | 难度 | 适合 | 网址 |
|------|------|------|------|
| **Protégé** | ⭐⭐ | 学生、工程师 | https://protege.stanford.edu/ |
| **TopBraid Composer** | ⭐⭐⭐ | 企业 | https://www.topquadrant.com/ |
| **PoolParty** | ⭐⭐ | 业务方 | https://www.poolparty.biz/ |
| **WebVOWL** | ⭐ | 所有人（看图）| http://vowl.visualdataweb.org/ |
| **VSCode + RDF 插件** | ⭐⭐ | 程序员 | 看 VSCode 市场 |

**新手推荐**：先装 Protégé，自带 "Pizza" 例子，玩 10 分钟就懂。

## A.2 三元组库（存 RDF 用）

| 工具 | 类型 | 难度 | 适合 | 网址 |
|------|------|------|------|------|
| **Apache Jena + Fuseki** | 开源 | ⭐⭐ | 学习、原型 | https://jena.apache.org/ |
| **GraphDB Free** | 商业免费版 | ⭐⭐ | 生产 | https://graphdb.ontotext.com/ |
| **Stardog** | 商业 | ⭐⭐⭐ | 大型 | https://www.stardog.com/ |
| **Blazegraph** | 开源 | ⭐⭐ | AWS Neptune 前身 | https://github.com/blazegraph/database |
| **Oxigraph** | 开源 | ⭐ | Rust 嵌入 | https://oxigraph.org/ |
| **Neo4j + RDF 插件** | 商业 | ⭐⭐ | 已有 Neo4j | https://neo4j.com/ |

**新手推荐**：Docker 跑 Fuseki（参考 03-engineering/01）。

## A.3 Python 库（写代码用）

| 库 | 干什么 | 装 |
|-----|--------|-----|
| **rdflib** | RDF 处理（事实标准）| `pip install rdflib` |
| **pyshacl** | SHACL 校验 | `pip install pyshacl` |
| **owlready2** | OWL 操作 | `pip install owlready2` |
| **SPARQLWrapper** | 远程 SPARQL 查询 | `pip install SPARQLWrapper` |
| **ontoenv** | 多本体管理 | `pip install ontoenv` |
| **anthropic** | Claude API | `pip install anthropic` |
| **gradio** | 聊天界面 | `pip install gradio` |

## A.4 物化 / 映射（SQL → RDF）

| 工具 | 干什么 | 难度 |
|------|--------|------|
| **Ontop** | 实时 SQL → RDF | ⭐⭐ |
| **morph-RDB** | 物化 | ⭐⭐ |
| **DB2Triples** | D2RQ 后继 | ⭐⭐⭐ |
| **R2RML Toolkit** | 标准处理 | ⭐⭐ |

## A.5 推理机（让机器"推理"用）

| 工具 | 备注 |
|------|------|
| **Pellet** | 经典 OWL DL 推理机 |
| **HermiT** | 斯坦福出品 |
| **FaCT++** | 轻量 |
| **ELK** | 医学领域常用（OWL 2 EL）|
| **Jena Reasoner** | 内置 RDFS + 部分 OWL |

## A.6 经典教材（书）

| 书 | 作者 | 难度 | 适合 |
|-----|------|------|------|
| *A Semantic Web Primer* (3rd) | Antoniou, van Harmelen | ⭐⭐ | 入门首选 |
| *Semantic Web for the Working Ontologist* (2nd) | Allemang, Hendler | ⭐⭐ | 工程师友好 |
| *Foundations of Semantic Web Technologies* | Hitzler, Krötzsch | ⭐⭐⭐ | 进阶 |
| *Learning SPARQL* (2nd) | Bob DuCharme | ⭐⭐ | SPARQL 速成 |
| *Ontology Engineering* | Staab, Studer | ⭐⭐⭐ | 学术派 |
| *Programming the Semantic Web* | Segaran, Evans, Taylor | ⭐⭐ | Python 视角 |

**新手推荐**：先读 *Semantic Web for the Working Ontologist*（案例多）。

## A.7 公共数据源（现成 KG）

| 数据源 | 数据量 | 用途 | 网址 |
|--------|--------|------|------|
| **Wikidata** | 1 亿+ | 通用 | https://www.wikidata.org/ |
| **DBpedia** | 几千万 | 维基百科结构化 | https://dbpedia.org/ |
| **Schema.org** | 几千 | 网页标记 | https://schema.org/ |
| **GeoNames** | 几百万 | 地理 | https://www.geonames.org/ |
| **FOAF** | 几百 | 人 + 关系 | http://xmlns.com/foaf/spec/ |
| **UniProt** | 几亿 | 蛋白质 | https://www.uniprot.org/ |
| **Gene Ontology** | 几万 | 基因 | http://geneontology.org/ |
| **ConceptNet** | 几千万 | 常识 | https://conceptnet.io/ |

## A.8 大模型 + 本体项目

| 项目 | 干什么 |
|------|--------|
| **LangChain** | LLM + KG 集成 |
| **LlamaIndex** | KG-RAG |
| **Microsoft GraphRAG** | 社区检测 + 摘要 |
| **Neo4j LLM Builder** | 一键建图 |
| **LangChain SPARQL Chain** | NL → SPARQL |
| **OWL2Vec*** | OWL → embedding |
| **Microsoft Fabric IQ Ontology** | 企业级本体 + MCP |

## A.9 学到什么程度用哪个

| 你的水平 | 用什么 |
|----------|--------|
| 5 分钟 demo | Docker + Fuseki |
| 1 周 | Protégé + 写小本体 |
| 1 月 | Ontop + SPARQL + R2RML |
| 3 月 | SHACL + 推理机 + 性能调优 |
| 1 年 | 自研企业级本体平台 |

## A.10 速查 URL

| 资源 | 网址 |
|------|------|
| W3C 语义网首页 | https://www.w3.org/2001/sw/ |
| W3C RDF | https://www.w3.org/RDF/ |
| W3C SPARQL | https://www.w3.org/TR/sparql11-query/ |
| W3C OWL | https://www.w3.org/TR/owl2-overview/ |
| W3C SHACL | https://www.w3.org/TR/shacl/ |
| W3C R2RML | https://www.w3.org/TR/r2rml/ |
| Apache Jena | https://jena.apache.org/ |
| Protégé | https://protege.stanford.edu/ |
| Wikidata SPARQL | https://query.wikidata.org/ |
| schema.org | https://schema.org/ |
| Anthropic MCP | https://modelcontextprotocol.io/ |
