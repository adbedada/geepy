import ee
import shapefile
import fiona

ee.Initialize()


def get_metadata(product):
    '''
    check an image product's meta data
    :param product: Name of a single Image or Tile
    :return: meta data
    '''
    try:
        img = ee.Image(product)
        print(img.getInfo())
    except:
        img = ee.ImageCollection(product)
        print(img.getInfo())


def get_epsg(shp):
    with fiona.open(shp) as src:
        epsg = src.crs['init']
        pos = 5
        epsg_num = epsg[pos:]
    return epsg_num


def get_features(shp):
    '''
    converts shapefile to ee's feature collection
    :param shp:
    :return: feature collection
    '''

    reader = shapefile.Reader(shp)
    fields = reader.fields[1:]
    field_names = [field[0] for field in fields]
    projection = get_epsg(shp)
    wgs84 = ee.Projection('EPSG:4326')
    features = []
    # convert geometry to feature collection
    # transform the shapefile's projection to WGS84
    for sr in reader.shapeRecords():
        atr = dict(zip(field_names, sr.record))
        geom = sr.shape.__geo_interface__
        ee_geometry = ee.Geometry(geom, 'EPSG:' + projection) \
                        .transform(wgs84, 1)
        feat = ee.Feature(ee_geometry, atr)
        features.append(feat)

    return ee.FeatureCollection(features)


def read_single_image(product, aoi,start_date,
                      end_date,bands=['B2', 'B3', 'B4']):

    geometry = get_features(aoi)
    img = ee.ImageCollection(product)\
        .filterBounds(geometry)\
        .filterDate(start_date, end_date) \
        .select(bands)\
        .median() \

    return img


def get_landsat(product, aoi,
                start_date, end_date,
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
    geometry = get_features(aoi)
    img = ee.ImageCollection(product)\
        .filterBounds(geometry)\
        .filterDate(start_date, end_date) \
        .median() # return the median band
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
        task = ee.batch.Export.image.toDrive(mosaic,
                                             region=region,
                                             description = output)
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


def get_sentinel(product, aoi,
                 start_date, end_date,
                 pcc=3,
                 output='output',
                 bands = ['B2', 'B3', 'B4', 'B8'],
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

    geometry = get_features(aoi)
    img = ee.ImageCollection(product) \
            .filterDate(start_date, end_date) \
            .filterBounds(geometry) \
            .map(sentinel_cloud_mask) \
            .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', pcc))

    col = img.median()

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
        task = ee.batch.Export.image.toDrive(mosaic,
                                             region=region,
                                             description=output)
        task.start()


def save_output(col, geometry, band):

    length = len(col.getInfo()['features'])
    img_list = col.toList(length)

    region = ee.Feature(geometry.first()) \
        .geometry().bounds().getInfo()['coordinates']

    for i in range(length):
        img = ee.Image(img_list.get(i)).clip(geometry)
        timestamp = (img.getInfo()['properties']['system:index'])
        name = (str(band[0] + "_") + timestamp)
        task = ee.batch.Export.image.toDrive(img,
                                             region=region,
                                             description=name)

        return task


def get_modis(product, aoi, start_date, end_date,
              band=['NDVI'], export=False):

    geometry = get_features(aoi)
    col = ee.ImageCollection(product) \
        .filterBounds(geometry) \
        .filterDate(start_date, end_date) \
        .select(band)

    if export is False:
        return col

    else:

        length = len(col.getInfo()['features'])
        img_list = col.toList(length)

        region = ee.Feature(geometry.first())\
                    .geometry().bounds().getInfo()['coordinates']

        for i in range(length):
            img = ee.Image(img_list.get(i)).clip(geometry)
            timestamp = (img.getInfo()['properties']['system:index'])
            name = (str(band) + "_" + timestamp)

            task = ee.batch.Export.image.toDrive(img,
                                                 region=region,
                                                 description=name,
                                                 maxPixels=1e13)

            print("submitted "+name+" for downloading")

            task.start()


def get_chirps(product, aoi, start_date,
               end_date, export=False):

    '''
    :param product: CHIRPS (precipitation) daily or pentad(5-days) data
    :param aoi: area of interest
    :param start_date: date to start from
    :param end_date: last date to check to
    :param export: option to export as a tif file
    :return: collection of images or output geotiff
    '''

    band = ['precipitation']
    geometry = get_features(aoi)
    col = ee.ImageCollection(product) \
            .filterBounds(geometry) \
            .filterDate(start_date, end_date) \
            .select(band)

    if export is False:
        return col

    else:
        length = len(col.getInfo()['features'])
        img_list = col.toList(length)

        region = ee.Feature(geometry.first()) \
            .geometry().bounds().getInfo()['coordinates']

        for i in range(length):
            img = ee.Image(img_list.get(i)).clip(geometry)
            timestamp = (img.getInfo()['properties']['system:index'])
            name = (str(band[0] + "_") + timestamp)

            task = ee.batch.Export.image.toDrive(img,
                                                 region=region,
                                                 description=name,
                                                 maxPixels=1e15)

            print("submitted "+name+" for downloading")

            task.start()


def get_terraclimate(product, aoi, start_date, end_date,
              band=['aet'], export=False):

    geometry = get_features(aoi)
    col = ee.ImageCollection(product) \
        .filterBounds(geometry) \
        .filterDate(start_date, end_date) \
        .select(band)

    if export is False:
        return col

    else:

        length = len(col.getInfo()['features'])
        img_list = col.toList(length)

        region = ee.Feature(geometry.first())\
                    .geometry().bounds().getInfo()['coordinates']

        for i in range(length):
            img = ee.Image(img_list.get(i)).clip(geometry)
            timestamp = (img.getInfo()['properties']['system:index'])

            name = (str(band) + "_" + timestamp)

            task = ee.batch.Export.image.toDrive(img,
                                                region=region,
                                                description=name)

            print("submitted "+name+" for downloading")

            task.start()