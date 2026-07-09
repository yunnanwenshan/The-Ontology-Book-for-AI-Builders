"""SHACL 校验：故意写错数据，看 SHACL 能否抓到."""
from pyshacl import validate
from rdflib import Graph

shapes = Graph().parse("data/shapes.ttl", format="turtle")
data   = Graph().parse("data/bad-data.ttl", format="turtle")

conforms, report_graph, _ = validate(data, shacl_graph=shapes, inference="rdfs")
print("=== SHACL 校验 ===")
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
