# 阶段 3.2 · 架构设计：Agent ↔ 本体层 ↔ 业务数据

> **一句话**：标准三层架构，Agent 不直接碰数据库
> **目标**：画得出图、说得出每层职责

## 1. 一句话总结

**标准架构**：

```
Agent (决策)
   ↓ MCP / Tool 调用
本体语义层 (统一 schema)
   ↓ 物化 / 实时查询
业务数据源 (真相)
```

**单向数据流**：业务数据源 → 本体层 → Agent。

## 2. 生活类比：点菜 App

```
你 (Agent)
   ↓
服务员 (本体层)
   │ "你有 200 元预算"
   │ "不吃辣"
   │ "想快点上"
   ↓
厨房 (业务数据源)
   │ 真的做菜
   │ 真的备料
   ↓
上菜
```

**你**（Agent）不直接进厨房（数据库）。
**服务员**（本体层）把"你的需求"翻译成厨房能懂的指令。
**厨房**（业务数据源）只管做菜。

## 3. 三层职责

| 层 | 职责 | 不应该做 |
|----|------|----------|
| **Agent** | 理解用户意图、调工具 | 自己写 SQL |
| **本体层** | 提供统一视图、约束、推理 | 自己存"业务真相" |
| **数据源** | 存原始数据 | 改 schema 迎合本体 |

**Agent 的工作流**：

```
用户问："Alice 买过什么？"
   ↓
Agent 选工具：query_ontology
   ↓
工具传 SPARQL：SELECT ?p WHERE { ex:Alice ex:purchased ?p }
   ↓
本体层：返回结果
   ↓
Agent 整理成自然语言
   ↓
用户得到答案
```

## 4. 架构图

```
              ┌──────────────────────────────┐
              │   Agent  (Claude / GPT / 自研) │
              │   - 理解用户意图              │
              │   - 拆解任务                 │
              │   - 调工具                   │
              └──────────────┬───────────────┘
                             │
                  MCP / Tool  │  (JSON-RPC 协议)
                             │
              ┌──────────────▼───────────────┐
              │  本体语义层  (Ontology Layer) │
              │  - OWL 本体 (TBox)            │
              │  - 业务数据 (ABox)            │
              │  - SHACL 校验                │
              │  - SPARQL 端点               │
              │  - 推理机 (可选)              │
              └──────────────┬───────────────┘
                             │
              物化 / 视图 / CDC │  (R2RML / Ontop / Debezium)
                             │
              ┌──────────────▼───────────────┐
              │  业务数据源  (Source of Truth)│
              │  - MySQL / PostgreSQL        │
              │  - MongoDB / Elasticsearch   │
              │  - S3 / 文件                 │
              └──────────────────────────────┘
```

## 5. 5 分钟上手：让 Agent 调用 SPARQL

### 5.1 安装 MCP

```bash
pip install mcp
```

### 5.2 写 MCP Server

新建 `ontology_mcp.py`：

```python
from mcp.server import Server
import requests
import os

app = Server("ontology-mcp")

# 本体 SPARQL 端点
ENDPOINT = os.getenv("ONTOLOGY_ENDPOINT", "http://localhost:3030/shop/query")

@app.tool()
def sparql_query(query: str) -> list:
    """执行 SPARQL 1.1 查询并返回结果。

    Args:
        query: 标准的 SPARQL 1.1 查询字符串
    """
    resp = requests.get(ENDPOINT,
                        params={"query": query, "format": "json"})
    resp.raise_for_status()
    return resp.json()["results"]["bindings"]

if __name__ == "__main__":
    app.run()
```

### 5.3 配置 Claude Desktop

macOS：`~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "ontology": {
      "command": "python3",
      "args": ["/Users/你的用户名/ontology-mcp/ontology_mcp.py"]
    }
  }
}
```

重启 Claude Desktop。

### 5.4 测试

打开 Claude，问：

> "请用 ontology 工具查一下哪些客户买过 iPhone"

