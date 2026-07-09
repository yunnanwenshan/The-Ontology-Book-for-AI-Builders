# Foundry 平台 · Palantir 风格企业本体

> **场景**：把 7 个业务案例的能力合并成统一平台（Object/Action/Function/ABAC/CDC）
> **难度 / 时间**：🏆 集成 / 2-3 小时
> **谁在用**：架构师搭平台 / 业务方看仪表盘 / 开发者跑 6 脚本

## 这是什么？

Palantir Foundry 是企业数据中台的"集大成者"，核心理念是 **"一个 Ontology 覆盖整个企业"**。
我们用 RDF + Python 复现了它的 6 大能力，规模适合 1-10 万级 Object。

| Palantir Foundry 概念 | RDF 实现 | 我们的实现 |
|----------------------|----------|-----------|
| Object Type | `owl:Class` | 12 个（Order/Customer/Product/...）|
| Link Type | `ObjectProperty` + `owl:inverseOf` | 5 个 |
| Property | `DatatypeProperty` | 22 个 |
| Action Type | Action 子类 + Python 函数 | 5 个 |
| Function | Python 函数 | 2 个 |
| Object Validation | SHACL Shape | 7 个 |
| Pipeline Builder | R2RML 物化 | `r2rml_materialize.py` |
| Object View / Workshop | SPARQL + HTML | `build_dashboard.py` |
| AIP (LLM 调本体) | MCP Server | `mcp_server.py` (7 工具) |
| Granular Security | ABAC 规则 + sensitivity 标签 | `abac_security.py` |
| Stream Mode | 文件 watcher + 增量物化 | `cdc_demo.py` |

## 6 个工程脚本

按"用户使用顺序"排：

### 1️⃣ run_platform.py · 核心 9 section

```bash
python3 run_platform.py
```

跑通：SHACL 验证 / Object 概览 / Link 图 / Function 对账 / Action / Dashboard / KPI / Audit。
**2 分钟看完 9 个 section**。

### 2️⃣ mcp_server.py · AIP / LLM 集成（7 工具）

```bash
python3 mcp_server.py            # CLI 演示
python3 mcp_server.py --mcp      # 启动 MCP Server（接 Claude Desktop）
```

7 个工具：`query_orders` / `get_order_detail` / `dashboard_kpi` / `reconcile_orders` / `approve_order` / `reserve_inventory` / `assign_customer`

**接 Claude Desktop**：在 `claude_desktop_config.json` 加 1 个 mcpServers 条目，重启 Claude，就可以直接问"查华为的订单"。

### 3️⃣ r2rml_materialize.py · SQL → RDF 物化

```bash
python3 r2rml_materialize.py
```

模拟 ERP（SQLite，4 张表，19 行）→ R2RML 映射 → RDF → 校验。
**真实场景**：把 MySQL/PostgreSQL 物化成 RDF（Foundry Pipeline Builder 核心能力）。

### 4️⃣ build_dashboard.py · HTML 仪表盘

```bash
python3 build_dashboard.py
# 打开 dashboard.html（暗色 Foundry 风格）
```

4 个 KPI 卡 + Object Type 分布 + 订单全链路 + Audit 时间线。
不需 Web Server，双击打开。

### 5️⃣ abac_security.py · 字段级 ABAC 权限

```bash
python3 abac_security.py
```

4 个敏感度等级 + 6 个用户角色 + 字段级过滤。
**真实场景**：销售看不到付款金额，财务能看所有，审计员只能看财务字段。

### 6️⃣ cdc_demo.py · 实时数据同步

```bash
python3 cdc_demo.py    # 4 轮演示自动停
```

监控源数据文件 → 变化触发自动物化。
**真实场景**：ERP 导出新订单 → 自动变 RDF → 仪表盘自动刷新。

## 端到端工程流程

```
ERP (MySQL/PostgreSQL/SQLite)
   ↓
r2rml_materialize.py           ← Pipeline Builder
   ↓
RDF Graph (data/platform-data-mat.ttl)
   ↓
SHACL 验证                     ← Object Validation
   ↓
本体平台（4 个主脚本）：
   ├── run_platform.py           ← 9 section 核心
   ├── build_dashboard.py        ← Workshop
   ├── mcp_server.py             ← AIP
   └── abac_security.py          ← 权限
   ↓
   CDC 监控（cdc_demo.py）         ← Stream Mode
   ↓
Claude Desktop / Claude Code   ← 业务人员用
```

