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
import matplotlib.pyplot as plt

wd = "/home/vegveg/michmap/michmap/"
os.chdir(wd)
clear_threshold = 10000
flag_MANUALDROPS = True # if we have a manual drop file 
scalefactor = 10000
years = [2017]
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

# =============================================================================
# functions
# =============================================================================
def drop_from_csv(fn, dropcsv):
    for d in dropcsv:
            fn = [v for v in fn if v != d]
            return fn

# =============================================================================
# main loop
# =============================================================================
for year in years:
    # import metadata
    meta = pd.read_csv("../data/" + str(year) + "/CU-LC08-001-Statistics.csv")
    qa = pd.read_csv("../data/" + str(year) + "/CU-LC08-001-PIXELQA-Statistics-QA.csv")
    qa_lookup = pd.read_csv("../data/" + str(year) + "/CU-LC08-001-PIXELQA-lookup.csv")
    
    # list clear values
    qa_clear_values = qa_lookup[(qa_lookup['Cloud'] == "No") & 
                                (qa_lookup['Cloud Shadow'] == "No")]["Value"].tolist()
    qa_clear_values_str = [str(x) for x in qa_clear_values] # convert to string
    
    # filter for good (non cloud values)
    qa['clear'] = np.nansum(qa[qa_clear_values_str], axis = 1)
    qa = qa[qa['clear'] > clear_threshold] # note: currently not using this
    
    # list good values in aerosol bands
    sr_clear_aerosol = [2, 4, 32,
                        66, 68, 96, 100,
                        130, 132, 160, 164] # higher numbers are high aerosol
    
    # grab str(year)_doy
    qa['Date']= pd.to_datetime(qa['Date'])
    qa['yeardoy'] = (qa['Date'].dt.year*1000 + qa['Date'].dt.dayofyear) # index for finding filenames
    # sort
    qa = qa.sort_values(by = 'yeardoy')
    
    # find unique doys
    fn = np.unique(qa['yeardoy'])
    
    # filter manual drops (these were manually inspected and found to have bad
    # cloud/aerosol detection)
    if flag_MANUALDROPS:
        manualdropsfn = "../data/" + str(year) + "/manual_drops.csv"
        if os.path.isfile(manualdropsfn):
            manualdrops = pd.read_csv("../data/" + str(year) + "/manual_drops.csv").values
            fn = drop_from_csv(fn, manualdrops)
        else:
            print("manual_drops.csv does not exist /nrunning with all image dates")
    
    # =============================================================================
    # compute band means from all images in the year sample
    # =============================================================================
    # import reference image metadata
    image_meta = rio.open("../data/" + str(year) + "/CU_LC08.001_SRB1_doy" + str(fn[0]) + "_aid0001.tif").meta
    # update metadata
    image_meta = image_meta.copy()
    image_meta.update({'count': 1,
                       'nodata': -9999,
                       'dtype': 'float32'})
    
    ### this loop runs through each band's files and does the following
    # masks for non-clear values using pixel qa
    # reassigns bad values
    # take mean per-pixel reflectance (via per-pixel sum/count)
    # outputs as year_SRBx.tif
    
    # note: this setup allows for single band processing, so we process the pixel qa
    # for each band (which is unnecessary). can optimize by swapping the order
    # of processing. 
    for b in range(len(bands)):
        print(datetime.now())
        print("band: " + bands[b])
        print("__________________________________________________________________")
        # initialize arrays
        image_sum = np.zeros([1, image_meta['height'], image_meta['width']], dtype = np.float32)
        image_count = np.zeros([1, image_meta['height'], image_meta['width']], dtype = np.int16)
        image_mean = np.zeros([1, image_meta['height'], image_meta['width']], dtype = np.float32)
        for f in fn:
            print("file: " + str(f))
            # import pixel qa + cloud flags
            px_qa_f = rio.open("../data/" + str(year) + "/CU_LC08.001_PIXELQA_doy" + str(f) + "_aid0001.tif").read()
            px_qa_fm = np.isin(px_qa_f, qa_clear_values).astype(np.int16) # convert to boolean and then to float, good values = 1
            # import sr_aerosol qa flags
            px_sraerosol_f = rio.open("../data/" + str(year) + "/CU_LC08.001_SRAEROSOLQA_doy" + str(f) + "_aid0001.tif").read()
            px_sraerosol_fm = np.isin(px_sraerosol_f, sr_clear_aerosol).astype(np.int16)
            # import surface reflectance band
            bf = rio.open("../data/" + str(year) + "/CU_LC08.001_" + bands[b] + "_doy" + str(f) + "_aid0001.tif").read().astype(np.float32)
            # reassign reflectances outside of range bad values
            bf[bf < 0] = 1 
            bf[bf > scalefactor] = scalefactor
            # apply qa masks
            mask = px_qa_fm * px_sraerosol_fm
            bfm = bf * mask
            # add to image sum
            image_sum = image_sum + bfm
            # add to image count
            mask_count = mask.copy()
            mask_count[mask_count > 0] = 1
            image_count = image_count + mask_count
        # take average, apply scale factor
        image_mean = ((image_sum/image_count)/scalefactor)
        # tag nodata
        image_mean[image_mean <= 0] = -9999
        # output
        with rio.open("../data/" + str(year) + "_" + bands[b] + ".tif", 'w', **image_meta) as dst:
            dst.write(image_mean)
            
    print(datetime.now())
    print("finshed")