import config
import overpy
import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON

def extractQID(s):
	start = s.rfind('/')+1
	end = len(s)
	s = s[start:end]
	return s

sparql = SPARQLWrapper("https://query.wikidata.org/bigdata/namespace/wdq/sparql", agent = "https://github.com/hdevine825/wd-osm-burials")

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
  ?burialPlace wdt:P131/wdt:P131* wd:{0}. #place of burial in config city
  OPTIONAL{{?item p:P119 [ ps:P119 ?placeburial; pq:P625 ?location ].}} #return the coordinate location qualifier of place of burial if it exists
  ?sitelink schema:about ?item. #get site links
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }} #default label thing
  Optional{{?item schema:description"en".}} #get English description
}}
GROUP BY ?item ?itemLabel ?location ?burialPlace ?burialPlaceLabel ?itemDescription #group items, if other field are to be shown they need to be added to this
ORDER BY DESC( COUNT( ?sitelink ) ) #sort by number of sitelinks for each item
""".format(config.city))

print('Running WD query')
results = sparql.query().convert()
print('WD query complete')
wddf = pd.json_normalize(results['results']['bindings'])
print("Wikidata returned {0} results".format(wddf.shape[0]))
#print(wddf.columns)
wddf['personQID'] = wddf.apply(lambda row: extractQID(row['item.value']),axis=1)
wddf['burialPlaceQID'] = wddf.apply(lambda row: extractQID(row['burialPlace.value']),axis=1)
wdcemdf = wddf.get(['burialPlaceQID','burialPlaceLabel.value'])
wdcemdf = wdcemdf.drop_duplicates()
print("Found {0} unique cemeteries in results from Wikidata".format(wdcemdf.shape[0]))
print(wdcemdf)

