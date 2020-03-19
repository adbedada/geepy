import ee
import shapefile
import fiona
import os

ee.Initialize()


def get_metadata(product):
    '''
    check an image product's meta data
    :param product: Name of a single Image or Tile
    :return: meta data
    '''
    try:
        img = ee.Image(product)
        print(img.getInfo())
    except:
        img = ee.ImageCollection(product)
        print(img.getInfo())


def get_epsg(shp):
    with fiona.open(shp) as src:
        epsg = src.crs['init']
        pos = 5
        epsg_num = epsg[pos:]
    return epsg_num

      
def get_bbox(shp):
    '''
    gets bounding box of shape
    :param shp:
    :return: geometry object with bounding box
    '''
    reader = shapefile.Reader(shp).bbox
    bb = ee.Geometry.Rectangle(reader )
    bb = ee.Algorithms.ProjectionTransform(bb)
    return  bb

def get_features(shp):
    '''
    converts shapefile to ee's feature collection
    :param shp:
    :return: feature collection
    '''

    reader = shapefile.Reader(shp)
    fields = reader.fields[1:]
    field_names = [field[0] for field in fields]
    projection = get_epsg(shp)
    wgs84 = ee.Projection('EPSG:4326')
    features = []

    for sr in reader.shapeRecords():
        atr = dict(zip(field_names, sr.record))
        geom = sr.shape.__geo_interface__
        if projection == 4326:
            ee_geometry = ee.Geometry(geom,'EPSG:4326')
        else:
            ee_geometry = ee.Geometry(geom, 'EPSG:' + projection)\
                            .transform(wgs84, 1)
        feat = ee.Feature(ee_geometry, atr)
        features.append(feat)

    return ee.FeatureCollection(features)


def read_single_image(product, aoi,start_date,
                      end_date,bands=['B2', 'B3', 'B4']):

    geometry = get_features(aoi)
    img = ee.ImageCollection(product)\
        .filterBounds(geometry)\
        .filterDate(start_date, end_date) \
        .select(bands)\
        .median() \

    return img


def get_landsat(product, aoi, start_date, end_date,
                pcc=5, output='output',
                bands=['B2','B3','B4'],
                export=False):

    '''
    Export or Read meta dat of a landsat product cropped with a shapefile
    :param product: Landsat product type
    :param aoi: area of interest (shapefile)
    :param start_date: date to start from
    :param end_date: last date to check to
    :param pcc: percent_of_cloud_cover
    :param output: name of output file
    :param bands: bands to select (defaulted to RGB of Landsat 8)
    :param export: option to export image
    :return: tiff file exported to gdrive or meta data if exporting is false
    '''
    geometry = get_features(aoi)
    img = ee.ImageCollection(product)\
        .filterBounds(geometry)\
        .filterDate(start_date, end_date) \
        .median() # return the median band
    col = img.filter(ee.Filter.lt('ClOUD_COVER',pcc))

    if export is False:
        return col
    else:
        # mosaic tiles into a single tiff
        mosaic = ee.ImageCollection([
                    col.select(bands)]).mosaic()

        # region to bound the export view to
        region = ee.Feature(geometry.first())\
                            .geometry().bounds()\
                            .getInfo()['coordinates']

        # start exporting as a single tile/image
        task = ee.batch.Export.image.toDrive(mosaic.unmask(-9999),
                                             skipEmptyTiles= True,
                                             defaultValue=-9999,
                                             folder ='GEE_downloads',
                                             scale=30,
                                             region=get_bbox(aoi).getInfo()['geometry']['coordinates'],
                                             description = output)
        task.start()


def sentinel_cloud_mask(image):
    '''
    Cloud mask for Sentinel-2 Imagery
    :param image: sentinel -2
    :return: cloud mask
    '''

    qa = image.select('QA60')
    cloudbitmask = ee.Number(2).pow(10).int()
    cirrusbitmask = ee.Number(2).pow(11).int()
    cldmask = qa.bitwiseAnd(cloudbitmask).eq(0)
    mask = cldmask.bitwiseAnd(cirrusbitmask).eq(0)
    return image.updateMask(mask).divide(10000)\
                .copyProperties(image, ["system:time_start"])


def get_sentinel(product, aoi, start_date, end_date,
                 pcc=3,output='output',
                 bands = ['B2', 'B3', 'B4', 'B8'],
                 export=False):
    '''
    :param product: sentinel imagery product name
    :param aoi: area of interest as a shapefile
    :param start_date: date to start from
    :param end_date: last date to check to
    :param pcc: percent_of_cloud_cover
    :param output: name of output file
    :param bands: bands to select (defaulted to bands with 10 meter resolution)
    :param export: option to export image
    :return: tiff file exported to gdrive or meta data if exporting is false
    '''

    geometry = get_features(aoi)
    img = ee.ImageCollection(product) \
            .filterDate(start_date, end_date) \
            .filterBounds(geometry) \
            .map(sentinel_cloud_mask) \
            .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', pcc))

    col = img.median()

    if export is False:
        return col
    else:
        # mosaic tiles into a single tiff
        mosaic = ee.ImageCollection([
            col.select(bands)]).mosaic()

        # region to bound the export view to
        region = ee.Feature(geometry.first()) \
            .geometry().bounds() \
            .getInfo()['coordinates']

        # start exporting as a single tile/image
        task = ee.batch.Export.image.toDrive(mosaic.unmask(-9999),
                                             skipEmptyTiles= True,
                                             defaultValue=-9999,
                                             folder ='GEE_downloads',
                                             scale=30,
                                             region=get_bbox(aoi).getInfo()['geometry']['coordinates'],
                                             description=output)
        task.start()


