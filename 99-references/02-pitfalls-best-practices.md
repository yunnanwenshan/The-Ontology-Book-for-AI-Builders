# 附录 B · 常见陷阱与最佳实践

> 小白最容易踩的坑 + 大牛都在用的方法。

## B.1 七大常见陷阱

### 1. 过度建模

**症状**：200 个类，70% 永远不被用。

```
❌ 错的：
ex:Customer
  ├── ex:GoldCustomer
  │   ├── ex:GoldCustomerFrom2024
  │   │   ├── ex:GoldCustomerFrom2024Q1
  │   │   │   ├── ex:GoldCustomerFrom2024Q1Region-East
  │   │   │   │   ...  ← 疯了
```

**对策**：
- 3-5 层类层级足够
- 用属性（`ex:level`）表达"金牌/银牌"，不要用类层级
- 任何类只有 1 个实例 → 删掉

### 2. 命名不一致

```
❌ ex:hasCustomer / ex:hasCustomerRef / ex:customerId
✅ ex:hasCustomer （统一）
```

**对策**：
- 单一原则：一个概念一个名
- 优先用 schema.org（schema:customer）
- 风格统一：驼峰 OR 下划线

### 3. 混淆 TBox 和 ABox

```
❌ 在 TBox 写业务数据：
ex:MyCompanySales a owl:Class .   # 这是类定义，不是数据

✅ 在 ABox 写：
ex:sales-2025-q1 a ex:Sales ; ex:amount 1234567 .
```

### 4. 谓词方向混乱

```
❌ 双向都写：
A ex:owns B .
B ex:ownedBy A .

✅ 用 inverseOf：
ex:owns owl:inverseOf ex:ownedBy .
# 数据里只写一个方向
```

### 5. 闭世界假设搞反

- OWL 默认**开世界**：你没说的事实，不代表不存在
- SHACL 默认**闭世界**：必须满足的，就是必须满足

```
❌ 在 OWL 里校验数据：
ex:Person rdfs:subClassOf [
    owl:onProperty ex:name ;
    owl:cardinality 1
] .   # 这样会让没 name 的"不算 Person"

✅ 用 SHACL 校验
```

### 6. 时间维度没处理

```
❌ ex:worksFor ex:Matrix .   # 2024 还是 2026？

✅ 用时间区间：
ex:employment-001 a ex:Employment ;
    ex:person ex:Neo ;
    ex:company ex:Matrix ;
    ex:startDate "2025-01-01"^^xsd:date ;
    ex:endDate   "2025-12-31"^^xsd:date .
```

### 7. URI 不稳定

```
❌ 用数据库 ID：<http://shop.com/order/12345>
   哪天 12345 被复用？URI 指向变了？

✅ 用业务键：<http://shop.com/order/2025-001-AB>
   一旦发布，永久不变
```

## B.2 十条最佳实践

### 1. 先用现成本体

- `schema.org`：电商、人物、地点（**先查这个**）
- `FOAF`：人 + 关系
- `SKOS`：分类、词表
- `Dublin Core`：元数据
- `PROV-O`：溯源

**别重复造轮子**。

### 2. 单一来源原则

一个概念只在一个本体里定义。其他本体要扩展，用 `rdfs:subClassOf`。

### 3. 从需求倒推

```
1. 列出 5-10 个真实问题
2. 看哪些类/属性回答这些问题
3. 只建模"被问到"的
```

### 4. 用"七步法"

来自 Noy & McGuinness 2001：

```
1. 确定领域和范围
2. 考虑复用现成本体
3. 列出关键术语
4. 定义类
5. 定义属性
6. 定义属性的约束（SHACL）
7. 创建实例
```

### 5. 版本化

```turtle
<http://shop.com/ont/2025-01> owl:versionInfo "1.0" ;
                              owl:priorVersion <http://shop.com/ont/2024-12> .
```

### 6. 加多语言 label

```turtle
ex:Customer rdfs:label "客户"@zh, "Customer"@en ;
            rdfs:comment "购买过本平台商品或服务的个人或机构"@zh .
```

**为什么**：
- LLM 读中文 label 推理更准
- 给非本体专家看

### 7. 写测试用例

```turtle
# 测试：每个 Order 都有 customer
ASK WHERE {
    ?o a ex:Order .
    FILTER NOT EXISTS { ?o ex:customer ?c }
}
# 应该返回 false
```

集成到 CI：每次 PR 跑一次。

### 8. 性能与表达力平衡

| 复杂 OWL = 推理慢
| 不推理的 RDFS = 快
| 生产往往**关闭推理**，只跑 SHACL

### 9. 治理流程

| 角色 | 职责 |
|------|------|
| 业务方 | 提需求、改类名 |
| 本体管理员 | 评审、合并 PR |
| 工程师 | 实现映射、加数据 |
| 数据治理 | 监控 SHACL 报告 |

### 10. 文档化

- 本体顶部写"用途"和"非用途"
- 变更要写 changelog
- 每个类至少 1 个真实例子

## B.3 五条"别干"

```
1. ❌ 别用 OWL 表达所有事
   → 推理贵，大部分用 RDFS + SHACL
2. ❌ 别把业务规则藏在代码里
   → 写在 SHACL
3. ❌ 别频繁改本体 URI
   → 一旦发布，永久
4. ❌ 别忽视 SHACL
   → OWL 推理不能替代业务校验
5. ❌ 别跳过"先用现成的"阶段
   → 先用 schema.org，再考虑自建
```

## B.4 给小白的 5 条速记

```
1. URI 用业务键，不用数据库 ID
2. 先查 schema.org，没有再自己造
3. 类层级 ≤ 5 层
4. 业务规则写 SHACL，不写 OWL
5. 每次 PR 跑一次校验
```

## B.5 速读建议

| 时间 | 看哪节 |
|------|--------|
| 3 分钟 | B.1（7 大陷阱）|
| 10 分钟 | + B.2.1-3（复用 + 单一来源 + 需求倒推）|
| 20 分钟 | + B.3、B.4（别干什么）|

## 参考文献

- Noy, N. F., & McGuinness, D. L. (2001). *Ontology Development 101*.
- Allemang, D., & Hendler, J. (2011). *Semantic Web for the Working Ontologist* (2nd ed.).
- Wikidata:Best Practices. https://www.wikidata.org/wiki/Wikidata:Best_practices
