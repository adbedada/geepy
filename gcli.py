import click
import ee
import shapefile


@click.command()
@click.argument('product')
def check_metadata(product):
    ee.Initialize()
    ''' - check metadata of an image product '''

    img = ee.Image(product)
    print(img.getInfo())


@click.command()
@click.argument('shp')
def check_features(shp):
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


@click.group(chain=True)
def commands():
    pass


commands.add_command(check_features)
commands.add_command(check_metadata)
commands.add_command(copy)