def save_output(col, geometry, aoi, band, scale):
    
    try:
        length = len(col.getInfo()['features'])
    except:
        print('Area is too large or feature too complex, not sure, create a simple feature with 1 or more attributes')
        raise 
    img_list = col.toList(length)
    #
    #region = ee.Feature(geometry.first())\
    #            .geometry().bounds().getInfo()['coordinates']

    print("\n Total number of bands requested: " + str(length)+"\n")

    for i in range(length):
        img = ee.Image(img_list.get(i)).clip(geometry)
        timestamp = (img.getInfo()['properties']['system:index'])
        name = (str(band) + "_" + timestamp+'_'+str(scale)+'m')
        task = ee.batch.Export.image.toDrive(img.unmask(-9999),
                                            region=get_bbox(aoi).getInfo()['geometry']['coordinates'] ,
                                            skipEmptyTiles= True,
                                            description=name,
                                            scale = scale, 
                                            folder ='GEE_downloads',
                                            #defaultValue=-9999,
                                            maxPixels=1e13,
                                            crs='EPSG:4326')
  
        print("submitted "+name+" for downloading")

        task.start()


def get_modis(aoi, start_date, end_date, 
              product = "MODIS/006/MOD13Q1", 
              band='NDVI', export=False, scale = 250):

    geometry = get_features(aoi)
    print(geometry)
    col = ee.ImageCollection(product) \
        .filterBounds(geometry) \
        .filterDate(start_date, end_date) \
        .select(band)

    if export is False:
        return col

    else:
        save_output(col, geometry, aoi, band, scale = 250)


def get_chirps(aoi, start_date, end_date, 
               product= 'UCSB-CHG/CHIRPS/PENTAD',  
               band = 'precipitation',
               export=False, scale = 250):

    '''
    :param product: CHIRPS (precipitation) daily or pentad(5-days) data
    :param aoi: area of interest
    :param start_date: date to start from
    :param end_date: last date to check to
    :param export: option to export as a tif file
    :return: collection of images or output geotiff
    '''
   
    geometry = get_features(aoi)
    col = ee.ImageCollection(product) \
            .filterBounds(geometry) \
            .filterDate(start_date, end_date) \
            .select(band)

    if export is False:
        return col

    else:
        save_output(col, geometry, aoi, band, scale = scale)


def get_terraclimate(aoi, start_date, end_date,
                     product='IDAHO_EPSCOR/TERRACLIMATE',
                     band='aet', export=False):

    print(
        '''
        Name	Units	Min	Max	Scale	Description
        aet	mm	0*	3140*	0.1	
        Actual evapotranspiration, derived using a one-dimensional soil water balance model
        
        def	mm	0*	4548*	0.1	
        Climate water deficit, derived using a one-dimensional soil water balance model
        
        pdsi		-4317*	3418*	0.01	
        Palmer Drought Severity Index
        
        pet	mm	0*	4548*	0.1	
        Reference evapotranspiration (ASCE Penman-Montieth)
        
        pr	mm	0*	7245*		
        Precipitation accumulation
        
        ro	mm	0*	12560*		
        Runoff, derived using a one-dimensional soil water balance model
        
        soil	mm	0*	8882*	0.1	
        Soil moisture, derived using a one-dimensional soil water balance model
        
        srad	W/m^2	0*	5477*	0.1	
        Downward surface shortwave radiation
        
        swe	mm	0*	32767*		
        Snow water equivalent, derived using a one-dimensional soil water balance model
        
        tmmn	°C	-770*	387*	0.1	
        Minimum temperature
        
        tmmx	°C	-670*	576*	0.1	
        Maximum temperature
        
        vap	kPa	0*	14749*	0.001	
        Vapor pressure
        
        vpd	kPa	0*	1113*	0.01	
        Vapor pressure deficit
        
        vs	m/s	0*	2923*	0.01	
        Wind-speed at 10m
        '''
        )
    geometry = get_features(aoi)
    col = ee.ImageCollection(product) \
            .filterBounds(geometry) \
            .filterDate(start_date, end_date) \
            .select(band)

    if export is False:
        return col

    else:
        save_output(col, geometry, aoi, band,scale = 4500 )



def get_image(aoi, product, band,
               export=False, scale = 250):
 
    geometry = get_features(aoi)
    col = ee.Image(product) \
            .clip(geometry) \
            .select(band)

    if export is False:
        return col

    else:
        # start exporting as a single tile/image
        task = ee.batch.Export.image.toDrive(col.unmask(-9999),
                                        skipEmptyTiles= True,
                                        folder ='GEE_downloads',
                                        scale=scale,
                                        maxPixels=1e13,
                                        region=get_bbox(aoi).getInfo()['geometry']['coordinates'],
                                        description   = (os.path.basename(product)+'_'+str(band)+'_'+str(scale)+'m') ) 
        task.start()

 

def get_collection(aoi, start_date, end_date, 
               product, band, scale,
               export=False ):

    '''
    :param product: path to collection
    :param aoi: area of interest
    :param start_date: date to start from
    :param end_date: last date to check to
    :param export: option to export as a tif file
    :return: collection of images or output geotiff
    '''

    geometry = get_features(aoi)
    col = ee.ImageCollection(product) \
            .filterBounds(geometry) \
            .filterDate(start_date, end_date) \
            .select(band)

    if export is False:
        return col

    else:
        save_output(col, geometry, aoi, band, scale)



