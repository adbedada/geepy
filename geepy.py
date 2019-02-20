import ee
from ee import batch
import shapefile


def read_meta_data(product):
    '''
    check an image product's meta data
    :param product: Name of a single Image or Tile
    :return: meta data
    '''
    ee.Initialize()
    img = ee.Image(product)
    return img.getInfo()


def read_feature_collection(shp):
    '''
    converts shapefile to ee's feature collection
    :param shp:
    :return: feature collection
    '''

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


def read_single_image(product, aoi,start_date, end_date,bands=['B2', 'B3', 'B4']):

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
                pcc=5,
                output='output',
                bands=['B2','B3','B4'],
                export=False):

    '''
    Export or Read meta dat of a landsat product cropped with a shapefile
    :param product: Landsat product type
    :param aoi: area of interest (shapefile)
    :param start_date: date to start from
    :param end_date: last date to check to
    :param pcc: percent_of_cloud_cover
    :param output: name of output file
    :param bands: bands to select (defaulted to RGB of Landsat 8)
    :param export: option to export image
    :return: tiff file exported to gdrive or meta data if exporting is false
    '''
    geometry = read_feature_collection(aoi)
    img = ee.ImageCollection(product)\
        .filterBounds(geometry)\
        .filterDate(start_date, end_date) \

    col = img.filter(ee.Filter.lt('ClOUD_COVER',pcc))

    if export is False:
        return col
    else:
        # mosaic tiles into a single tiff
        mosaic = ee.ImageCollection([
                    col.select(bands)]).mosaic()

        # region to bound the export view to
        region = ee.Feature(geometry.first())\
                            .geometry().bounds()\
                            .getInfo()['coordinates']

        # start exporting as a single tile/image
        task = ee.batch.Export.image.toDrive(mosaic, region=region, description = output)
        task.start()


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
    geometry = read_feature_collection(aoi)
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


