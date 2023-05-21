import config
import overpy
import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("https://query.wikidata.org/bigdata/namespace/wdq/sparql")

sparql.setReturnFormat(JSON)

sparql.setQuery("""SELECT 
  ?item 
  ?itemLabel
  ?itemDescription
  ?burialPlace
  ?burialPlaceLabel
  ?location
  ( COUNT( ?sitelink ) AS ?sitelink_count ) 
WHERE 
{{
  ?item wdt:P31 wd:Q5. #instance of human
  ?item wdt:P119 ?burialPlace. #place of burial
  ?burialPlace wdt:P131 wd:{0}. #place of burial in Brooklyn
  OPTIONAL{{?item p:P119 [ ps:P119 ?placeburial; pq:P625 ?location ].}} #return the coordinate location qualifier of place of burial if it exists
  ?sitelink schema:about ?item. #get site links
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }} #default label thing
  Optional{{?item schema:description"en".}} #get English description
}}
GROUP BY ?item ?itemLabel ?location ?burialPlace ?burialPlaceLabel ?itemDescription #group items, if other field are to be shown they need to be added to this
#HAVING ( COUNT( ?sitelink ) > 0 ) #only show if there is at least 1 sitelink
ORDER BY DESC( COUNT( ?sitelink ) ) #sort by number of sitelinks for each item
""".format(config.city))

print('Running query')
results = sparql.query().convert()
print('query complete')
results_df = pd.json_normalize(results['results']['bindings'])
print(results_df.head())

