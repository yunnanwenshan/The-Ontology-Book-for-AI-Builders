# The LLM Grounding Playbook

> **让 LLM 不胡说** — 7 个本体实战 + 1 个 Palantir 风格平台
> **v1.0 · 2026-07** · 写给开发者的小白友好版

## 5 分钟上手

```bash
pip install rdflib pyshacl SPARQLWrapper
cd ~/Documents/projects/ai/ontology/04-zero-install-demo
python3 examples/1-first-rdf.py
```

看到 4 条三元组 = 成功。卡住？[故障排查](04-zero-install-demo/README.md#故障排查)

## 三条路径

| 时间 | 路径 | 入口 |
|------|------|------|
| 30 分钟 | 老板速览 | [01-history/03](01-history/03-ai-ontology-why.md) |
| 4 小时 | 周末突击 | [04-zero-install-demo](04-zero-install-demo/) |
| 3 周 | 系统学习 | [00-overview](00-overview/00-overview.md) |

→ 不知道选哪个？[看案例梯度](05-real-cases/00-场景对比总表.md)

## 已交付

- ✅ **7 个真实业务案例**（HR / 客服 / 财务 / 商品 / 医疗 / 物流 / CRM）
- ✅ **1 个 Foundry 平台**（6 脚本：核心 / AIP / 物化 / 仪表盘 / ABAC / CDC）
- ✅ **PDF 教程**（[The-LLM-Grounding-Playbook.pdf](99-references/) · 463 KB）
- ✅ **30 道作业**（[06-exercises](06-exercises/)）

## 目录

```
├── BOOK.md                           ← 书名 + 副标题 + 章节映射
├── 00-overview/                      总览 + 作者手记 + Review 报告
├── 01-history/                       哲学源流（速读版）
├── 02-specs/                         技术规范速查
├── 02-实战指南/                       手把手主线
├── 03-engineering/                   Docker 版工程化
├── 04-zero-install-demo/              ★ 零安装 demo
├── 05-real-cases/                     ★ 7 案例 + Foundry 平台
├── 06-exercises/                      30 道作业
└── 99-references/                    附录（PDF 教程、FAQ、术语表等）
```

## 怎么选路径

| 你是... | 推荐 |
|--------|------|
| **开发者做项目** | 7 案例 → Foundry 平台 |
| **技术负责人评估** | 00-overview + 01-history/03 |
| **想给 AI 配数据** | Foundry 平台（核心 + AIP）|
| **想造 AI agent** | 02-specs → 04 demo → MCP |

## 反馈

- 文档错：直接改文件
- 跑不通：把报错发我
- 缺场景：告诉我行业/业务，我加

## 阅读路线图

不知道先读哪个？[00-overview/LEARNING-ROADMAP.md](00-overview/LEARNING-ROADMAP.md) 有按时间/角色/目标的 3 条路径。

## License

CC BY-SA 4.0
