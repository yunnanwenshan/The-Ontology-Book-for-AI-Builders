# 读者地图 · 7 类读者 × 定制阅读路径

> **找不到你？** 直接看 
> **PDF 一本全包**： (463 KB)
> **全套资源**：43 个 .md + 21 个 .py + 35 个 .ttl + 1 个 PDF ≈ 1.2 MB

---

## 0. 通用入口（推荐先看）

所有读者都应先读这 3 个：

1. ****（30 行 · 1 分钟）—— 5 分钟上手 + 三条路径
2. ****（6.8 KB · 5 分钟）—— 项目总览 + 案例梯度
3. ****（3 KB · 2 分钟）—— 书名 + 副标题 + 章节映射

---

## 1. 老板 / 投资人 / 决策者

> **"这技术值不值得投？"**
> **时间**：30-60 分钟
> **目标**：知道"为什么需要本体" + "市面上谁在做" + "投资回报率"

### 必读（4 篇 · 20 分钟）

| # | 文档 | 时间 | 你会得到什么 |
|---|------|------|-------------|
| 1 |  | 5 分钟 | LLM 的 3 个病，本体能治 |
| 2 |  | 10 分钟 | 本体 vs RAG 成本对比 |
| 3 |  | 5 分钟 | 8 个业务场景 1 张表 |
| 4 |  | 10 分钟 | 企业级本体平台长啥样 |

### 推荐读（2 篇 · 15 分钟）

-  — 哪些场景不要用本体
-  — 业务方常见问题

### 不必读

- 所有 RDF / RDFS / OWL / SPARQL / SHACL 规范
- 所有 .py 脚本
- 哲学章 2400 年历史
- 30 道作业

### 一句话总结给你

> **本体 = 给 LLM 配"真经"**。如果你的项目 AI 需要答"准确事实"（不是闲聊），用本体比 RAG 准 5-10 倍。Palantir 估值 600 亿美元，就是用这个做。

---

## 2. 产品经理 / 业务负责人

> **"我能让 AI 做啥？"**
> **时间**：2-4 小时
> **目标**：看懂 8 个业务场景 + 知道 Foundry 平台能给业务方看什么

### 必读（3 篇 · 30 分钟）

| # | 文档 | 时间 | 你会得到什么 |
|---|------|------|-------------|
| 1 |  | 10 分钟 | 8 场景对照表 |
| 2 |  | 10 分钟 | "我能用在哪"决策树 |
| 3 |  | 10 分钟 | AI 业务方看啥 |

### 推荐读（选 2 个最像你业务的案例 · 1-2 小时）

-  —— 客服
-  —— 财务
-  —— 电商
-  —— 物流
-  —— 销售
-  —— 医院
-  —— HR

### 可选读

-  § 按目标

### 不必读

- 02-specs/ 技术规范
- 02-实战指南/ 跟跑
- 全部 .py 脚本
- 哲学章

### 一句话总结给你

> **看 8 个业务场景图，找最像你的那个**。本项目能让你"AI 客服、AI 财务、AI 销售"都跑通，**前提是你有结构化数据**（ERP / CRM / 订单系统）。

---

## 3. AI 应用开发者

> **"我要在产品里接入本体"**
> **时间**：1-3 天
> **目标**：跑通 demo + 改自己数据 + 接入产品

### 必读（按顺序 · 4-6 小时）

| # | 文档 | 时间 | 你会得到什么 |
|---|------|------|-------------|
| 1 |  | 30 分钟 | 跑通第一个 RDF |
| 2 |  | 30 分钟 | 写自己的 RDF |
| 3 |  | 1 小时 | 写 SPARQL 查询 |
| 4 |  | 1 小时 | 写业务规则 |
| 5 | 1 个最像你业务的案例（推荐 ） | 2 小时 | 看真实数据查询 |

### 推荐读（继续深入 · 半天）

-  — RDF 速查手册
-  — SPARQL 速查手册
-  — SHACL 速查手册
-  — 让 Claude Desktop 调本体

### 可选读

-  — 环境检查
-  — 速查表

### 不必读

- 哲学章 2400 年史
- 03-engineering/ Docker 版（除非你要部署）

### 跑通后做什么

1. 改 `04-zero-install-demo/data/people.csv` 为你自己数据
2. 跑 7 个 demo
3. 选 1 个案例 README，把 `data/*-data.ttl` 换成你公司数据
4. 跑 `*-query.py` 看 6 个查询结果
5. 接 Claude Desktop 跑 MCP

---

## 4. 后端工程师 / 数据工程师

> **"我要搭一个本体平台"**
> **时间**：1-2 周
> **目标**：懂所有规范 + 跑 Foundry 6 脚本 + 接生产

