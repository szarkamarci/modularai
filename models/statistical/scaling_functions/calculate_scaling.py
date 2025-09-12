import os

import numpy as np
import pandas as pd
import json

from sklearn.preprocessing import PowerTransformer


def scale_feature_all(df, scaler, case, i):
    
    feature_all = df.columns
    
    if feature_all[1].lower() != 'sgid' and feature_all[1].lower() != 'dmc':
        print(f"ERROR: {error} for ttnr = {case['ttnr']}. DATA file first column at sheet {case['sheet_names'][i]} is not a product ID (sgid or dmc)!")
        return False
    
    df[feature_all[1:]] = scaler.fit(df[feature_all[1:]]).transform(df[feature_all[1:]])

def scale_df_all(df_all, scaler, case):
    
    i = 0
    for df in df_all:
        scale_feature_all(df, scaler, case, i)
        i+=1
    
    return True