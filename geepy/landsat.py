import ee
from .features import read_feature_collection as rfc

ee.Initialize()

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
    geometry = rfc(aoi)
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