## 跑 6 个脚本的顺序

```bash
# 推荐顺序
python3 run_platform.py          # 1. 先看核心 9 section
python3 r2rml_materialize.py     # 2. 试物化
python3 build_dashboard.py       # 3. 看仪表盘
python3 mcp_server.py            # 4. 看 AIP
python3 abac_security.py         # 5. 看权限
python3 cdc_demo.py              # 6. 看 CDC
```

每个约 1-2 分钟，全跑完 10 分钟。

## 跟真实 Palantir Foundry 的能力对照

| Foundry 能力 | 实现 | 状态 |
|-------------|------|------|
| Object Type + Property | ✅ | 12 Object + 22 Property |
| Link Type + Inverse | ✅ | 5 Link Type |
| Object Validation | ✅ | 7 SHACL Shape |
| Action Type | ✅ | 5 Action Type |
| Function (Python) | ✅ | 2 Function |
| Object View / Workshop | ✅ | SPARQL + HTML |
| Pipeline Builder (ETL) | ✅ | R2RML 物化 |
| AIP (LLM 调本体) | ✅ | MCP Server (7 工具) |
| Granular Security | ✅ | ABAC 权限 |
| Stream Mode | ✅ | CDC 实时同步 |
| Object Sets / Dynamic Schema | ⚠️ | 未集成（需 ontology reasoner）|
| Workshop UI (拖拽) | ❌ | HTML 替代 |
| 千万级 Object 性能 | ❌ | 适合 1-10 万级 |
| 多用户权限 + UI 登录 | ❌ | 未集成（仅代码层）|

**RDF 实现已覆盖 Foundry 80% 核心能力**。

## 故障排查

跟 [04-zero-install-demo](../../04-zero-install-demo/README.md#故障排查) 一样的 5 个错误。
**额外注意**：
- 别把脚本命名 `platform.py`（跟 stdlib 冲突）
- `mcp_server.py` 需要 `pip install mcp` 才能用 MCP 模式

## 文件清单

```
foundry-platform/
├── README.md                    ← 本文件
├── run_platform.py              ← 1. 核心 9 section
├── mcp_server.py                ← 2. AIP 7 工具
├── r2rml_materialize.py         ← 3. SQL → RDF
├── build_dashboard.py           ← 4. HTML 仪表盘
├── abac_security.py             ← 5. ABAC 权限
├── cdc_demo.py                  ← 6. CDC 同步
├── cdc_sync.py                  ← 6 备选（无限循环版，需手动停）
├── dashboard.html               ← 4 生成的仪表盘
└── data/
    ├── platform-ont.ttl                ← 本体
    ├── platform-ont-with-security.ttl  ← 5 加 ABAC 标签的本体
    ├── platform-shapes.ttl             ← SHACL 规则
    ├── platform-data.ttl                ← 业务数据
    ├── platform-data-mat.ttl            ← 3 物化输出
    ├── platform-data-updated.ttl        ← Action 后的数据
    └── shop.db                          ← 3 用的 SQLite
```

## 真实数据示例

跑 `run_platform.py` 会看到：

```
[4] Function: 订单实际金额（重新计算）
  O0000000003  声明 ¥25,997.00  /  实际 ¥29,997.00  ❌ 差异 ¥4000.00
  O0000000001  声明 ¥21,997.00  /  实际 ¥21,994.00  ❌ 差异 ¥-3.00
  O0000000005  声明 ¥100.00     /  实际 ¥0.00      ❌ 差异 ¥-100.00
```

**O0000000003 差 4000 元** —— 这就是 Action 触发的真实业务洞察，业务方需要查。

## 进阶

- **接 Claude Desktop**：参考 `mcp_server.py` 头部注释
- **接真实 ERP**：改 `r2rml_materialize.py` 里的 SQLite → MySQL
- **接 GraphRAG**：把本体和向量数据库结合
- **写更多 README**：把这个 README 翻译成英文/日文
