# The LLM Grounding Playbook

> **中文副标题**：让 LLM 不胡说 — 7 个本体实战 + 1 个 Palantir 风格平台
> **v1.0 · 2026-07**

---

## 第一部分 · 本书背景

**这是什么**

一本关于"如何让 AI 不胡说"的实战手册。AI（特别是 LLM）是个会编故事的算命先生。本书教你给它一本"真经"——**本体（Ontology）**。

**为什么需要这本书**

- LLM 严重幻觉：问"订单状态"会编一个不存在的
- 数据孤岛：销售在 MySQL，物流在 PostgreSQL，订单在 Oracle
- 黑盒：AI 答对了但不知道为什么
- 缺事实锚点：AI 不知道"什么是真"

**本体的 3 个核心能力**

1. **结构化** — 统一 schema，跨源查询
2. **可推理** — 机器自动推出新事实
3. **可校验** — 业务规则自动抓违规

**对照市面上其他书**

| 其它 AI 书 | 这本书 |
|------------|--------|
| 教你怎么调 API | 教你怎么让 AI **不胡说** |
| 教你怎么写 Prompt | 教你怎么让 AI **有记忆** |
| 教你怎么 Embedding | 教你怎么让 AI **有共识** |
| 重点在"模型" | 重点在"数据骨架" |

**完整交付**

- 1 份 PDF 教程（463 KB，13 章 + 3 附录）
- 1 份 PDF 教程源 Markdown（21 KB）
- 20 个真机跑通的 Python 脚本
- 12 个 RDF 本体文件
- 7 个 SHACL Shape 文件
- 8 个业务场景（HR / 客服 / 财务 / 商品 / 医疗 / 物流 / CRM + Foundry 平台）
- 30 道作业（基础 / 进阶 / 实战 三档）

**对应行业**：电商 / 跨境电商 / 物流 / 医院 / 制造 / 金融 / 互联网 / B2B SaaS

---

## 第二部分 · 适合什么读者

### 2 类典型读者

#### 读者 A · AI 应用开发者 / 数据工程师

**你是谁**：写 Python、懂 SQL、没碰过本体/语义网

**你想干嘛**：
- 用 AI 答"准确业务问题"
- 给 LLM 配数据
- 搭一个 AI 驱动的内部系统

**你的回报**：
- 1-3 天：跑通 + 改自己数据
- 1-2 周：搭企业级本体平台
- 长期：AI 答业务问题准确率 95%+

#### 读者 B · 技术负责人 / 架构师

**你是谁**：评估技术栈、做技术选型、给老板/业务方解释

**你想干嘛**：
- 评估"本体 / KG / Foundry"该不该上
- 选 Palantir Foundry 还是自研
- 给老板算账

**你的回报**：
- 2-3 天：懂全貌 + 写选型报告
- 长期：能管 5-10 人的本体团队

### 其他读者

如果你**不是**上面 2 类，但也想看：

| 你 | 推荐 | 备注 |
|----|------|------|
| 老板 / 投资人 | 看本书第三部分 §1 哲学 + §10 案例 | 跳过规范和代码 |
| 产品经理 / 业务方 | 看 §8 案例对照 + §9 Foundry 平台 | 跳过规范和代码 |
| 学生 / 学术研究 | 按 §3 完整顺序读 4 周 | 全文 |
| 业务方 / 销售 | 看 §10 案例 + 1 个最像你行业的 | 跳过规范 |

---

## 第三部分 · 完整阅读手册

按"先跑通，再深入"的顺序。**每一章都告诉你：读什么文件 / 跑什么命令 / 大概要多久**。

### 阶段 0 · 5 分钟上手（30 秒装环境 + 30 秒跑通）

**目标**：让 AI 跑出第一条 RDF

**操作**：

```bash
# 1. 装环境
pip install rdflib pyshacl SPARQLWrapper

# 2. 跑第一个 demo
cd ~/Documents/projects/ai/ontology/04-zero-install-demo
python3 examples/1-first-rdf.py
```

**你应该看到**：4 条三元组 + Turtle 输出

**文件**：
- 读 `04-zero-install-demo/README.md`（5 分钟）

**卡住了**：看 `04-zero-install-demo/README.md` 末尾的"故障排查"（5 个最常见错误 + 修法）

---

### 阶段 1 · 历史速读（10 分钟）

**目标**：知道"为什么需要本体"

**操作**：依次读这 3 个 .md，每个 1-3 分钟

