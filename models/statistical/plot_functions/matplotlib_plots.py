import os

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns

from scipy.stats import shapiro

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

def plot_distribution_curve(df_data, row, feature, scaler, title, name, path_save):
    if create_plot_save_directory(path_save):
        
        data_1d = df_data[feature][~df_data[feature].isna()]
        
        data_2d = df_data[[feature]][~df_data[feature].isna()]
        data_scaled = scaler.fit(data_2d).transform(data_2d).reshape(-1)

        y = np.linspace(0, 1, data_1d.shape[0])

        fig, ax = plt.subplots(2, 2, figsize = (15, 10))
        fig.suptitle(title)
        
        for i in range(2):
            for j in range(2):
                ax[i][j].grid(True)
        
        ###Original data's plots
        old_limit_lower = round(row['old_limit_lower'], 3)
        old_limit_upper = round(row['old_limit_upper'], 3)
        ax_00_title = f"lower_lim = {old_limit_lower}, upper_lim = {old_limit_upper}"
        
        ax[0][0].set_title(ax_00_title)
        ax[0][0].scatter(data_1d.sort_values(), y, color = 'blue', label = f"{feature} original")
        
        #ax[0][0].axhline(y = old_limit_lower, color ='darkred', label = 'lower limit')
        #ax[0][0].axhline(y = old_limit_upper, color ='red', label = 'upper limit')
        
        shapiro_wilks = shapiro(data_1d.values)
        
        ax_01_title = f"Unscaled shapiro_stat = {round(shapiro_wilks[0], 3)}, shapiro_p = {round(shapiro_wilks[1], 3)}"
        ax[0][1].set_title(ax_01_title)
        ax[0][1].hist(data_1d, bins = 10, color = 'red', label = f"{feature} original dist")

        ###Scaled data's plots
        scaled_limit_lower = round(row['scaled_limit_lower'], 3)
        scaled_limit_upper = round(row['scaled_limit_upper'], 3)
        
        ax[1][0].scatter(sorted(data_scaled), y, color = 'blue', label = f"{feature} scaled")
        #ax[1][0].axhline(y = scaled_limit_lower, color ='darkred', label = 'lower limit')
        #ax[1][0].axhline(y = scaled_limit_upper, color ='red', label = 'upper limit')
        
        shapiro_stat = round(row['shapiro_statistic'], 3)
        shapiro_p = round(row['shapiro_p-value'], 3)
        ax_11_title = f"Scaled shapiro_stat = {shapiro_stat}, shapiro_p = {shapiro_p}"
        ax[1][1].set_title(ax_11_title)
        ax[1][1].hist(data_scaled, bins = 10, color = 'red', label = f"{feature} scaled dist")

        for i in range(2):
            for j in range(2):
                ax[i][j].legend()

        plt.savefig(path_save + name + '.png')
    
def plot_data_all(df_data_all, df_res, scaler, path_save):
    
    for index, row in df_res.iterrows():
        
        sheet = row['sheet']
        sheet_id = row['sheet_id']
        ttnr = row['ttnr']
        feature = row['feature']
        
        df_data = df_data_all[sheet_id]
        df_limit = df_data_all[sheet_id]
        
        title = f"{ttnr}/ {sheet}/ {feature} with {''}"
        name = f"{ttnr}_{sheet}_{feature}"
        
        plot_distribution_curve(df_data, row, feature, scaler, title, name, path_save)