### 必读（系统读 · 3-5 天）

**Week 1: 理论 + 跑通**

| # | 文档 | 时间 |
|---|------|------|
| 1 |  | 10 分钟（1 屏速读）|
| 2 |  全部 demo | 半天 |
| 3 |  | 1 小时 |
| 4 |  | 1.5 小时 |
| 5 |  | 1.5 小时 |
| 6 |  | 1.5 小时 |
| 7 | 7 案例全跑一遍 | 1 天 |

**Week 2: Foundry 平台**

| # | 文档/脚本 | 时间 |
|---|---------|------|
| 1 |  | 30 分钟 |
| 2 | `run_platform.py` | 10 分钟（跑）|
| 3 | `mcp_server.py` | 30 分钟（跑 + 改）|
| 4 | `r2rml_materialize.py` | 1 小时（跑 + 改 SQL）|
| 5 | `build_dashboard.py` | 30 分钟（跑）|
| 6 | `abac_security.py` | 1 小时（跑 + 改权限）|
| 7 | `cdc_demo.py` | 1 小时（跑 + 改）|

### 推荐读

-  — 5 个坑
-  — 最佳实践
-  — 30 道作业
-  — Docker 版（如果要部署）

### 不必读

- 哲学章 2400 年史
- 02-实战指南/ （跟跑 + 案例已覆盖）

### 接生产检查清单

- [ ] 选 1 个业务场景跑通
- [ ] 把 SQL 数据接 R2RML 物化
- [ ] 写 SHACL 业务规则
- [ ] 加 ABAC 权限
- [ ] 接 MCP / Claude Desktop
- [ ] 加 CDC 同步
- [ ] 写 HTML 仪表盘
- [ ] 部署到生产（考虑  Docker 版）

---

## 5. 数据治理 / 架构师

> **"我评估这套技术栈"**
> **时间**：2-3 天
> **目标**：懂哲学 + 全规范 + 决策能力

### 必读（深度读 · 2 天）

| # | 文档 | 时间 |
|---|------|------|
| 1 |  全部 3 篇 | 30 分钟 |
| 2 |  全部 4 篇 | 6 小时 |
| 3 |  | 1 小时 |
| 4 |  | 30 分钟 |
| 5 |  | 1 小时 |
| 6 |  | 1 小时（看代码）|
| 7 |  | 1 小时 |
| 8 |  | 1 小时 |

### 推荐读

-  — 我们做这套时踩的坑
-  — 生产环境
-  — 完整电商案例

### 不必读

- 02-实战指南/ （跟跑）
- 6-exercises/ 30 道作业

### 评估检查清单

- [ ] 哲学理解（2400 年 + AI 时代）
- [ ] 5 大规范（RDF / RDFS / OWL / SPARQL / SHACL）
- [ ] Foundry 6 大能力（Object / Link / Action / Function / Validation / Pipeline）
- [ ] 8 业务场景
- [ ] 性能瓶颈（1-10 万级 Object 用 RDF，千万级需 Neptune / Blazegraph）
- [ ] 团队成本（开发者 1-2 人 + 数据治理 1 人）
- [ ] 投资估算（小型 100 万 / 中型 1000 万 / 大型 1 亿）

---

## 6. 学生 / 学术研究

> **"我要全貌"**
> **时间**：3-4 周
> **目标**：从哲学到工程全懂，能写论文 / 做研究

### 必读（按顺序 · 3-4 周）

**Week 1: 历史 + 规范**

| # | 文档 | 时间 |
|---|------|------|
| 1 |  全部 | 1 小时 |
| 2 |  全部 | 8 小时 |
| 3 |  全部 | 4 小时 |

**Week 2: 工程 + 案例**

| # | 文档 | 时间 |
|---|------|------|
| 1 |  全部 | 8 小时 |
| 2 | 5 个最难的案例（物流 / CRM / 医疗 / Foundry / 财务）| 16 小时 |

**Week 3: 作业 + 论文素材**

| # | 文档 | 时间 |
|---|------|------|
| 1 |  30 道作业 | 16 小时 |
| 2 | 跑 Foundry 全部 6 脚本 | 4 小时 |
| 3 | 写 1 个自己的小本体 | 8 小时 |

**Week 4: 写报告 / 论文**

- 整理笔记
- 写 1 篇博客 / 课程作业

### 推荐读

-  — 论文 / 规范索引
-  — 术语表
-  — 踩坑心得

### 论文素材方向

- 语义网 30 年综述
- LLM + 本体 / KG 综述
- Palantir Foundry 国产替代方案
- ABAC 在语义层的应用
- CDC 在 RDF 物化的应用

---

## 7. 业务方 / 销售 / 非技术

