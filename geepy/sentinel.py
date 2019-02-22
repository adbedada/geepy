import ee
from .features import read_feature_collection as rfc


def sentinel_cloud_mask(image):
    '''
    Cloud mask for Sentinel-2 Imagery
    :param image: sentinel -2
    :return: cloud mask
    '''

    qa = image.select('QA60')
    cloudbitmask = ee.Number(2).pow(10).int()
    cirrusbitmask = ee.Number(2).pow(11).int()
    cldmask = qa.bitwiseAnd(cloudbitmask).eq(0)
    mask = cldmask.bitwiseAnd(cirrusbitmask).eq(0)
    return image.updateMask(mask).divide(10000)\
                .copyProperties(image, ["system:time_start"])


def get_sentinel(product, aoi, start_date, end_date,
                pcc=3,
                output='output',
                bands=['B2','B3','B4','B8'],
                export=False):
    '''

    :param product: sentinel imagery product name
    :param aoi: area of interest as a shapefile
    :param start_date: date to start from
    :param end_date: last date to check to
    :param pcc: percent_of_cloud_cover
    :param output: name of output file
    :param bands: bands to select (defaulted to bands with 10 meter resolution)
    :param export: option to export image
    :return: tiff file exported to gdrive or meta data if exporting is false
    '''
    geometry = rfc(aoi)
    img = ee.ImageCollection(product) \
        .filterBounds(geometry) \
        .filterDate(start_date, end_date) \
        .map(sentinel_cloud_mask) \

    col = img.filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', pcc))

    if export is False:
        return col
    else:
        # mosaic tiles into a single tiff
        mosaic = ee.ImageCollection([
            col.select(bands)]).mosaic()

        # region to bound the export view to
        region = ee.Feature(geometry.first()) \
            .geometry().bounds() \
            .getInfo()['coordinates']

        # start exporting as a single tile/image
        task = ee.batch.Export.image.toDrive(mosaic, region=region, description=output)
        task.start()
