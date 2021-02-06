#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 19:57:53 2021

@author: mallen
"""

import pandas as pd
import geopandas as gpd
import folium
import os, shutil
from glob import glob
import os
import matplotlib.pyplot as plt

os.chdir("/Users/mallen/Documents/q11/mich_map2/code")


shp = gpd.read_file("../data/Michigan_U.S._Congressional_Districts__v17a_-shp/Michigan_U.S._Congressional_Districts__v17a_MERGE_reproj.shp")

# get daytime (descending wrs2 grid, L8)
wrs = gpd.read_file('../data/WRS2_descending_0/WRS2_descending.shp')
wrs_intersection = wrs[wrs.intersects(shp.geometry[0])]

shp.plot()
wrs_intersection.plot()

fig, ax = plt.subplots(1, 1)

wrs_intersection.plot(ax = ax, edgecolor = 'r', facecolor = 'none')
shp.plot(ax = ax, facecolor = 'k')

