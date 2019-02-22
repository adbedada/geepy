import ee
from .features import read_feature_collection as rfc

def read_single_image(product, aoi,start_date, end_date,bands=['B2', 'B3', 'B4']):

    geometry = rfc(aoi)
    img = ee.ImageCollection(product)\
        .filterBounds(geometry)\
        .filterDate(start_date, end_date) \
        .select(bands)\
        .median() \

    return img