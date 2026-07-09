# 阅读路线图

> **不知道先读哪个？** 看这张图。
> 三种时间预算，三种角色，三条路径。

---

## 1. 按时间预算

```
你有 30 分钟?
├── YES → [路径 A: 速览]
│         01-history/03  +  README 案例梯度
│         目标：知道"为什么用本体"
│
└── NO, 有 4 小时?
    ├── YES → [路径 B: 突击]
    │         04-zero-install-demo (5 个 demo)
    │         + 1 个真实案例（推荐 HR）
    │         目标：跑通 + 改 1 行自己的数据
    │
    └── NO, 有 3 周?
        └── [路径 C: 系统]
              按 00-overview/00-overview.md 顺序
              + 做 30 道作业
              目标：能搭企业级平台
```

---

## 2. 按角色

### 你是**应用开发者**？

```
第 1 周：技术基础
├── Day 1-2: 04-zero-install-demo/   (5 个 demo)
├── Day 3-4: 02-实战指南/             (4 篇手把手)
└── Day 5:   02-specs/01-04          (速查手册)

第 2 周：真实场景
├── Day 1-2: 05-real-cases/hr  +  customer-service
├── Day 3:   05-real-cases/finance  +  product
├── Day 4:   05-real-cases/logistics  +  crm
└── Day 5:   05-real-cases/medical  +  foundry-platform

第 3 周：工程化
├── Day 1-2: Foundry 平台 6 脚本
├── Day 3:   ABAC 权限
├── Day 4:   CDC 同步
└── Day 5:   接 Claude Desktop
```

### 你是**技术负责人 / 架构师**？

```
第 1 天: 00-overview/  (1 小时)
第 2 天: 01-history/    (1 小时，看 review report)
第 3 天: 03-engineering/03-comparison  (本体 vs RAG)
第 4 天: 5-real-cases/foundry-platform  (1 个完整平台)
第 5 天: 99-references/01-resources  (技术选型)
```

### 你是**业务方 / 决策者**？

```
第 1 小时: README + 00-overview (知道有什么)
第 2 小时: 01-history/03  (为什么 AI 需要本体)
第 3 小时: 05-real-cases/00-场景对比总表  (哪个案例适合你)
第 4 小时: 找一个最像的案例 README  (看能解决你什么)
```

### 你是**老板 / 投资人**？

```
30 分钟: 01-history/03-ai-ontology-why.md
       + 03-engineering/03-comparison.md
       (知道为什么 + 选哪个方案)
```

---

## 3. 按目标

| 你的目标 | 推荐路径 | 预计时间 |
|----------|----------|---------|
| 给公司试点 | 1 案例 + 改自己数据 | 1-2 天 |
| 评估技术 | 00-overview + 01-history | 2-3 小时 |
| 做企业平台 | Foundry 6 脚本 | 2-3 周 |
| 给 AI 配数据 | Foundry 核心 + AIP | 1 周 |
| 写技术博客 | 跑通 demo + 看 1 案例 | 半天 |
| 投简历 / 面试 | 5 个 demo + 1 案例 | 1 天 |

---

## 4. 章节依赖图

```
04-zero-install-demo
        ↓
02-实战指南 (跟跑)
        ↓
02-specs (速查)
        ↓
   ┌────┴────┐
   ↓         ↓
案例 (1 个)   Foundry 平台
   ↓         ↓
   └────┬────┘
        ↓
06-exercises (30 题)
        ↓
99-references (查漏补缺)
```

**最短路径**：04 → 02-实战 → 1 案例（4 小时）

**最全路径**：04 → 02-specs → 02-实战 → 7 案例 → Foundry → 6-exercises → 99-refs（3 周）

---

## 5. 不要做

| 不要做 | 原因 |
|--------|------|
| ❌ 先读 01-history/2400 年哲学 | 对做项目没用，跑通 demo 再回来看 |
| ❌ 直接读 02-specs/ 不跑代码 | 看语法不如直接跑 |
| ❌ 同时学 7 案例 | 选 1 个跑通，再换下一个 |
| ❌ 跳过 04 故障排查 | 跑不出来时再找就晚了 |
| ❌ 试图读完全部 100 个文件 | 不知道读啥就看这张图 |

---

## 6. 读完这页

- 知道下一步该做啥了？→ **去 04-zero-install-demo 跑第一个 demo**
- 还是不确定？→ 读 [AUTHOR-NOTES.md](AUTHOR-NOTES.md) 的"我推荐的学习顺序"
- 想看作者踩了什么坑？→ [AUTHOR-NOTES.md](AUTHOR-NOTES.md) 的"我踩过的 5 个坑"
