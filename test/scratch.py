import ee
import shapefile
import geepy as g
import fiona
import numpy as np
import pandas as pd
import json
import random

try:
    import ogr, osr
    from osgeo import ogr
except ImportError:
    raise ImportError('OGR must be installed')

def get_random_point(shp):
    with fiona.open(shp) as src:
        geom = src[0]['geometry']
        geom = json.dumps(geom)
        polygon = ogr.CreateGeometryFromJson(geom)
        # print(polygon)

    env = polygon.GetEnvelope()
    xmin, ymin, xmax, ymax = env[0], env[2], env[1], env[3]
    point = ogr.Geometry(ogr.wkbPoint)
    point.AddPoint(random.uniform(xmin, xmax),
                   random.uniform(ymin, ymax))

    long = point.GetX()
    lat = point.GetY()

    random_point = ee.Geometry.Point([long, lat])
    return random_point


random_spot = get_random_point('../data/sample.shp')

area = g.get_features('../data/sample.shp')
#a = g.get_metadata('MODIS/006/MOD13A1')
#print()
#
col = g.get_chirps("UCSB-CHG/CHIRPS/PENTAD", "../data/sample.shp", "2017-12-01", "2017-12-15")

length = len(col.getInfo()['features'])
list = col.toList(length)

#
# #print(area.getInfo())
bands=['precipitation']
region=ee.Feature(area.first()).geometry().bounds().getInfo()['coordinates']
#print(region)
for i in range(length):
        img = ee.Image(list.get(i)).clip(area)
        #random_pixel = img.clip(random_spot)
        random_sample = img.sample(region=area, scale=5000, numPixels=1)
        #print(random_sample)
        loc = col.getRegion(random_sample, int(5000)).getInfo()
        df = pd.DataFrame.from_records(region[1:len(region)])
        print(df)

        timestamp = (img.getInfo()['properties']['system:index'])
        name = (str(bands[0]+"_")+timestamp)


        task = ee.batch.Export.image.toDrive(img,
                                            region=region,
                                            description=name)

        print("submitted "+name + " for downloading")

        task.start()






