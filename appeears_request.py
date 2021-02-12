#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 18 09:04:21 2020

@author: mallen
"""

# Import packages 
import requests as r
import getpass, pprint, time, os, cgi, json
import geopandas as gpd

# Set input directory, change working directory
wd = "/home/vegveg/michmap/michmap/"
os.chdir(wd)
api = 'https://lpdaacsvc.cr.usgs.gov/appeears/api/'

### parameters
# year of interest
year = 2014
# name the task
task_name = 'michmap_v2_2014'

# input username and password
user = getpass.getpass(prompt = 'Enter NASA Earthdata Login Username: ')
password = getpass.getpass(prompt = 'Enter NASA Earthdata Login Password: ')

# insert api url, call login service, provide credentials & return json
token_response = r.post('{}login'.format(api), auth=(user, password)).json()
del user, password
token_response

# list all products
product_response = r.get('{}product'.format(api)).json()
# Create a dictionary indexed by product name & version
products = {p['ProductAndVersion']: p for p in product_response}
# print metadata for product
products['CU_LC08.001']

# create a list of the requested products
prods = ['CU_LC08.001'] # note: can request layers from more than one product

# list layers from products
r.get('{}product/{}'.format(api, prods[0])).json()

# create list of layers
layers = [(prods[0],'SRB1'),
          (prods[0],'SRB2'),
          (prods[0],'SRB3'),
          (prods[0],'SRB4'),
          (prods[0],'SRB5'), 
          (prods[0],'SRB6'),
          (prods[0],'SRB7'),
          (prods[0],'LINEAGEQA'),
          (prods[0],'PIXELQA'),
          (prods[0],'RADSATQA'),
          (prods[0],'SRAEROSOLQA')]

# convert tupled list of layers to list of dict
prodLayer = []
for l in layers:
    prodLayer.append({
            "layer": l[1],
            "product": l[0]
          })

# =============================================================================
# 
# =============================================================================
# save token
token = token_response['token']
head = {'Authorization': 'Bearer {}'.format(token)}

# import the request shapefile
nps = gpd.read_file('../data/shp/michmap_request_bbox.shx').to_json()
# convert to json
nps = json.loads(nps)

# select task type, projection, and output
task_type = 'area'
proj = 'geographic'
outFormat = 'geotiff'
# start and end date
startDate = '05-15-' + str(year)
endDate = '08-31-' + str(year)
recurring = False

# compile into an area request
task = {
    'task_type': task_type,
    'task_name': task_name,
    'params': {
         'dates': [
         {
             'startDate': startDate,
             'endDate': endDate
         }],
         'layers': prodLayer,
         'output': {
                 'format': {
                         'type': outFormat}, 
                         'projection': proj},
         'geo': nps,
    }
}

# submit
task_response = r.post('{}task'.format(api), json=task, headers=head).json()
task_response
