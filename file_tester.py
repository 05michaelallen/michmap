#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 12:28:29 2021

@author: mallen
"""

import rasterio as rio
import os
import numpy as np
import pandas as pd
from datetime import datetime

# flags
flag_RETESTBADFN = True

# =============================================================================
# functions
# =============================================================================
"""
generate list of unique filenames for dl/test, also loads metadata for reference
inputs:
    year: int
    sensor: string, either LC08 or LT05 for Landsat 8 and Landsat 5
    clear_threshold: images are thrown out if below this total px count

returns:
    fn: list of filenames 
    meta: raw metadata file from Appeears download

"""

def generate_fn_list(year, sensor, clear_threshold):
    ### initial download from metadata files
    # import metadata
    meta = pd.read_csv("../data/" + str(year) + "/CU-" + sensor + "-001-Statistics.csv")
    qa = pd.read_csv("../data/" + str(year) + "/CU-" + sensor + "-001-PIXELQA-Statistics-QA.csv")
    qa_lookup = pd.read_csv("../data/" + str(year) + "/CU-" + sensor + "-001-PIXELQA-lookup.csv")
    
    # list clear values
    qa_clear_values = qa_lookup[(qa_lookup['Cloud'] == "No") & (qa_lookup['Cloud Shadow'] == "No")]["Value"].tolist()
    qa_clear_values_str = [str(x) for x in qa_clear_values] # convert to string
    
    # filter for good (non cloud values)
    qa['clear'] = np.nansum(qa[qa_clear_values_str], axis = 1)
    qa = qa[qa['clear'] > clear_threshold]
    
    # grab yeardoy
    qa['Date']= pd.to_datetime(qa['Date'])
    qa['yeardoy'] = (qa['Date'].dt.year*1000 + qa['Date'].dt.dayofyear) # index for finding filenames
    # sort
    qa = qa.sort_values(by = 'yeardoy')
    
    # find unique doys
    fn = np.unique(qa['yeardoy'])
    return fn, meta


# =============================================================================
# set parameters
# =============================================================================
wd = "/home/vegveg/michmap/michmap/"
os.chdir(wd)
clear_threshold = 10000
year = 2009
# specify sensor prefix
if year < 2013:
    sensor = "LT05"
elif year > 2013: 
    sensor = "LC08"
else: 
    raise ValueError('Year not valid. Must be int.')
    
    
# initialize bands
bands = [
    'SRB1', 
    'SRB2', 
    'SRB3', 
    'SRB4', 
    'SRB5', 
    'SRB6', 
    'SRB7'
    ]

# drop band 6 if not landsat 8
if sensor == "LT05":
    try:
        bands.remove('SRB6')
    except:
        pass

# =============================================================================
# build list of files to test
# =============================================================================
if flag_RETESTBADFN:
    ### testing dates with bands that were re-downloaded after failed/corrupted dl
    if os.path.isfile("../data/" + str(year) + "/badfn.csv"):
        fn_list = pd.read_csv("../data/" + str(year) + "/badfn.csv").iloc[:,1].values.tolist()
        fn = []
        for f in fn_list:
            fn.append(str(year) + f.split(str(year))[1])
        fn = np.unique(fn)
    else:
        print("no badfn.csv file in data dir, terting entire set") ### put in function
        fn, meta = generate_fn_list(year, sensor, clear_threshold)

else:
    fn, meta = generate_fn_list(year, sensor, clear_threshold)

# =============================================================================
# main testing loop
# =============================================================================
### test each file by opening it via rio.open().read(), store failed reads in badfn.csv in data dir
badfn = []
for f in fn:
    print(datetime.now())
    print("file: " + str(f))
    # import pixelqa, aerosol/optical thickness
    try: 
        px_qa_f = rio.open("../data/" + str(year) + "/CU_" + sensor + ".001_PIXELQA_doy" + str(f) + "_aid0001.tif").read()    
    except:
        badfn.append("_PIXELQA_doy" + str(f))
    try:
        if sensor == 'LT05':
            aerosol = rio.open()
        elif == 'LT05'
                
    # import selected bands for fn
    for b in range(len(bands)):
        print("band: " + bands[b])
        try:
            bf = rio.open("../data/" + str(year) + "/CU_" + sensor + ".001_" + bands[b] + "_doy" + str(f) + "_aid0001.tif").read()
        except:
            badfn.append("_" + bands[b] + "_doy" + str(f))
            print("bad band")
            pass # doing nothing on exception
            
bad_fndf = pd.DataFrame(badfn)
bad_fndf.to_csv("../data/" + str(year) + "/badfn.csv")