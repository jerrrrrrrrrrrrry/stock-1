# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 21:47:43 2021

@author: admin
"""

import os
import sys
import datetime
import Config
sys.path.append(Config.GLOBALCONFIG_PATH)

import Global_Config as gc
import tools
import numpy as np
import pandas as pd
from pandas import Series, DataFrame

import datetime
def main():
    halflife = 20
    turn_rate = 0.2
    n = int(1 / turn_rate)
    lag = 1
    
    #get ic
    ic_list = []
    for i in range(n):
        ic_list.append(pd.read_csv('%s/Results/IC_%s.csv'%(gc.IC_PATH, i), index_col=[0], parse_dates=[0]))
    
    def f(df_list, turn_rate=0.1):
        s = 1 / turn_rate * (1 + turn_rate) / 2
        mean = DataFrame(0, index=df_list[0].index, columns=df_list[0].columns)
        
        for i in range(len(df_list)):
            mean = mean + df_list[i] * (1 - i * turn_rate)
        mean = mean / s
        
        ret = mean
        return ret
    
    ic_mean_hat_list = [ic_list[n].ewm(halflife=halflife).mean().shift(n+lag) for n in range(len(ic_list))]
    ic_std_hat_list = [ic_list[n].ewm(halflife=halflife).std().shift(n+lag) for n in range(len(ic_list))]
    ic_cov_hat_list = [ic_list[n].ewm(halflife=halflife).cov().shift(len(ic_list[0].columns)*(n+lag)) for n in range(len(ic_list))]
    
    weight_list = [DataFrame(index=ic_mean_hat_list[n].index, columns=ic_mean_hat_list[n].columns) for n in range(len(ic_mean_hat_list))]
    for date in dates:
        for n in range(len(weight_list)):
            weight_list[n].loc[date, :] = np.linalg.inv(100*np.eye(len(ic_cov_hat_list[n].loc[date, :, :])) + ic_cov_hat_list[n].loc[date, :, :].values).dot(ic_mean_hat_list[n].loc[date, :].values.reshape(-1, 1)).reshape(1, -1)
            
            #print(ic_cov_hat_list[n].loc[date,:,:])
            print(date, n)
            # print(np.linalg.inv(ic_cov_hat_list[n].loc[date, :, :]))
            # print(ic_mean_hat_list[n].loc[date, :])
            # print(weight_list[n].loc[date, :])
            print('---------------------')
    weight = f(weight_list, turn_rate)
    weight.to_csv('%s/Results/weight.csv'%gc.IC_PATH)
    
    #ic_cov_hat_inv_list = [[np.linalg.inv(ic_cov_hat.loc[ind, :, :]) for ind in ic_cov_hat.index] for ic_cov_hat in ic_cov_hat_list]
    
    #ic_cov_hat_inv_list = [DataFrame([np.linalg.inv(ic_cov_hat.loc[ind, :, :]) for ind in ic_cov_hat.index], index=ic_cov_hat.index, columns=ic_cov_hat.columns) for ic_cov_hat in ic_cov_hat_list]

    #ir_hat_list = [ic_cov_hat_inv_list[n].dot(ic_mean_hat_list[n]).shift(n+lag) for n in range(len(ic_mean_hat_list))]
    
    #print(ic_list[0].ewm(halflife=halflife).cov())
    #ir_hat_list = [(np.linalg.inv(ic_list[n].ewm(halflife=halflife).cov()) % ic_list[n].ewm(halflife=halflife).mean()).shift(n+lag) for n in range(len(ic_list))]
    
    # ic_hat = f(ic_hat_list, turn_rate)
    ir_hat = f(ir_hat_list, turn_rate)
    
    # ic_hat.to_csv('%s/Results/IC_hat.csv'%gc.IC_PATH)
    ir_hat.to_csv('%s/Results/IR_hat.csv'%gc.IC_PATH)

if __name__ == '__main__':
    main()