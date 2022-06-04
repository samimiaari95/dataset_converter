from cgi import test
from email import header
import pandas as pd
import numpy as np
import os


def search_input_file(input_folder, ext, keyword, onefile=True):
    
    myfile = [os.path.join(input_folder, file_path) for file_path in os.listdir(
        input_folder) if ext in file_path and keyword in file_path]
    if not myfile:
        raise Exception(
            "No files were found with the extension and keyword provided")
    if onefile:
        if len(myfile) > 1:
            raise Exception(
                f"You are searching for 1 file with the extension {ext} and keyword/keyname {keyword} however {len(myfile)} were found, either change your keyword or use another function to search for multiple files")
        else:
            return myfile[0]
    else:
        return myfile

def main():
    directory = "C:/Users/Sami/Desktop/tesi_desk/datasets/test_hdf_to_tiff/daily_sm"
    var = "soil_moisture" # change here
    subbasin = 'main_nile'
    conv = 273.15

    input_files = search_input_file(directory, '.csv', 'sm', onefile=False)
    #data1 = pd.read_csv(f'{directory + "/main_nile_obs_tas_min_1983-2005.txt"}', header = None, sep='\s+')
    #data2 = pd.read_csv(f'{directory + "/main_nile_obs_tas_min_2006-2016.txt"}', header = None, sep='\s+')
    #for row in data1.itertuples():
    #    temp = data1.loc[row.Index][1]
    #    data1.at[row.Index, 1] = temp + conv
    wind_speed = pd.DataFrame()
    for file in input_files:
        data = pd.read_csv(file)
        wind_speed = pd.concat([wind_speed, data], ignore_index=True)
    #wind_speed = pd.read_csv(directory+'/sorteddate_soil_moisture.csv')
    #headers = ['date', f'{var}']
    #indicator.to_csv(f'{directory + f"/{var}.csv"}', index=False, header=headers)
    wind_speed = wind_speed.sort_values(by='date').reset_index()
    del wind_speed['index']

    
    indexes = [row.Index for row in wind_speed.itertuples() if '02-29' in wind_speed.loc[row.Index]['date']]

    wind_speed = wind_speed.drop(wind_speed.index[indexes]).reset_index()
    del wind_speed['index']

    #####input_data = pd.read_csv(f'{directory + f"/{var}.csv"}')
    data = {'year':[], 'week':[], f'{var}':[]}
    for year in range(0,36):
        for week in range(0,52):
            print(f"week: {week}, year: {year}")
            weekdays = [wind_speed.loc[(year*365)+week*7+i][f'{subbasin}'] for i in range(0,7)]
            data['year'].append(1981 + year)
            data['week'].append(week + 1)
            data[f'{var}'].append(np.sum(weekdays))
            #data[f'{var}'].append(np.average(weekdays))


    agg_results = pd.DataFrame(data)
    agg_results.to_csv(f'{directory + "/agg_" + var + ".csv"}', index=False)
    #wind_speed.to_csv(f'{directory + "/" + var + ".csv"}', index=False)


main()