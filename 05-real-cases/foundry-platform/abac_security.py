"""ABAC 权限系统（Attribute-Based Access Control）.

对齐 Palantir Foundry 的 Granular Security:
- 每个 Object / Link / Property 可以标记为敏感
- 每个 User 有一组属性（角色/部门/项目）
- 规则：if (user.role in [...]) and (obj.sensitivity in [...]) -> allow

我们用 RDF + SPARQL 实现:
- 敏感度标签: ex:sensitivity "Public" / "Internal" / "Confidential" / "Restricted"
- 用户属性: ex:userRole, ex:userDepartment
- ABAC 规则: SPARQL 模板（用 FILTER 模拟授权）
"""
from pathlib import Path
from rdflib import Graph, Namespace, Literal, URIRef, BNode
from rdflib.plugins.sparql import prepareQuery
from rdflib.namespace import RDF, XSD
import json

DATA_DIR = Path(__file__).parent / "data"
ont  = Graph().parse(str(DATA_DIR / "platform-ont.ttl"),    format="turtle")
data = Graph().parse(str(DATA_DIR / "platform-data.ttl"),   format="turtle")
g = ont + data
ex = Namespace("http://platform.com/")
g.bind("ex", ex)

# ============================================================
# 1. 在本体里加 sensitivity 标签
# ============================================================
SENSITIVITY_LEVELS = ["Public", "Internal", "Confidential", "Restricted"]
# 数字越大越敏感
SENSITIVITY_RANK = {l: i for i, l in enumerate(SENSITIVITY_LEVELS)}

# 给 Object Type / Property 加 sensitivity
SENSITIVITY_MAP = {
    # Object Type 级别
    "ex:Order":      "Internal",
    "ex:OrderItem":  "Internal",
    "ex:Customer":   "Confidential",
    "ex:Product":    "Public",
    "ex:Employee":   "Internal",
    "ex:Warehouse":  "Public",
    "ex:InventoryItem": "Internal",
    "ex:Shipment":   "Internal",
    "ex:Invoice":    "Confidential",
    "ex:Payment":    "Restricted",   # 财务，最敏感
    # Property 级别（覆盖）
    "ex:paymentAmount":  "Restricted",
    "ex:invoiceAmount":  "Confidential",
    "ex:orderTotalAmount": "Internal",
    "ex:customerEmail":   "Confidential",
    "ex:customerPhone":   "Confidential",
    "ex:salary":          "Restricted",
}

# 把 sensitivity 写入本体
for prop_uri_str, level in SENSITIVITY_MAP.items():
    prop_uri = URIRef(prop_uri_str)
    g.add((prop_uri, ex.sensitivity, Literal(level)))

print(f"✓ 已为 {len(SENSITIVITY_MAP)} 个属性打上 sensitivity 标签")

# ============================================================
# 2. 定义用户 + 角色
# ============================================================
USERS = [
    {
        "id": "u-001",
        "name": "王经理（销售部经理）",
        "role": "Manager",
        "department": "Sales",
        "clearance": "Confidential",   # 最高能看 Confidential
    },
    {
        "id": "u-002",
        "name": "李销售（销售员）",
        "role": "Sales",
        "department": "Sales",
        "clearance": "Internal",
    },
    {
        "id": "u-003",
        "name": "张客服",
        "role": "CustomerService",
        "department": "Service",
        "clearance": "Confidential",
    },
    {
        "id": "u-004",
        "name": "赵财务（财务总监）",
        "role": "Finance",
        "department": "Finance",
        "clearance": "Restricted",   # 能看所有
    },
    {
        "id": "u-005",
        "name": "钱仓管",
        "role": "Warehouse",
        "department": "Warehouse",
        "clearance": "Internal",
    },
    {
        "id": "u-006",
        "name": "外部审计员",
        "role": "Auditor",
        "department": "External",
        "clearance": "Confidential",   # 审计只能看到部分
        "constraints": ["only_financial"],  # 只能看财务相关
    },
]

