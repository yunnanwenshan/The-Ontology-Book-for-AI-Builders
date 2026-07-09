# 阶段 2 · 实战指南：手把手带你写 4 个核心规范

> **目的**：30 分钟用 Python 跑通 4 个规范
> **特点**：所有代码**已在本机验证**过

## 怎么用这章

每节 5-10 分钟，按顺序学：

1. **2.1 RDF**（5 min） — 知识怎么写
2. **2.2 RDFS/OWL**（10 min） — 知识怎么分类和推理
3. **2.3 SPARQL**（10 min） — 知识怎么查
4. **2.4 SHACL**（10 min） — 知识怎么校验

## 跟 `02-specs/` 的区别

- `02-specs/` 是**教程版**：概念 + 例子 + 速查
- `02-实战指南/` 是**手把手版**：每步都跟跑

**建议**：先学 02-实战指南（这个），有不懂再查 02-specs/。

## 5 个验证过的脚本

```
~/Documents/projects/ai/ontology/04-zero-install-demo/
├── examples/
│   ├── 1-first-rdf.py       ← 2.1 用
│   ├── 2-csv-to-rdf.py      ← 2.1 练
│   ├── 3-shacl.py           ← 2.4 用
│   ├── 7-shop.py            ← 2.3 用
│   ├── 8-shacl-e2e.py       ← 2.4 练
│   └── 9-promo-demo.py      ← 综合用
└── data/                    ← 数据文件
```

**详细说明**：`04-zero-install-demo/README.md`

## 学习流程

```bash
# 1. 装环境
pip install rdflib pyshacl SPARQLWrapper

# 2. 进项目
cd ~/Documents/projects/ai/ontology/04-zero-install-demo

# 3. 按顺序跑
python3 examples/1-first-rdf.py        # 2.1
python3 examples/2-csv-to-rdf.py       # 2.1 练
python3 examples/7-shop.py             # 2.3
python3 examples/3-shacl.py            # 2.4
python3 examples/8-shacl-e2e.py        # 2.4 练
python3 examples/9-promo-demo.py       # 综合

# 4. 跑完看 04-zero-install-demo/README.md 看每个的输出
```

## 章节对照

| 节 | 跑哪个脚本 | 学到什么 |
|----|-----------|----------|
| 2.1 RDF | `1-first-rdf.py` + `2-csv-to-rdf.py` | 写、读、转 |
| 2.2 OWL | 暂用 OWL 教程（在 02-specs/02）| 分类、推理 |
| 2.3 SPARQL | `7-shop.py` + `6-wikidata.py` | 5 种查询模式 |
| 2.4 SHACL | `3-shacl.py` + `8-shacl-e2e.py` | 校验、抓违规 |
| 综合 | `9-promo-demo.py` | 端到端 demo |

## 速读建议

| 时间 | 看什么 |
|------|--------|
| 5 分钟 | 跑 1 个脚本 |
| 30 分钟 | 跑完 6 个脚本 |
| 1 小时 | + 读 `04-zero-install-demo/README.md` |
| 2 小时 | + 改脚本里的数据，看输出变化 |
