# 阶段 2.4 · SHACL：业务规则守门员

> **一句话**：用 SHACL 把"订单必须有客户"写成机器可校验的规则
> **目标**：能写 5 种常见业务规则

## 1. 一句话总结

- **OWL 擅长"分类"**：什么是订单
- **SHACL 擅长"校验"**：订单必须有客户、金额必须 > 0

OWL + SHACL = 完整本体解决方案。

## 2. 生活类比：质检员

```
OWL   = 商品说明书       "这是水瓶，500ml，塑料"
SHACL = 质检标准         "瓶身不能有裂纹、容量不能少于 480ml、必须印生产日期"
```

**OWL 描述"是什么"，SHACL 检查"对不对"。**

## 3. 为什么需要 SHACL（OWL 做不到的）

| 业务规则 | 用 OWL？ | 用 SHACL？ |
|---------|----------|------------|
| 订单必须有客户 | 难（OWL 偏"分类"）| ✅ 容易 |
| 金额必须 > 0 | 难 | ✅ 容易 |
| 状态只能是 {草稿/已签/已付} | 难 | ✅ 容易 |
| 每个商品至少有 1 张图片 | 难 | ✅ 容易 |

**OWL 适合推理，SHACL 适合校验。**

## 4. SHACL 第一个 Shape

**需求**："每个 Order 至少有 1 个 customer"

```turtle
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix ex: <http://example.com/shop#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:OrderShape
    a sh:NodeShape ;                       # 节点 shape
    sh:targetClass ex:Order ;              # 目标：所有 Order 实例
    sh:property [
        sh:path ex:customer ;              # 校验 customer 属性
        sh:minCount 1 ;                    # 至少 1 个
        sh:maxCount 1 ;                    # 最多 1 个
        sh:class ex:Customer ;             # 必须是 Customer
    ] .
```

**注意**：
- `sh:NodeShape` 表示对"节点"校验（对类）
- `sh:property` 表示对"属性"校验
- `sh:path` 指向被校验的属性

## 5. 10 个最常用约束

| 约束 | 含义 | 例子 |
|------|------|------|
| `sh:minCount N` | 至少 N 个值 | 订单至少 1 个商品 |
| `sh:maxCount N` | 最多 N 个值 | 身份证号最多 1 个 |
| `sh:datatype xsd:int` | 数据类型 | 年龄必须是整数 |
| `sh:minInclusive N` | 数值最小值 | 金额 ≥ 0 |
| `sh:maxInclusive N` | 数值最大值 | 折扣 ≤ 100 |
| `sh:pattern "^1[3-9]\d{9}$"` | 正则 | 手机号 |
| `sh:nodeKind sh:IRI` | 必须是 URI | customer 必须指向某个实体 |
| `sh:nodeKind sh:Literal` | 必须是字面量 | 名字必须是字符串 |
| `sh:in ( ... )` | 枚举 | 状态 ∈ {draft, paid, shipped} |
| `sh:class ex:X` | 必须是某类 | customer 必须是 Customer |

## 6. 5 个高级约束

### 6.1 AND（必须都满足）

```turtle
sh:and (
    [ sh:property [ sh:path ex:name ; sh:minCount 1 ] ]
    [ sh:property [ sh:path ex:age  ; sh:minInclusive 0 ] ]
)
```

### 6.2 OR（任一满足）

```turtle
sh:or (
    [ sh:property [ sh:path ex:phone ] ]
    [ sh:property [ sh:path ex:email ] ]
)
# 至少 phone 或 email 二选一
```

### 6.3 NOT（都不满足）

```turtle
sh:not [
    sh:property [ sh:path ex:deletedAt ]
]
# 不能有 deletedAt
```

### 6.4 比较两个属性

```turtle
sh:property [
    sh:path ex:endDate ;
    sh:greaterThan ex:startDate ;   # 结束 > 开始
]
```

**SHACL 内置比较**：
- `sh:lessThan`
- `sh:lessThanOrEquals`
- `sh:greaterThan`
- `sh:greaterThanOrEquals`
- `sh:equals`
- `sh:disjoint`

### 6.5 跨节点校验（PropertyShape）

校验"订单的客户必须有邮箱"：
```turtle
ex:OrderShape sh:property [
    sh:path ex:customer ;
    sh:node ex:CustomerShape ;  # 引用另一个 Shape
] .

ex:CustomerShape sh:property [
    sh:path ex:email ;
    sh:minCount 1 ;
] .
```

