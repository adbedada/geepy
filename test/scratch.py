import ee
import shapefile

def read_feature_collecton(shp):
    # read the shapefile
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


geometry = read_feature_collecton('../data/addis_abeba.shp')

#
img = ee.ImageCollection('COPERNICUS/S2')
col = img.filterDate("2017-01-01", "2018-01-01") \
         .filterBounds(geometry) \
         .median()

bands=['B2','B3', 'B4','B8']

region=ee.Feature(geometry.first()).geometry().bounds().getInfo()['coordinates']
#map.centerObject(fc, 9)
mosaic = ee.ImageCollection([col.select(bands).clip(geometry)]).mosaic()

task = ee.batch.Export.image.toDrive(mosaic,
                                     region=region,
                                     description ="Addis_Abeba")

task.start()
