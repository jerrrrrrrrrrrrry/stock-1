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

if __name__ == '__main__':
    
    y = pd.read_csv('%s/Data/y.csv'%gc.LABELBASE_PATH, index_col=[0], parse_dates=[0])

    stocks = tools.get_stocks()
    
    industrys = tools.get_industrys('L1', stocks)
    
    stocks = list(set(y.columns).intersection(set(stocks)))
    
    industrys = tools.get_industrys('L1', stocks)
    
    y = y.loc[:, stocks]
    y_s = tools.standardize(y)

    y_ind = DataFrame({ind:y.loc[:, industrys[ind]].mean(1) for ind in industrys.keys()})
    
    y_neutral_ind = tools.standardize_industry(y, industrys)
    
    files = os.listdir('%s/PreprocessData/'%gc.FACTORBASE_PATH)
    files = list(filter(lambda x:x[0] > '9', files))
    factors = [file[:-4] for file in files]
    #行业轮动因子列表
    industry_list = ['MomentumInd']
    
    #原IC,beta
    beta_dic = {}
    #分2段IC
    beta_pos_dic = {}
    beta_neg_dic = {}
    #分3段IC
    beta_big_dic = {}
    beta_middle_dic = {}
    beta_small_dic = {}
    
    for factor in factors:
        print(factor)
        print(datetime.datetime.now())
        factor_df = pd.read_csv('%s/PreprocessData/%s.csv'%(gc.FACTORBASE_PATH, factor), index_col=[0], parse_dates=[0]).loc[:, stocks]
        x = factor_df.copy()
        if factor in industry_list:
            y = y_ind
            x = DataFrame({ind:x.loc[:, industrys[ind]].mean(1) for ind in industrys.keys()})
        else:
            y = y_neutral_ind
            x = DataFrame(x, index=y.index, columns=y.columns)
            big_mask = x.ge(x.quantile(0.975, 1), 0)
            small_mask = x.le(x.quantile(0.025, 1), 0)
            x[y.isna()] = np.nan
            x[big_mask|small_mask] = np.nan
        
        y_pos = y.copy()
        y_neg = y.copy()
        
        x_pos = x.copy()
        x_neg = x.copy()
        
        y_big = y.copy()
        y_middle = y.copy()
        y_small = y.copy()
        
        x_big = x.copy()
        x_middle = x.copy()
        x_small = x.copy()
        
        pos_mask = x.ge(x.quantile(0.5, 1), 0)
        neg_mask = x.le(x.quantile(0.5, 1), 0)
        
        big_mask = x.ge(x.quantile(2/3, 1), 0)
        middle_mask = x.ge(x.quantile(1/3, 1), 0) & x.le(x.quantile(2/3, 1), 0)
        small_mask = x.le(x.quantile(1/3, 1), 0)
        
        y_pos[~pos_mask] = np.nan
        y_neg[~neg_mask] = np.nan
        
        x_pos[~pos_mask] = np.nan
        x_neg[~neg_mask] = np.nan
        
        y_big[~big_mask] = np.nan
        y_middle[~middle_mask] = np.nan
        y_small[~small_mask] = np.nan
        
        x_big[~big_mask] = np.nan
        x_middle[~middle_mask] = np.nan
        x_small[~small_mask] = np.nan
        
        beta_dic[factor] = x.corrwith(y, axis=1) * y.std(1) / x.std(1)
        
        beta_pos_dic[factor] = x_pos.corrwith(y_pos, 1) * y_pos.std(1) / x_pos.std(1)
        beta_neg_dic[factor] = x_neg.corrwith(y_neg, 1) * y_neg.std(1) / x_neg.std(1)
        
        beta_big_dic[factor] = x_big.corrwith(y_big, 1) * y_big.std(1) / x_big.std(1)
        beta_middle_dic[factor] = x_middle.corrwith(y_middle, 1) * y_middle.std(1) / x_middle.std(1)
        beta_small_dic[factor] = x_small.corrwith(y_small, 1) * y_small.std(1) / x_small.std(1)
        
    beta = DataFrame(beta_dic)
    
    beta_pos = DataFrame(beta_pos_dic)
    beta_neg = DataFrame(beta_neg_dic)
    
    beta_big = DataFrame(beta_big_dic)
    beta_middle = DataFrame(beta_middle_dic)
    beta_small = DataFrame(beta_small_dic)
    
    trade_cal = tools.get_trade_cal(start_date='20170701', end_date=datetime.datetime.today().strftime('%Y%m%d'))
    trade_cal = [pd.Timestamp(i) for i in trade_cal]
    dates = beta.index
    dates = list(filter(lambda x:x in trade_cal, dates))
    
    beta = beta.loc[dates, :]
    
    beta_pos = beta_pos.loc[dates, :]
    beta_neg = beta_neg.loc[dates, :]
    
    beta_big = beta_big.loc[dates, :]
    beta_middle = beta_middle.loc[dates, :]
    beta_small = beta_small.loc[dates, :]
    
    beta.to_csv('../Results/beta.csv')
    
    beta_pos.to_csv('../Results/beta_pos.csv')
    beta_neg.to_csv('../Results/beta_neg.csv')
    
    beta_big.to_csv('../Results/beta_big.csv')
    beta_middle.to_csv('../Results/beta_middle.csv')
    beta_small.to_csv('../Results/beta_small.csv')
