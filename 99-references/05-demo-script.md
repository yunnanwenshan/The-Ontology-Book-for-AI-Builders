# 10 分钟 demo 脚本

> 完整脚本：从 0 到第一个查询，全在 10 分钟内。

## 完整脚本（10 行命令）

```bash
# 1. 建目录
mkdir -p ~/onto-demo && cd ~/onto-demo

# 2. 写 docker-compose.yml
cat > docker-compose.yml <<'EOF'
version: "3.8"
services:
  fuseki:
    image: stain/jena-fuseki:5.0.0
    ports: ["3030:3030"]
    environment:
      - ADMIN_PASSWORD=***      - FUSEKI_DATASET_1=/shop
EOF

# 3. 启动
docker compose up -d
sleep 10

# 4. 创建 dataset
curl -s -X POST http://admin:admin@localhost:3030/\$/datasets \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "dbName=shop&dbType=tdb2"

# 5. 写本体
cat > data.ttl <<'EOF'
@prefix ex: <http://shop.com/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .

ex:Person a owl:Class ; rdfs:label "人"@zh .
ex:knows rdfs:domain ex:Person ; rdfs:range ex:Person .

ex:Alice a ex:Person ; ex:knows ex:Bob .
ex:Bob   a ex:Person ; ex:knows ex:Alice .
ex:Alice a ex:Person ; ex:knows ex:Carol .
EOF

# 6. 上传
curl -X POST http://admin:admin@localhost:3030/shop/data \
    -H "Content-Type: text/turtle" \
    --data-binary @data.ttl

# 7. 第一个查询
curl -G http://localhost:3030/shop/query \
    --data-urlencode "query=PREFIX ex: <http://shop.com/>
SELECT ?friend WHERE {
    ex:Alice ex:knows ?friend .
}"
```

**期望输出**：
```
?friend
<http://shop.com/Bob>
<http://shop.com/Carol>
```

## 一行命令版

把上面 7 步合成一个：

```bash
bash <(curl -s https://raw.githubusercontent.com/.../demo.sh)
```

## 关闭

```bash
docker compose down
```
