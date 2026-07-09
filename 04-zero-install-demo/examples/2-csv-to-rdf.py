"""CSV 转 RDF：读 CSV 文件，生成 RDF 三元组."""
import csv
from rdflib import Graph, Literal, Namespace
from rdflib.namespace import RDF

g = Graph()
EX = Namespace("http://example.com/people/")

# 准备测试 CSV
with open("data/people.csv", "w", newline='') as f:
    w = csv.writer(f)
    w.writerow(["name", "email", "company"])
    w.writerow(["Alice", "alice@shop.com", "Apple"])
    w.writerow(["Bob", "bob@shop.com", "Google"])
    w.writerow(["Carol", "carol@shop.com", "Apple"])

# 读 CSV 转 RDF
with open("data/people.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        person = EX[row["name"].replace(" ", "_")]
        g.add((person, RDF.type, EX.Person))
        g.add((person, EX.name, Literal(row["name"])))
        g.add((person, EX.email, Literal(row["email"])))
        g.add((person, EX.company, Literal(row["company"])))

print("=== CSV 转 RDF ===")
print(g.serialize(format="turtle"))
print(f"\n✅ 共生成 {len(g)} 条三元组")
