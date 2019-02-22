import ee

ee.Initialize()

def read_meta_data(product):
    '''
    check an image product's meta data
    :param product: Name of a single Image or Tile
    :return: meta data
    '''
    img = ee.Image(product)
    return img.getInfo()
