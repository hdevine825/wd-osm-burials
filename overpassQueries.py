cemeteries = """
area[wikidata={0}]->.searchArea;
(
  nwr[landuse=cemetery](area.searchArea);
  nwr[amenity=graveyard](area.searchArea);
)->.cemeteries;
.cemeteries out center;"""
