# -*- coding: utf-8 -*-
"""Soil moisture MERRA

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Ery7cifeADE31BK0uKt8FpC_cshFH0z_
"""

from google.colab import drive
drive.mount('/content/drive')
!pip install xarray
!pip install rioxarray
!pip install geopandas

import xarray as xr 
import rioxarray as rio
import geopandas as gpd
from shapely.geometry import mapping
from osgeo import gdal
import sys
import glob
import numpy as np
import re
import pandas as pd

def nc_to_raster(filename, shp, subbasin):
  nc_file = xr.open_dataset(filename)
  globalr = nc_file['GWETPROF']
  globalr = globalr.rio.set_spatial_dims('lon', 'lat')
  Niler = globalr.rio.set_crs(shp.crs).rio.clip(shp.geometry.apply(mapping))
  name = filename.split('/')[-1].replace('.nc4','.tif')
  tifname = subbasin + name
  Niler.rio.to_raster(f"/content/drive/MyDrive/tesi/tiffiles/{tifname}")
  return tifname

def nc_to_rasterfile(filename, shp, subbasin):
  nc_file = xr.open_dataset(filename)
  globalr = nc_file['GWETPROF']
  globalr = globalr.rio.set_spatial_dims('lon', 'lat')
  Niler = globalr.rio.set_crs(shp.crs).rio.clip(shp.geometry.apply(mapping))
  name = filename.split('/')[-1].replace('.nc4','.tif')
  tifname = subbasin + name
  Niler.rio.to_raster(f"/content/drive/MyDrive/tesi/tiffiles/{tifname}")
  return tifname

def read_bands(tifname):
  daily_data = gdal.Open(f"/content/drive/MyDrive/tesi/tiffiles/{tifname}")
  #daily_data = tifname
  daily_sm = []
  for band in range(daily_data.RasterCount):
      band += 1
      srcband = daily_data.GetRasterBand(band)

      stats = srcband.GetStatistics( True, True )
      mean = stats[2]
      daily_sm.append(mean)
  return np.average(daily_sm)

def from_to(date):
  year = date.split("-")[0]
  month = date.split("-")[1]
  y_m = [year, month]
  csvdate = "-".join(y_m)
  return csvdate

def get_date(filename):
  output = re.findall('[0-9]{5,9}', filename)
  rlist = list(output[0])
  year = "".join(rlist[0:4])
  month = "".join(rlist[4:6])
  day = "".join(rlist[6:])
  date = f"{year}-{month}-{day}"
  return date

files = glob.glob("/content/drive/MyDrive/tesi/ncfiles/"+ '/*.nc4')

shp_files = glob.glob("/content/drive/MyDrive/tesi/shpfile/"+ '/*.shp')
error = {'error': []}
results = {'date': [], 'bahr_el_ghazal': [], 'bahr_el_jebel': [], 'bako_akobbo-sobat': [], 'blue_nile': [], 'lake_albert': [], 'lake_victoria': [], 'main_nile': [], 'tekeze_atbara': [], 'victoria_nile': [], 'white_nile': []}
for file in files:

  date = get_date(file)
  if files.index(file) == 0:
    csvfrom = from_to(date)
  if files.index(file) == len(files)-1:
    csvto = from_to(date)
  all_subbasins = {'bahr_el_ghazal': [], 'bahr_el_jebel': [], 'bako_akobbo-sobat': [], 'blue_nile': [], 'lake_albert': [], 'lake_victoria': [], 'main_nile': [], 'tekeze_atbara': [], 'victoria_nile': [], 'white_nile': []}
  try:
    for shp_file in shp_files:
      shp = gpd.read_file(f"{shp_file}")
      subbasin = shp_file.split('/')[-1].replace('.shp','')
      tifname = nc_to_raster(file, shp, subbasin)
      daily_sm = read_bands(tifname)
      all_subbasins[f'{subbasin}'].append(daily_sm)
    for key in list(all_subbasins.keys()):
      results[f'{key}'].append(all_subbasins[f'{key}'][0])
    results['date'].append(date)
    print(f"finished {date}")
  except:
    print(f"retry for {file}")
    error['error'].append(date)
soil_moisture = pd.DataFrame(results)
soil_moisture.to_csv(f"/content/drive/MyDrive/tesi/sm{csvfrom}_{csvto}.csv", index=False, mode="w")
errorfiles = pd.DataFrame(error)
errorfiles.to_csv(r"/content/drive/MyDrive/tesi/sm_error.csv", index=False, mode="w")