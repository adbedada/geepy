import ee
from ee import batch
import fiona

def read_meta_data(product):
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


def sentinel_cloud_mask(image):
    qa = image.select('QA60')
    cloudBitMask = ee.Number(2).pow(10).int()
    cirrusBitMask = ee.Number(2).pow(11).int()
    cldmask = qa.bitwiseAnd(cloudBitMask).eq(0)
    mask= cldmask.bitwiseAnd(cirrusBitMask).eq(0)
    return image.updateMask(mask).divide(10000)\
                .copyProperties(image, ["system:time_start"])


def get_sentinel(product, aoi,start_date, end_date,
                percent_of_cloud_cover=3,
                bands=['B2','B3','B4','B8'],
                export=False):
    geometry = read_feature(aoi)
    col = ee.ImageCollection(product) \
        .filterBounds(geometry) \
        .filterDate(start_date, end_date) \
        .map(sentinel_cloud_mask) \
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', percent_of_cloud_cover))

    mosaic = ee.ImageCollection([col.select(bands)]).mosaic()

    if export is False:
        return mosaic
    else:
        #mosaic_tiff =img.mosaic()

        task_config = {
            'description': 'imageToDriveExample',
            'scale': 30,
             'crs': "EPSG:4326",
        }
        task = batch.Export.image.toDrive(mosaic,
                                          '00_exported_image',
                                          task_config)



        task.start()
        print("Completed exporting Tiff To Google Drive :-)")
