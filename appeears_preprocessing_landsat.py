#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 12:56:31 2021

@author: mallen
"""

import rasterio as rio
import os
import numpy as np
import pandas as pd
from datetime import datetime

os.chdir("/Volumes/ellwood/michmap/code")
flag_TESTER = True
clear_threshold = 1600000
scalefactor = 10000
year = 2017

# =============================================================================
# import and initialize
# =============================================================================
# import metadata
meta = pd.read_csv("../data/" + str(year) + "/CU-LC08-001-Statistics.csv")
qa = pd.read_csv("../data/" + str(year) + "/CU-LC08-001-PIXELQA-Statistics-QA.csv")
qa_lookup = pd.read_csv("../data/" + str(year) + "/CU-LC08-001-PIXELQA-lookup.csv")

# list clear values
qa_clear_values = qa_lookup[(qa_lookup['Cloud'] == "No") & (qa_lookup['Cloud Shadow'] == "No")]["Value"].tolist()
qa_clear_values_str = [str(x) for x in qa_clear_values] # convert to string

# filter for good (non cloud values)
qa['clear'] = np.nansum(qa[qa_clear_values_str], axis = 1)
qa = qa[qa['clear'] > clear_threshold]

# grab str(year)_doy
qa['Date']= pd.to_datetime(qa['Date'])
qa['yeardoy'] = (qa['Date'].dt.year*1000 + qa['Date'].dt.dayofyear) # index for finding filenames
# sort
qa = qa.sort_values(by = 'yeardoy')

# find unique doys
fn = np.unique(qa['yeardoy'])

# =============================================================================
# compute band means from all images
# =============================================================================
# import reference image metadata
image_meta = rio.open("../data/" + str(year) + "/CU_LC08.001_SRB1_doy" + str(fn[1]) + "_aid0001.tif").meta
# update metadata
image_meta = image_meta.copy()
image_meta.update({'count': 1,
                   'nodata': -999,
                   'dtype': 'float64'})

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

### this loop runs through each band's files and does the following
# masks for non-clear values using pixel qa
# reassigns bad values
# take mean per-pixel reflectance (via per-pixel sum/count)
# outputs as year_SRBx.tif

for b in range(len(bands)):
    print(datetime.now())
    print("band: " + b)
    # initialize arrays
    image_sum = np.zeros([1, image_meta['height'], image_meta['width']])
    image_count = np.zeros([1, image_meta['height'], image_meta['width']], dtype = np.int16)
    image_mean = np.zeros([1, image_meta['height'], image_meta['width']])
    for f in fn:
        print(datetime.now())
        print("file: " + str(f))
        # import pixel quality flags
        px_qa_f = rio.open("../data/" + str(year) + "/CU_LC08.001_PIXELQA_doy" + str(f) + "_aid0001.tif").read()
        px_qa_fm = np.isin(px_qa_f, qa_clear_values).astype(int) # convert to boolean, good values = True
        # import band
        bf = rio.open("../data/" + str(year) + "/CU_LC08.001_" + bands[b] + "_doy" + str(f) + "_aid0001.tif").read()
        # apply qa mask
        bfm = bf * px_qa_fm
        # reissue bad values
        bfm[bfm <= 0] = 0
        bfm[bfm >= scalefactor] = scalefactor
        # add to image sum
        image_sum[b,:,:] = image_sum[b,:,:] + bfm
        # add to image count
        px_qa_fm_count = px_qa_fm.copy()
        px_qa_fm_count[px_qa_fm_count > 0] = 1
        image_count[b,:,:] = image_count[b,:,:] + px_qa_fm_count
        # take average
        image_mean[b,:,:] = image_sum[b,:,:]/image_count[b,:,:]
        # tag nodata
        image_mean[image_mean <= 0] = np.nan
        # output
        with rio.open("../data/" + str(year) + "_" + b + ".tif", 'w', **image_meta) as dst:
            dst.write(image_mean)
        
print(datetime.now())
print("import done")

    
# =============================================================================
# TESTER
# =============================================================================
if flag_TESTER:    
    badfn = []
    for f in fn:
        print(datetime.now())
        print("file: " + str(f))
        # import pixelqa
        px_qa_f = rio.open("../data/" + str(year) + "/CU_LC08.001_PIXELQA_doy" + str(f) + "_aid0001.tif").read()    
        # import selected bands for fn
        for b in range(len(bands)):
            print("band: " + bands[b])
            try:
                bf = rio.open("../data/" + str(year) + "/CU_LC08.001_" + bands[b] + "_doy" + str(f) + "_aid0001.tif").read()
            except:
                badfn.append(str(f) + "_" + bands[b])
                print("bad band")
                pass # doing nothing on exception
                
    bad_fndf = pd.DataFrame(badfn)
    bad_fndf.to_csv("../data/" + str(year) + "/badfn.csv")
