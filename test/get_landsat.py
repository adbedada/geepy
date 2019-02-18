
import ee
import geepy
ee.Initialize()

#print meta_data
sample = geepy.get_landsat('LANDSAT/LC8_L1T_TOA',
                           '../data/tza_dar_es_salaam.shp',
                           "2013-01-01", "2018-01-01",
                           bands=['B4','B3','B2'],
                    export=False)

print(sample.getInfo())

