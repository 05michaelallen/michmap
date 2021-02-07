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

# =============================================================================
# set parameters
# =============================================================================
# define and set wd
wd = "/Volumes/ellwood/michmap/code/"
os.chdir(wd)
# path to api
API = 'https://lpdaacsvc.cr.usgs.gov/appeears/api/' 
# set task id (from request JSON)
# note: can also pair this with api data request, can pull tast_id straight from 
# data request
task_id = '365f4241-7afe-47c7-b002-6ea3421fc259'

# =============================================================================
# login, get task statys
# =============================================================================
# insert api authorization, call login service, provide credentials, and return json
login_response = requests.post(f"{API}/login", auth = ('mallen85', '!Lesson982')).json()

# assign the token to a variable
token = login_response['token']
head = {'Authorization': f"Bearer {token}"}

# get task status
status_response = requests.get(f"{API}/status/{task_id}", headers = head)
status_response.json()

# use while statement to ping the api every 20 seconds until a response of 'done' is returned
starttime = time.time()
while requests.get(f"{API}/task/{task_id}", headers=head).json()['status'] != 'done':
    print(requests.get(f"{API}/task/{task_id}", headers=head).json()['status'])
    time.sleep(20.0 - ((time.time() - starttime) % 20.0))
print(requests.get(f"{API}/task/{task_id}", headers= head).json()['status'])

# call api and return bundle contents for the task_id as json
bundle = requests.get(f"{API}/bundle/{task_id}").json()

# fill dictionary with file_id as keys and file_name as values
files = {}
for f in bundle['files']:
    files[f['file_id']] = f['file_name']

# set up output directory
outfn = '../data/2016/'
if not os.path.exists(outfn):
    os.makedirs(outfn)

# =============================================================================
# loop to download each file in files dict
# =============================================================================
# note: peer connection will occasionally drop, so the loop will request download
# wait if connection is bad, then retry. this appears to fix the problem.
c = 0
#urls is the list of urls as strings
for file in files:
    trycnt = 5  # max try cnt
    while trycnt > 0:
        try:
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