# 附录 D · 一页纸 cheat sheet

> 打印这一页贴显示器旁边。

## 三阶段

```
历史理念 → 技术规范 → 工程落地
why        what        how
```

## 4 个核心规范

| 规范 | 干什么 | 关键词 |
|------|--------|--------|
| **RDF** | 记事实 | 三元组：主-谓-宾 |
| **RDFS** | 建类层级 | subClassOf、domain、range |
| **OWL** | 加逻辑 | 推理、约束、互斥 |
| **SHACL** | 校验数据 | 业务规则、SHAPE |
| **SPARQL** | 查数据 | SELECT、WHERE、FILTER |

## 5 个最常用 SPARQL 模式

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

## 5 个最常用 OWL 构造器

```turtle
# 类构造
ex:A   owl:equivalentClass [ owl:intersectionOf (ex:B ex:C) ]  # 交集
ex:A   owl:equivalentClass [ owl:unionOf (ex:B ex:C) ]         # 并集
ex:A   owl:equivalentClass [ owl:complementOf ex:B ]            # 补集

# 属性构造
ex:p   a   owl:TransitiveProperty      # 传递
ex:p   a   owl:SymmetricProperty       # 对称
ex:p   a   owl:FunctionalProperty      # 函数
ex:p   a   owl:InverseFunctionalProperty # 逆函数
ex:p   owl:inverseOf   ex:q            # 逆
ex:A   owl:disjointWith ex:B           # 互斥
```

## 5 个最常用 SHACL 约束

```turtle
sh:property [
    sh:path ex:prop ;
    sh:minCount 1 ;            # 至少 1 个
    sh:maxCount 1 ;            # 最多 1 个
    sh:datatype xsd:int ;      # 数据类型
    sh:minInclusive 0 ;        # 最小值
    sh:maxInclusive 100 ;      # 最大值
    sh:pattern "^1[3-9]\d{9}$" ;  # 正则
    sh:in ( "A" "B" "C" ) ;   # 枚举
    sh:class ex:Customer ;     # 类约束
    sh:nodeKind sh:IRI ;       # 节点类型
]
```

## 决策树

```
你的数据有结构化 schema 吗？
├── 否 → 用 RAG
└── 是
    ├── 准确率 95%+？→ 本体 + SPARQL
    └── 灵活为主？  → RAG / GraphRAG
```

## 5 行启动 Fuseki

```bash
mkdir -p ~/onto && cd ~/onto
cat > docker-compose.yml <<'EOF'
services:
  fuseki:
    image: stain/jena-fuseki:5.0.0
    ports: ["3030:3030"]
    environment: [ADMIN_PASSWORD=***, FUSEKI_DATASET_1=/shop]
EOF
docker compose up -d
sleep 5
open http://localhost:3030
```

## 5 行查询

```bash
curl -G http://localhost:3030/shop/query \
    --data-urlencode "query=PREFIX ex: <http://shop.com/>
SELECT ?x WHERE { ?x a ex:Product } LIMIT 10"
```

## 5 行 Python 校验

```python
from pyshacl import validate
from rdflib import Graph
shapes = Graph().parse("shapes.ttl", format="turtle")
data   = Graph().parse("data.ttl",   format="turtle")
print(validate(data, shacl_graph=shapes, inference="rdfs")[0])
```

## 5 行 MCP Server

```python
from mcp.server import Server
import requests
app = Server("ontology")
@app.tool()
def sparql(q: str): return requests.get(
    "http://localhost:3030/shop/query",
    params={"query": q, "format": "json"}).json()
app.run()
```

## 速查 URL

| 资源 | 网址 |
|------|------|
| 公共 SPARQL | https://query.wikidata.org/ |
| Protégé | https://protege.stanford.edu/ |
| schema.org | https://schema.org/ |
| W3C RDF | https://www.w3.org/TR/rdf11-concepts/ |
| W3C SPARQL | https://www.w3.org/TR/sparql11-query/ |
| W3C SHACL | https://www.w3.org/TR/shacl/ |
| Apache Jena | https://jena.apache.org/ |

## 5 个口头禅

1. "事实进本体，概率进 LLM"
2. "OWL 分类，SHACL 校验，SPARQL 查询"
3. "Agent 不直接调数据库"
4. "模板化查询胜过自由生成"
5. "5 分钟上手，30 分钟理解，3 周精通"
