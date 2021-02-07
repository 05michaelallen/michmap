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
import geopandas as gpd
import matplotlib.pyplot as plt
from datetime import datetime

os.chdir("/Volumes/ellwood/michmap/code")

clear_threshold = 1600000
scalefactor = 10000

# =============================================================================
# import and 
# =============================================================================
# import metadata
meta = pd.read_csv("../data/2017/CU-LC08-001-Statistics.csv")
qa = pd.read_csv("../data/2017/CU-LC08-001-PIXELQA-Statistics-QA.csv")
qa_lookup = pd.read_csv("../data/2017/CU-LC08-001-PIXELQA-lookup.csv")

# import reference image metadata
image_meta = rio.open("../data/2017/CU_LC08.001_PIXELQA_doy2017139_aid0001.tif").meta

# list clear values
qa_clear_values = qa_lookup[(qa_lookup['Cloud'] == "No") & (qa_lookup['Cloud Shadow'] == "No")]["Value"].tolist()
qa_clear_values_str = [str(x) for x in qa_clear_values] # convert to string

# filter for good (non cloud values)
qa['clear'] = np.nansum(qa[qa_clear_values_str], axis = 1)
qa = qa[qa['clear'] > clear_threshold]

# grab year_doy
qa['Date']= pd.to_datetime(qa['Date'])
qa['yeardoy'] = (qa['Date'].dt.year)*1000 + qa['Date'].dt.dayofyear # index for finding filenames
# sort
qa = qa.sort_values(by = 'yeardoy')

# find unique doys
fn = np.unique(qa['yeardoy'])

# initialize bands
bands = [
    #'SRB1', 
    #'SRB2', 
    #'SRB3', 
    'SRB4', 
    'SRB5', 
    #'SRB6', 
    #'SRB7'
    ]

# for f in fn:
#     print(datetime.now())
#     print("file: " + str(f))
#     # import pixelqa
#     px_qa_f = rio.open("../data/2017/CU_LC08.001_PIXELQA_doy" + str(f) + "_aid0001.tif").read()
#     px_qa_fm = np.isin(px_qa_f, qa_clear_values).astype(int)
#     # import bands
#     d = []
#     for b in bands:
#         bf = rio.open("../data/2017/CU_LC08.001_" + b + "_doy" + str(f) + "_aid0001.tif").read()/scalefactor
#         bfm = bf * px_qa_fm
#         bfm[bfm <= 0] = 0
#         bfm[bfm >= 1] = 1
#         d.append(bfm)

# =============================================================================
# compute band means from all images
# =============================================================================
image_sum = np.zeros([len(bands), image_meta['height'], image_meta['width']])
image_count = np.zeros([len(bands), image_meta['height'], image_meta['width']], dtype = np.int16)

for f in fn[0:3]:
    print(datetime.now())
    print("file: " + str(f))
    # import pixelqa
    px_qa_f = rio.open("../data/2017/CU_LC08.001_PIXELQA_doy" + str(f) + "_aid0001.tif").read()
    px_qa_fm = np.isin(px_qa_f, qa_clear_values).astype(int)
    
    # import selected bands for fn
    for b in range(len(bands)):
        bf = rio.open("../data/2017/CU_LC08.001_" + bands[b] + "_doy" + str(f) + "_aid0001.tif").read()/scalefactor
        # apply mask
        bfm = bf * px_qa_fm
        # reissue bad values
        bfm[bfm <= 0] = 0
        bfm[bfm >= 1] = 1
        # add to image sum
        image_sum[b,:,:] = image_sum + bfm
        # add to image count
        px_qa_fm_count = px_qa_fm.copy()
        px_qa_fm_count[px_qa_fm_count > 0] = 1
        image_count[b,:,:] = image_count + px_qa_fm_count
        
print(datetime.now())
print("import done")