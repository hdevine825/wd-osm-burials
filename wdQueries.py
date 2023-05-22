buriedPeople = """SELECT 
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
GROUP BY ?item ?itemLabel ?location ?burialPlace ?burialPlaceLabel ?itemDescription ?burialPlaceCoords #group items, if other field are to be shown they need to be added to this
ORDER BY DESC( COUNT( ?sitelink ) ) #sort by number of sitelinks for each item
"""

cemeteries = """SELECT DISTINCT ?item ?itemLabel ?coordLocation WHERE {{
  ?item wdt:P31 wd:Q39614. #instance of cemetery
  ?item wdt:P131+ wd:{0}. #located in brooklyn or area in brooklyn
  ?item wdt:P625 ?coordLocation.
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE]". }}
}}"""
