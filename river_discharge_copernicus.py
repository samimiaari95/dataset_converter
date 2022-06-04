# -*- coding: utf-8 -*-
"""River discharge Copernicus

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1MoR3IHtaOH-HonO2rFAHf4hNit_98uUF
"""


from osgeo import gdal, gdal_array
import json
import os
import geopandas as gpd
import rasterio
from rasterio.mask import mask
import re
import os
import warnings
import glob
from calendar import monthrange, isleap
import numpy as np
import pandas as pd

def getFeatures(gdf):
    """Function to parse features from GeoDataFrame in such a manner that rasterio wants them"""
    return [json.loads(gdf.to_json())['features'][0]['geometry']]

def get_date(filename):
    date = filename.split('_')[0]
    return date

def day_month_year(day_value, year):
    # ----------------get monthly data---------------------#
    day_index = 0
    for month in range(1,13):
        for day in range(1, monthrange(int(year), int(month))[1]+1):
            day_index += 1
            if int(month) == 2 and day > 28 and day_index == int(day_value):
                return None, True
            if day_index == int(day_value):
                return f'{year}-{str(month).zfill(2)}-{str(day).zfill(2)}', False

def crop_tif(tifname, year, key):
#    shp_dir = r"C:\Users\Sami\My Drive\tesi\shpfile\merged_features"
#    shp_files = [os.path.join(shp_dir, x) for x in os.listdir(shp_dir) if '.shp' in x]
    shp_files = glob.glob("C:/Users/Sami/My Drive/tesi/shpfile/merged_features/"+ '/*.shp')

    date, skip = day_month_year(key, year)
    out_tifs = {}
    if not skip:
        for shp_file in shp_files:
            subbasin = os.path.basename(shp_file).replace('.shp','')
            shp = gpd.read_file(shp_file)
            tif  = rasterio.open(tifname)
            coords = getFeatures(shp)
            clipped_array, clipped_transform = mask(dataset=tif, shapes=coords, crop=True)
            shp = shp.to_crs(tif.crs)
            out_meta = tif.meta.copy()
            out_meta.update({"driver": "GTiff",
                             "height": clipped_array.shape[1],
                             "width": clipped_array.shape[2],
                             "transform": clipped_transform})
            out_tif= tifname.replace('river_discharge_tif', 'river_discharge_subtif').replace('.tif', f'_{subbasin}_{date}.tif')
            with rasterio.open(out_tif, "w", **out_meta) as dest:
                dest.write(clipped_array)
                dest.close()
            dest = None
            out_tifs[f'{subbasin}'] = out_tif
    return out_tifs, date

def read_bands(tifname):
  daily_data = gdal.Open(tifname)
  nb_bands = daily_data.RasterCount
  #if nb_bands != 24:
  #    raise Exception(f"number of bands not equal to 24 but actually {nb_bands}")
  hourly = []
  for band in range(nb_bands):
      band += 1
      srcband = daily_data.GetRasterBand(band)
      stats = srcband.GetStatistics(True, True)
      mean = stats[2]
      hourly.append(mean)
  return np.average(hourly)


def read_bands_new(filename):
  daily_data = gdal.Open(filename)
  nb_bands = daily_data.RasterCount
  hourly = []
  for band in range(nb_bands):
      band += 1
      srcband = daily_data.GetRasterBand(band)
      # TODO this doesn't work since it should load specific bands not all the file
      rasterArray = gdal_array.LoadFile(filename)
      nodata = -9999
      rasterArray = np.ma.masked_equal(rasterArray, nodata)
      mean = np.mean(rasterArray)
      #stats = srcband.GetStatistics(True, True)
      #mean = stats[2]
      hourly.append(mean)
  return np.average(hourly)


#def main():
warnings.filterwarnings("ignore")
filenames = glob.glob("C:/Users/Sami/Desktop/tesi_desk/datasets/river_discharge/"+ '/*.grib')
#src_filename = r"C:\Users\Sami\Desktop\tesi_desk\datasets\river_discharge\river_discharge_1984.grib"
for filename in filenames:
    # Open grib file
    src_ds = gdal.Open(filename)
    print('Opened')
    #print(src_ds)

    # Open output format driver
    out_form= "GTiff"
    year = re.findall('[0-9]{3,9}', filename)[0]

    # get daily data
    hour_index = 0
    number_bands = src_ds.RasterCount
    daily_bands = {f'{x}':[x] for x in range(1, int(number_bands) +1)}

    # output dictionary
    results = {'date': [], 'bahr_el_ghazal': [], 'bahr_el_jebel': [], 'bako_akobbo-sobat': [], 'blue_nile': [], 'lake_albert': [], 'lake_victoria': [], 'main_nile': [], 'tekeze_atbara': [], 'victoria_nile': [], 'white_nile': []}
    # gdal translate grib to tif, crop it, get the mean, save it in the output dictionary
    for key in daily_bands.keys():
        if int(key) > -1:
            dst_filename = f'C:/Users/Sami/Desktop/tesi_desk/datasets/river_discharge_tif/river_discharge_{year}-{key}.tif'
            print(f'creating {year}-{key}')
            # Output to new format using gdal.Translate. See https://gdal.org/python/ for osgeo.gdal.Translate options.
            dst_ds = gdal.Translate(dst_filename, src_ds, format=out_form, bandList=daily_bands[f'{key}'])
            print('cropping it')
            cropped_tifs, date = crop_tif(dst_filename, year, key)
            if cropped_tifs:
                for subbasin in cropped_tifs.keys():
                    daily_et = read_bands(cropped_tifs[f'{subbasin}'])
                    results[f'{subbasin}'].append(daily_et)
                results['date'].append(date)
                output = pd.DataFrame(results)
                output.to_csv(f'C:/Users/Sami/OneDrive - Politecnico di Milano/tesi/river_discharge_{year}.csv', index=False)
            dst_ds = None
            os.remove(dst_filename)

    print("finished")
    # Properly close the datasets to flush to disk

    src_ds = None