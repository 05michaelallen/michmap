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

#os.chdir("/Volumes/ellwood/michmap/code")
os.chdir("/home/vegveg/michmap/michmap/")
clear_threshold = 0
year = 2018

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