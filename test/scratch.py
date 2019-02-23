import ee
import shapefile
import geepy as g


area = g.get_features('../data/sample.shp')
#g.get_metadata('MODIS/006/MOD13A1')

col = g.get_modis("MODIS/006/MOD13A1", "../data/sample.shp", "2017-11-01", "2018-01-01",export=False)

length = len(col.getInfo()['features'])
list = col.toList(length)

#print(area.getInfo())
bands=['EVI']
region=ee.Feature(area.first()).geometry().bounds().getInfo()['coordinates']
#print(region)
for i in range(length):
    img = ee.Image(list.get(i)).clip(area)
    timestamp = (img.getInfo()['properties']['system:index'])
    name = (str(bands[0]+"_")+timestamp)

    task = ee.batch.Export.image.toDrive(img,
                                        region=region,
                                        description=name)

    task.start()
print("submitted task for downloading your request")
