# michmap


This is a set of scripts to *request*, *download*, *test*, and *pre-process* (i.e., mask, mosaic, merge) Landsat ARD imagery from the [LP DAAC AppEEARS API](https://lpdaacsvc.cr.usgs.gov/appeears/). I originally wrote this to download a multi-year time series of ARD Landsat and MODIS surface reflectances to [track drought impacts on urban vegetation in Los Angeles](https://www.sciencedirect.com/science/article/abs/pii/S2212095520306829). I have since generalized the code. 

An example Landsat 5 is below (left 543, right 321) from summertime imagery over 2009-2010. 

![link](./example_data/michmap_09-10_543_321_merge.jpg)

**Geospatial Dependencies:**

>Rasterio, GDAL (>1.1), Geopandas

### Scripts:

#appeears_request.py

*Requests band-by-band data from the [AppEEARS catalogue](https://lpdaacsvc.cr.usgs.gov/appeears/products) using a user-defined shapefile/bounding box.*

Requires:
- time bounds. The script uses *year* as a keyword (will generalize this soon), so preferrably a timeframe within a year.
- a bounding box. Preferably a .shp, GeoJSON is fine too but [should be wgs-84](http://switchfromshapefile.org/). 
- a (free) NASA Earthdata account.

#**appeears_download.py** 
>*Pings the AppEEARS API to see if the request is complete. If complete, it downloads imagery band by band.*

Requires:
- \*request.json file from the AppEEARS request. Note: You can either manually retrieve the task ID from the request, or download the \*request.json file from the AppEEARS platform (under "Explore" in your profile).

**file_tester.py** *Tests each .tif file by loading it temporarally. Logs bad files into badfn.csv.*
- badfn.csv can be read by *appeears_download.py* to redownload corrupted files (set flag_REDOWNLOADBADFN = True).
- note: if you are re-testing a batch of bad files, set flag_RETESTBADFN = True to only test the files in badfn.csv.

**preprocessing_landsat.py** *Performs a suite of pre-processing steps (mask, mosaic, merge, average) on the downloaded imagery.*
- imagery is masked using the **PIXELQA** and **SRAEROSOLQA** (for LC08) and **PIXELQA** and **SRATMOSOPACITYQA** (for LT05) files. 
- per-pixel reflectances are calculated as averages of unmasked pixels. 
- we use the [LEDAPS](https://daac.ornl.gov/MODELS/guides/LEDAPS_V2.html) and [LaSRC](https://www.usgs.gov/media/files/landsat-8-collection-1-land-surface-reflectance-code-product-guide) recommended cutoffs from the ATB documents*.

>For LT05: AOD < 0.3, mask all cloud and cloud shadow. 
>For LC08: Aerosol < High, mask all cloud and cloud shadow

## Notes

*We did some sensitivity testing and these values appear appropriate in most cases. We do see occasional aerosol and thin cloud intrusion. These are the best values we found to optimize cloud detection vs. false positives (e.g., bright urban cover, sand, etc.). test