> **"我同事要干啥 / 这事能给我啥"**
> **时间**：1-2 小时
> **目标**：知道 AI 系统能给你看什么

### 必读（1 小时）

| # | 文档 | 时间 | 你会得到什么 |
|---|------|------|-------------|
| 1 |  | 5 分钟 | 为什么 AI 会胡说 |
| 2 | 1-2 个业务场景 README（你所在的行业）| 30 分钟 | 看 AI 能给啥 |
| 3 |  | 10 分钟 | 看 1 个完整工作流 |
| 4 |  | 15 分钟 | 业务方常见问题 |

### 推荐读

- 
-  — 看修复记录（知道项目成熟度）

### 不必读

- 所有规范
- 所有 .py 脚本

### 一句话总结给你

> **你不需要懂代码**。你需要懂"AI 给你的数据哪些可信、怎么提问"。

具体：
- 看仪表盘（`build_dashboard.py` 生成的 dashboard.html）
- 用 Claude Desktop 问（`mcp_server.py` 接的 7 工具）
- 提交需求给 IT（让他们改本体 / 加 SHACL 规则）

---

## 附录：所有文档按"读者类型"标星

> ★ = 必读
> ☆ = 推荐读
> · = 可选读
> × = 不必读

| 文档 | 老板 | PM | 开发者 | 工程师 | 架构师 | 学生 | 业务方 |
|------|------|----|--------|--------|--------|------|--------|
| [README.md](../README.md) | ☆ | ☆ | ★ | ★ | ★ | ★ | ☆ |
| [00-overview/00-overview.md](00-overview.md) | ☆ | ☆ | ★ | ★ | ★ | ★ | · |
| [00-overview/BOOK.md](BOOK.md) | · | · | · | · | · | ☆ | · |
| [00-overview/AUTHOR-NOTES.md](AUTHOR-NOTES.md) | ☆ | · | · | ☆ | ☆ | ☆ | ☆ |
| [00-overview/LEARNING-ROADMAP.md](LEARNING-ROADMAP.md) | · | ☆ | ☆ | · | · | · | · |
| [00-overview/REVIEW-REPORT.md](REVIEW-REPORT.md) | · | · | · | · | ☆ | · | · |
| [01-history/01-ontology-philosophy.md](../01-history/01-ontology-philosophy.md) | · | · | · | · | ★ | ★ | · |
| [01-history/02-knowledge-representation.md](../01-history/02-knowledge-representation.md) | · | · | · | · | ★ | ★ | · |
| [01-history/03-ai-ontology-why.md](../01-history/03-ai-ontology-why.md) | ★ | ☆ | ☆ | ☆ | ★ | ★ | ★ |
| [02-specs/01-rdf.md](../02-specs/01-rdf.md) | × | × | ★ | ★ | ★ | ★ | × |
| [02-specs/02-rdfs-owl.md](../02-specs/02-rdfs-owl.md) | × | × | ☆ | ★ | ★ | ★ | × |
| [02-specs/03-sparql.md](../02-specs/03-sparql.md) | × | × | ★ | ★ | ★ | ★ | × |
| [02-specs/04-shacl.md](../02-specs/04-shacl.md) | × | × | ★ | ★ | ★ | ★ | × |
| [02-实战指南/2.1-rdf-hands-on.md](../02-实战指南/2.1-rdf-hands-on.md) | × | × | ★ | ★ | ☆ | ★ | × |
| [02-实战指南/2.3-sparql-hands-on.md](../02-实战指南/2.3-sparql-hands-on.md) | × | × | ★ | ★ | ☆ | ★ | × |
| [02-实战指南/2.4-shacl-hands-on.md](../02-实战指南/2.4-shacl-hands-on.md) | × | × | ★ | ★ | ☆ | ★ | × |
| [03-engineering/01-hello-world.md](../03-engineering/01-hello-world.md) | × | · | ☆ | ★ | ★ | ★ | × |
| [03-engineering/02-architecture.md](../03-engineering/02-architecture.md) | × | · | ☆ | ★ | ★ | ★ | × |
| [03-engineering/03-comparison.md](../03-engineering/03-comparison.md) | ★ | ☆ | ☆ | ★ | ★ | ★ | · |
| [03-engineering/04-case-ecommerce.md](../03-engineering/04-case-ecommerce.md) | × | · | ☆ | ★ | ★ | ★ | × |
| 04-zero-install-demo/ | × | × | ★ | ★ | ★ | ★ | × |
| [05-real-cases/00-场景对比总表.md](../05-real-cases/00-场景对比总表.md) | ★ | ★ | ☆ | ☆ | ☆ | ☆ | ★ |
| [05-real-cases/hr/README.md](../05-real-cases/hr/README.md) | · | · | ★ | ★ | · | ★ | · |
| [05-real-cases/customer-service/README.md](../05-real-cases/customer-service/README.md) | · | · | ★ | ★ | · | ★ | · |
| [05-real-cases/finance/README.md](../05-real-cases/finance/README.md) | · | · | ★ | ★ | · | ★ | · |
| [05-real-cases/product/README.md](../05-real-cases/product/README.md) | · | · | ★ | ★ | · | ★ | · |
| [05-real-cases/logistics/README.md](../05-real-cases/logistics/README.md) | · | · | ☆ | ★ | · | ★ | · |
| [05-real-cases/crm/README.md](../05-real-cases/crm/README.md) | · | · | ☆ | ★ | · | ★ | · |
| [05-real-cases/medical/README.md](../05-real-cases/medical/README.md) | · | · | ☆ | ★ | · | ★ | · |
| [05-real-cases/foundry-platform/README.md](../05-real-cases/foundry-platform/README.md) | ★ | ★ | ★ | ★ | ★ | ★ | ★ |
| 06-exercises/ | × | × | ☆ | ★ | · | ★ | × |
| [99-references/01-resources.md](../99-references/01-resources.md) | · | · | ☆ | ☆ | ★ | ★ | · |
| [99-references/02-pitfalls-best-practices.md](../99-references/02-pitfalls-best-practices.md) | · | · | ☆ | ★ | ★ | ☆ | · |
| [99-references/03-study-plan.md](../99-references/03-study-plan.md) | · | · | · | · | · | ★ | · |
| [99-references/04-env-checklist.md](../99-references/04-env-checklist.md) | × | × | ☆ | ★ | ☆ | ☆ | × |
| [99-references/05-demo-script.md](../99-references/05-demo-script.md) | × | × | ☆ | ☆ | · | ☆ | × |
| [99-references/06-cheatsheet.md](../99-references/06-cheatsheet.md) | × | × | ★ | ★ | ☆ | ★ | × |
| [99-references/07-FAQ.md](../99-references/07-FAQ.md) | ☆ | ☆ | ☆ | ☆ | ☆ | ☆ | ★ |
| [99-references/08-glossary.md](../99-references/08-glossary.md) | · | · | ☆ | ☆ | ☆ | ★ | · |
| [99-references/09-pdf-tutorial.md](../99-references/09-pdf-tutorial.md) | · | · | · | · | · | · | · |
| 99-references/The-LLM-Grounding-Playbook.pdf | ☆ | ☆ | ☆ | ☆ | ☆ | ☆ | ☆ |
| [CHANGELOG.md](../CHANGELOG.md) | · | · | · | · | · | · | · |

