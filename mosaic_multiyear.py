#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 17 18:02:31 2021

@author: vegveg
"""

import os
import rasterio as rio
from rasterio.merge import merge
import numpy as np

# flags
flag_MULTIBAND = False

# =============================================================================
# functions
# =============================================================================
def merge_nanmean(b0, b1):
    b0 = np.nanmean([b0, b1])

# =============================================================================
# set parameters
# =============================================================================
# define and set wd
wd = "/media/vegveg/bedlam/michmap/michmap/"
os.chdir(wd)

# years to merge
years = [1999, 2000]

# initialize bands
bands = [
    'SRB1', 
    'SRB2', 
    'SRB3', 
    'SRB4', 
    'SRB5', 
    #'SRB6', 
    'SRB7'
    ]

# =============================================================================
# main loop 
# =============================================================================
if flag_MULTIBAND:
    # open connection
    y0 = rio.open("../data/" + str(years[0]) + "_Landsat.tif")
    y1 = rio.open("../data/" + str(years[1]) + "_Landsat.tif")
    # merge and output
    merge([y0, y1], method = merge_nanmean, dst_path = "../data/" + str(years[0]) + "_" + str(years[1]) + "tt.tif")
else:
    for b in bands:
        # open connection
        y0 = rio.open("../data/" + str(years[0]) + "_" + b + ".tif")
        y1 = rio.open("../data/" + str(years[1]) + "_" + b + ".tif")
        out_meta = y0.meta.copy()
        
        # take mean
        y = np.array([y0.read(), y1.read()])
        out_mean = np.nanmean(y, axis = 0)
        out_mean[out_mean < 0] = -9999
        
        # output 
        with rio.open("../data/" + str(years[0]) + "_" + str(years[1]) + "_" + b + ".tif", 'w', **out_meta) as dst:
            dst.write(out_mean)