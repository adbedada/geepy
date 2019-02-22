import ee
from .features import read_feature_collection as rfc

ee.Initialize()

##### needs work #####

def get_modis(product, aoi, start_date, end_date,
              band='NDVI', output='output', export=False):

    geometry = rfc(aoi)
    col = ee.ImageCollection(product) \
        .filterBounds(geometry) \
        .filterDate(start_date, end_date) \
        .select(band)

    if export is False:
        return col

    else:
        list = col.toList(col.size())
        for i in len(list):
            #needs work
            image = ee.Image(list.get(i))

            mosaic = image.mosaic()

        # region to bound the export view to
            region = ee.Feature(geometry.first()) \
                .geometry().bounds() \
                .getInfo()['coordinates']

        # start exporting as a single tile/image
            task = ee.batch.Export.image.toDrive(mosaic, region=region, description=output)
            task.start()
