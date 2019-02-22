
import ee
from geepy import geepy

ee.Initialize()

#print meta_data of MODIS 16-day product
geepy.get_modis('MODIS/006/MOD13Q1',
                   '../data/addis_abeba.shp',
                   "2017-01-01", "2017-06-01",
                output="addis_modis_ndvi",
                export=False)




