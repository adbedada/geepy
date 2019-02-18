import ee
from ee import batch
import geopandas as gpd
import fiona
import pprint
import os



def read_single_image(product):
    ee.Initialize()
    img = ee.Image(product)
    return img.getInfo()

#print(read_single_image('srtm90_v4'))


def read_feature(shapefile):
    with fiona.open(shapefile) as src:
        feature_col= (src['geometry'])
        return feature_col

    #shp = gpd.GeoDataFrame.from_file(shapefile)
    #shp_cols = shp.drop(['geometry'],axis=1)
    #return shp_cols

#read_features('../sample_data/tza_dar_es_salaam.shp')

# def get_sentinel(product, aoi,start_date="2017-01-01"
#                   , end_date="2018-03-31", bands=['B2', 'B3', 'B4', 'B8']):
#     area = read_features(aoi)
#     col = ee.ImageCollection(product)\
#             .filterBounds(area)\
#             .select(bands)\
#             .filterDate(start_date, end_date)
#     return col


def read_single_image(product, aoi,start_date, end_date):
    bands=['B2', 'B3', 'B4']
    geometry = read_feature(aoi)
    img = ee.ImageCollection(product)\
        .filterBounds(geometry)\
        .filterDate(start_date, end_date) \
        .select(bands)\
        .median() \

    return img

def convertBit(self):
    return self.multiply(512).uint8()

def get_landsat(product, aoi,start_date, end_date,
                percent_of_cloud_cover=5,
                bands=['B2','B3','B4'],
                export=False):
    geometry = read_feature(aoi)
    col = ee.ImageCollection(product)\
        .filterBounds(geometry)\
        .filterDate(start_date, end_date) \
        .select(bands)
    img = col.filter(ee.Filter.lt('ClOUD_COVER',percent_of_cloud_cover))

    if export is False:
        return img
    else:
        #mosaic_tiff =img.mosaic()

        task_config = {
            'description': 'imageToDriveExample',
            'scale': 30,
             'crs': "EPSG:4326",
        }
        task = batch.Export.image.toDrive(img,
                                          '_exported_image',
                                          task_config)


        task.start()
        print("Completed exporting Tiff To Google Drive :-)")

if __name__== "__main__":
    ee.Initialize()
    #m1= read_features('../sample_data/tza_dar_es_salaam.shp')
    #print(m1)
    get_landsat('LANDSAT/LC8_L1T_TOA',
                           '../sample_data/tza_dar_es_salaam.shp',
                           "2013-01-01", "2018-01-01",
                           bands=['B4','B3','B2'],
                     export=True)

