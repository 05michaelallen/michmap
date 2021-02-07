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
import requests
import time
import cgi

wd = "/Volumes/ellwood/michmap/code/"

os.chdir(wd)
API = 'https://lpdaacsvc.cr.usgs.gov/appeears/api/' 

# Insert API URL, call login service, provide credentials & return json
login_response = requests.post(f"{API}/login", auth = ('mallen85', '!Lesson982')).json()


# Assign the token to a variable
token = login_response['token']
head = {'Authorization': f"Bearer {token}"}

# set task id
task_id = '365f4241-7afe-47c7-b002-6ea3421fc259' # for 2016

# get task status
status_response = requests.get(f"{API}/status/{task_id}", headers=head)
status_response.json()

# Use while statement to ping the API every 20 seconds until a response of 'done' is returned
starttime = time.time()
while requests.get(f"{API}/task/{task_id}", headers=head).json()['status'] != 'done':
    print(requests.get(f"{API}/task/{task_id}", headers=head).json()['status'])
    time.sleep(20.0 - ((time.time() - starttime) % 20.0))
print(requests.get(f"{API}/task/{task_id}", headers=head).json()['status'])

# Call API and return bundle contents for the task_id as json
bundle = requests.get(f"{API}/bundle/{task_id}").json()    
bundle

files = {}
for f in bundle['files']:
    files[f['file_id']] = f['file_name']    # Fill dictionary with file_id as keys and file_name as values
files

# Set up output directory on local machine
outfn = f'{wd}outputs/' 
if not os.path.exists(outfn):
    os.makedirs(outfn)


for file in files:
    download_response = requests.get(f"{API}/bundle/{task_id}/{file}", stream=True)                                   # Get a stream to the bundle file
    filename = os.path.basename(cgi.parse_header(download_response.headers['Content-Disposition'])[1]['filename'])    # Parse the name from Content-Disposition header
    filepath = os.path.join(outfn, filename)                                                                         # Create output file path
    with open(filepath, 'wb') as file:                                                                                # Write file to dest dir
        for data in download_response.iter_content(chunk_size=8192):
            file.write(data)
print("Downloading complete!")