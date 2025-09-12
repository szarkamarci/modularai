import numpy as np
import pandas as pd

from scipy.stats import arcsine, gamma, laplace, laplace_asymmetric, weibull_min, genhyperbolic


def calc_fitness_gamma(data):
    mean_all = []
    
    n = len(data)
    data = sorted((data - min(data))/abs(max(data) - min(data)))
    
    for shape in np.linspace(1, 10, 10):
        g_ppf = gamma.ppf(np.linspace(0.001, 0.999, n), shape, 1)
        g_ppf = sorted((g_ppf - min(g_ppf))/abs(max(g_ppf) - min(g_ppf)))

        dif = [abs(g_ppf[i] -  data[i]) for i in range(n)]
        mean = np.mean(dif)
        mean_all.append(mean_all)
    
    p = np.argmin(mean_all)
    
    return 1 - mean_all[p], np.linspace(1, 10, 10)[p]
    
def calc_fitness_laplace(data):
    n = len(data)
    data = sorted((data - min(data))/abs(max(data) - min(data)))
    
    l_ppf = laplace.ppf(np.linspace(0.001, 0.999, n))
    l_ppf = sorted((l_ppf - min(l_ppf))/abs(max(l_ppf) - min(l_ppf)))
    
    dif = [abs(l_ppf[i] -  data[i]) for i in range(n)]
    mean = np.mean(dif)
    
    return 1 - mean, 0.5

def calc_laplace_asymmetric(data):
    mean_all = []
       
    n = len(data)
    data = sorted((data - min(data))/abs(max(data) - min(data)))
    
    for shape in np.linspace(1, 10, 10):
        la_ppf = laplace_asymmetric.ppf(np.linspace(0.001, 0.999, n), shape)
        la_ppf = sorted((la_ppf - min(la_ppf))/abs(max(la_ppf) - min(la_ppf)))
        
        dif = [abs(la_ppf[i] -  data[i]) for i in range(n)]
        mean = np.mean(dif)
        mean_all.append(mean_all)
    
    p = np.argmin(mean_all)
    
    return 1 - mean_all[p], np.linspace(1, 10, 10)[p]
    
def calc_fitness_weibull_min(data):
    mean_all = []
    
    n = len(data)
    data = sorted((data - min(data))/abs(max(data) - min(data)))
    
    for shape in np.linspace(1, 10, 10):
        w_ppf = weibull_min.ppf(np.linspace(0.001, 0.999, n), shape)
        w_ppf = sorted((w_ppf - min(w_ppf))/abs(max(w_ppf) - min(w_ppf)))
        
        dif = [abs(w_ppf[i] -  data[i]) for i in range(n)]
        mean = np.mean(dif)
        mean_all.append(mean_all)
    
    p = np.argmin(mean_all)
    
    return 1 - mean_all[p], np.linspace(1, 10, 10)[p]
    
def calc_fitness_genhyperbolic(data):
    mean_all = []
    
    n = len(data)
    data = sorted((data - min(data))/abs(max(data) - min(data)))
    
    p = 1
    a = 1 
    for b in np.linspace(-0.9, 0.9, 19):
        gh_ppf = genhyperbolic.ppf(np.linspace(0.001, 0.999, 150), p, a, b)
        gh_ppf = sorted((gh_ppf - min(gh_ppf))/abs(max(gh_ppf) - min(gh_ppf)))
        
        dif = [abs(gh_ppf[i] -  data[i]) for i in range(150)]
        mean = np.mean(dif)
        mean_all.append(mean_all)
    
    p = np.argmin(mean_all)
    
    return 1 - mean_all[p], np.linspace(-0.9, 0.9, 19)[p]

def calc_fitness_arcsine(data):
    n = len(data)
    data = sorted((data - min(data))/abs(max(data) - min(data)))
    
    a_ppf = arcsine.ppf(np.linspace(0.001, 0.999, n))
    a_ppf = sorted((a_ppf - min(a_ppf))/abs(max(a_ppf) - min(a_ppf)))
    
    dif = [abs(a_ppf[i] -  data[i]) for i in range(n)]
    mean = np.mean(dif)
    
    return 1 - mean, 0.5
    

def calc_fitness_measure_all(df_data_all, df_dist_all, acceptance_limit):
    res_all = []
    
    for index, row in df_dist_all.iterrows():
        dist_type = index
        sheet = row['sheet']
        sheet_id = row['sheet_id']
        ttnr = row['ttnr']
        feature = row['feature']
        
        data = df_data_all[sheet_id][feature].values
        
        if dist_type == 'dgamma':
            similarity, p = calc_fitness_gamma(data)
            
        elif dist_type == 'laplace':
            similarity, p = calc_fitness_laplace(data)
        elif dist_type == 'laplace_asymmetric':
            similarity, p = calc_laplace_asymmetric(data)
        elif dist_type == 'dweibull':
            similarity, p = calc_fitness_weibull_min(data)
        elif dist_type == 'genhyperbolic':
            similarity, p = calc_fitness_genhyperbolic(data)
        elif dist_type == 'arcsine':
            similarity, p = calc_fitness_arcsine(data)
        else:
            error = 0
            p = None
        
        if similarity >= acceptance_limit:
            status = 'accapted_distribution'
        else:
            status = 'failed_distribution'
        
        
        res_all.append([dist_type, sheet, sheet_id, ttnr, feature, similarity, status])
    
    df_res_all = pd.DataFrame(res_all, columns = ['type', 'sheet', 'sheet_id',
                                                  'ttnr', 'feature', 'similarity', 'status'])
    return df_res_all

def calc_fitness_measure_all_distribution(df_data_all, df_dist_all, acceptance_limit):
    print('calc_fitness_measure_all_distribution()')
    res_all = []
    
    dist_type_all = ['laplace_asymmetric', 'dweibull', 'genhyperbolic', 'dgamma', 'laplace', 'arcsine']
    
    for index, row in df_dist_all.iterrows():
        similarity_feature = []
        p_feature = []
        
        sheet = row['sheet']
        sheet_id = row['sheet_id']
        ttnr = row['ttnr']
        feature = row['feature']
        
        print(feature)
        
        data = df_data_all[sheet_id][feature].values
       
        similarity_g, p_g = calc_fitness_gamma(data)
        similarity_feature.append(similarity_g)
        p_feature.append(p_g)
        
        similarity_l, p_l = calc_fitness_laplace(data)
        similarity_feature.append(similarity_l)
        p_feature.append(p_l)
        
        similarity_la, p_la = calc_laplace_asymmetric(data)
        similarity_feature.append(similarity_la)
        p_feature.append(p_la)
        
        similarity_wmi, p_wmi = calc_fitness_weibull_min(data)
        similarity_feature.append(similarity_wmi)
        p_feature.append(p_wmi)
        
        similarity_gh, p_gh = calc_fitness_genhyperbolic(data)
        similarity_feature.append(similarity_gh)
        p_feature.append(p_gh)
        
        similarity_a, p_a = calc_fitness_arcsine(data)
        similarity_feature.append(similarity_a)
        p_feature.append(p_a)

        
        pos = np.argmax(similarity_feature)
        similarity = similarity_feature[pos]
        p = p_feature[pos]
        dist_type = dist_type_all[pos]
        
        if similarity >= acceptance_limit:
            status = 'accapted_distribution'
        else:
            status = 'failed_distribution'
        
        
        res_all.append([dist_type, sheet, sheet_id, ttnr, feature, similarity, status])
    
    df_res_all = pd.DataFrame(res_all, columns = ['type', 'sheet', 'sheet_id',
                                                  'ttnr', 'feature', 'similarity', 'status'])
    return df_res_all
