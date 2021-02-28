#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 19:57:53 2021

@author: mallen
"""

import os
import requests
import time
import cgi
import json
import getpass
import pandas as pd

# flags
flag_REDOWNLOADBADFN = True
flag_VERBOSE = False

# =============================================================================
# set parameters
# =============================================================================
# define and set wd
#wd = "/Volumes/ellwood/michmap/code/"
wd = "/home/vegveg/michmap/michmap/"
os.chdir(wd)
# path to api
API = 'https://lpdaacsvc.cr.usgs.gov/appeears/api/' 
# set task id (from request JSON)
# note: can also pair this with api data request, can pull tast_id straight from 
# data request
year = 2009
# specify sensor prefix
if year < 2013:
    sensor = "LT05"
elif year > 2013: 
    sensor = "LC08"
# import json
req_params = open("../data/" + str(year) + "/mimap-" + str(year) + "-request.json")
req_params = json.loads(req_params.read())
# get task id
task_id = req_params['task_id']

# =============================================================================
# login, get task status
# =============================================================================
# insert api authorization, call login service, provide credentials, and return json
u = getpass.getpass(prompt = 'Enter NASA Earthdata Login Username: ')
p = getpass.getpass(prompt = 'Enter NASA Earthdata Login Password: ')
login_response = requests.post(f"{API}/login", auth = (u, p)).json()
del u, p

# assign the token to a variable
token = login_response['token']
head = {'Authorization': f"Bearer {token}"}

# get task status
status_response = requests.get(f"{API}/status/{task_id}", headers = head)
status_response.json()

# use while statement to ping the api every 20 seconds until a response of 'done' is returned
starttime = time.time()
while requests.get(f"{API}/task/{task_id}", headers = head).json()['status'] != 'done':
    print(requests.get(f"{API}/task/{task_id}", headers = head).json()['status'])
    time.sleep(20.0 - ((time.time() - starttime) % 20.0))
print(requests.get(f"{API}/task/{task_id}", headers = head).json()['status'])

# call api and return bundle contents for the task_id as json
bundle = requests.get(f"{API}/bundle/{task_id}").json()

# fill dictionary with file_id as keys and file_name as values
files = {}
for f in bundle['files']:
    files[f['file_id']] = f['file_name']
    
# if re-downloading files identified as corrupted in badfn.csv (generated by file_tester.py)
# filter files dict for badfn.csv
if flag_REDOWNLOADBADFN:
    # try to load badfn file
    if os.path.isfile("../data/" + str(year) + "/badfn.csv"):
        badfn = pd.read_csv("../data/" + str(year) + "/badfn.csv")
        # recreate filename
        badfn['prefix'] = next(iter(files.values())).split('/')[0] # get prefix 
        badfn['reconfn'] = badfn['prefix'] + "/CU_" + sensor + ".001" + badfn.iloc[:,1] + "_aid0001.tif"
        files_redownload = []
        # now find keys for badfn
        for row in range(len(badfn)):
            files_redownload.append([Key for Key, Value in files.items() if Value == badfn['reconfn'][row]][0])
        files = files_redownload # substitute entire dict of requested files with a list of the keys for the ones needed
    else:
        print("no badfn.csv file in data dir, downloading entire request")

# set up output directory
outfn = '../data/' + str(year) + "/"

# =============================================================================
# loop to download each file in files dict
# =============================================================================
# note: peer connection will occasionally drop, so the loop will request download
# wait if connection is bad, then retry. 
c = 0
#urls is the list of urls as strings
for file in files:
    trycnt = 5  # max try cnt
    while trycnt > 0:
        try:
            if flag_VERBOSE:
                print(file)
            download_response = requests.get(f"{API}/bundle/{task_id}/{file}", stream = True)
            # parse the name from Content-Disposition header
            filename = os.path.basename(cgi.parse_header(download_response.headers['Content-Disposition'])[1]['filename'])
            filepath = os.path.join(outfn, filename)  
            c += 1 # add to count
            # write file to dest dir
            with open(filepath, 'wb') as file:
                for data in download_response.iter_content(chunk_size = 8192):
                    file.write(data)
            trycnt = 0 # success
        except:
            if trycnt <= 0: 
                print("Failed to retrieve: " + file)
            else: 
                trycnt -= 1  # retry
            time.sleep(10)  # wait 10 seconds then retry 

# completed dl
print("download complete")