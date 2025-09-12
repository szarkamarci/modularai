# Databricks notebook source
# MAGIC %pip install openpyxl
# MAGIC
# MAGIC %restart_python

# COMMAND ----------

import numpy as np
import pandas as pd
import json

# COMMAND ----------

import main

# COMMAND ----------

main.main()

# COMMAND ----------

#input_dir/
d

# COMMAND ----------



# COMMAND ----------



# COMMAND ----------



# COMMAND ----------



# COMMAND ----------



# COMMAND ----------



# COMMAND ----------



# COMMAND ----------

print(

# COMMAND ----------

def plot_data_and_dist(df, feature):
    data = sorted(df[feature][~df[feature].isna()].values)
    min_d = data[0]
    max_d = data[-1]
    
    n = len(data)
    y = np.linspace(0, 1, n)
    
    fig, ax = plt.subplots(1, 2, figsize = (14, 5))
    fig.suptitle(feature) 
    
    ax[0].grid(True)
    ax[0].scatter(data, y, color = 'blue', label  = feature)
    ax[0].legend()
    
    kde = gaussian_kde(data)
    x_vals = np.linspace(min_d, max_d, 16)
    y_vals = kde(x_vals)
    
    ax[1].grid(True)
    ax[1].hist(data, bins = 10, color = 'red', label = 'Histogram')
    ax[1].legend()
    
    ax_1 = ax[1].twinx()
    ax_1.plot(x_vals, y_vals, color = 'green', label = 'KDE')
    
    plt.show()

# COMMAND ----------



# COMMAND ----------

'''
C:/Users/JEK2BP/Desktop/HLA/exe/
''''''

# COMMAND ----------

path = 'C:/Users/JEK2BP/Desktop/HLA/exe/21_03/'
name = '02033BA487_TTMMICParameters.xlsx_failed_feature_best_distribution.xlsx'

# COMMAND ----------

df_dist = pd.read_excel(path + name)
df_dist = df_dist.rename(columns = {'Unnamed: 0': "type"})
df_dist['feature_unique'] = df_dist.apply(lambda x: f"{x['sheet']}_{x['feature']}", axis = 1)

df_dist_best = df_dist.drop_duplicates('feature_unique')#.sort_values('sumsquare_error')

# COMMAND ----------

df_dist.head(20)

# COMMAND ----------

df_dist[df_dist['type'] == 'laplace'].head(20)

# COMMAND ----------

df_dist['type'].value_counts()

# COMMAND ----------

selected_distribution  = ['dgamma', 'dweibull', 'genhyperbolic', 'laplace_asymmetric']

# COMMAND ----------

print(len(df_dist['feature_unique'].unique()))
print(len(df_dist['feature_unique'][df_dist['ks_pvalue'] >= 0.05].unique()))
print(len(df_dist['feature_unique'][(df_dist['ks_pvalue'] >= 0.05) & (df_dist['type'].isin(selected_distribution))].unique()))
print()

feature_in_dist_all = df_dist['feature_unique'][(df_dist['ks_pvalue'] >= 0.05) & 
                                                (df_dist['type'].isin(selected_distribution))].unique()
print(df_dist['type'][~df_dist['feature_unique'].isin(feature_in_dist_all)].value_counts())

# COMMAND ----------

df_dist[~df_dist['feature_unique'].isin(feature_in_dist_all)].sort_values('ks_pvalue', ascending = False)

# COMMAND ----------



# COMMAND ----------

path = "C:/Users/JEK2BP/Desktop/HLA/exe/input_dir/"
name = "02033BA487_TTMMICParameters.xlsx"

df_data = pd.read_excel(path + name, sheet_name = 'Rx_2024')

# COMMAND ----------

feature_all = df_data.columns[1:-4]

for feature in feature_all:
    print(feature)
    
    data = df_data[feature].values
    shape, loc, scale = stats.gamma.fit(data)
    ks_statistic, p_value = stats.kstest(data, 'gamma', args=(shape, loc, scale))
    print(f"Gamma - K-S Statistic: {ks_statistic}, P-value: {p_value}")

    loc, scale = stats.laplace.fit(data)
    ks_statistic, p_value = stats.kstest(data, 'laplace', args=(loc, scale))
    print(f"Laplace - K-S Statistic: {ks_statistic}, P-value: {p_value}")

    c, loc, scale = stats.weibull_min.fit(data)
    ks_statistic, p_value = stats.kstest(data, 'weibull_min', args=(c, loc, scale))
    print(f"Weibull - K-S Statistic: {ks_statistic}, P-value: {p_value}")

    '''gh = GeneralizedHyperbolic.fit(data)
    ks_statistic, p_value = stats.kstest(data, 'generalized_hyperbolic', args=gh)
    print(f"Generalized Hyperbolic - K-S Statistic: {ks_statistic}, P-value: {p_value}")'''

    df = df_data
    feature = feature
    plot_data_and_dist(df, feature)

# COMMAND ----------

scaler = PowerTransformer()
df_data[feature_all] = scaler.fit(df_data[feature_all]).transform(df_data[feature_all])

for feature in feature_all:
    print(feature)
    
    data = df_data[feature].values
    shape, loc, scale = stats.gamma.fit(data)
    ks_statistic, p_value = stats.kstest(data, 'gamma', args=(shape, loc, scale))
    print(f"Gamma - K-S Statistic: {ks_statistic}, P-value: {p_value}")

    loc, scale = stats.laplace.fit(data)
    ks_statistic, p_value = stats.kstest(data, 'laplace', args=(loc, scale))
    print(f"Laplace - K-S Statistic: {ks_statistic}, P-value: {p_value}")

    c, loc, scale = stats.weibull_min.fit(data)
    ks_statistic, p_value = stats.kstest(data, 'weibull_min', args=(c, loc, scale))
    print(f"Weibull - K-S Statistic: {ks_statistic}, P-value: {p_value}")

    '''gh = GeneralizedHyperbolic.fit(data)
    ks_statistic, p_value = stats.kstest(data, 'generalized_hyperbolic', args=gh)
    print(f"Generalized Hyperbolic - K-S Statistic: {ks_statistic}, P-value: {p_value}")'''

    df = df_data
    feature = feature
    plot_data_and_dist(df, feature)

# COMMAND ----------

path = "C:/Users/JEK2BP/Desktop/HLA/exe/input_dir/"
name_data = "02033BA487_TTMMICParameters.xlsx"
name_limit = "02033BA487_TTMMICParameters_limits.xlsx"
ttnr = '02033BA487'
sheet_names = ["Rx_2024", "Tx_2025", "Tx_2068", "Tx_2147", "Blocker_2027", "Blocker_2113", "Blocker_2114", "BBNL_2028", "BBNL_2103", "BBNL_2112", "BBNL_2211"]

# COMMAND ----------

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

# COMMAND ----------

best_dist_all = []

for df, sheet in zip(df_data_all, sheet_names):
    print(sheet)
    feature_all = df.columns[1:]
    
    for feature in feature_all:
        print('\t',feature)
        data = df[feature].values
        u = np.unique(data)
        if len(u) < 3:
            continue
        
        f = Fitter(data,
            distributions = get_distributions())
        f.fit()
        df_dist = f.summary(plot = True, Nbest = 10)
        df_dist['unique_feature'] = f"{sheet}_{feature}"
        
        best_dist_all.append(df_dist)
        
df_dist_all = pd.concat(best_dist_all, axis = 0)

# COMMAND ----------

len(best_dist_all)

# COMMAND ----------

df_dist_all['type'].value_counts().head(10)

# COMMAND ----------

best_dist_scaled_all = []

for df, sheet in zip(df_data_all, sheet_names):
    print(sheet)
    feature_all = df.columns[1:]
    
    scaler = PowerTransformer()
    df[feature_all] = scaler.fit(df[feature_all]).transform(df[feature_all])
    
    for feature in feature_all:
        print('\t',feature)
        data = df[feature].values
        u = np.unique(data)
        if len(u) < 3:
            continue
        
        f = Fitter(data,
            distributions = get_distributions())
        f.fit()
        df_dist = f.summary(plot = True, Nbest = 10)
        df_dist['unique_feature'] = f"{sheet}_{feature}"
        
        best_dist_scaled_all.append(df_dist)
        
df_dist_scaled_all = pd.concat(best_dist_scaled_all, axis = 0)

# COMMAND ----------



# COMMAND ----------



# COMMAND ----------

df_dist['type'].value_counts()

# COMMAND ----------

n = df_dist.shape[0]/5
typa_all = df_dist['type'].value_counts().index.values
m = len(typa_all)

cover_ratio_all = []
type_full_cover = []
erro_limitation = []

for i in range(m):
    cover_size = df_dist['feature_unique'][df_dist["type"].isin(typa_all[:i+1])].unique().shape[0]
    cover_ratio_all.append(cover_size/n)
    
    df_covered = df_dist[df_dist["type"].isin(typa_all[:i+1])]
    covered_uf = df_covered['feature_unique'].values
    df_dist_best_covered = df_dist_best[df_dist_best['feature_unique'].isin(covered_uf)]
    
    df_covered['covered_error_ratio'] = df_covered.apply(lambda x: x['sumsquare_error']/\
                                        df_dist_best_covered['sumsquare_error']
                                        [df_dist_best_covered['feature_unique'] == x['feature_unique']].iloc[0], axis = 1)
    df_covered = df_covered.drop_duplicates('feature_unique')
    
    erro_limitation.append(df_covered['covered_error_ratio'].mean())
    
    '''if cover_size/n == 1:
        type_full_cover = typa_all[:i+1]
        break'''

# COMMAND ----------



# COMMAND ----------

fig, ax = plt.subplots(1, 1, figsize = (8, 5))
fig.suptitle("feature_unique distribution coverage vs mean(error)")
ax.grid(True)

ax_twin_x = ax.twinx()

ax.plot(range(m), cover_ratio_all, color = 'blue', marker = 'o', label = 'cover_ratio_all')
ax_twin_x.plot(range(m), erro_limitation, color = 'red', marker = 'o', label = 'erro_limitation')

ax.legend()
ax_twin_x.legend()

plt.show()

# COMMAND ----------