| # | 文件 | 你会得到什么 |
|---|------|-------------|
| 1 | `01-history/01-ontology-philosophy.md` | 本体 2400 年哲学（速读版） |
| 2 | `01-history/02-knowledge-representation.md` | 60 年知识表示演变 |
| 3 | `01-history/03-ai-ontology-why.md` | LLM 的 3 个病，本体怎么治 |

**可选**：不想读哲学 → 跳到阶段 2

---

### 阶段 2 · 5 个 demo（1 小时）

**目标**：把 5 个核心 demo 全跑通

**操作**：

```bash
cd ~/Documents/projects/ai/ontology/04-zero-install-demo

# 1. 第一个 RDF
python3 examples/1-first-rdf.py

# 2. CSV 转 RDF
python3 examples/2-csv-to-rdf.py

# 3. SHACL 校验
python3 examples/3-shacl.py

# 4. 端到端电商 + 3 个查询
python3 examples/7-shop.py

# 5. 完整促销（本体+数据+SHACL+SPARQL+问答）
python3 examples/9-promo-demo.py
```

**文件**：
- 读 `04-zero-install-demo/README.md` 全文
- 看代码：`04-zero-install-demo/examples/*.py`（每个 20-50 行）

**练一下**：
- 把 `04-zero-install-demo/data/people.csv` 改成你自己 3 个朋友
- 跑 `examples/2-csv-to-rdf.py` 看结果
- 改 SPARQL 查询，找"30 岁以上的朋友"

---

### 阶段 3 · 4 个核心规范（4 小时，可选）

**目标**：懂 4 个技术规范

**操作**：读这 4 个 .md，每个 1 小时

| # | 文件 | 时间 | 你会学到 |
|---|------|------|----------|
| 1 | `02-specs/01-rdf.md` | 1 小时 | RDF 三元组 / Turtle / rdflib |
| 2 | `02-specs/02-rdfs-owl.md` | 1.5 小时 | RDFS subClassOf / OWL 推理 |
| 3 | `02-specs/03-sparql.md` | 1.5 小时 | SPARQL 查询（5 个核心模式）|
| 4 | `02-specs/04-shacl.md` | 1.5 小时 | SHACL 业务规则校验 |

**配套手把手**（跟跑）：

| # | 文件 | 时间 |
|---|------|------|
| 1 | `02-实战指南/2.1-rdf-hands-on.md` | 30 分钟 |
| 2 | `02-实战指南/2.3-sparql-hands-on.md` | 1 小时 |
| 3 | `02-实战指南/2.4-shacl-hands-on.md` | 1 小时 |

**卡住了**：每个 .md 顶部有"5 分钟上手"快速跑通

---

### 阶段 4 · 1 个真实业务案例（2-4 小时）

**目标**：看一个真实业务场景怎么用本体

**选案例**（按你行业）：

| 你的行业 | 推荐案例 | 时间 |
|----------|----------|------|
| HR / 招聘 | `05-real-cases/hr/` | 2 小时（最简单）|
| 客服 | `05-real-cases/customer-service/` | 2 小时 |
| 电商运营 / 采购 | `05-real-cases/product/` | 4 小时 |
| 财务 / 会计 | `05-real-cases/finance/` | 4 小时 |
| 物流 / 快递 | `05-real-cases/logistics/` | 6 小时 |
| B2B 销售 | `05-real-cases/crm/` | 6 小时 |
| 医院 / 诊所 | `05-real-cases/medical/` | 6 小时 |

**操作**（以 HR 为例）：

```bash
cd ~/Documents/projects/ai/ontology/05-real-cases/hr
python3 hr-query.py
```

**你应该看到**：数据校验 ✅ 通过 + 6 个查询结果

**文件**：
- 读 `05-real-cases/hr/README.md` 全文
- 看代码：`hr-query.py`（106 行）
- 看本体：`data/hr-ont.ttl`
- 看数据：`data/hr-data.ttl`

**练一下**：
- 把 `data/hr-data.ttl` 里的 5 个候选人换成你公司数据
- 加 1 个你自己的查询（参考现有的 6 个）

**其他 6 个案例**：等你跑通 1 个，**第 2 天**再换下一个

---

### 阶段 5 · Palantir Foundry 风格平台（半天到 2 天）

**目标**：把 7 个案例的能力合并成一个企业平台

**操作**（按顺序跑 6 个脚本）：

