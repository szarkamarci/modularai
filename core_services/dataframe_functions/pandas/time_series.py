import numpy as np
import pandas as pd

def calc_sma_info(df : pd.DataFrame, column: str, sma: int, shift: int):

    column_sma = f"{column}_sma"
    column_std = f"{column}_std"
    column_z = f"{column}_z"

    df[column_sma] = df[column].rolling(sma).mean().fillna()
    df[column_std] = df[column].rolling(sma).std().fillna()
    df[column_z] = df.apply(lambda x: (x[column] - x[column_sma])/x[column_std], axis = 1)

    return df[[column, column_sma, column_std, column_z]]


def bell_model_train(df : pd.DataFrame, column: str, sma: int, shift: int):
    n = df.shape[0]

    column_sma = f"{column}_sma"
    column_std = f"{column}_std"
    column_z = f"{column}_z"
    column_chg = f"{column}_chg"

    df[column_sma] = df[column].rolling(sma).mean()
    df[column_std] = df[column].rolling(sma).std()
    df[column_z] = df.apply(lambda x: (x[column] - x[column_sma])/x[column_std], axis = 1)
    df[column_chg] = df[column].pct_change(periods = shift).shift(periods = -shift)
    
    df =  df.tail(-sma).head(-shift)
    
    std_chg = df[column_chg].std()

    x = df[column_z].values
    y = df[column_chg].values
    data = np.vstack([x, y])
    kde = gaussian_kde(data)

    x_grid, y_grid = np.meshgrid(np.linspace(-4, 4, 101), np.linspace(-4*std_chg, 4*std_chg, 101))
    grid_coords = np.vstack([x_grid.ravel(), y_grid.ravel()])
    z_grid = kde(grid_coords).reshape(101, 101)
    
    x = x_grid.flatten()
    y = y_grid.flatten()
    z = z_grid.flatten()
    z = z/sum(z)
    
    df_model = pd.DataFrame({'column_z': x, 'column_chg': y, 'prob_all': z})
    
    return df_model

def bell_model_predict(df: pd.DataFrame, df_model : pd.DataFrame, column: str, sma: int, shift: int):
    column_sma = f"{column}_sma"
    column_std = f"{column}_std"
    column_z = f"{column}_z"

    df[column_sma] = df[column].rolling(sma).mean()
    df[column_std] = df[column].rolling(sma).std()
    df[column_z] = df.apply(lambda x: (x[column] - x[column_sma])/x[column_std], axis = 1)
    
    df_predict = df.tail(-sma)
    
    pred_values_all = []
    pred_probs_all = []
    
    for index, row in df_predict.iterrows():
        v = row['Open']
        z = row['Open_z']
        
        df_sub_model = df_model[(z - 0.08 <= df_model['column_z']) & (df_model['column_z'] <= z + 0.08)]
        lower, upper = list(df_sub_model['column_z'].unique())

        df_lower = df_sub_model[df_sub_model['column_z'] == lower]
        df_upper = df_sub_model[df_sub_model['column_z'] == upper]
        
        pred_values = (df_lower['column_chg'].values + df_upper['column_chg'].values + 1) *v
        pred_probs = df_lower['prob_all'].values + df_upper['prob_all'].values
        pred_probs *= 1/sum(pred_probs)
        
        pred_values_all.append(pred_values)
        pred_probs_all.append(pred_probs)
    
    df_predict['pred_values'] = pred_values_all
    df_predict['pred_probs'] = pred_probs_all
    
    return df_predict