# ============================================================
# 3. ABAC 授权决策函数
# ============================================================
def can_user_see(user: dict, sensitivity: str) -> bool:
    """简化 ABAC 决策."""
    user_rank = SENSITIVITY_RANK[user["clearance"]]
    obj_rank = SENSITIVITY_RANK[sensitivity]
    return user_rank >= obj_rank


def can_user_see_property(user: dict, prop_uri: str) -> tuple:
    """返回 (能否看, 原因)."""
    if prop_uri not in SENSITIVITY_MAP:
        return True, "Public"

    sensitivity = SENSITIVITY_MAP[prop_uri]
    if not can_user_see(user, sensitivity):
        return False, f"sensitivity={sensitivity} > clearance={user['clearance']}"

    # 角色约束（如审计员只能看财务）
    if "constraints" in user and "only_financial" in user["constraints"]:
        if "Payment" not in prop_uri and "Invoice" not in prop_uri and "payment" not in prop_uri.lower() and "invoice" not in prop_uri.lower() and "Amount" not in prop_uri:
            return False, "审计员只能看财务字段"

    return True, f"OK ({sensitivity})"


# ============================================================
# 4. SPARQL 查询 + 字段级过滤
# ============================================================
def query_orders_for_user(user: dict, customer_name=None, status=None):
    """查订单，按用户权限过滤字段."""
    filters = ["?o a ex:Order", "?o ex:orderNo ?no"]
    if customer_name:
        filters.append("?o ex:orderHasCustomer ?c")
        filters.append("?c ex:customerName ?cn")
        filters.append(f'FILTER (CONTAINS(?cn, "{customer_name}"))')
    if status:
        filters.append(f'FILTER (STR(?status) = "{status}")')
    # 注意：故意不直接 SELECT sensitive 字段，让代码后续过滤

    q = prepareQuery(f"""
    PREFIX ex: <http://platform.com/>
    SELECT ?o ?no WHERE {{
        {' . '.join(filters)}
    }} ORDER BY ?no
    """)
    results = list(g.query(q))

    out = []
    for r in results:
        d = r.asdict()
        order = d['o']
        no = d['no']
        # 字段级过滤
        row = {"订单号": no}

        # 订单金额（Internal）
        if can_user_see_property(user, "ex:orderTotalAmount")[0]:
            q_amt = prepareQuery("""
            PREFIX ex: <http://platform.com/>
            SELECT ?amt WHERE { ?o ex:orderTotalAmount ?amt . FILTER (?o = ?order) }
            """)
            for r2 in g.query(q_amt, initBindings={'order': order}):
                row["金额"] = f"¥{float(r2.amt):,.2f}"
        else:
            row["金额"] = "🔒 隐藏"

        # 客户信息（默认 Internal 可见）
        # 客户名 + 邮箱（如果能看）
        q_cname = prepareQuery("""
        PREFIX ex: <http://platform.com/>
        SELECT ?cname WHERE {
            ?o ex:orderHasCustomer ?c .
            ?c ex:customerName ?cname .
            FILTER (?o = ?order)
        }
        """)
        for r2 in g.query(q_cname, initBindings={'order': order}):
            row["客户"] = r2.cname

        if can_user_see_property(user, "ex:customerEmail")[0]:
            q_email = prepareQuery("""
            PREFIX ex: <http://platform.com/>
            SELECT ?email WHERE {
                ?o ex:orderHasCustomer ?c .
                ?c ex:customerEmail ?email .
                FILTER (?o = ?order)
            }
            """)
            emails = [str(r.email) for r in g.query(q_email, initBindings={'order': order})]
            row["客户邮箱"] = emails[0] if emails else "(未填)"
        else:
            row["客户邮箱"] = "🔒 隐藏"

        # 付款金额（Restricted）—— 仅财务 / 审计
        if can_user_see_property(user, "ex:paymentAmount")[0]:
            q_pay = prepareQuery("""
            PREFIX ex: <http://platform.com/>
            SELECT (SUM(?amt) AS ?total) WHERE {
                ?pay ex:paymentForInvoice ?inv ; ex:paymentAmount ?amt .
                ?inv ex:orderHasInvoice ?order .
            }
            """)
            for r2 in g.query(q_pay, initBindings={'order': order}):
                row["付款"] = f"¥{float(r2.total):,.2f}" if r2.total else "—"
        else:
            row["付款"] = "🔒 隐藏"

        out.append(row)
    return out


