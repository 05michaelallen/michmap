#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 10:47:39 2021

@author: vegveg
"""

import os
import rasterio as rio
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

os.chdir("/media/vegveg/scratch1/michmap_oldextent/")
clear_threshold = 0
year = 2018

# =============================================================================
# import and initialize
# =============================================================================
# import metadata
meta = pd.read_csv(str(year) + "/CU-LC08-001-Statistics.csv")
qa = pd.read_csv(str(year) + "/CU-LC08-001-PIXELQA-Statistics-QA.csv")
qa_lookup = pd.read_csv(str(year) + "/CU-LC08-001-PIXELQA-lookup.csv")

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
# import and loop to plot
# =============================================================================
for f in fn:
    p = []
    qa_img= rio.open(str(year) + "/CU_LC08.001_PIXELQA_doy" + str(f) + "_aid0001.tif").read()[0]
    print(str(f))
    p = plt.imshow(qa_img)
    plt.colorbar(p)
    plt.show()