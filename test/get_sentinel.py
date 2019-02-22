
import ee
from geepy import geepy

ee.Initialize()

#print meta_data
geepy.get_sentinel('COPERNICUS/S2',
                   '../data/addis_abeba.shp',
                   "2017-01-01", "2018-01-01",
                   output='Addis_test_img',
                   export=True)




