import ee
import shapefile
import geepy as g


area = g.get_features('../data/sample.shp')

col = g.get_modis("MODIS/006/MOD13A1", "../data/sample.shp", "2017-01-01", "2018-01-01",export=True)

length=len(col.getInfo()['features'])
list = col.toList(length)

#print(area.getInfo())
bands=['NDVI']
region=ee.Feature(area.first()).geometry().bounds().getInfo()['coordinates']

for i in range(length):
    img = ee.Image(list.get(i)).clip(area)
    name = (img.getInfo()['properties']['system:index'])
    task = ee.batch.Export.image.toDrive(img,
                                         region=region,
                                        description=name)

    task.start()
print("submitted task for downloading your request")
