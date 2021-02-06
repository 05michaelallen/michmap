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

os.chdir("/Volumes/ellwood/michmap/code")

clear_threshold = 1600000

# =============================================================================
# import and 
# =============================================================================
# import metadata
meta = pd.read_csv("../data/2020/CU-LC08-001-Statistics.csv")
qa = pd.read_csv("../data/2020/CU-LC08-001-PIXELQA-Statistics-QA.csv")
qa_lookup = pd.read_csv("../data/2020/CU-LC08-001-PIXELQA-lookup.csv")

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
bands = ['SRB1', 'SRB2', 'SRB3', 'SRB4', 'SRB5', 'SRB6', 'SRB7']
for f in fn:
    # import pixelqa
    px_qa_f = rio.open("../data/2020/CU_LC08.001_PIXELQA_doy" + str(f) + "_aid0001.tif").read()
    px_qa_fm = np.isin(px_qa_f, qa_clear_values)
    # import bands
    d = []
    for b in bands:
        bf = rio.open("../data/2020/CU_LC08.001_" + b + "_doy" + str(f) + "_aid0001.tif").read()
        d.append(bf * px_qa_fm)
        
        
        
        
        
    
