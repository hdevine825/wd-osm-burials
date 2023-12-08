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
	
def osmToDF(result, tagArray):
	columns = tagArray.copy()
	columns.insert(0, 'id')
	columns.insert(1, 'geom')
	df = pd.DataFrame(columns=columns)
	for i in result.nodes:
		rowValues = []
		rowValues.append('n'+str(i.id))
		rowValues.append("POINT ({0} {1})".format(i.lon, i.lat))
		for t in tagArray:
			rowValues.append(i.tags.get(t))
		rvdf = pd.DataFrame(rowValues).T
		rvdf.set_axis(columns,axis=1,inplace=True)
		df = pd.concat([df,rvdf])
	for i in result.ways:
		rowValues = []
		rowValues.append('w'+str(i.id))
		rowValues.append("POINT ({0} {1})".format(i.center_lon, i.center_lat))
		for t in tagArray:
			rowValues.append(i.tags.get(t))
		rvdf = pd.DataFrame(rowValues).T
		rvdf.set_axis(columns,axis=1,inplace=True)
		df = pd.concat([df,rvdf])
	for i in result.relations:
		rowValues = []
		rowValues.append('r'+str(i.id))
		rowValues.append("POINT ({0} {1})".format(i.center_lon, i.center_lat))
		for t in tagArray:
			rowValues.append(i.tags.get(t))
		rvdf = pd.DataFrame(rowValues).T
		rvdf.set_axis(columns,axis=1,inplace=True)
		df = pd.concat([df,rvdf])
	return df
		
		
		

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
print("Wikidata returned {0} people buried in {1} places".format(wddf.shape[0],wddf['burialPlace.value'].nunique()))
sparql.setQuery(wdQueries.cemeteries.format(config.city))
print('Running WD cemeteries query')
results = sparql.query().convert()
print('WD cemeteries query complete')
wdcemdf = pd.json_normalize(results['results']['bindings'])
print("Wikidata returned {0} cemeteries".format(wdcemdf.shape[0]))
wdcemdf['cemeteryQID'] = wdcemdf.apply(lambda row: extractQID(row['item.value']),axis=1)
osmcem = overpass.query(overpassQueries.cemeteries.format(config.city))
print("Cemeteries on OSM: {0} nodes, {1} ways, {2} relations".format(len(osmcem.nodes),len(osmcem.ways),len(osmcem.relations)))
osmcemdf = osmToDF(osmcem, ['name','wikidata'])
print(osmcemdf.head())
mergedCemdf = pd.merge(left=wdcemdf,right=osmcemdf,left_on='cemeteryQID',right_on='wikidata')
print(mergedCemdf.query("wikidata.isnull()", engine='python'))

for index, row in mergedCemdf.iterrows():
	print("Checking {0}:".format(row['itemLabel.value']))
	print("Wikidata Coordinates: {0} OSM Coordinates: {1}".format(row['coordLocation.value'],row['geom']))
	burialsdf = wddf.query("burialPlaceQID=='{0}'".format(row["cemeteryQID"]))
	for pindex, prow in burialsdf.iterrows():
		print(prow["itemLabel.value"])
			


