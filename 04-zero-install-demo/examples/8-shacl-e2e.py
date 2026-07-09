"""端到端 SHACL 校验: 故意写错数据，看能抓到几条."""
from pyshacl import validate
from rdflib import Graph

shapes = Graph().parse("data/shop-shapes.ttl", format="turtle")
data   = Graph().parse("data/shop-bad.ttl",   format="turtle")

conforms, report_graph, _ = validate(data, shacl_graph=shapes, inference="rdfs")
print("=== SHACL 端到端校验 ===")
print(f"通过？ {conforms}")

if not conforms:
    import re
    report_str = report_graph.serialize(format="turtle")
    matches = re.findall(
        r'sh:focusNode\s+(\S+).*?sh:resultMessage\s+"([^"]+)"',
        report_str, re.DOTALL
    )
    print(f"违规数: {len(matches)}")
    for i, (node, msg) in enumerate(matches, 1):
        node_short = node.split("#")[-1] if "#" in node else node
        print(f"  违规 {i}: {node_short}")
        print(f"    原因: {msg}")
