import click
import ee
import shapefile
import geepy

@click.command()
@click.argument('product')
def check_metadata(product):
    ''' - check metadata of an image or image collection'''
    ee.Initialize()
    img = ee.Image(product)
    print(img.getInfo())


@click.command()
@click.argument('shp')
def check_features(shp):
    ''' - check shapefile readiness for processing '''
    ee.Initialize()
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

    print(ee.FeatureCollection(features))


@click.command()
@click.argument('input', type=click.File('rb'), nargs=-1)
@click.argument('output', type=click.File('wb'))
def copy(input, output):

    for f in input:
        while True:
            chunk = f.read(1024)
            if not chunk:
                break
            output.write(chunk)
            output.flush


@click.command()
@click.argument('product')
@click.argument('aoi')
@click.argument('start_date')
@click.argument('end_date')
@click.argument('band')
def download_modis(product, aoi, start_date, end_date,
              band='NDVI', export=True):
    ''' - download modis products in area of interest'''

    geometry = geepy.get_features(aoi)
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
            name = (img.getInfo()['properties']['system:index'])
            task = ee.batch.Export.image.toDrive(img,
                                                 region=region,
                                                 description=name)

            task.start()
        print("submitted task for downloading your request")


@click.group(chain=True)
def commands():
    """
    Access Google Earth Engine Products by Area of Interest
    """
commands.add_command(check_features)
commands.add_command(check_metadata)
commands.add_command(download_modis)


