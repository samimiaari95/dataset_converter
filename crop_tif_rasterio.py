import json
import glob
import os
import geopandas as gpd
import rasterio
from rasterio.mask import mask
from calendar import monthrange, isleap
from osgeo import gdal
import numpy as np
import pandas as pd



def getFeatures(gdf):
    """Function to parse features from GeoDataFrame in such a manner that rasterio wants them"""
    return [json.loads(gdf.to_json())['features'][0]['geometry']]


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
    shp_dir = r"C:\Users\Sami\My Drive\tesi\shpfile\merged_features"
    shp_files = [os.path.join(shp_dir, x) for x in os.listdir(shp_dir) if '.shp' in x]

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
            out_tif= tifname.replace('prepare_ET', 'tiffiles').replace('.tif', f'_{subbasin}_{date}.tif')
            with rasterio.open(out_tif, "w", **out_meta) as dest:
                dest.write(clipped_array)
                dest.close()
            dest = None
            out_tifs[f'{subbasin}'] = out_tif
    return out_tifs, date


def read_bands(tifname):
    daily_data = gdal.Open(tifname)
    nb_bands = daily_data.RasterCount
    if nb_bands != 24:
        raise Exception(f"number of bands not equal to 24 but actually {nb_bands}")
    hourly = []
    for band in range(nb_bands):
        band += 1
        srcband = daily_data.GetRasterBand(band)
        stats = srcband.GetStatistics(True, True)
        mean = stats[2]
        hourly.append(mean)
    return np.average(hourly)


def read_cropped():
    tif_files = glob.glob("C:/Users/Sami/Desktop/tesi_desk/datasets/test_hdf_to_tiff/evaporation_cropped_tif/" + "*.tif")
    #tif_files = ["C:/Users/Sami/My Drive/tesi/prepare_ET/evaporation_1983-2.tif", "C:/Users/Sami/My Drive/tesi/prepare_ET/evaporation_1983-3.tif"]

    year = 1983
    results = {'date': [], 'bahr_el_ghazal': [], 'bahr_el_jebel': [], 'bako_akobbo-sobat': [], 'blue_nile': [], 'lake_albert': [], 'lake_victoria': [], 'main_nile': [], 'tekeze_atbara': [], 'victoria_nile': [], 'white_nile': []}
    columns = [x for x in results.keys()]
    et = pd.DataFrame(columns=columns)
    for tif_file in tif_files:
        name = os.path.basename(tif_file)
        subbasin_date = name.rsplit('_', 1)
        date = subbasin_date[-1].replace('.tif','')
        subbasin_listname = subbasin_date[0].split('_')
        subbasin_listname.pop(0)
        subbasin_listname.pop(0)
        subbasin_name = '_'.join(subbasin_listname)
        daily_et = read_bands(tif_file)
        if date in et['date'].to_list():
            #idx = et['date'].to_list()
            et.loc[et['date']==date, f'{subbasin_name}'] = daily_et
        else:
            data = {'date': date, 'bahr_el_ghazal': 0, 'bahr_el_jebel': 0, 'bako_akobbo-sobat': 0, 'blue_nile': 0, 'lake_albert': 0, 'lake_victoria': 0, 'main_nile': 0, 'tekeze_atbara': 0, 'victoria_nile': 0, 'white_nile': 0}
            #et.loc[f'{date}'][f'{subbasin_name}'] = daily_et
            data[f'{subbasin_name}'] = daily_et
            et = et.append(data, ignore_index=True)
        print(et)
    et.to_csv(f'C:/Users/Sami/My Drive/tesi/evaporation_{year}.csv', index=False)
    return

def crop_and_read():
    tif_files = glob.glob("C:/Users/Sami/My Drive/tesi/prepare_ET/" + "*.tif")
    year = 1983
    results = {'date': [], 'bahr_el_ghazal': [], 'bahr_el_jebel': [], 'bako_akobbo-sobat': [], 'blue_nile': [], 'lake_albert': [], 'lake_victoria': [], 'main_nile': [], 'tekeze_atbara': [], 'victoria_nile': [], 'white_nile': []}

    for tif_file in tif_files:
        name = os.path.basename(tif_file)
        year_day = name.split('_')[-1].replace('.tif','')
        print(f"cropping {year_day}")
        day_idx = year_day.split('-')[-1]
        cropped_tifs, date = crop_tif(tif_file, year, day_idx)
        if cropped_tifs:
            for subbasin in cropped_tifs.keys():
                daily_et = read_bands(cropped_tifs[f'{subbasin}'])
                results[f'{subbasin}'].append(daily_et)
            results['date'].append(date)
            output = pd.DataFrame(results)
            output.to_csv(f'C:/Users/Sami/My Drive/tesi/evaporation_{year}.csv', index=False)


read_cropped()