"""查 Wikidata 真实数据：诺兰导演的电影 Top 5."""
from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
sparql.setReturnFormat(JSON)

# 查诺兰的电影
sparql.setQuery("""
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>

SELECT ?film ?filmLabel ?date WHERE {
  ?film wdt:P57 wd:Q25191 .
  ?film wdt:P577 ?date .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en,zh" . }
}
ORDER BY DESC(?date)
LIMIT 5
""")

results = sparql.query().convert()
print("=== 诺兰电影 Top 5 ===")
for r in results["results"]["bindings"]:
    print(f"  {r['date']['value'][:10]}  {r['filmLabel']['value']}")
