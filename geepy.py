import ee
from ee import batch
import shapefile


def read_meta_data(product):
    ee.Initialize()
    img = ee.Image(product)
    return img.getInfo()


def read_feature_collection(shp):
    '''convert shapefile to feature collection'''

    reader = shapefile.Reader(shp)
    fields = reader.fields[1:]
    field_names = [field[0] for field in fields]

    features = []
    for sr in reader.shapeRecords():
        atr = dict(zip(field_names, sr.record))
        geom = sr.shape.__geo_interface__
        ee_geometry = ee.Geometry(geom)
        feat = ee.Feature(ee_geometry, atr)
        features.append(feat)

    return ee.FeatureCollection(features)


def read_single_image(product, aoi,start_date, end_date):
    bands=['B2', 'B3', 'B4']
    geometry = read_feature_collection(aoi)
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
                name_of_output_file='output',
                bands=['B2','B3','B4'],
                export=False):
    geometry = read_feature_collection(aoi)
    img = ee.ImageCollection(product)\
        .filterBounds(geometry)\
        .filterDate(start_date, end_date) \

    col = img.filter(ee.Filter.lt('ClOUD_COVER',percent_of_cloud_cover))

    if export is False:
        return col
    else:
        mosaic = ee.ImageCollection([
                     col.select(bands).clip(geometry),
                     ]).mosaic()

        task = ee.batch.Export.image(mosaic, description = name_of_output_file)
        task.start()



def sentinel_cloud_mask(image):
    qa = image.select('QA60')
    cloudBitMask = ee.Number(2).pow(10).int()
    cirrusBitMask = ee.Number(2).pow(11).int()
    cldmask = qa.bitwiseAnd(cloudBitMask).eq(0)
    mask= cldmask.bitwiseAnd(cirrusBitMask).eq(0)
    return image.updateMask(mask).divide(10000)\
                .copyProperties(image, ["system:time_start"])


def get_sentinel(product, aoi, start_date, end_date,
                percent_of_cloud_cover=3,
                name_of_output_file='output',
                bands=['B2','B3','B4','B8'],
                export=False):
    geometry = read_feature_collection(aoi)
    img = ee.ImageCollection(product) \
        .filterBounds(geometry) \
        .filterDate(start_date, end_date) \
        .map(sentinel_cloud_mask) \

    col = img.filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', percent_of_cloud_cover))

    if export is False:
        return col
    else:
        mosaic = ee.ImageCollection([
            col.select(bands).clip(geometry),
        ]).mosaic()

        task = ee.batch.Export.image(mosaic, description=name_of_output_file)

        task.start()
        print("Completed exporting Tiff To Google Drive. ")

