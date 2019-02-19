
import ee
import geepy
ee.Initialize()

#print meta_data
geepy.get_sentinel('COPERNICUS/S2',
                           '../data/tza_dar_es_salaam.shp',
                           "2017-01-01", "2018-01-01",
                           bands = ['B2','B3','B4','B8'],
                    export=True)




