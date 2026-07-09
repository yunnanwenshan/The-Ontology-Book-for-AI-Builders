# 阶段 2.1 · RDF：知识表示的基础语法

> **一句话**：RDF 把所有事实写成"主-谓-宾"三元组
> **目标**：30 分钟能用 RDF 表达任何事实

## 1. 一句话总结

**RDF = 一句话表达任何事实 = "主语 谓语 宾语"**

例如：
- 阿里巴巴由 马云 创立 → (阿里巴巴, 创始人, 马云)
- 玫瑰花 是 一种花 → (玫瑰, 是, 花)

学会 RDF，你就学会了"知识表示"的普通话。

## 2. 生活类比：填表

| 主体（谁） | 关系（是什么） | 客体（什么） |
|------------|----------------|--------------|
| 王老师 | 教 | 张三 |
| 张三 | 学 | 数学 |
| 数学 | 属于 | 理科 |

填这张表 = 写 RDF。
**RDF 就是结构化填表**。

## 3. 第一个 RDF 文件

新建 `hello.ttl`：

```turtle
@prefix ex: <http://example.com/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

ex:Neo a ex:Hacker ;
    ex:realName "Thomas Anderson" ;
    ex:loves ex:Trinity .

ex:Trinity a ex:Hacker ;
    ex:loves ex:Neo .
```

**读法**：
- 第一行：定义 `ex:` 这个前缀（全名是 `http://example.com/`）
- `ex:Neo a ex:Hacker`：Neo 是一个 Hacker（`a` 是 `rdf:type` 的简写）
- `ex:Neo ex:loves ex:Trinity`：Neo 爱 Trinity

## 4. 三元组 = 知识原子

**任何事实都能拆成"主谓宾"**：

```
我今天买了杯美式
  → (我, 买, 美式咖啡)
  → (我, 时间, 今天)
  → (美式咖啡, 类型, 咖啡)
  → (我, 花费, 30元)
```

**4 条三元组 = 一句完整的话。**

## 5. 5 分钟上手：用 Python 写第一个 RDF

```bash
pip install rdflib
```

新建 `first_rdf.py`：

```python
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS

# 1. 建一个空图
g = Graph()

# 2. 定义命名空间（你的"姓氏"）
EX = Namespace("http://example.com/")

# 3. 加 3 个三元组
g.add((EX.Alice, RDF.type, EX.Person))                    # Alice 是个 Person
g.add((EX.Alice, EX.age, Literal(30, datatype=...         # Alice 30 岁
g.add((EX.Alice, EX.knows, EX.Bob))                       # Alice 认识 Bob
g.add((EX.Bob, RDF.type, EX.Person))                      # Bob 是个 Person

# 4. 打印所有三元组
for s, p, o in g:
    print(f"{s} -- {p} --> {o}")

# 5. 输出成 Turtle 格式
print("\n--- Turtle ---")
print(g.serialize(format="turtle"))
```

**运行**：
```bash
python3 first_rdf.py
```

**应该看到**：
```
http://example.com/Alice -- http://www.w3.org/1999/02/22-rdf-syntax-ns#type --> http://example.com/Person
http://example.com/Alice -- http://example.com/age --> 30
http://example.com/Alice -- http://example.com/knows --> http://example.com/Bob
http://example.com/Bob -- http://www.w3.org/1999/02/22-rdf-syntax-ns#type --> http://example.com/Person
```

**恭喜你**：你已经写过 RDF 了。

## 6. 语法速查

### 6.1 三个角色

| 角色 | 含义 | 在 Triple 里 |
|------|------|--------------|
| **主语** | 谁 | 节点（URI / 匿名） |
| **谓语** | 是什么 | 必须是 URI（属性） |
| **宾语** | 什么 | 节点 / 字面量 |

### 6.2 三种值

| 类型 | 例子 | 用途 |
|------|------|------|
| **URI** | `<http://example.com/Neo>` | 标识一个"东西" |
| **字面量** | `"30"`, `"hello"@zh` | 具体的"值" |
| **空白节点** | `_:b1` 或 `[ ]` | 匿名分组 |

### 6.3 三种写法

| 语法 | 例子 | 适合 |
|------|------|------|
| **Turtle** | `<s> <p> <o> .` | **人写，最常用** |
| **N-Triples** | 一行一个三元组 | 数据交换 |
| **JSON-LD** | `{"@id": "s", "p": "o"}` | Web API |

## 7. 5 个常见模式

### 7.1 简单陈述

```turtle
ex:Alice ex:name "Alice" .
```

### 7.2 多个属性

```turtle
ex:Alice a ex:Person ;
    ex:name "Alice" ;
    ex:age 30 ;
    ex:city "Shanghai" .
```

**`;` 表示"还是这个主语"**，不用重复写。

### 7.3 多个值

```turtle
ex:Alice ex:knows ex:Bob , ex:Carol , ex:Dave .
```

**`,` 表示"还是这个谓语"**。

### 7.4 中文标签

```turtle
ex:Contract rdfs:label "合同"@zh, "Contract"@en .
```

**`@zh` 是语言标签**，让 LLM 知道"Contract 就是合同"。

### 7.5 数据类型

```turtle
ex:Alice ex:age 30 .                    # 整数
ex:Alice ex:height "1.75"^^xsd:decimal . # 浮点
ex:Alice ex:birthday "1995-01-01"^^xsd:date .  # 日期
```

**`^^xsd:date` 是数据类型**，让机器知道"这是日期"。

## 8. 5 分钟上手：从你的数据生成 RDF

```python
import csv
from rdflib import Graph, Literal, URIRef, Namespace
from rdflib.namespace import RDF

g = Graph()
EX = Namespace("http://example.com/people/")

with open("contacts.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        person = EX[row["name"].replace(" ", "_")]
        g.add((person, RDF.type, EX.Person))
        g.add((person, EX.name, Literal(row["name"])))
        g.add((person, EX.email, Literal(row["email"])))
        g.add((person, EX.company, Literal(row["company"])))

g.serialize("output.ttl", format="turtle")
print(f"生成了 {len(g)} 条三元组")
```

**一行 CSV → 一份本体**。

## 9. 避坑提示

- ❌ **别用数据库 ID 当 URI**：`<http://shop.com/order/12345>`，哪天 12345 被复用就乱套
- ✅ **用业务键**：`urn:order:2025-001-AB`，稳定不变
- ❌ **别全用字面量**：`<s> <p> "hello"` 比不上 `<s> <p> ex:hello`
- ✅ **字面量留给人看的"值"**，URI 给"实体"
- ❌ **别忘了 `@zh`**：LLM 读中文本体更准
- ✅ **rdfs:label 加多种语言**
- ❌ **别忘了末尾的 `.`**：Turtle 没 `.` 不算一条

## 10. 速读建议

| 时间 | 看哪几节 |
|------|----------|
| 5 分钟 | 1、2、3 |
| 15 分钟 | + 4、5、6、7 |
| 30 分钟 | + 8、9（跑通 5 分钟上手） |

## 参考文献

- W3C. (2014). *RDF 1.1 Concepts*. https://www.w3.org/TR/rdf11-concepts/
- W3C. (2014). *RDF 1.1 Turtle*. https://www.w3.org/TR/turtle/
- rdflib 文档. https://rdflib.readthedocs.io/
