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

wd = "/media/vegveg/bedlam/michmap/michmap/"
os.chdir(wd)
clear_threshold = 10000
flag_MANUALDROPS = False # if we have a manual drop file 
scalefactor = 10000
years = [2009]
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
    """uses manually defined drops list to drop files from the processing list
    
    inputs:
        fn: filelist
    
    """
    for d in dropcsv:
            fn = [v for v in fn if v != d]
            return fn
       
    
def generate_fn_list(year, sensor, clear_threshold):
    """generate list of unique filenames for dl/test, also loads metadata for reference
    inputs:
        year: int
        sensor: string, either LC08 or LT05 for Landsat 8 and Landsat 5
        clear_threshold: int, images are thrown out if below this total px count
    
    returns:
        fn: list of filenames 
        meta: raw metadata file from Appeears download
        qa_clear_values: lists values of good qa pixels
    
    """
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
    return fn, meta, qa_clear_values


# =============================================================================
# main loop
# =============================================================================
for year in years:
    # specify sensor prefix
    if year < 2013:
        sensor = "LT05"
        aerosol_prefix = "SRATMOSOPACITYQA"
    elif year > 2013: 
        sensor = "LC08"
        aerosol_prefix = "SRAEROSOLQA"
    else: 
        raise ValueError('Year not valid. Must be int.')
    
    
    # drop band 6 if not landsat 8
    if sensor == "LT05":
        try:
            bands.remove('SRB6')
        except:
            pass
        
    # import metadata, list files
    fn, meta, qa_clear_values = generate_fn_list(year, sensor, clear_threshold)
    
    # list good values in aerosol bands (note: LC08 and LT05 have different aerosol products)
    # like the qa LC08 are bitpacked, but using raw values is fine
    if sensor == "LC08":
        sr_clear_aerosol = [2, 4, 32,
                            66, 68, 96, 100,
                            130, 132, 160, 164] # higher numbers are high aerosol
    elif sensor == "LT05":
        sr_clear_aerosol = 300 # <0.3 AOT is reasonably clear
    
    # filter manual drops (these were manually inspected and found to have bad
    # cloud/aerosol detection)
    if flag_MANUALDROPS:
        manualdropsfn = "../data/" + str(year) + "/manual_drops.csv"
        if os.path.isfile(manualdropsfn):
            manualdrops = pd.read_csv("../data/" + str(year) + "/manual_drops.csv").values
            fn = drop_from_csv(fn, manualdrops)
        else:
            print("manual_drops.csv does not exist in the data dir -- running with all image dates")
    
    # =============================================================================
    # compute band means from all images in the year sample
    # =============================================================================
    # import reference image metadata
    image_meta = rio.open("../data/" + str(year) + "/CU_" + sensor + ".001_SRB1_doy" + str(fn[0]) + "_aid0001.tif").meta
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
    
    # note: this setup allows for single band processing, so we load the pixel qa
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
        
        ### enter loop for each file in the list
        for f in fn:
            print("file: " + str(f))
            # import pixel qa + cloud flags
            px_qa_f = rio.open("../data/" + str(year) + "/CU_" + sensor + ".001_PIXELQA_doy" + str(f) + "_aid0001.tif").read()
            px_qa_fm = np.isin(px_qa_f, qa_clear_values).astype(np.int16) # convert to boolean and then to float, good values = 1
            # import sr_aerosol qa flags (if LC08)   
            if sensor == 'LC08':
                px_sraerosol_f = rio.open("../data/" + str(year) + "/CU_" + sensor + ".001_" + aerosol_prefix + "_doy" + str(f) + "_aid0001.tif").read()
                px_sraerosol_fm = np.isin(px_sraerosol_f, sr_clear_aerosol).astype(np.int16)
                # create mask
                mask = px_qa_fm * px_sraerosol_fm
            elif sensor == 'LT05':
                px_aero_f = rio.open("../data/" + str(year) + "/CU_" + sensor + ".001_" + aerosol_prefix + "_doy" + str(f) + "_aid0001.tif").read()
                px_aero_f[px_aero_f <= sr_clear_aerosol] = 1
                px_aero_f[px_aero_f >= sr_clear_aerosol] = 0
                mask = px_qa_fm * px_aero_f
            # import surface reflectance band
            bf = rio.open("../data/" + str(year) + "/CU_" + sensor + ".001_" + bands[b] + "_doy" + str(f) + "_aid0001.tif").read().astype(np.float32)
            # reassign reflectances outside of range bad values
            bf[bf < 0] = 1 
            bf[bf > scalefactor] = scalefactor
            # apply qa masks
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