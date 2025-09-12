import os

import numpy as np
import pandas as pd
from fitter import Fitter, get_common_distributions, get_distributions

def get_distribution_data(data, search_type, distribution_types = None):
        
    if search_type == 'given':
        pass
    elif search_type == 'common':
        distribution_types = get_common_distributions()
    elif search_type == 'all':
        distribution_types = get_distributions()
    else:
        return False
    
    f = Fitter(data,
               distributions = distribution_types)
    f.fit()
    
    df_dist = f.summary(plot=False, Nbest = 1)
    #plot_dist = f.plot()
    
    return df_dist#, plot_dist

def create_plot_save_directory(path_save):
    
    try:
        os.makedirs(path_save)
    except FileExistsError:
        pass
    except PermissionError:
        print(f"Permission denied: Unable to create '{directory_name}'.")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    
    return True

def get_distribution_all(df_data_all, df_attribute_all, path_save, search_type, distribution_types = None):
    #create_plot_save_directory(path_save)
    
    df_dist_all = []
    
    for index, row in df_attribute_all.iterrows():
        sheet = row['sheet']
        sheet_id = row['sheet_id']
        ttnr = row['ttnr']
        feature = row['feature']
        
        df = df_data_all[sheet_id][[feature]]
        data = df[feature][~df[feature].isna()].values
        
        #df_dist, plot = get_distribution_data(data, search_type, distribution_types = None)
        df_dist = get_distribution_data(data, search_type, distribution_types)
        
        df_dist['sheet'] = sheet
        df_dist['sheet_id'] = sheet_id
        df_dist['ttnr'] = ttnr
        df_dist['feature'] = feature
        
        df_dist_all.append(df_dist)
        
        '''name = f"{ttnr}_{sheet}_{feature}_distribution"
        plot.savefig(path_save + name + '.png')'''
    
    df_dist_all = pd.concat(df_dist_all, axis = 0)

    
    return df_dist_all
        