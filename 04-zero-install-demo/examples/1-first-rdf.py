"""你的第一个 RDF：写 4 条三元组，输出 Turtle 格式."""
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS

g = Graph()
EX = Namespace("http://example.com/")

# 加 4 条三元组
g.add((EX.Alice, RDF.type, EX.Person))
g.add((EX.Alice, EX.age, Literal(30)))
g.add((EX.Alice, EX.knows, EX.Bob))
g.add((EX.Bob, RDF.type, EX.Person))

print("=== 你的第一个 RDF ===")
for s, p, o in g:
    print(f"  {s} -- {p} --> {o}")
print(f"\n共 {len(g)} 条三元组")
print("\n=== Turtle 输出 ===")
print(g.serialize(format="turtle"))
