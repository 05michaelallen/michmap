# michmap


This is a set of scripts to *request*, *download*, *test*, and *pre-process* (i.e., mask, mosaic, merge) Landsat ARD imagery from the [LP DAAC AppEEARS API](https://lpdaacsvc.cr.usgs.gov/appeears/). I originally wrote this to download a multi-year time series of Landsat and MODIS imagery for the state of Michigan to track reforestation. I have since generalized the code.

**Geospatial Dependencies:**
> Rasterio 
> GDAL (>1.1 I believe)
> Geopandas
- Note: If you don't have these, I recommend installing Rasterio first. Follow the instructions [here](https://rasterio.readthedocs.io/en/latest/installation.html).

See an example output below RGB (654) using all summertime imagery from 2019-20 (approx. 200gb of data).


## Scripts are below:

*appeears_request.py* Requests band-by-band data using a user-defined shapefile/bounding box. 
Requires:
- time/space bounds (preferably a .shp). 
- a (free) NASA Earthdata account.

*appeears_download.py* Pings the AppEEARS API to see if the request is complete. If complete, it downloads imagery band by band.
Requires:
- \*request.json file from the AppEEARS request. Note: You can either manually retrieve the task ID from the request script, or download the \*request.json file from the AppEEARS platform.

*file_tester.py* Tests each .tif file by loading it temporarally. Logs bad files into badfn.csv.
- badfn.csv can be read by *appeears_download.py* to redownload corrupted files (set flag_REDOWNLOADBADFN = True).
- note: if you are re-testing a batch of bad files, set flag_RETESTBADFN = True to only test the files in badfn.csv.

*preprocessing_landsat.py* Performs a suite of pre-processing steps (mask, mosaic, merge, average) on the downloaded imagery. Output is mean surface reflectance over the time slice for each pixel. 
- imagery is masked using the **PIXELQA** and **SRAEROSOLQA** (for LC08) and **PIXELQA** and **SRATMOSOPACITYQA** (for LT05) files. 
- note: we use the LeeDAPS and recommended cutoffs from the ABT documents. We did some sensitivity testing and these values appear appropriate in most cases*. 
-- For LT05: AOD < 0.3, mask all cloud and cloud shadow with confidence > low
-- For LC08: 


*note: we do see occasional aerosol and thin cloud intrusion. These are the best values we found to optimize cloud detection vs. false positives (e.g., bright urban cover, sand).
WIPWIPWIP
