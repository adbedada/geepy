#### Command line examples

Check features

    geepy check-features 'data/addis_abeba.shp' 

Get Modis Data
    
    geepy download-modis 'MODIS/006/MOD13A1' 'data/addis_abeba.shp' '2017-05-01' '2018-01-05' NDVI
 
Get CHIRPS Data
    
    geepy download-chirps'UCSB-CHG/CHIRPS/PENTAD' 'data/addis_abeba.shp' '2017-11-01' '2018-01-05'
    
Get TerraClimate Data
    
    geepy download-terraclimate-data 'IDAHO_EPSCOR/TERRACLIMATE' 'data/addis_abeba.shp' '2017-05-01' '2018-01-05' 'aet'