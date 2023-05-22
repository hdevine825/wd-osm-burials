import config
import overpassQueries
import wdQueries
import overpy
import pandas as pd
import shapely
from SPARQLWrapper import SPARQLWrapper, JSON

def extractQID(s):
	start = s.rfind('/')+1
	end = len(s)
	s = s[start:end]
	return s

overpass = overpy.Overpass()

sparql = SPARQLWrapper("https://query.wikidata.org/bigdata/namespace/wdq/sparql", agent = "https://github.com/hdevine825/wd-osm-burials")

sparql.setReturnFormat(JSON)

sparql.setQuery(wdQueries.buriedPeople.format(config.city))

print('Running WD people query')
results = sparql.query().convert()
print('WD people query complete')
wddf = pd.json_normalize(results['results']['bindings'])
#print(wddf.columns)
wddf['personQID'] = wddf.apply(lambda row: extractQID(row['item.value']),axis=1)
wddf['burialPlaceQID'] = wddf.apply(lambda row: extractQID(row['burialPlace.value']),axis=1)
print("Wikidata returned {0} people buried in {1} cemeteries".format(wddf.shape[0],wddf['burialPlace.value'].nunique()))

sparql.setQuery(wdQueries.cemeteries.format(config.city))
print('Running WD cemeteries query')
results = sparql.query().convert()
print('WD cemeteries query complete')
wdcemdf = pd.json_normalize(results['results']['bindings'])
print("Wikidata returned {0} cemeteries".format(wdcemdf.shape[0]))

osmcem = overpass.query(overpassQueries.cemeteries.format(config.city))
print("Cemeteries on OSM: {0} nodes, {1} ways, {2} relations".format(len(osmcem.nodes),len(osmcem.ways),len(osmcem.relations)))

