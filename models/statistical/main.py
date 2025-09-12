import os

import numpy as np
import pandas as pd
import json

from datetime import datetime

from sklearn.preprocessing import PowerTransformer

import model_functions.calculate_attribute as mfca
import plot_functions.matplotlib_plots as pfmp
#import filter_distribution_functions.find_distribution_type as fffd
import distribution_check.calculate_fitnes as dccf

import warnings 
warnings.filterwarnings('ignore')

def find_path_to_desktop(path):
    path_elements = path.split('\\')
    res_path = ''

    for element in path_elements:
        
        res_path += element + '/'
        if element == 'Desktop':
            return res_path
    
    return res_path

def load_data(case_obj):
    ttnr = case_obj['ttnr']
    
    name_data = case_obj['name_data']
    name_limit = case_obj['name_limit']
    sheet_names = case_obj['sheet_names']
    
    path = case_obj['path']
    
    
    df_data_all = []
    df_limit_all = []
    
    for sheet in sheet_names:
        try:
            df_data = pd.read_excel(path + name_data, sheet_name = sheet)
            df_data_all.append(df_data)
        except  Exception as error:
            print(f"ERROR: {error} for ttnr = {ttnr} at DATA excel loading where sheet = {sheet}.")
            df_data_all.append([])
           
        try:
            df_lim = pd.read_excel(path + name_limit, sheet_name = sheet)
            df_limit_all.append(df_lim)
        except  Exception as error:
            print(f"ERROR: {error} for ttnr = {ttnr} at LIMIT excel loading where sheet = {sheet}.")
            df_limit_all.append([])
        
       
    return df_data_all, df_limit_all

def get_feature_nr_all(df_all):
    res_nr = 0
    
    for df in df_all:
        res_nr += len(df.columns[1:])
    
    return res_nr

def get_valid_feature_nr_all(df_all, min_value_nr):
    res_nr = 0
    
    for df in df_all:
        feature_all = df.columns[1:]
        
        for feature in feature_all:
            if len(df[feature].unique()) >= int(min_value_nr):
                res_nr += 1
    
    return res_nr

def run_rule_all_on_valid_feature_all(df_res, rule_all):
    for rule in rule_all:
        df_res = df_res[df_res[rule] >= float(rule_all[rule])]
        
    return df_res

def save_df(df, path_save, name):
    directory_name = path_save

    try:
        os.makedirs(directory_name)
    except FileExistsError:
        pass
    except PermissionError:
        print(f"ERROR: Permission denied: Unable to create '{directory_name}'.")
        return
    except Exception as e:
        print(f"ERROR: An error occurred: {e}")
        return
    
    df.to_excel(path_save + name)
    
