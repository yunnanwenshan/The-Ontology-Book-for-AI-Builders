# 阶段 2.3 · SPARQL：本体时代的 SQL

> **一句话**：SPARQL = RDF 的 SQL，5 个模式搞定 90% 查询
> **目标**：30 分钟会写 5 种 SPARQL 查询

## 1. 一句话总结

**SPARQL 是给 RDF 数据用的查询语言。**
**语法像 SQL，但操作的是"三元组"而不是"行"。**

| SQL | SPARQL |
|-----|--------|
| `SELECT * FROM table WHERE` | `SELECT ?x WHERE { ?x ... }` |
| 表 | 类 + 属性 |
| 行 | 资源（URI）|

## 2. 生活类比

```
SQL 查数据库 = "从 100 万行里找出上海客户"
SPARQL 查图谱 = "从 100 万个三元组里找出认识 Alice 的人"
```

**两者思路一样**：声明"我要什么"，引擎找出来。

## 3. 第一个 SPARQL 查询

**SQL 版**：
```sql
SELECT name FROM hackers WHERE type = 'Hacker';
```

**SPARQL 版**：
```sparql
PREFIX ex: <http://example.org/matrix#>
SELECT ?name
WHERE {
    ?person a ex:Hacker ;
            ex:name ?name .
}
```

**区别**：用 `?name`（变量）表示"想要这个"。

## 4. 5 个最常用模式

### 4.1 基本图模式（基本查找）

**人话**："所有买过 iPhone 的客户"

```sparql
PREFIX ex: <http://shop.com/>
SELECT ?cust
WHERE {
    ?cust ex:purchased ex:iPhone15 .
}
```

### 4.2 FILTER（过滤）

**人话**："订单金额超过 1000 元的"

```sparql
PREFIX ex: <http://shop.com/>
SELECT ?order ?amount
WHERE {
    ?order a ex:Order ;
           ex:amount ?amount .
    FILTER (?amount > 1000)
}
```

**FILTER 后的条件支持**：
- `>`, `<`, `>=`, `<=`, `=`, `!=`
- `&&`, `||`
- `BOUND(?x)`：变量是否绑定
- `regex(?str, "^1[3-9]")`：正则
- `lang(?str) = "zh"`：语言标签

### 4.3 OPTIONAL（可选）

**人话**："所有客户，**如果有**手机号就显示"

```sparql
PREFIX ex: <http://shop.com/>
SELECT ?cust ?phone
WHERE {
    ?cust a ex:Customer .
    OPTIONAL { ?cust ex:phone ?phone . }
}
```

**没有手机号**的客户也会出现，只是 phone 列为空。

### 4.4 UNION（联合）

**人话**："员工或客户"

```sparql
PREFIX ex: <http://shop.com/>
SELECT ?person
WHERE {
    { ?person a ex:Employee . }
    UNION
    { ?person a ex:Customer . }
}
```

### 4.5 property paths（路径）

**人话**："Alice 的所有朋友的朋友"

```sparql
PREFIX ex: <http://example.com/social#>
SELECT ?fof
WHERE {
    ex:Alice ex:knows+ ?fof .   # + 表示 1 个或多个
}
```

| 路径符号 | 含义 | 例子 |
|---------|------|------|
| `ex:knows` | 1 跳 | 直接朋友 |
| `ex:knows+` | 1+ 跳 | 朋友和朋友 |
| `ex:knows*` | 0+ 跳 | 自己 + 朋友链 |
| `ex:knows/foaf:name` | 1 跳后接 name | 朋友的名字 |
| `ex:knows\|ex:worksWith` | 任一 | 朋友或同事 |

## 5. 5 个聚合函数

```sparql
PREFIX ex: <http://shop.com/>
SELECT (COUNT(?o) AS ?cnt)
       (SUM(?amount) AS ?total)
       (AVG(?amount) AS ?avg)
       (MAX(?amount) AS ?max)
       (MIN(?amount) AS ?min)
WHERE {
    ?o a ex:Order ;
       ex:amount ?amount .
}
```

## 6. 5 分钟上手：用 Wikidata 实战

打开 https://query.wikidata.org/

在浏览器输入框粘这段（**Ctrl+Enter 跑**）：

