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
    # halflife = 20
    # turn_rate = 0.2
    n = 10
    #get y
    #y = pd.read_csv('%s/Data/y.csv'%gc.LABELBASE_PATH, index_col=[0], parse_dates=[0])
    y = pd.read_csv('%s/Data/r.csv'%gc.LABELBASE_PATH, index_col=[0], parse_dates=[0])
    
    stocks = list(y.columns)
    industrys = tools.get_industrys('L1', stocks)
    tmp = {}
    for k in industrys.keys():
        if len(industrys[k]) > 0:
            tmp[k] = industrys[k]
    industrys = tmp
    
    y_neutral_ind = tools.standardize_industry(y, industrys)
    
    market_capitalization = DataFrame({stock: pd.read_csv('%s/StockTradingDerivativeData/Stock/%s.csv'%(gc.DATABASE_PATH, stock), index_col=[0], parse_dates=[0]).loc[:, 'TOTMKTCAP'] for stock in stocks})
    market_capitalization = np.log(market_capitalization)
    market_capitalization = market_capitalization.loc[y.index.dropna(), :]
    market_capitalization = tools.standardize_industry(market_capitalization, industrys)
    beta = (y_neutral_ind * market_capitalization).sum(1) / (market_capitalization * market_capitalization).sum(1)
    y_neutral_mc = y_neutral_ind - market_capitalization.mul(beta, axis=0)
    
    
    # lag = 1
    #get factor
    files = os.listdir('%s/Data/'%gc.FACTORBASE_PATH)
    files = list(filter(lambda x:x[0] > '9', files))
    factors = {file[:-4]:pd.read_csv('%s/Data/%s'%(gc.FACTORBASE_PATH, file), index_col=[0], parse_dates=[0]) for file in files}
    
    
    no_industry_neutral_list = ['MomentumInd']
    no_mc_neutral_list = ['MC']
    
    ic_list = [DataFrame({factor: (factors[factor].corrwith(y.rolling(n).sum().shift(-n+1), method='pearson', axis=1) if factor in no_industry_neutral_list else factors[factor].corrwith(y_neutral_ind.rolling(n).sum().shift(-n+1), method='pearson', axis=1) if factor in no_mc_neutral_list else factors[factor].corrwith(y_neutral_mc.rolling(n).sum().shift(-n+1), method='pearson', axis=1)) for factor in factors.keys()}) for n in range(1, 1+n)]
    
    trade_cal = tools.get_trade_cal(start_date='20200101', end_date=datetime.datetime.today().strftime('%Y%m%d'))
    trade_cal = [pd.Timestamp(i) for i in trade_cal]
    dates = ic_list[0].index
    dates = list(filter(lambda x:x in trade_cal, dates))
    ic_list = [ic.loc[dates, :] for ic in ic_list]
    
    for n in range((len(ic_list))):
        ic_list[n].to_csv('../Results/IC_%s.csv'%n)
    
    # n = 20
    # r = pd.read_csv('%s/Data/r.csv'%gc.LABELBASE_PATH, index_col=[0], parse_dates=[0])
    # # lag = 1
    # #get factor
    # files = os.listdir('%s/Data/'%gc.FACTORBASE_PATH)
    # files = list(filter(lambda x:x[0] > '9', files))
    # factors = {file[:-4]:pd.read_csv('%s/Data/%s'%(gc.FACTORBASE_PATH, file), index_col=[0], parse_dates=[0]) for file in files}
    
    # no_industry_neutral_list = ['MomentumInd']
    # no_mc_neutral_list = ['MC']
    
    # ic_list = []
    # for factor in factors.keys():
    #     if factor in no_industry_neutral_list:
    #         ic = factors[factor].corrwith(r.rolling(-n).sum())
    # def f(df_list, turn_rate=0.1):
    #     s = 1 / turn_rate * (1 + turn_rate) / 2
    #     mean = DataFrame(0, index=df_list[0].index, columns=df_list[0].columns)
    #     #var = DataFrame(0, index=df_list[0].index, columns=df_list[0].columns)
        
    #     for i in range(len(df_list)):
    #         mean = mean + df_list[i] * (1 - i * turn_rate)
    #     mean = mean / s
        
    #     #for i in range(len(df_list)):
    #     #    var = var + (df_list[i] - mean)**2 * q**i
    #     #var = var / q_sum
    #     #std = np.sqrt(var)
    #     #t = mean
    #     ret = mean
    #     return ret
    # # for n in range(len(ic_list)):
    # #     ic_list[n] = ic_list[n].shift(n)
    # # ic = f(ic_list, turn_rate)
    # # ic_hat = ic.ewm(halflife=halflife).mean().shift()
    # # ir_hat = (ic.ewm(halflife=halflife).mean() / ic.ewm(halflife=halflife).std()).shift()
    
    # #ic_hat_list = [ic_list[n].ewm(halflife=halflife).mean().shift(n+lag) for n in range(len(ic_list))]
    # ir_hat_list = [(ic_list[n].ewm(halflife=halflife).mean() / ic_list[n].ewm(halflife=halflife).std()).shift(n+lag) for n in range(len(ic_list))]
    
    # ic_mean_hat_list = [ic_list[n].ewm(halflife=halflife).mean().shift(n+lag) for n in range(len(ic_list))]
    # ic_std_hat_list = [ic_list[n].ewm(halflife=halflife).std().shift(n+lag) for n in range(len(ic_list))]
    
    # ic_cov_hat_list = [ic_list[n].ewm(halflife=halflife).cov().shift(len(ic_list[0].columns)*(n+lag)) for n in range(len(ic_list))]
    
    # weight_list = [DataFrame(index=ic_mean_hat_list[n].index, columns=ic_mean_hat_list[n].columns) for n in range(len(ic_mean_hat_list))]
    # for date in dates:
    #     for n in range(len(weight_list)):
    #         weight_list[n].loc[date, :] = np.linalg.inv(100*np.eye(len(ic_cov_hat_list[n].loc[date, :, :])) + ic_cov_hat_list[n].loc[date, :, :].values).dot(ic_mean_hat_list[n].loc[date, :].values.reshape(-1, 1)).reshape(1, -1)
            
    #         #print(ic_cov_hat_list[n].loc[date,:,:])
    #         print(date, n)
    #         # print(np.linalg.inv(ic_cov_hat_list[n].loc[date, :, :]))
    #         # print(ic_mean_hat_list[n].loc[date, :])
    #         # print(weight_list[n].loc[date, :])
    #         print('---------------------')
    # weight = f(weight_list, turn_rate)
    # weight.to_csv('%s/Results/weight.csv'%gc.IC_PATH)
    
    # #ic_cov_hat_inv_list = [[np.linalg.inv(ic_cov_hat.loc[ind, :, :]) for ind in ic_cov_hat.index] for ic_cov_hat in ic_cov_hat_list]
    
    # #ic_cov_hat_inv_list = [DataFrame([np.linalg.inv(ic_cov_hat.loc[ind, :, :]) for ind in ic_cov_hat.index], index=ic_cov_hat.index, columns=ic_cov_hat.columns) for ic_cov_hat in ic_cov_hat_list]

    # #ir_hat_list = [ic_cov_hat_inv_list[n].dot(ic_mean_hat_list[n]).shift(n+lag) for n in range(len(ic_mean_hat_list))]
    
    # #print(ic_list[0].ewm(halflife=halflife).cov())
    # #ir_hat_list = [(np.linalg.inv(ic_list[n].ewm(halflife=halflife).cov()) % ic_list[n].ewm(halflife=halflife).mean()).shift(n+lag) for n in range(len(ic_list))]
    
    # # ic_hat = f(ic_hat_list, turn_rate)
    # ir_hat = f(ir_hat_list, turn_rate)
    
    # # ic_hat.to_csv('%s/Results/IC_hat.csv'%gc.IC_PATH)
    # ir_hat.to_csv('%s/Results/IR_hat.csv'%gc.IC_PATH)

if __name__ == '__main__':
    main()