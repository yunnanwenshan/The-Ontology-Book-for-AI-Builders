# 阶段 3.1 · Hello World：30 分钟跑通本体驱动项目

> **一句话**：30 分钟把一份 SQL 数据变成可查询的本体
> **目标**：跑通 Docker + Fuseki + 第一个 SPARQL

## 1. 一句话总结

**今天 30 分钟做完：**
1. 装 Docker
2. 启动 Fuseki（SPARQL 服务器）
3. 加载 4 个文件（数据 + 本体 + Shape + 查询）
4. 在浏览器看到结果

## 2. 生活类比

```
Fuseki  = 餐厅（点餐系统）
SPARQL  = 菜单 + 点单语言
OWL     = 菜品种类（凉菜/热菜/汤）
数据    = 实际菜品
SHACL   = 菜必须有的条件（必须热、必须有菜名）
```

今天开一家"本体餐厅"。

## 3. 准备（10 分钟）

### 3.1 装 Docker

- **macOS**：
- **Windows**：装 WSL2 后再装 Docker Desktop
- **Linux**：直接 `sudo apt install docker.io`

**检查**：
```bash
docker --version
# 看到版本号即可
```

### 3.2 建工作目录

```bash
mkdir -p ~/ontology-hello && cd ~/ontology-hello
mkdir -p data
```

## 4. 启动 Fuseki（5 分钟）

### 4.1 创建 `docker-compose.yml`

```bash
cat > docker-compose.yml <<'EOF'
version: "3.8"

services:
  fuseki:
    image: stain/jena-fuseki:5.0.0
    container_name: fuseki
    ports:
      - "3030:3030"
    environment:
      - ADMIN_PASSWORD=***      - FUSEKI_DATASET_1=/shop
    volumes:
      - ./data:/fuseki/databases
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3030/$/ping"]
      interval: 10s
      timeout: 5s
      retries: 5
EOF
```

### 4.2 启动

```bash
docker compose up -d
docker compose logs -f fuseki
# 看到 "Started Apache Jena Fuseki" 即可
```

### 4.3 验证

打开浏览器：http://localhost:3030

**应该看到 Fuseki 控制台**。

- 用户名：`admin`
- 密码：`admin`

> ⚠ **避坑**：看不到控制台？等 30 秒，Docker 第一次拉镜像慢。
> 看到 "Connection refused"？检查 Docker Desktop 是否启动。

## 5. 创建第一个本体（5 分钟）

### 5.1 在 Fuseki 里建数据集

1. 打开 http://localhost:3030
2. 点击 "manage datasets" → "add new dataset"
3. Dataset name: `shop`
4. 选 "Persistent"（数据持久化）
5. 点击 "create"

**现在你应该看到 `/shop` dataset**。

### 5.2 加载数据

下载下面 3 个文件到 `~/ontology-hello/data/`：

**1. `ontology.ttl`（本体定义）**：

```turtle
@prefix ex: <http://example.com/shop#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# === 类 ===
ex:Customer a owl:Class ; rdfs:label "客户"@zh .
ex:Order    a owl:Class ; rdfs:label "订单"@zh .
ex:Product  a owl:Class ; rdfs:label "商品"@zh .

# === 属性 ===
ex:customer    rdfs:domain ex:Order    ; rdfs:range ex:Customer .
ex:item        rdfs:domain ex:Order    ; rdfs:range ex:Product .
ex:totalAmount rdfs:domain ex:Order    ; rdfs:range xsd:decimal .
ex:customerName rdfs:domain ex:Customer ; rdfs:range xsd:string .
ex:productName  rdfs:domain ex:Product ; rdfs:range xsd:string .
ex:price        rdfs:domain ex:Product ; rdfs:range xsd:decimal .
```

**2. `data.ttl`（业务数据）**：

```turtle
@prefix ex: <http://example.com/shop#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# 客户
ex:cust-001 a ex:Customer ; ex:customerName "Alice" .
ex:cust-002 a ex:Customer ; ex:customerName "Bob" .
ex:cust-003 a ex:Customer ; ex:customerName "Carol" .

# 商品
ex:item-A a ex:Product ; ex:productName "iPhone 15" ; ex:price 6999.00 .
ex:item-B a ex:Product ; ex:productName "iPad Pro"  ; ex:price 8999.00 .
ex:item-C a ex:Product ; ex:productName "小米 14"   ; ex:price 3999.00 .

# 订单
ex:order-101 a ex:Order ;
    ex:customer ex:cust-001 ;
    ex:item ex:item-A ;
    ex:totalAmount 6999.00 .

ex:order-102 a ex:Order ;
    ex:customer ex:cust-001 ;
    ex:item ex:item-B ;
    ex:totalAmount 8999.00 .

ex:order-103 a ex:Order ;
    ex:customer ex:cust-002 ;
    ex:item ex:item-C ;
    ex:totalAmount 3999.00 .

ex:order-104 a ex:Order ;
    ex:customer ex:cust-003 ;
    ex:item ex:item-A ;
    ex:totalAmount 13998.00 .
```

