import ee
import shapefile
import geepy as g


area = g.get_features('../data/sample.shp')
#a = g.get_metadata('MODIS/006/MOD13A1')
#print()
#
col = g.get_chirps("UCSB-CHG/CHIRPS/PENTAD", "../data/sample.shp", "2017-12-01", "2018-01-01")
#
length = len(col.getInfo()['features'])
list = col.toList(length)

#
# #print(area.getInfo())
bands=['precipitation']
region=ee.Feature(area.first()).geometry().bounds().getInfo()['coordinates']
#print(region)
for i in range(length):
    img = ee.Image(list.get(i)).clip(area)
    timestamp = (img.getInfo()['properties']['system:index'])
    name = (str(bands[0]+"_")+timestamp)

#
    task = ee.batch.Export.image.toDrive(img,
                                        region=region,
                                        description=name)

    print("submitted "+name + " for downloading")

    task.start()
