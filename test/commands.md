#### Command line examples

Check features

    geepy check-features -shp 'data/addis_abeba.shp' 

Get Modis Data
    
    geepy download-modis -p 'MODIS/006/MOD13A1' -a 'data/addis_abeba.shp' -sd '2017-05-01' -ed '2018-01-05' -b 'NDVI'
 
Get CHIRPS Data
    
    geepy download-chirps -p 'UCSB-CHG/CHIRPS/PENTAD' -a 'data/addis_abeba.shp' -sd '2017-11-01' -ed '2018-01-05' -b 'precipitation'
    
Get TerraClimate Data
    
    geepy download-terraclimate -p 'IDAHO_EPSCOR/TERRACLIMATE' -a 'data/addis_abeba.shp' -sd '2015-10-01' -ed '2015-12-31' -b 'aet'
