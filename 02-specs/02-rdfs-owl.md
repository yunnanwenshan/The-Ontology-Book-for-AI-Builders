# 阶段 2.2 · RDFS 与 OWL：让机器"推理"

> **一句话**：RDF 记事实，RDFS+OWL 让机器推出新事实
> **目标**：能区分 RDFS/OWL/SHACL 各自干什么

## 1. 一句话总结

- **RDF**：记事实。"张三是人。"
- **RDFS**：建类层级。"人是动物的子类。"
- **OWL**：加逻辑约束。"人是动物 + 有理性。"

## 2. 生活类比：现实世界

```
RDF   = 你今天干了什么     "9 点开会"
RDFS  = 你的角色           "我是开发"
OWL   = 你的责任 + 规则    "开发要写代码、要 review、要发版"
SHACL = 公司的规定        "上班不能迟到"
```

**RDF 记事、RDFS 定身份、OWL 定逻辑、SHACL 定规则**。

## 3. RDFS —— 4 个核心词汇

| 词汇 | 作用 | 例子 |
|------|------|------|
| `rdfs:Class` | 声明一个类 | `ex:Hacker a rdfs:Class .` |
| `rdfs:subClassOf` | 父子类 | `ex:Hacker rdfs:subClassOf ex:Person .` |
| `rdfs:domain` | 属性的主语类型 | `ex:loves rdfs:domain ex:Person .` |
| `rdfs:range` | 属性的宾语类型 | `ex:loves rdfs:range ex:Person .` |

### 推理演示

```turtle
ex:Cat rdfs:subClassOf ex:Animal .
ex:Tom a ex:Cat .
```

**推理机自动推出**：
```turtle
ex:Tom a ex:Animal .   # 因为 Cat 是 Animal 的子类
```

## 4. OWL —— 5 个类构造器

OWL 比 RDFS 强 10 倍。先记 5 个最常用的：

### 4.1 intersectionOf（交集）

**"既…又…"**
```turtle
ex:EmployedStudent owl:equivalentClass [
    owl:intersectionOf ( ex:Employee ex:Student )
] .
# EmployedStudent = 既是员工又是学生
```

### 4.2 unionOf（并集）

**"或…或…"**
```turtle
ex:FamilyMember owl:equivalentClass [
    owl:unionOf ( ex:Parent ex:Child ex:Spouse )
] .
# 家人 = 父母 + 孩子 + 配偶
```

### 4.3 complementOf（补集）

**"不是…"**
```turtle
ex:Minor owl:equivalentClass [
    owl:complementOf ex:Adult
] .
# 未成年人 = 不是成年人
```

### 4.4 allValuesFrom（全称量词）

**"所有的…都是…"**
```turtle
ex:Person rdfs:subClassOf [
    a owl:Restriction ;
    owl:onProperty ex:hasChild ;
    owl:allValuesFrom ex:Human
] .
# 人这种类的 hasChild 属性只能是 Human
```

### 4.5 someValuesFrom（存在量词）

**"至少有一个…"**
```turtle
ex:Parent rdfs:subClassOf [
    a owl:Restriction ;
    owl:onProperty ex:hasChild ;
    owl:someValuesFrom ex:Human
] .
# 父母这种类必须至少有一个 Human 孩子
```

## 5. OWL —— 5 个属性特征

### 5.1 传递性（Transitive）

```turtle
ex:ancestorOf a owl:TransitiveProperty .

ex:Alice ex:ancestorOf ex:Bob .
ex:Bob   ex:ancestorOf ex:Carol .
# 推理机自动推出：Alice ancestorOf Carol
```

**生活例子**：祖辈是传递的（"爷爷"是"爸爸"的爸爸）。

### 5.2 对称性（Symmetric）

```turtle
ex:marriedTo a owl:SymmetricProperty .

ex:Tom ex:marriedTo ex:Jerry .
# 推出：Jerry marriedTo Tom
```

**生活例子**：婚姻、朋友、邻居都是对称的。

### 5.3 互斥（Disjoint）

