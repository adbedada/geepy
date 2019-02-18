import ee
from ee import batch
import fiona

def read_single_image(product):
    ee.Initialize()
    img = ee.Image(product)
    return img.getInfo()


def read_feature(shapefile):
    with fiona.open(shapefile) as src:
        feature_col= (src['geometry'])
        return feature_col


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
