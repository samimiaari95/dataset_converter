import geopandas as gpd
from shapely.geometry import mapping
from osgeo import gdal, gdal_array
import sys
import glob
import numpy as np
import json
import os
import warnings
import shutil
import rasterio
from rasterio.mask import mask
import re
import pandas as pd
#from google.colab import drive
#drive.mount('/content/drive')

def getFeatures(gdf):
    """Function to parse features from GeoDataFrame in such a manner that rasterio wants them"""
    return [json.loads(gdf.to_json())['features'][0]['geometry']]

def crop_tif(tifname):
  # TODO change directoy here
  shp_files = glob.glob("G:/My Drive/tesi/mod_shp/"+ '/*.shp')

  out_tifs = {}
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
      # TODO change subtiff directory here
      out_tif= tifname.replace("raw NDVI","NDVI_IRR").replace('.tif', f'_{subbasin}.tif')
      with rasterio.open(out_tif, "w", **out_meta) as dest:
          dest.write(clipped_array)
          dest.close()
      dest = None
      out_tifs[f'{subbasin}'] = out_tif
  return out_tifs

def read_bands(tifname):
  weekly_data = gdal.Open(tifname)
  srcband = weekly_data.GetRasterBand(1)
  arr = srcband.ReadAsArray()
  stats = srcband.GetStatistics(True, True)
  mean = stats[2]
  return mean

def read_bands_new(filename):
  weekly_data = gdal.Open(filename)
  srcband = weekly_data.GetRasterBand(1)
  rasterArray = gdal_array.LoadFile(filename)
  nodata = -9999
  rasterArray = np.ma.masked_equal(rasterArray, nodata)
  mx = np.amax(rasterArray)
  mn = np.amin(rasterArray)
  avg = (float(mx)+float(mn))/2
  #mean = np.mean(rasterArray)
  return avg

def get_date(filename):
  output = re.findall('[0-9]{4,9}', filename)
  rlist = list(output[0])
  year = "".join(rlist[0:4])
  week = "".join(rlist[-2:])
  # day = "".join(rlist[6:])
  date = f"{year}-{week}"
  return date


def get_the_date(filename):
  year_week = filename.split('_')[1].replace('.tif','')
  return year_week

#files = glob.glob("/content/drive/MyDrive/tesi/tiffiles/" + "/*.tif")
warnings.filterwarnings("ignore")
#already_done = pd.read_csv(r"G:\My Drive\tesi\NDVI_mainnile_irrigatedarea.csv")

#already_done2 = pd.read_csv(r"G:\My Drive\tesi\NDVI_mainnile_irrigatedarea_v2.csv")
#df =pd.concat([already_done, already_done2], ignore_index=True)
#skip_list = df['date'].to_list()
# TODO change raw NDVI directory here
path = r'G:\My Drive\tesi\raw NDVI'
main_nile_tif = [os.path.join(path, x) for x in os.listdir(path)]
results = {'date': [], 'main_nile_irrigated_area_wgs84': []}

for file in main_nile_tif:
  idx = main_nile_tif.index(file)
  date = get_the_date(file)
  print(f"performing for {date} as {idx} out of {len(main_nile_tif)}")
  #if date not in skip_list:
  cropped_tifs= crop_tif(file)
  if cropped_tifs:
    for subbasin in cropped_tifs.keys():
        weekly_NDVI = read_bands_new(cropped_tifs[f'{subbasin}'])
        results[f'{subbasin}'].append(weekly_NDVI)
    results['date'].append(date)
    output = pd.DataFrame(results)
    # TODO change output directory here
    output.to_csv('G:/My Drive/tesi/NDVI_main_nile_irr_avgmaxmin.csv', index=False)
    #os.remove(file)
    # TODO change where to move raw files
    #shutil.move(file,file.replace('rawNDVI','finished_raw_NDVI'))