```sparql
SELECT ?film ?filmLabel ?date WHERE {
  ?film wdt:P57 wd:Q25191 .          # P57 = 导演，Q25191 = 诺兰
  ?film wdt:P577 ?date .             # P577 = 发布日期
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en,zh" . }
}
ORDER BY DESC(?date)
LIMIT 10
```

**返回**：诺兰导演的所有电影，按时间倒序。

**这就是"无幻觉"的 AI 查询**——所有数据来自维基百科事实库。

## 7. 5 分钟上手：用 Python 查 Wikidata

```bash
pip install SPARQLWrapper
```

```python
from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

query = """
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>

SELECT ?film ?filmLabel WHERE {
  ?film wdt:P57 wd:Q25191 .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . }
}
LIMIT 5
"""

sparql.setQuery(query)
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

for r in results["results"]["bindings"]:
    print(r["filmLabel"]["value"])
```

**运行**：
```bash
python3 query_wikidata.py
```

**输出**：
```
Inception
The Dark Knight
Interstellar
...
```

## 8. 真实业务例子

### 8.1 找 3 月买过 iPhone 的客户

```sparql
PREFIX ex: <http://shop.com/>
SELECT ?cust WHERE {
    ?order a ex:Order ;
           ex:customer ?cust ;
           ex:date ?date ;
           ex:item ex:iPhone15 .
    FILTER (?date >= "2025-03-01"^^xsd:date && ?date < "2025-04-01"^^xsd:date)
}
```

### 8.2 找 Alice 的"二度人脉"

```sparql
PREFIX ex: <http://example.com/social#>
SELECT ?fof WHERE {
    ex:Alice (ex:knows/ex:knows) ?fof .
    FILTER (?fof != ex:Alice)
}
LIMIT 100
```

### 8.3 找买过手机且最近 30 天没买手机的客户（推荐用）

```sparql
PREFIX ex: <http://shop.com/>
SELECT DISTINCT ?cust WHERE {
    ?cust ex:purchased ex:iPhone15 .
    FILTER NOT EXISTS {
        ?cust ex:purchased ?other .
        ?other a ex:Phone ;
               ex:purchaseDate ?d .
        FILTER (?d > "2025-05-09"^^xsd:date)
    }
}
```

### 8.4 CONSTRUCT：把查询结果"反向写回"图

```sparql
PREFIX ex: <http://shop.com/>
CONSTRUCT {
    ?cust a ex:VIPCustomer .
}
WHERE {
    {
        SELECT ?cust (SUM(?amount) AS ?spend) WHERE {
            ?order a ex:Order ;
                   ex:customer ?cust ;
                   ex:amount ?amount .
        }
        GROUP BY ?cust
        HAVING (SUM(?amount) > 100000)
    }
}
```

**实际意义**：一次查询，自动给累计消费超 10 万的客户打 VIP 标签。

## 9. 4 个公共端点

| 端点 | 网址 | 数据 |
|------|------|------|
| Wikidata | https://query.wikidata.org/sparql | 全球最大 KG |
| DBpedia | https://dbpedia.org/sparql | 维基百科结构化 |
| 本地 Fuseki | http://localhost:3030/ds/query | 你自己的 |
| bio2rdf | https://bio2rdf.org/sparql | 生物医学 |

## 10. 避坑提示

- ❌ **别忘了 `PREFIX`**：没前缀的查询不报错但慢
- ❌ **别用 `!=` 过滤**：用 `FILTER NOT EXISTS`
- ❌ **别把时间当字符串**："2025-03-01" 加 `^^xsd:date`
- ✅ **先 LIMIT 10 调试**：写完大查询前先 LIMIT 几行看
- ✅ **OPTIONAL 用于"可能有"**：不要用 FILTER 处理缺失
- ❌ **别用 `*` 投影**：`SELECT *` 在 SPARQL 里没意义
- ✅ **明确写 `SELECT ?a ?b`**：列出要的字段

## 11. 速读建议

| 时间 | 看哪几节 |
|------|----------|
| 5 分钟 | 1、2、3 |
| 15 分钟 | + 4、5 |
| 30 分钟 | + 6、7（跑通 Wikidata） |

## 参考文献

- W3C. (2013). *SPARQL 1.1 Query Language*. https://www.w3.org/TR/sparql11-query/
- Wikidata SPARQL Tutorial. https://www.wikidata.org/wiki/Wikidata:SPARQL_tutorial
- SPARQLWrapper. https://sparqlwrapper.readthedocs.io/
