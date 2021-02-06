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

os.chdir("/Volumes/ellwood/mich_map2/code")

# =============================================================================
# 
# =============================================================================
# import metadata
meta = pd.read_csv("../data/2020/CU-LC08-001-Statistics.csv")
qa = pd.read_csv("../data/2020/CU-LC08-001-PIXELQA-Statistics-QA.csv")
qa_lookup = pd.read_csv("../data/2020/CU-LC08-001-PIXELQA-lookup.csv")

# shapefile for clipping
t = rio.open("../data/2020_appeears/CU_LC08.001_SRB5_doy2020236_aid0001.tif")
t.meta

