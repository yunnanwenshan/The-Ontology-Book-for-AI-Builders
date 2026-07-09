# 04 · 零安装小白 demo

> **30 秒跑通第一个 RDF**
> 不用 Docker / 不用 Java / 不用数据库
> 只要 Python 3.10+

## 1. 装环境（30 秒）

```bash
pip install rdflib pyshacl SPARQLWrapper
```

**验证**：
```bash
python3 -c "import rdflib; print(rdflib.__version__)"
# 应该看到版本号，比如 7.0.0
```

## 2. 跑 5 个 demo（按顺序）

| 顺序 | 脚本 | 学到什么 | 时间 |
|------|------|----------|------|
| 1 | `1-first-rdf.py` | 写第一个 RDF（4 条三元组） | 30 秒 |
| 2 | `2-csv-to-rdf.py` | CSV 转 RDF | 30 秒 |
| 3 | `3-shacl.py` | SHACL 抓违规 | 30 秒 |
| 4 | `7-shop.py` | 端到端电商 + 3 个查询 | 1 分钟 |
| 5 | `9-promo-demo.py` | 完整促销（本体+数据+SHACL+SPARQL+问答） | 2 分钟 |

```bash
cd ~/Documents/projects/ai/ontology/04-zero-install-demo
python3 examples/1-first-rdf.py
python3 examples/2-csv-to-rdf.py
python3 examples/3-shacl.py
python3 examples/7-shop.py
python3 examples/9-promo-demo.py
```

每个都该看到 "✅" 或中文输出。如果看到"❌"或报错，**查下面故障排查**。

## 3. 看代码

每个脚本 30-50 行。**重点看 9-promo-demo.py**——它包含一个完整业务场景。

## 4. 数据在哪

所有数据在 `data/` 目录：

```
data/
├── shapes.ttl         SHACL 规则
├── shop-data.ttl      端到端电商数据
├── promo-ont.ttl      促销本体
├── promo-shapes.ttl   促销 SHACL
├── promo-data.ttl     促销数据
├── people.csv         CSV 转换测试
```

**练一下**：把 `data/people.csv` 改成你自己的数据，再跑 `2-csv-to-rdf.py`。

## 5. 故障排查（5 个最常见错误）

### ❌ `ModuleNotFoundError: No module named 'rdflib'`

**原因**：没装库
**修法**：
```bash
pip install rdflib pyshacl SPARQLWrapper
```

### ❌ `ImportError: cannot import name 'platform'`

**原因**：文件叫 `platform.py`，跟 Python stdlib 冲突
**修法**：改名，叫 `run_platform.py` 或别的

### ❌ `ParseException: Expected SelectQuery, found 'UNION'`

**原因**：SPARQL `BIND` 在 `UNION` 块里位置错
**修法**：拆成多个独立查询，或在 `UNION` 块里别用 `BIND`

### ❌ `AttributeError: 'return' / 'type' / 'from'`（SPARQL 变量名）

**原因**：用了 Python 关键字当变量名（如 `?return` / `?type`）
**修法**：改名（如 `?ret` / `?t`），或用 `r.asdict()` 访问：
```python
for r in g.query(q):
    d = r.asdict()
    print(d['type'])   # 而不是 r.type
```

### ❌ `pyshacl` 报 "Value does not match pattern"

**原因**：SHACL 正则和你的数据格式不匹配
**修法**：看 SHACL 的 `sh:pattern`，比如 `^O\d{10}$` 需要 `O` + 10 个数字
**快速调试**：临时改成 `"^.*$"` 看是不是其他字段问题

### ❌ 其他错误

跑下面这个"环境检查"：

```bash
python3 -c "
import rdflib, pyshacl, SPARQLWrapper
print('rdflib', rdflib.__version__)
print('pyshacl OK')
print('SPARQLWrapper OK')
"
```

如果都 OK，问题就在你的代码；如果某个错，重装那个库。

## 6. 跑通后做什么

| 你想... | 跳到 |
|--------|------|
| 学更多语法 | [02-specs/](../../02-specs/)（RDF / SPARQL / SHACL 速查）|
| 边学边做 | [02-实战指南/](../../02-实战指南/)（手把手）|
| 看真实案例 | [05-real-cases/](../../05-real-cases/)（7 业务 + Foundry 平台）|
| 做企业级 | [05-real-cases/foundry-platform/](../../05-real-cases/foundry-platform/) |

## 7. 文件清单

```
04-zero-install-demo/
├── README.md           本文件
├── data/               数据
└── examples/           7 个 demo 脚本
```
