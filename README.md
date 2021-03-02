# michmap
<<<<<<< HEAD
=======


This is a set of scripts to *request*, *download*, *test*, and *pre-process* (i.e., mask, mosaic, merge) Landsat ARD imagery from the [LP DAAC AppEEARS API](https://lpdaacsvc.cr.usgs.gov/appeears/). 

**Geospatial Dependencies:**
- Rasterio 
- GDAL (>1.1 I believe)
- Geopandas
- Note 2: If you don't have these, I recommend installing Rasterio first. Follow the instructions [here](https://rasterio.readthedocs.io/en/latest/installation.html)

**Scripts are below:**

*appeears_request.py:* Requests band-by-band data using a user-defined shapefile/bounding box. Requires:
- time/space bounds (preferably a .shp)
- a (free) NASA Earthdata account.  

*appeears_download.py:* Pings the AppEEARS API to see if the request is complete. Downloads imagery band by band.
- Either manually retrieve the task ID from the request script, or download the \*request.json file from the AppEEARS platform. This script scrapes the JSON for the task ID and then calls the api to check done-ness. 
- The download loop will try to download each file 5 times, will raise a runtime error if it is unable to retrieve a specific file
- 
>>>>>>> a2df9eb4c2b2b7a5b84ad953b90b940f0dff1b27