---

## 附录：所有 Python 脚本按读者标星

| 脚本 | 老板 | PM | 开发者 | 工程师 | 架构师 | 学生 | 业务方 |
|------|------|----|--------|--------|--------|------|--------|
| 04-zero-install-demo/examples/*.py | × | × | ★ | ★ | ★ | ★ | × |
| 05-real-cases/*-query.py | × | · | ★ | ★ | ☆ | ★ | × |
| 05-real-cases/foundry-platform/run_platform.py | · | · | ★ | ★ | ★ | ★ | · |
| 05-real-cases/foundry-platform/mcp_server.py | × | × | ★ | ★ | ★ | ★ | × |
| 05-real-cases/foundry-platform/r2rml_materialize.py | × | × | ☆ | ★ | ★ | ★ | × |
| 05-real-cases/foundry-platform/build_dashboard.py | × | ☆ | ★ | ★ | ★ | ★ | ☆ |
| 05-real-cases/foundry-platform/abac_security.py | × | × | ☆ | ★ | ★ | ★ | × |
| 05-real-cases/foundry-platform/cdc_demo.py | × | × | ☆ | ★ | ★ | ★ | × |

---

## 附录：不知道你属于哪类？

3 个问题帮你判断：

1. **你要不要写代码？**
   - 不要 → 看 老板 / PM / 业务方 路径
   - 要 → 继续

2. **你做的项目是"建一个新系统"还是"集成到现有系统"？**
   - 集成 → AI 开发者（路径 3）
   - 建新系统 → 继续

3. **团队多大？**
   - 1-2 人 → AI 开发者（路径 3）
   - 3-10 人 → 后端工程师（路径 4）
   - 10+ 人 / 选型阶段 → 架构师（路径 5）

---

## 附录：找错路径了？

如果读了一段发现"这不对"：
- 老板但读规范太枯燥 → 跳到案例 README 看图
- 开发者但读哲学太学术 → 跳到 04 demo 跑代码
- 业务方但读 02-specs 太硬 → 跳到案例 README 看图

**项目设计是"模块化"**——任何时候可以从任何一段开始。