def run(config_obj):
    run_info = []
    cases = config_obj['cases']
    
    print(f"Application START, {len(cases)} CASES to process")
    
    success_count = 0
    for i, case in enumerate(cases):
        ttnr = case['ttnr']
  
        name_data = case['name_data']
        name_limit = case['name_limit']
        sheet_names = case['sheet_names']
        
        path = case['path']
        path_save = case['path_save']
        
        print(f"\tCASE {i+1} process has STARTED, ttnr = {ttnr} with DATA file name = {name_data} aand LIMIT file name = {name_limit}")
        
        #DATA loading
        print("\t\tDATA loading")
        df_data_all, df_limit_all = load_data(case)
        
        #DATA processing
        print("\t\tDATA processing")
        scaler = PowerTransformer()
        print_info = True
        df_res = mfca.calculate_attributes_data_all(df_data_all, df_limit_all, case, scaler, print_info)
        df_res['feature_unique'] = df_res.apply(lambda x: f"{x['sheet']}_{x['feature']}", axis = 1)
        
        df_res_passed = run_rule_all_on_valid_feature_all(df_res, case['rule_all'])
        df_res['status'] = df_res['feature_unique'].apply(lambda x: 1 if x in df_res_passed['feature_unique'].values else 0)
        df_res_failed = df_res[df_res['status'] == 0]
        
        '''
        #FIND alternate distribution
        print("\t\tFIND alternate distribution")
        
        search_type = 'given'
        distribution_types = ['laplace_asymmetric', 'dweibull', 'genhyperbolic', 'dgamma', 'laplace', 'arcsine'] 
        dist_plot_path_save = f"{path_save}dist_plot_failed/"
        df_f_dist_all = fffd.get_distribution_all(df_data_all, df_res_failed, dist_plot_path_save, search_type, distribution_types)
        save_df(df_f_dist_all, path_save, f"{name_data.split('.')[0]}_not_normal_distribution.xlsx")
        '''
       
        #CALCULATE alternate distribution quality
        print("\t\tCALCULATE alternate distribution")
        acceptance_limit = float(case['rule_all']['shapiro_statistic'])
        #df_fitness_info = dccf.calc_fitness_measure_all(df_data_all, df_f_dist_all, acceptance_limit)
        df_fitness_info = dccf.calc_fitness_measure_all_distribution(df_data_all, df_res_failed, acceptance_limit)
        save_df(df_fitness_info, path_save, f"{name_data.split('.')[0]}_alternate_distribution.xlsx")
        
        ######################################
        data_size = df_data_all[0].shape[0]
        
        feature_nr_all = get_feature_nr_all(df_data_all)
        feature_valid_nr_all = get_valid_feature_nr_all(df_data_all, case['min_value_nr'])
        
        feature_nr_investigated = df_res['feature'].shape[0]
        feature_nr_passed = df_res_passed.shape[0]
        pass_ratio = feature_nr_passed/feature_nr_investigated
            
        #Case info saving
        run_info.append([ttnr, name_data, data_size,
                         feature_nr_all, feature_valid_nr_all,
                         feature_nr_investigated, feature_nr_passed,
                         pass_ratio
                        ])
        
        #DATA saving
        print("\t\tDATA saving")
        
        save_df(df_res, path_save, f"{name_data.split('.')[0]}_all.xlsx")
        save_df(df_res_passed, path_save, f"{name_data.split('.')[0]}_passed.xlsx")
        #save_df(df_res_failed, path_save, f"{name_data.split('.')[0]}_failed_results.xlsx")
        
        
        #Plott case features
        print("\t\tPlotting")
        
        if case['plott_passed'] == 'True':
            plot_path_save = f"{path_save}passed/"
            pfmp.plot_data_all(df_data_all, df_res_passed, scaler, plot_path_save)
            
        if case['plott_failed'] == 'True':
            plot_path_save = f"{path_save}failed/"
            pfmp.plot_data_all(df_data_all, df_res_failed, scaler, plot_path_save)
        
        print(f"\tCase {i+1} for ttnr = {ttnr} and DATA file = {name_data} was SUCCESSFUL!")
    
    #For loop END
    df_run_info = pd.DataFrame(run_info, columns = ['ttnr', 'name_data', 'data_size',
                                                    'feature_nr_all', 'feature_valid_nr_all', 
                                                    'feature_nr_investigated', 'feature_nr_passed',
                                                    'pass_ratio'])
    
    now = str(datetime.now()).replace(':', '_')
    save_df(df_run_info, path_save, f"run_info_{now}.xlsx")
    
    print(f"Application RUN terminated at: {now}")
        

def main():
    print("Enter config_obj.json files path: ", end = ' ')
    config_obj_path = ''
    config_obj_path = input()
    print("config_obj.json files path = \'" + config_obj_path + "\'")

    if len(config_obj_path) == 0:
        print('Configuration path was NOT given!')
        
        config_obj_path = find_path_to_desktop(os.getcwd()) + 'config_obj.json'
        #config_obj_path += 'C:/Users/JEK2BP/Desktop/HLA/exe/input_dir/config_obj.json'

        print('Changing to default path: ' + config_obj_path)
        print()
    else:
        config_obj_path += 'config_obj.json'

    try:
        with open(config_obj_path, 'r') as file:
            config_obj = json.load(file)
    except FileNotFoundError as error:
        print(f"ERROR: given configuration path was incorrect!:  {config_obj_path}, {error}")
        return False
       
    run(config_obj)
    print("Press Enter ot Exit: ", end = ' ')
    config_obj_path = input()
    return True
    
if __name__ == "__main__":
    main()