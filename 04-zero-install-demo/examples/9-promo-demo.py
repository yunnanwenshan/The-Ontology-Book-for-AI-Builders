"""完整促销 demo: 本体 + SHACL + SPARQL 全跑一遍."""
from rdflib import Graph
from rdflib.plugins.sparql import prepareQuery
from pyshacl import validate

# 1. 加载
ont  = Graph().parse("data/promo-ont.ttl",    format="turtle")
data = Graph().parse("data/promo-data.ttl",   format="turtle")
shapes = Graph().parse("data/promo-shapes.ttl", format="turtle")
all_g = ont + data
print(f"[加载] 本体 {len(ont)} 条，数据 {len(data)} 条，合计 {len(all_g)} 条")

# 2. SHACL 校验
conforms, _, _ = validate(all_g, shacl_graph=shapes, inference="rdfs")
print(f"[校验] SHACL: {'✅ 通过' if conforms else '❌ 失败'}")

# 3. 业务问题 1: iPhone 参加了哪些促销
q1 = prepareQuery("""
PREFIX ex: <http://shop.com/>
SELECT ?promo WHERE {
    ex:iphone-15 ex:hasPromotion ?promo .
}
""")
print("\n[问题1] iPhone 15 参加了哪些促销？")
for row in all_g.query(q1):
    print(f"  → {row.promo.split('/')[-1]}")

# 4. 业务问题 2: 折扣规则详情
q2 = prepareQuery("""
PREFIX ex: <http://shop.com/>
SELECT ?min ?off WHERE {
    ex:promo-001 ex:discountRule ?disc .
    ?disc ex:minAmount ?min ;
           ex:discountAmt ?off .
}
""")
print("\n[问题2] promo-001 的折扣规则？")
for row in all_g.query(q2):
    print(f"  → 满 {row.min} 减 {row.off}")

# 5. 模拟"自然语言"问答
def ask(question: str) -> str:
    """简单意图识别 → SPARQL 模板."""
    if "参加了" in question and "促销" in question:
        sparql = """
        PREFIX ex: <http://shop.com/>
        SELECT ?promo WHERE {
            ?p a ex:Product ; ex:hasPromotion ?promo .
        }
        """
        results = list(all_g.query(sparql))
        return f"共 {len(results)} 个商品参加促销"

    if "满" in question and "减" in question:
        sparql = """
        PREFIX ex: <http://shop.com/>
        SELECT ?promo ?min ?off WHERE {
            ?promo ex:discountRule ?disc .
            ?disc ex:minAmount ?min ;
                   ex:discountAmt ?off .
        }
        """
        for r in all_g.query(sparql):
            return f"{r.promo.split('/')[-1]}: 满 {r.min} 减 {r.off}"

    return "我不知道怎么答。试试 'iPhone 参加了什么促销' 或 '满 200 减 50 的规则'"

print(f"\n[问答] 'iPhone 参加了什么促销？'")
print(f"  → {ask('iPhone 参加了什么促销')}")
print(f"\n[问答] '满 200 减 50 的规则是什么？'")
print(f"  → {ask('满 200 减 50 的规则是什么？')}")

print()
print("=" * 50)
print("  ✅ 完整 demo 跑通")
print("=" * 50)
