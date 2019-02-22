
import ee
from geepy import geepy

ee.Initialize()


#print meta_data
geepy.get_landsat('LANDSAT/LC08/C01/T1_SR',
                           '../data/aa_sample_data.shp',
                           "2017-01-01", "2018-01-01",
                  output="aa_test",
                  bands=['B2', 'B3', 'B4'],
                  export=True)

