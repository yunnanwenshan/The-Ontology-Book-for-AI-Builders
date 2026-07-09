"""商品本体: 6 个常见查询（电商运营/采购场景）."""
from rdflib import Graph
from rdflib.plugins.sparql import prepareQuery
from pyshacl import validate

ont  = Graph().parse("data/product-ont.ttl",     format="turtle")
data = Graph().parse("data/product-data.ttl",    format="turtle")
shapes = Graph().parse("data/product-shapes.ttl", format="turtle")
g = ont + data

conforms, _, _ = validate(g, shacl_graph=shapes)
print(f"数据校验：{'✅ 通过' if conforms else '❌ 失败'}\n")

# Q1: 总库存金额
q1 = prepareQuery("""
PREFIX ex: <http://shop.com/>
SELECT ?skuName ?qty ?p WHERE {
    ?inv a ex:Inventory ;
         ex:inventoryOf ?sku ;
         ex:quantity ?qty .
    ?pr a ex:PriceList ;
         ex:priceOf ?sku ;
         ex:priceType "Retail" ;
         ex:price ?p .
    ?sku ex:skuName ?skuName .
}
""")
print("Q1: 总库存金额（按零售价）")
total = 0
for r in g.query(q1):
    total += int(r.qty) * float(r.p)
print(f"  ¥{total:,.2f}")
print()

# Q2: 低于安全库存的 SKU（预警）
q2 = prepareQuery("""
PREFIX ex: <http://shop.com/>
SELECT ?skuName ?warehouse ?qty ?safety WHERE {
    ?inv a ex:Inventory ;
         ex:inventoryOf ?sku ;
         ex:storedAt ?wh ;
         ex:quantity ?qty ;
         ex:safetyStock ?safety .
    ?sku ex:skuName ?skuName .
    ?wh ex:warehouseName ?warehouse .
    FILTER (?qty < ?safety)
} ORDER BY ?qty
""")
print("Q2: ⚠️ 库存预警（低于安全库存）")
results = list(g.query(q2))
if results:
    for r in results:
        print(f"  {r.skuName}  @ {r.warehouse}  现 {r.qty} / 安全 {r.safety}")
else:
    print("  （无）")
print()

# Q3: 各仓库库存数量
q3 = prepareQuery("""
PREFIX ex: <http://shop.com/>
SELECT ?warehouse (COUNT(?sku) AS ?skus) (SUM(?qty) AS ?total_qty) WHERE {
    ?inv a ex:Inventory ; ex:storedAt ?wh ; ex:quantity ?qty ; ex:inventoryOf ?sku .
    ?wh ex:warehouseName ?warehouse .
} GROUP BY ?wh ?warehouse
ORDER BY DESC(?total_qty)
""")
print("Q3: 各仓库库存")
for r in g.query(q3):
    print(f"  {r.warehouse}  {r.skus} 个 SKU  /  共 {r.total_qty} 件")
print()

# Q4: 同一 SPU 下的 SKU
q4 = prepareQuery("""
PREFIX ex: <http://shop.com/>
SELECT ?spuName ?skuName ?spec WHERE {
    ?sku a ex:SKU ;
         ex:skuOf ex:spu-iphone15 ;
         ex:skuName ?skuName ;
         ex:skuSpec ?spec .
}
""")
print("Q4: iPhone 15 下的所有 SKU")
for r in g.query(q4):
    print(f"  {r.skuName}  ({r.spec})")
print()

# Q5: 当前在售的促销价
q5 = prepareQuery("""
PREFIX ex: <http://shop.com/>
SELECT ?skuName ?price ?from ?to WHERE {
    ?p a ex:PriceList ; ex:priceType "Promotional" ;
       ex:priceOf ?sku ; ex:price ?price ;
       ex:priceFrom ?from ; ex:priceTo ?to .
    ?sku ex:skuName ?skuName .
    FILTER (?from <= "2026-07-09"^^xsd:date && ?to >= "2026-07-09"^^xsd:date)
}
""")
print("Q5: 当前有效的促销价")
results = list(g.query(q5))
if results:
    for r in results:
        d = r.asdict()
        sku_name = d['skuName']
        price = d['price']
        date_from = d['from']
        date_to = d['to']
        print(f"  {sku_name}  ¥{price}  ({date_from} ~ {date_to})")
else:
    print("  （无）")
print()

# Q6: 品牌 SKU 分布
q6 = prepareQuery("""
PREFIX ex: <http://shop.com/>
SELECT ?brand (COUNT(DISTINCT ?spu) AS ?spus) (COUNT(DISTINCT ?sku) AS ?skus) (SUM(?qty) AS ?total) WHERE {
    ?sku a ex:SKU ; ex:skuOf ?spu .
    ?spu ex:brand ?b .
    ?b ex:brandName ?brand .
    ?inv ex:inventoryOf ?sku ; ex:quantity ?qty .
} GROUP BY ?b ?brand
ORDER BY DESC(?total)
""")
print("Q6: 品牌 SKU 分布")
for r in g.query(q6):
    print(f"  {r.brand}  {r.spus} SPU / {r.skus} SKU  /  库存 {r.total}")
