'''
Command line interface for geepy allows users to download products from terminal

'''
import click
import geepy


@click.command()
@click.argument('product')
def check_metadata(product):
    '''
    check an image product's meta data
    '''

    geepy.get_metadata(product)


@click.command()
@click.argument('shp')
def check_features(shp):
    """
    check shapefile readiness for processing
    """
    features = geepy.get_features(shp)
    print(features)



@click.command()
@click.argument('product')
@click.argument('aoi')
@click.argument('start_date')
@click.argument('end_date')
@click.argument('band')
def download_modis(product, aoi, start_date, end_date,
              band='NDVI', export=True):

    """
    download modis products in area of interest
    """
    geepy.get_modis(product, aoi, start_date, end_date,
              band=band, export=export)


@click.command()
@click.argument('product')
@click.argument('aoi')
@click.argument('start_date')
@click.argument('end_date')
@click.argument('pcc')
@click.argument('output')
def download_sentinel(product, aoi,
                      start_date, end_date,
                      pcc=3, output='output',
                       export=True):
    '''
    download sentinel imagery by area of interest
    '''

    geepy.get_sentinel(product, aoi, start_date, end_date,
                              pcc, output, export=export)




@click.command()
@click.argument('product')
@click.argument('aoi')
@click.argument('start_date')
@click.argument('end_date')
def download_chirps(product, aoi,start_date,
                    end_date, export=True):
    '''
    download chrips imagery by area of interest
    '''

    geepy.get_chirps(product, aoi, start_date,
                     end_date, export=export)


@click.command()
@click.argument('product')
@click.argument('aoi')
@click.argument('start_date')
@click.argument('end_date')
@click.argument('band')
def download_terraclimate_data(product, aoi, start_date, end_date,
              band=['aet'], export=True):
    geepy.get_terraclimate(product, aoi, start_date, end_date,
              band=band, export=export)


@click.group(chain=True)
def commands():
    """
    Access Google Earth Engine Products by Area of Interest
    """


commands.add_command(check_features)
commands.add_command(check_metadata)
commands.add_command(download_modis)
commands.add_command(download_chirps)
commands.add_command(download_sentinel)
commands.add_command(download_terraclimate_data)