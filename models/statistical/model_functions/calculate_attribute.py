import os

import numpy as np
import pandas as pd
import json

from scipy.stats import shapiro, norm
from scipy.integrate import quad

from sklearn.preprocessing import PowerTransformer

def integrand(a, b, mu, sigma):
    return norm.cdf(b, loc=mu, scale=sigma) - norm.cdf(a, loc=mu, scale=sigma)

def calc_new_limits(old_cent, old_limit_min, old_limit_max, 
                    old_std_min, old_std_max,
                    new_cent = 0, new_std_min = 1, new_std_max = 1):
        
    new_limit_min = new_cent - abs((old_cent - old_limit_min)/old_std_min)/new_std_min
    new_limit_max = new_cent + abs((old_cent - old_limit_max)/old_std_max)/new_std_max
        
    return new_limit_min, new_limit_max

def calculate_attributes_data(df_data, df_limit, case, i, scaler, print_info = False):
    ttnr = case['ttnr']
    sheet = case['sheet_names'][i]
    ppm = float(case['ppm'])
    
    feature_all = df_data.columns[1:]
    
    res_all = []
    
    for feature in feature_all:
        if print_info:
            print(f"\t\t\tfeature = {feature}")
         
        try:
            old_limit_lower = df_limit[feature].iloc[0]
            old_limit_upper = df_limit[feature].iloc[1]
            print('OK 00')
        except KeyError as error:
            print(f"DATA ERROR: for ttnr = {ttnr}. At LIMIT file, sheet = {sheet}, MISSING column = {feature}!")
            continue
        
        if old_limit_lower != None  and old_limit_upper != None:
            data_1d = df_data[feature][~df_data[feature].isna()]
            data_2d = df_data[[feature]][~df_data[feature].isna()]
            print('OK 01')

            if len(data_1d.unique()) < 2:
                print('OK 01.1')
                continue
            
            print('OK 01.2')
            data_scaled = scaler.fit(data_2d).transform(data_2d).reshape(-1)
            print('OK 01.3')
            
            #print(data_scaled)
            sw_test = shapiro(data_scaled)
            print('OK 01.4')
            
            old_cent = data_1d.median()
            print('OK 02')

            lower_old = list(data_1d[data_1d < old_cent].values) + list(old_cent + abs(old_cent - data_1d[data_1d < old_cent].values))
            upper_old = list(old_cent - abs(old_cent - data_1d[old_cent <= data_1d].values)) + list(data_1d[old_cent <= data_1d])
            old_std_lower = np.std(lower_old)                          
            old_std_upper = np.std(upper_old)
            
            print('OK 03')

            lower_new = list(data_scaled[data_scaled < 0]) + list(0 + abs(0 - data_scaled[data_scaled < 0]))
            upper_new = list(0 - abs(0 - data_scaled[0 <= data_scaled])) + list(data_scaled[0 <= data_scaled])
            new_std_lower = np.std(lower_new)                          
            new_std_upper = np.std(upper_new)
            
            print('OK 04')
        
            new_limit_lower, new_limit_upper  = calc_new_limits(old_cent, old_limit_lower, old_limit_upper, 
                                                                old_std_lower, old_std_upper,
                                                                0,  1,  1)

            P = integrand(new_limit_lower, new_limit_upper, 0, 1) - ppm

            z_lower = abs(0 - new_limit_lower)
            z_upper = abs(0 - new_limit_upper)

            res_all.append([sheet, i, ttnr, feature, 
                            sw_test[0], sw_test[1],
                            old_limit_lower, old_limit_upper,
                            new_limit_lower, new_limit_upper,
                            P,
                            z_lower, norm.sf(z_lower), 
                            z_upper, norm.sf(z_upper)])
            
            print('OK 05')
        else:
            print(f"DATA ERROR: for ttnr = {ttnr}. At LIMIT file, sheet = {sheet}, column = {feature} MISSING VALUE!")
        
    return res_all

def calculate_attributes_data_all(df_data_all, df_limit_all, case, scaler, print_info = False):
    
    res_attribute_all = []
    
    i = 0
    for df_data, df_limit in zip(df_data_all, df_limit_all):
        if print_info:
            print(f"\t\tSheet = {case['sheet_names'][i]}")
        
        feature_data_all = df_data.columns
        feature_limit_all = df_limit.columns
        
        if (feature_data_all[1:] != feature_limit_all[1:]).all():
            print(f"ERROR: {error} for ttnr = {case['ttnr']}. DATA file columns and LIMIT file columns at sheet = {case['sheet_names'][i]} are missmatching!")
            return False
        
        res_attribute = calculate_attributes_data(df_data, df_limit, case, i, scaler, print_info)
        res_attribute_all += list(res_attribute)
        
        i+=1
       
    df_res = pd.DataFrame(res_attribute_all, columns = ['sheet', 'sheet_id', 'ttnr', 'feature',
                                                        'shapiro_statistic', 'shapiro_p-value',
                                                        'old_limit_lower', 'old_limit_upper',
                                                        'scaled_limit_lower', 'scaled_limit_upper',
                                                        'probability',
                                                        'z_min', 'p_min',
                                                        'z_max', 'p_max'])
    
    df_res['final_significance'] = df_res['shapiro_statistic'] * (1 - (df_res['p_min'] + df_res['p_max'])/2)
    
    return df_res