## 7. 业务案例：促销规则

### 7.1 需求

- 每个促销必须有结束时间
- 结束时间 > 开始时间
- 折扣率 ∈ [0, 1)
- 适用商品至少 1 个

### 7.2 SHACL 实现

```turtle
ex:PromotionShape
    a sh:NodeShape ;
    sh:targetClass ex:Promotion ;
    sh:property [
        sh:path ex:startDate ;
        sh:minCount 1 ;
        sh:datatype xsd:dateTime ;
    ] , [
        sh:path ex:endDate ;
        sh:minCount 1 ;
        sh:datatype xsd:dateTime ;
    ] , [
        sh:path ex:discount ;
        sh:datatype xsd:decimal ;
        sh:minInclusive 0.0 ;
        sh:maxExclusive 1.0 ;
    ] , [
        sh:path ex:appliesTo ;
        sh:minCount 1 ;
        sh:class ex:Product ;
    ] ;
    sh:property [
        sh:path ex:endDate ;
        sh:greaterThan ex:startDate ;
    ] .
```

## 8. 5 分钟上手：用 Python 跑 SHACL 校验

```bash
pip install pyshacl rdflib
```

**Shapes**（`shapes.ttl`）：
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
    ] .
```

**数据**（`data.ttl`）：
```turtle
@prefix ex: <http://example.com/shop#> .

ex:order-001 a ex:Order ;
    ex:amount 299.00 .
    # 故意不写 ex:customer，触发错误
```

**校验**（`validate.py`）：
```python
from pyshacl import validate
from rdflib import Graph

shapes = Graph().parse("shapes.ttl", format="turtle")
data   = Graph().parse("data.ttl",   format="turtle")

conforms, report, _ = validate(data, shacl_graph=shapes, inference="none")
print(f"通过？ {conforms}")
print("---报告---")
print(report.decode() if isinstance(report, bytes) else report)
```

**运行**：
```bash
python3 validate.py
```

**输出**：
```
通过？ False
---报告---
Validation Report
Conforms: False
Results (1):
    Severity: sh:Violation
    Focus Node: <http://example.com/shop#order-001>
    Message: Less than 1 values for ex:customer
```

**恭喜**：你抓到一条业务规则违反。

## 9. 把校验接到 CI

```bash
# .github/workflows/shacl.yml
name: SHACL Check
on: [push]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install deps
        run: pip install pyshacl rdflib
      - name: Run SHACL
        run: python scripts/validate_all.py
```

每次 PR 跑一次，业务规则不通过不让合并。

## 10. SHACL vs OWL vs SPIN

| 维度 | OWL | SHACL | SPIN |
|------|-----|-------|------|
| 标准 | W3C 2004/2009 | W3C 2017 | 已弃用 |
| 偏重 | 分类、推理 | 校验 | 规则 |
| 学习曲线 | 陡 | 中 | 中 |
| 工业化 | 中 | 强 | 弱 |

**推荐组合**：
- OWL（分类）
- SHACL（约束）
- SPARQL（查询）

## 11. 避坑提示

- ❌ **别把业务规则写在 OWL 里**：用 SHACL
- ❌ **别在 SHACL 里写复杂逻辑**：超过 5 行就拆
- ❌ **别忘了 `sh:targetClass`**：没它，shape 不会跑
- ✅ **用 `sh:severity` 标严重程度**：`sh:Violation` / `sh:Warning` / `sh:Info`
- ✅ **用 `sh:message` 写友好提示**：`"订单 {?this} 必须有客户"`
- ❌ **别在生产用 RDFS 推理 + SHACL**：先关闭推理，只校验
- ✅ **用 shape group 分类管理**：`ShapeClass:CustomerShapes`、`ShapeClass:OrderShapes`

## 12. 速读建议

| 时间 | 看哪几节 |
|------|----------|
| 5 分钟 | 1、2、3、4 |
| 15 分钟 | + 5、6、7 |
| 30 分钟 | + 8、9（跑通校验脚本） |

## 参考文献

- W3C. (2017). *Shapes Constraint Language (SHACL)*. https://www.w3.org/TR/shacl/
- Knublauch, H. (2017). *SHACL and OWL Compared*. https://shacl.dev/
- pyshacl. https://github.com/RDFLib/pyshacl
