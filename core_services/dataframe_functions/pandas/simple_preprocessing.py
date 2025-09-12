import numpy as np
import pandas as pd

def convert_to_str(x, defult = None):
    if x is None or pd.isna(x):
        return defult
    else:
        if isinstance(x, str):
            return x.strip()
        elif isinstance(x, float) or isinstance(x, int):
            return str(int(x))
        else:
            return str(x)
    
    return defult

def rename_columns(df: pd.DataFrame, rename_rule_all: list, print_info = False):
    if print_info:
        print(f"\trename_columns(): START")

    for rename_rule in rename_rule_all:
        column = rename_rule[0]
        new_column = rename_rule[1]

        if column in df.columns:
            if print_info:
                print(f"\t\trename_columns(): {column} -> {new_column}")

            df.rename(columns = {column: new_column}, inplace = True)
        else:
            print(f"\t\t\tERROR: Column '{column}' not found in DataFrame")
        
        
    if print_info:
        print(f"\trename_columns(): FINISH")
    return df
    
def convert_column_values(df : pd.DataFrame, conversion_rule_all: list, print_info = True):
    if print_info:
        print(f"\tconvert_column_values(): START")

    for conversion_rule in conversion_rule_all:
        column = conversion_rule[0]
        conversion_func = conversion_rule[1]

        if column in df.columns:
            if print_info:
                print(f"\t\tconvert_column_values(): {column} -> {conversion_func}")

            try:
                df[column] = df[column].apply(conversion_func)
            except Exception as e:
                print(f"\t\t\tERROR: for '{conversion_func}' exception {e} is raised")
        else:
            print(f"\t\t\tERROR: Column '{column}' not found in DataFrame")

    if print_info:
        print(f"\tconvert_column_values(): FINISH")
    return df
    
def convert_column_values(df : pd.DataFrame, conversion_rule_all: list, print_info = True):
    if print_info:
        print(f"\tconvert_column_values(): START")

    for conversion_rule in conversion_rule_all:
        column = conversion_rule[0]
        conversion_func = conversion_rule[1]

        if column in df.columns:
            if print_info:
                print(f"\t\tconvert_column_values(): {column} -> {conversion_func}")

            try:
                df[column] = df[column].apply(conversion_func)
            except Exception as e:
                print(f"\t\t\tERROR: for '{conversion_func}' exception {e} is raised")
        else:
            print(f"\t\t\tERROR: Column '{column}' not found in DataFrame")

    if print_info:
        print(f"\tconvert_column_values(): FINISH")
    return df
    

def filter_nan(df: pd.DataFrame, column_all: list, print_info = False):
    if print_info:
        print(f"\tfilter_nan(): START")

    n_beg = df.shape[0]

    for column in column_all:

        if column in df.columns:
            if print_info:
                print(f"\t\tfilter_nan(): {column}")

            df = df[df[column].notna()]
        else:
            print(f"\t\t\tERROR: Column '{column}' not found in DataFrame")
    
    n_end = df.shape[0]

    if print_info:
        print(f"\t\tfilter_nan(): from {n_beg} rows to {n_end} ({round((n_end - n_beg)/n_beg*100, 2)}%)")
        print(f"\tfilter_nan(): FINISH")
    return df
   

def filter_by_rules(df: pd.DataFrame, rule_all: list, print_info = False):
    if print_info:
        print(f"\tfilter_by_rules(): START")

    n_beg = df.shape[0]

    for rule in rule_all:
        column = rule[0]
        value_list = rule[1]

        if column in df.columns:
            if print_info:
                print(f"\t\tfilter_by_rules(): {column}") 

            df = df[df[column].isin(value_list)]
        else:
            print(f"\t\t\tERROR: Column '{column}' not found in DataFrame")
    
    n_end = df.shape[0]

    if print_info:
        print(f"\t\tfilter_by_rules(): from {n_beg} rows to {n_end} ({round((n_end - n_beg)/n_beg*100, 2)}%)")
        print(f"\tfilter_by_rules(): FINISH")

    return df
    
def drop_duplicates(df: pd.DataFrame, duplicate_cols: list, print_info = False):
    n_beg = df.shape[0]
    if print_info:
        print(f"\tdrop_duplicates(): FINISH")

    df.drop_duplicates(subset = duplicate_cols, inplace = True)

    n_end = df.shape[0]
    if print_info:
        print(f"\t\tdrop_duplicates(): from {n_beg} rows to {n_end} ({round((n_end - n_beg)/n_beg*100, 2)}%)")
        print(f"\tdrop_duplicates(): FINISH")

    return df

def run_preporcessing_steps(df: pd.DataFrame, config_obj: dict, print_info = False): 
    
    function_catalog = { 'rename_columns' : rename_columns, 
                         'filter_nan' : filter_nan, 
                         'convert_column_values' : convert_column_values, 
                         'filter_by_rules' : filter_by_rules, 
                         'drop_duplicates' : drop_duplicates,
                         'to_datetime' : to_datetime
                        } 
                        
    if print_info: print(f"\tall_steps(): START") 
    
    for function_name in config_obj:
        function = function_catalog[function_name] 
        df = function(df = df, **config_obj[function_name], print_info = print_info) 
        
    if print_info: 
        print(f"\tall_steps(): FINISH") 
        
    return df