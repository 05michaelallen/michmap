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

#os.chdir("/Volumes/ellwood/michmap/code")
os.chdir("/home/vegveg/michmap/michmap/")
clear_threshold = 1600000
scalefactor = 10000
year = 2016
years = [2016]
# initialize bands
bands = [
    #'SRB1', 
    'SRB2', 
    'SRB3', 
    'SRB4', 
    'SRB5', 
    'SRB6', 
    'SRB7'
    ]
    

for year in years:
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
            # import pixel quality flags
            px_qa_f = rio.open("../data/" + str(year) + "/CU_LC08.001_PIXELQA_doy" + str(f) + "_aid0001.tif").read()
            px_qa_fm = np.isin(px_qa_f, qa_clear_values).astype(np.int16) # convert to boolean and then to float, good values = 1
            # import surface reflectance band
            bf = rio.open("../data/" + str(year) + "/CU_LC08.001_" + bands[b] + "_doy" + str(f) + "_aid0001.tif").read().astype(np.float32)
            # reassign reflectances outside of range bad values
            bf[bf < 0] = 1 
            bf[bf > scalefactor] = scalefactor
            # apply qa mask
            bfm = bf * px_qa_fm
            # add to image sum
            image_sum = image_sum + bfm
            # add to image count
            px_qa_fm_count = px_qa_fm.copy()
            px_qa_fm_count[px_qa_fm_count > 0] = 1
            image_count = image_count + px_qa_fm_count
        # take average, apply scale factor
        image_mean = ((image_sum/image_count)/scalefactor).astype(np.float32)
        # tag nodata
        image_mean[image_mean <= 0] = -9999
        # output
        with rio.open("../data/" + str(year) + "_" + bands[b] + ".tif", 'w', **image_meta) as dst:
            dst.write(image_mean)
            
    print(datetime.now())
    print("finshed")