Claude 会：
1. 看到 `sparql_query` 工具
2. 生成 SPARQL：
   ```sparql
   PREFIX ex: <http://example.com/shop#>
   SELECT ?name WHERE {
       ?order a ex:Order ;
              ex:customer ?cust ;
              ex:item ex:item-A .
       ?cust ex:customerName ?name .
   }
   ```
3. 调工具拿结果
4. 用自然语言回答

> ⚠ **避坑**：Claude Desktop 看不到工具？检查 JSON 文件路径和语法。

## 6. 三种"Agent 调本体"模式

### 6.1 模式 1：让 Agent 直接写 SPARQL

**适用**：查询简单，Agent 强
**风险**：Agent 可能写错 SPARQL
**优势**：灵活

### 6.2 模式 2：模板化查询（推荐）

**适用**：业务查询稳定
**风险**：业务变了要改模板
**优势**：稳定、可审计

```python
QUERIES = {
    "top_customers": {
        "template": """
            PREFIX ex: <http://example.com/shop#>
            SELECT ?name (SUM(?amount) AS ?total) WHERE {
                ?o a ex:Order ;
                   ex:customer ?c ;
                   ex:totalAmount ?amount .
                ?c ex:customerName ?name .
            } GROUP BY ?c ?name
            ORDER BY DESC(?total) LIMIT {N}
        """,
        "params": {"N": int}
    },
    # ... 更多查询
}

def run_query(name, **params):
    q = QUERIES[name]
    sparql = q["template"].format(**params)
    return query_ontology(sparql)
```

### 6.3 模式 3：自然语言 → 意图 → 查询

**适用**：业务复杂、查询多变
**优势**：最灵活
**风险**：意图分类出错

```python
# 1. 意图分类（用 LLM）
intent = classify(user_question)
# 2. 提取参数
params = extract_params(user_question)
# 3. 选模板
sparql = QUERIES[intent].format(**params)
# 4. 调本体
result = query_ontology(sparql)
```

## 7. 物化 vs 实时查询

| 方式 | 优点 | 缺点 | 适用 |
|------|------|------|------|
| **物化** | 查询快 | 延迟、占空间 | 小数据、准实时 |
| **实时** | 数据新 | 慢 | 大数据 |
| **CDC** | 准实时 | 复杂 | 中等数据、变更频繁 |

### 7.1 物化（Offtop 工具）

```bash
docker run -d --name ontop \
  -p 8080:8080 \
  ontop/ontop:latest \
  --dburl=jdbc:mysql://host:3306/shop \
  --ontology=/data/shop.owl \
  --mapping=/data/shop.ttl
```

### 7.2 CDC（Debezium）

```yaml
# 复杂，需要 Kafka + Debezium
# 适合数据量 100 万+ 的场景
```

## 8. 5 个安全考虑

| 风险 | 应对 |
|------|------|
| **SPARQL 注入** | 用参数化查询 + 模板 |
| **数据外泄** | 本体层做行/列权限（ABAC） |
| **推理爆炸** | 限制 OWL profile 到 DL |
| **查询超时** | 设查询超时（5 秒） |
| **备份缺失** | 物化数据每日备份 |

## 9. 速读建议

| 时间 | 看哪几节 |
|------|----------|
| 5 分钟 | 1、2、3、4 |
| 10 分钟 | + 5（跑通 MCP demo） |
| 20 分钟 | + 6、7、8 |

## 10. 避坑提示

- ❌ **别让 Agent 直接调数据库**：必走本体层
- ❌ **别忘了查询超时**：慢查询会拖死本体层
- ❌ **别在生产开 OWL 推理**：先关掉，需要时再开
- ✅ **用模板化查询**：稳定、可审计
- ✅ **加行/列权限**：本体层是访问控制点
- ✅ **监控查询日志**：发现异常 query

## 参考文献

- Anthropic. (2024). *Model Context Protocol Specification*. https://modelcontextprotocol.io/
- Ontop. https://ontop-vkg.org/
- Microsoft. (2026). *Use Ontology MCP Server*. https://learn.microsoft.com/en-us/fabric/iq/ontology/