```bash
cd ~/Documents/projects/ai/ontology/05-real-cases/foundry-platform

# 1. 核心 9 section
python3 run_platform.py

# 2. AIP / MCP Server（LLM 调本体）
python3 mcp_server.py            # CLI 演示
python3 mcp_server.py --mcp      # 接 Claude Desktop

# 3. SQL → RDF 物化（Pipeline Builder）
python3 r2rml_materialize.py

# 4. HTML 仪表盘
python3 build_dashboard.py
open dashboard.html              # 看效果

# 5. ABAC 字段级权限
python3 abac_security.py

# 6. CDC 实时同步
python3 cdc_demo.py
```

**文件**：
- 读 `05-real-cases/foundry-platform/README.md`（理解 6 大能力）
- 看代码：6 个 .py（每个 100-300 行）

**接 Claude Desktop**（可选）：
- 在 `claude_desktop_config.json` 加 mcpServers 配置
- 重启 Claude Desktop
- 问："查华为的所有订单" → Claude 调本体

---

### 阶段 6 · 30 道作业（1-2 周，选做）

**目标**：巩固 + 加深

**操作**：

```bash
# 打开作业清单
cat 06-exercises/README.md
```

**题目分级**：

| 难度 | 数量 | 时间 |
|------|------|------|
| 基础 | 10 题 | 半天 |
| 进阶 | 10 题 | 1 天 |
| 实战 | 10 题 | 2 天 |

**做完的标准**：每个作业有 1 个跑的通的 .py / .ttl

---

### 阶段 7 · 附录速查（用时需要再看）

| 想知道什么 | 看哪里 |
|------------|--------|
| W3C 规范 / 论文 / 工具 | `99-references/01-resources.md` |
| 7 个常见陷阱 + 10 个最佳实践 | `99-references/02-pitfalls-best-practices.md` |
| 7 天 / 30 天 / 90 天学习计划 | `99-references/03-study-plan.md` |
| 环境检查 + Python 库版本 | `99-references/04-env-checklist.md` |
| 速查表（5 大规范 + 命令）| `99-references/06-cheatsheet.md` |
| 业务方常见问题 | `99-references/07-FAQ.md` |
| 术语表 | `99-references/08-glossary.md` |
| 完整 PDF 教程 | `99-references/The-LLM-Grounding-Playbook.pdf` |

---

## 阅读总时间估算

| 读者 | 路线 | 时间 |
|------|------|------|
| **AI 开发者** | 阶段 0+2+3+4+5 | 5-7 天 |
| **架构师** | 阶段 0+1+3+5+7 | 3-5 天 |
| **老板 / PM** | 阶段 0+1+4（看 1 案例）+5（只看 README） | 半天到 1 天 |
| **学生** | 全部顺序 | 3-4 周 |

---

## 完整章节路径（备查）

> 这是 BOOK.md 章节映射的副本，方便一次性看完整本书结构。

| 章节 | 中文 | 目录 |
|------|------|------|
| 第 0 章 | 写在前面 | `00-overview/00-overview.md` |
| 第 1 章 | 哲学源流 | `01-history/01-ontology-philosophy.md` |
| 第 2 章 | 知识表示 | `01-history/02-knowledge-representation.md` |
| 第 3 章 | AI 时代为什么需要本体 | `01-history/03-ai-ontology-why.md` |
| 第 4 章 | RDF | `02-specs/01-rdf.md` |
| 第 5 章 | RDFS/OWL | `02-specs/02-rdfs-owl.md` |
| 第 6 章 | SPARQL | `02-specs/03-sparql.md` |
| 第 7 章 | SHACL | `02-specs/04-shacl.md` |
| 第 8 章 | 5 分钟跑通 | `04-zero-install-demo/` |
| 第 9 章 | 7 个真实业务案例 | `05-real-cases/` |
| 第 10 章 | Palantir Foundry 风格平台 | `05-real-cases/foundry-platform/` |
| 第 11 章 | AIP / MCP | `05-real-cases/foundry-platform/mcp_server.py` |
| 第 12 章 | 工程化进阶 | `05-real-cases/foundry-platform/` |
| 第 13 章 | 30 道作业 | `06-exercises/` |
| 附录 A | 资源与工具速查 | `99-references/01-resources.md` |
| 附录 B | 常见陷阱与最佳实践 | `99-references/02-pitfalls-best-practices.md` |
| 附录 C | 术语表 | `99-references/08-glossary.md` |

---

## 反馈

- 文档错：直接改文件
- 跑不通：把完整报错发我
- 缺场景：告诉我行业 / 业务，我加

**CC BY-SA 4.0**