# ============================================================
# 5. 演示
# ============================================================
def demo_single_user(user):
    """展示一个用户能看什么."""
    print(f"\n{'=' * 70}")
    print(f"  👤 用户: {user['name']}")
    print(f"     角色: {user['role']}  部门: {user['department']}")
    print(f"     密级: {user['clearance']}")
    if "constraints" in user:
        print(f"     约束: {user['constraints']}")
    print(f"{'=' * 70}")

    orders = query_orders_for_user(user, status="Delivered")
    if not orders:
        orders = query_orders_for_user(user)
    if not orders:
        print("  （无订单可见）")
        return

    print(f"  可见订单数: {len(orders)}\n")
    print(f"  {'订单号':<14} {'客户':<12} {'金额':<14} {'客户邮箱':<22} {'付款':<14}")
    print(f"  {'-' * 14} {'-' * 12} {'-' * 14} {'-' * 22} {'-' * 14}")
    for o in orders:
        print(f"  {o.get('订单号', '-'):<14} "
              f"{o.get('客户', '-'):<12} "
              f"{o.get('金额', '-'):<14} "
              f"{o.get('客户邮箱', '-'):<22} "
              f"{o.get('付款', '-'):<14}")


def main():
    print("=" * 70)
    print("  ABAC 权限系统演示（Palantir Foundry Granular Security 风格）")
    print("=" * 70)
    print(f"""
  4 个敏感度等级:
    Public       - 所有人都能看
    Internal     - 内部员工
    Confidential - 经理级 / 特定角色
    Restricted   - 仅财务 / 审计

  字段打标（部分）:
    ex:paymentAmount     → Restricted  (仅财务/审计)
    ex:invoiceAmount     → Confidential (经理级)
    ex:orderTotalAmount  → Internal    (内部员工)
    ex:customerEmail     → Confidential (经理级)
    ex:customerName      → 默认 Internal (所有人都能看)
    ex:productName       → Public
""")

    for user in USERS:
        demo_single_user(user)

    # 演示权限决策对比
    print("\n" + "=" * 70)
    print("  权限决策矩阵：谁能看 Payment")
    print("=" * 70)
    print(f"  {'用户':<25} {'角色':<15} {'能否看 payment':<18}")
    print(f"  {'-' * 25} {'-' * 15} {'-' * 18}")
    for u in USERS:
        ok, reason = can_user_see_property(u, "ex:paymentAmount")
        mark = "✅ 允许" if ok else "❌ 拒绝"
        print(f"  {u['name']:<25} {u['role']:<15} {mark:<18} ({reason})")

    print("\n  权限决策矩阵：谁能看 customerEmail")
    print(f"  {'-' * 25} {'-' * 15} {'-' * 18}")
    for u in USERS:
        ok, reason = can_user_see_property(u, "ex:customerEmail")
        mark = "✅ 允许" if ok else "❌ 拒绝"
        print(f"  {u['name']:<25} {u['role']:<15} {mark:<18} ({reason})")

    # 持久化带 sensitivity 的本体
    out_path = DATA_DIR / "platform-ont-with-security.ttl"
    g.serialize(str(out_path), format="turtle")
    print(f"\n✓ 已保存带 sensitivity 的本体：{out_path}")


if __name__ == "__main__":
    main()
