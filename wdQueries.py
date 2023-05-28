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
  ?burialPlace wdt:P131+ wd:{0}. #place of burial in config city
  OPTIONAL{{?item p:P119 [ ps:P119 ?placeburial; pq:P625 ?location ].}} #return the coordinate location qualifier of place of burial if it exists
  ?sitelink schema:about ?item. #get site links
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }} #default label thing
  Optional{{?item schema:description"en".}} #get English description
}}
GROUP BY ?item ?itemLabel ?location ?burialPlace ?burialPlaceLabel ?itemDescription ?burialPlaceCoords #group items, if other field are to be shown they need to be added to this
ORDER BY DESC( COUNT( ?sitelink ) ) #sort by number of sitelinks for each item
"""

cemeteries = """SELECT DISTINCT ?item ?itemLabel ?coordLocation WHERE {{
  ?item wdt:P131+ wd:{0}. #located in config city or area in config city
  ?item (wdt:P31|wdt:P31/wdt:P279|wdt:P31/wdt:P279/wdt:P279) wd:Q39614. #instance of cemetery, only goes 2 layers into subclasses to limit timeout issues
  OPTIONAL{{?item wdt:P625 ?coordLocation.}}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
}}"""