**3. `shapes.ttl`（业务规则）**：

```turtle
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix ex: <http://example.com/shop#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:OrderShape
    a sh:NodeShape ;
    sh:targetClass ex:Order ;
    sh:property [
        sh:path ex:customer ;
        sh:minCount 1 ;
        sh:class ex:Customer ;
    ] , [
        sh:path ex:totalAmount ;
        sh:datatype xsd:decimal ;
        sh:minInclusive 0 ;
    ] .
```

### 5.3 上传数据

Fuseki 控制台：
1. 点击 `/shop` dataset
2. 选 "add data"
3. 把 `ontology.ttl` 粘进去
4. 点击 "add"
5. 重复 `data.ttl`

或者用 curl：
```bash
curl -X POST http://admin:admin@localhost:3030/shop/data \
    -H "Content-Type: text/turtle" \
    --data-binary @data/ontology.ttl

curl -X POST http://admin:admin@localhost:3030/shop/data \
    -H "Content-Type: text/turtle" \
    --data-binary @data/data.ttl
```

> ⚠ **避坑**：上传时遇到 "Parse Error"？检查 TTL 语法（每行末尾必须有 `.` 或 `;`）。

## 6. 第一个查询（5 分钟）

回到 Fuseki 控制台 `/shop`，点 "query" 标签。

### 6.1 找所有订单

```sparql
PREFIX ex: <http://example.com/shop#>
SELECT ?order ?amount WHERE {
    ?order a ex:Order ;
           ex:totalAmount ?amount .
}
```

点击 "Run"，应该看到 4 条订单。

### 6.2 找 Alice 买过的商品

```sparql
PREFIX ex: <http://example.com/shop#>
SELECT ?product ?price WHERE {
    ?order a ex:Order ;
           ex:customer ?cust ;
           ex:item ?product .
    ?cust ex:customerName "Alice" .
    ?product ex:price ?price .
}
```

**返回**：
```
?product              ?price
<...item-A>           6999.00
<...item-B>           8999.00
```

### 6.3 找消费超过 5000 的客户

```sparql
PREFIX ex: <http://example.com/shop#>
SELECT ?name (SUM(?amount) AS ?total) WHERE {
    ?order a ex:Order ;
           ex:customer ?cust ;
           ex:totalAmount ?amount .
    ?cust ex:customerName ?name .
} GROUP BY ?cust ?name
HAVING (SUM(?amount) > 5000)
```

**返回**：
```
?name   ?total
Alice  15998.00
Carol  13998.00
```

## 7. 跑 SHACL 校验（3 分钟）

```bash
pip install pyshacl rdflib
```

新建 `validate.py`：
```python
from pyshacl import validate
from rdflib import Graph

shapes = Graph().parse("data/shapes.ttl", format="turtle")
data   = Graph().parse("data/data.ttl",   format="turtle")

conforms, report, _ = validate(data, shacl_graph=shapes, inference="rdfs")
print(f"通过？ {conforms}")
print(report if isinstance(report, str) else report.decode())
```

跑：
```bash
python3 validate.py
```

**应该看到**：
```
通过？ True
```

**故意改坏数据**试试：
```turtle
ex:order-bad a ex:Order ;
    ex:totalAmount -100.00 .   # 负数，违反规则
```
重跑会看到违规报告。

## 8. 全部命令回顾

```bash
# 启动
cd ~/ontology-hello
docker compose up -d
sleep 5

# 装 Python 依赖
pip install rdflib pyshacl

# 上传本体
curl -X POST http://admin:admin@localhost:3030/shop/data \
    -H "Content-Type: text/turtle" \
    --data-binary @data/ontology.ttl

# 上传数据
curl -X POST http://admin:admin@localhost:3030/shop/data \
    -H "Content-Type: text/turtle" \
    --data-binary @data/data.ttl

# 校验
python3 validate.py

# 查询（手动或用 curl）
curl -G http://localhost:3030/shop/query \
    --data-urlencode "query=PREFIX ex: <http://example.com/shop#>
SELECT ?o WHERE { ?o a ex:Order }"

# 关停
docker compose down
```

## 9. 避坑提示

- ❌ **别忘了登录认证**：上传用 `admin:admin@`，查询不需要
- ❌ **别用最新镜像**：5.0.0 验证过，其他版本可能有 bug
- ✅ **数据持久化**：选 "Persistent" 而不是 "In-memory"
- ❌ **TTL 末尾没 `.`**：解析失败
- ✅ **先测一个三元组**：上传大文件前先测一行
- ❌ **别忘了关 Docker**：不用时 `docker compose down`

## 10. 下一步

跑通了？恭喜你已经有"事实核查层"了。下一节学：
- 怎么把 SQL 实时变成 RDF（不用 ETL）
- 怎么用 MCP 把本体接 Agent

## 参考文献

- Apache Jena Fuseki. https://jena.apache.org/documentation/fuseki2/
- stain/jena-fuseki. https://hub.docker.com/r/stain/jena-fuseki/
- pyshacl. https://github.com/RDFLib/pyshacl
