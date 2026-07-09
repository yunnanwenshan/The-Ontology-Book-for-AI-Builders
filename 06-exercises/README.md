# 实战作业 · 30 道练习题

> 边学边做。**所有题都能用 `04-zero-install-demo/` 里的代码套路**。

## 作业 1 · RDF 基础（3 道）

### 1.1 写你的家庭本体

写一个 `family.ttl`：
- 至少 5 个家人
- 用 `knows` 关系建一张关系网
- 给 2 个人加 `age` 属性
- 1 个人加 `rdfs:label "..."@zh`

### 1.2 改造 CSV 转 RDF

把 `04-zero-install-demo/examples/2-csv-to-rdf.py` 改成读你自己的 CSV。

### 1.3 从 JSON 转 RDF

写一个脚本，把 JSON 数组转 RDF：

```python
people = [
    {"id": 1, "name": "Alice", "age": 30},
    {"id": 2, "name": "Bob",   "age": 25},
]
```

## 作业 2 · SPARQL 基础（5 道）

数据用 `04-zero-install-demo/data/shop-data.ttl`。

### 2.1 找最贵的商品

```sparql
SELECT ?name ?price WHERE {
    ?p a ex:Product ; ex:name ?name ; ex:price ?price .
} ORDER BY DESC(?price) LIMIT 1
```

### 2.2 找 Bob 买过什么

```sparql
PREFIX ex: <http://example.com/shop#>
SELECT ?product ?price WHERE {
    ?order ex:customer ex:Bob ;
           ex:item ?product .
    ?product ex:price ?price .
}
```

### 2.3 每个客户买了几个商品

```sparql
SELECT ?name (COUNT(?o) AS ?cnt) WHERE {
    ?o ex:customer ?cust ; ex:item ?p .
    ?cust ex:name ?name .
} GROUP BY ?cust ?name
```

### 2.4 金额 > 8000 的订单

```sparql
SELECT ?o ?amount WHERE {
    ?o a ex:Order ; ex:amount ?amount .
    FILTER (?amount > 8000)
}
```

### 2.5 找所有"Apple 公司员工"（挑战）

没数据，自己造 5 个员工 + 1 个公司，建本体，写查询。

## 作业 3 · OWL 推理（3 道）

### 3.1 父子类推理

```turtle
ex:Cat rdfs:subClassOf ex:Animal .
ex:Tom a ex:Cat .
```

问：Tom 是 Animal 吗？写代码验证。

### 3.2 传递性

```turtle
ex:ancestor a owl:TransitiveProperty .
ex:A ex:ancestor ex:B .
ex:B ex:ancestor ex:C .
```

问：A 的祖先包括 C 吗？用 owlready2 跑。

### 3.3 互斥

```turtle
ex:Cat owl:disjointWith ex:Dog .
ex:Fluffy a ex:Cat .
ex:Fluffy a ex:Dog .   # 这会矛盾
```

跑：会报什么错？

## 作业 4 · SHACL（4 道）

数据用 `04-zero-install-demo/data/shop-data.ttl`。

### 4.1 校验金额

写一个 SHACL：每个 Order 金额 > 0 且 <= 100000。

### 4.2 校验状态枚举

状态只能是 {Paid, Cancelled, Shipped, Delivered}。

### 4.3 跨属性校验

每个 Product 必须有 name、price，且 price > 0。

### 4.4 校验客户邮箱

邮箱格式必须 `@` 且 `.`。

## 作业 5 · 业务场景（5 道）

### 5.1 商品管理系统

建模：
- 商品（Product）
- 分类（Category）
- 库存（Inventory）

写本体 + 5 条数据 + 3 个查询。

### 5.2 图书管理系统

建模：
- 图书（Book）
- 作者（Author）
- 出版社（Publisher）
- 借阅（Loan）

加 SHACL 校验：每本书必须有作者和 ISBN。

### 5.3 电影评分系统

建模：
- 电影（Movie）
- 用户（User）
- 评分（Rating）
- 标签（Tag）

写查询：找平均分 > 4 的电影，按分数排。

### 5.4 餐厅订单

建模：
- 餐厅（Restaurant）
- 菜品（Dish）
- 订单（Order）
- 桌号（Table）

查询："5 号桌点了什么"，"今天的总营业额"。

### 5.5 医院病历（进阶）

建模：
- 病人（Patient）
- 医生（Doctor）
- 诊断（Diagnosis）
- 处方（Prescription）

SHACL 规则：每个处方必须关联诊断。

## 作业 6 · 实战（10 道）

数据用你自己的真实业务。

### 6.1 你的团队有几个人？

跑查询。

### 6.2 你公司有多少客户？

跑查询。

### 6.3 上个月销售额？

需要时间过滤。

### 6.4 哪个客户最值钱？

按消费排。

### 6.5 哪个产品最不受欢迎？

按销量排。

### 6.6 哪些订单没付款？

状态过滤。

### 6.7 哪些工单超时了？

时间对比。

### 6.8 你的领导问"上周表现如何"？

综合查询。

### 6.9 老板问"这个月新增多少客户"？

时间 + 计数。

### 6.10 写一篇博客《我是怎么用本体做数据分析的》

把上面 9 题的答案串成一篇。

## 评分

| 题数 | 等级 |
|------|------|
| 0-5 道 | 入门小白 |
| 6-15 道 | 初级开发者 |
| 16-25 道 | 中级专家 |
| 26-30 道 | 高级顾问 |

## 提示

每题答案 ≤ 30 行 Python + 30 行 TTL。

**遇到问题**：
1. 看 `02-实战指南/`
2. 改 `04-zero-install-demo/examples/` 的代码
3. 查 `99-references/07-FAQ.md`

## 速读建议

| 时间 | 做哪些 |
|------|--------|
| 30 分钟 | 作业 1（3 道）|
| 1 小时 | 作业 1-2（8 道）|
| 半天 | 作业 1-3（11 道）|
| 1 天 | 作业 1-4（15 道）|
| 1 周 | 全部 30 道 |
