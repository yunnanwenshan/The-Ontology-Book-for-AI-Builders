# The LLM Grounding Playbook · 总体地图

> **书名**：The LLM Grounding Playbook
> **中文副标题**：让 LLM 不胡说 — 7 个本体实战 + 1 个 Palantir 风格平台

> **适合谁**：写过程序、懂 SQL、没碰过本体/语义网
> **不适合谁**：完全不会写代码（先学 Python 基础）
> **学完之后**：能独立搭一个本体驱动的 AI 系统

## 本书 vs 其它 AI 书

| 其它 AI 书 | 这本书 |
|------------|--------|
| 教你怎么调 API | 教你怎么让 AI **不胡说** |
| 教你怎么写 Prompt | 教你怎么让 AI **有记忆** |
| 教你怎么 Embedding | 教你怎么让 AI **有共识** |
| 重点在"模型" | 重点在"数据骨架" |

## 三阶段 · 一图说清

```
┌─────────────────────────────────────────────┐
│  阶段 1 · 历史理念                            │
│  回答：为什么需要本体？                      │
│  学完：能用 1 分钟讲清"AI 幻觉怎么治"        │
│                                             │
│  哲学 → 知识表示 → AI 时代的复兴             │
└─────────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│  阶段 2 · 技术规范                            │
│  回答：用什么语言描述本体？                  │
│  学完：能写 RDF + OWL + SPARQL + SHACL     │
│                                             │
│  RDF → RDFS/OWL → SPARQL → SHACL           │
└─────────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│  阶段 3 · 工程落地                            │
│  回答：怎么把它跑起来？                      │
│  学完：能搭 Docker + 接 Agent + 上线        │
│                                             │
│  Hello World → 架构 → 方案对决 → 实战案例  │
└─────────────────────────────────────────────┘
```

## 三条学习路径（按你的时间选）

### 路径 A · 周末突击（4 小时）

- 只看：**04-zero-install-demo/** + **[02-实战指南/2.3-sparql-hands-on.md](../02-实战指南/2.3-sparql-hands-on.md)**
- 产出：能跑通 5 个脚本 + 写出 5 个查询
- 适合：想 30 分钟判断"这玩意对我有没有用"

### 路径 B · 系统学习（3 周，16-21 小时）

- 全看：按顺序读完所有章节 + 做 30 道作业
- 产出：能独立设计 + 建模 + 部署
- 适合：想动手做项目的开发者

### 路径 C · 老板速览（30 分钟）

- 只看：**1.3 AI 时代为什么需要本体** + **3.3 方案对决**
- 产出：能向团队讲清"为什么选这个不选 RAG"
- 适合：技术负责人 / 决策者

## 阅读约定

每篇文件都有统一结构：

```
1. 一句话总结（30 秒懂）
2. 生活类比（5 分钟，建立直觉）
3. 技术细节（10-15 分钟）
4. 5 分钟上手（必跑，命令可直接复制）
5. 避坑提示（最容易卡的地方）
6. 速读建议（按时间紧的只读前 3 节）
```

**5 分钟上手**标志：所有命令在 macOS / Linux 终端可直接复制跑。

## 环境准备（10 分钟，必做）

### 1. Python 3.10+

```bash
python3 --version
```

### 2. 装 3 个库

```bash
pip install rdflib pyshacl SPARQLWrapper
```

### 3. 验证

```bash
cd ~/Documents/projects/ai/ontology/04-zero-install-demo
python3 examples/1-first-rdf.py
```

**看到 4 条三元组 = 环境就绪**。

## 文件结构

```
~/Documents/projects/ai/ontology/
├── README.md
├── 00-overview/00-overview.md
├── 01-history/                            ← 阶段 1：历史理念
│   ├── 01-ontology-philosophy.md
│   ├── 02-knowledge-representation.md
│   └── 03-ai-ontology-why.md
├── 02-specs/                              ← 阶段 2：技术规范（教程版）
│   ├── 01-rdf.md
│   ├── 02-rdfs-owl.md
│   ├── 03-sparql.md
│   └── 04-shacl.md
├── 02-实战指南/                            ← 阶段 2：手把手（跟跑版）
│   ├── 2.1-rdf-hands-on.md
│   ├── 2.3-sparql-hands-on.md
│   └── 2.4-shacl-hands-on.md
├── 03-engineering/                        ← 阶段 3：工程落地
│   ├── 01-hello-world.md                  (Docker + Fuseki)
│   ├── 02-architecture.md
│   ├── 03-comparison.md
│   └── 04-case-ecommerce.md
├── 04-zero-install-demo/                  ★ 不装 Docker 也能跑（强烈推荐）
│   ├── README.md
│   ├── examples/                          (7 个验证过的脚本)
│   └── data/                              (9 个数据文件)
├── 05-real-cases/                         ★ 现实场景
│   ├── hr/                                (HR 招聘 6 个查询)
│   └── customer-service/                  (客服 6 个查询)
├── 06-exercises/                           ★ 30 道实战作业
└── 99-references/
    ├── 01-resources.md
    ├── 02-pitfalls-best-practices.md
    ├── 03-study-plan.md
    ├── 04-env-checklist.md
    ├── 05-demo-script.md
    ├── 06-cheatsheet.md
    ├── 07-FAQ.md
    └── 08-glossary.md
```

## 一句话总结

> **AI 没有本体 = 会说人话的算命先生**
> **AI 有了本体 = 看过病历的医生**

## 案例梯度（按难度）

8 个场景从易到难：

| 难度 | 案例 | 时间 |
|------|------|------|
| ⭐ 入门 | [HR 招聘](../05-real-cases/hr/README.md) | 30 分钟 |
| ⭐ 入门 | [客服](../05-real-cases/customer-service/README.md) | 30 分钟 |
| ⭐⭐ 中级 | [商品](../05-real-cases/product/README.md) | 1 小时 |
| ⭐⭐ 中级 | [财务](../05-real-cases/finance/README.md) | 1 小时 |
| ⭐⭐⭐ 高级 | [物流](../05-real-cases/logistics/README.md) | 1.5 小时 |
| ⭐⭐⭐ 高级 | [CRM](../05-real-cases/crm/README.md) | 1.5 小时 |
| ⭐⭐⭐ 高级 | [医疗](../05-real-cases/medical/README.md) | 1.5 小时 |
| 🏆 集成 | [Foundry 平台](../05-real-cases/foundry-platform/README.md) | 2-3 小时 |

**不知道选哪个？** 看  的业务问题反查表。