```turtle
ex:Male   owl:disjointWith ex:Female .
ex:Single owl:disjointWith ex:Married .
```

**生活例子**：一个人不能既是男又是女（除非有医学奇迹）。

### 5.4 函数性（Functional）

```turtle
ex:hasBirthday a owl:FunctionalProperty .
# 一个人最多一个生日
```

**生活例子**：身份证号是 functional（一人一号）。

### 5.5 逆属性（Inverse）

```turtle
ex:hasParent owl:inverseOf ex:hasChild .
```

**生活例子**：hasParent 和 hasChild 是反义。

## 6. 业务案例：合同 + 审批

```turtle
# 1. 定义类
ex:Contract rdfs:subClassOf ex:Document .

# 2. 状态互斥（不能同时是草稿和已批准）
ex:Draft     owl:disjointWith ex:Approved .
ex:Approved  owl:disjointWith ex:Rejected .
ex:Draft     owl:disjointWith ex:Rejected .

# 3. 约束：高额合同必须有 CFO 审批
ex:HighValueContract rdfs:subClassOf [
    a owl:Restriction ;
    owl:onProperty ex:amount ;
    owl:minInclusive 10000
] , [
    a owl:Restriction ;
    owl:onProperty ex:approvedBy ;
    owl:hasValue ex:CFO
] .
```

**推理机能自动检测**：
- 状态冲突（同一合同同时是 Draft 和 Approved）→ 报错
- 合规违反（10 万合同没 CFO 审批）→ 报错

## 7. 5 分钟上手：用 Python 验证 OWL 推理

```bash
pip install owlready2
```

```python
from owlready2 import *

onto = get_ontology("http://example.com/test.owl")

with onto:
    class Person(Thing):
        pass

    class Cat(Thing):
        pass

    class PetOwner(Person):
        equivalent_to = [Person & has_pet.some(Cat)]
        # 拥有至少一只猫的人

# 验证
onto.save("test.owl")
print("本体已保存")

# 推理（Pellet）
sync_reasoner_pellet([onto], infer_property_values=True)
print("推理完成")

# 看所有 Person
for p in onto.Person.instances():
    print(p)
```

## 8. 速查表：什么时候用什么

| 你要做的 | 用什么 |
|---------|--------|
| 简单类层级（父类-子类） | RDFS |
| 复杂属性约束（传递、对称） | OWL |
| 类等价、互斥 | OWL |
| 业务规则（必须有、不能小于） | **SHACL**（不是 OWL）|
| 大规模数据校验 | SHACL |
| 推理推出隐含事实 | OWL + Reasoner |

**重要**：OWL 推理慢且贵。生产环境往往**只用 SHACL 校验，不开 OWL 推理**。

## 9. 避坑提示

- ❌ **别在 OWL 里表达业务规则**：OWL 是分类系统，规则用 SHACL
- ❌ **别开 OWL Full profile**：推理机不支持
- ❌ **别用 OWL 校验数据**（用 SHACL）
- ✅ **OWL 用于分类、推理**
- ✅ **SHACL 用于校验数据**
- ❌ **别忘了 OWL DL 的限制**：不能既用 `inverseOf` 又对相同属性用 `FunctionalProperty`（会冲突）
- ✅ **小规模用 RDFS 足够**

## 10. 速读建议

| 时间 | 看哪几节 |
|------|----------|
| 5 分钟 | 1、2、3 |
| 10 分钟 | + 4、5 |
| 20 分钟 | + 6、7、8（跑通 5 分钟上手） |

## 参考文献

- W3C. (2012). *OWL 2 Web Ontology Language Document Overview*. https://www.w3.org/TR/owl2-overview/
- Hitzler, P., Krötzsch, M., & Rudolph, S. (2010). *Foundations of Semantic Web Technologies*. Chapman & Hall.
- Antoniou, G., & van Harmelen, F. (2008). *A Semantic Web Primer* (2nd ed.). MIT Press.
- owlready2. https://owlready2.readthedocs.io/
