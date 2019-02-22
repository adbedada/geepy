import click
import ee
import shapefile

ee.Initialize()


@click.group(chain=True)
def cli():

    " Extract Google Earth Engine products with a shapefile "


@click.command('check_metadata')
@click.argument('product')
def read_meta_data(product):

    ''' - check metadata of an image product '''

    img = ee.Image(product)
    print (img.getInfo())


@cli.command('check_features')
@click.argument('product')
def read_feature_collection(shp):
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
