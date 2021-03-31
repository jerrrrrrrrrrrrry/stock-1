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

import multiprocessing as mp


def f(dic_mp_ic_mega, dic_mp_ic_big, dic_mp_ic_small, dic_mp_ic_micro, i, factors, industry_list, no_mc_neutral_list, y_s, y_ind, y_neutral_ind, y_neutral_mc, industrys, mc):
    
    dic_mega_df = {}
    dic_big_df = {}
    dic_small_df = {}
    dic_micro_df = {}
    
    for factor in factors.keys():
        x = factors[factor].copy()
        if factor in industry_list:
            y = y_ind.rolling(i).sum().shift(1-i)
            # y = y_s.rolling(i).sum().shift(1-i)
            x = DataFrame({ind:x.loc[:, industrys[ind]].mean(1) for ind in industrys.keys()})
        elif factor in no_mc_neutral_list:
            y = y_neutral_ind.rolling(i).sum().shift(1-i)
            x = tools.standardize_industry(x, industrys)
        else:
            y = y_neutral_mc.rolling(i).sum().shift(1-i)
            x = tools.standardize_industry(x, industrys)
            x = x - mc.mul((x * mc).sum(1) / (mc * mc).sum(1), axis=0)
        
        y_mega = y.copy()
        y_big = y.copy()
        y_small = y.copy()
        y_micro = y.copy()
        
        x_mega = x.copy()
        x_big = x.copy()
        x_small = x.copy()
        x_micro = x.copy()
        
        mega_mask = x.ge(x.quantile(0.75, 1), 0)
        big_mask = x.ge(x.quantile(0.5, 1), 0) & x.le(x.quantile(0.75, 1), 0)
        small_mask = x.ge(x.quantile(0.25, 1), 0) & x.le(x.quantile(0.5, 1), 0)
        micro_mask = x.le(x.quantile(0.25, 1), 0)
        
        y_mega[~mega_mask] = np.nan
        y_big[~big_mask] = np.nan
        y_small[~small_mask] = np.nan
        y_micro[~micro_mask] = np.nan
        
        x_mega[~mega_mask] = np.nan
        x_big[~big_mask] = np.nan
        x_small[~small_mask] = np.nan
        x_micro[~micro_mask] = np.nan
        
        dic_mega_df[factor] = x_mega.corrwith(y_mega, axis=1)
        dic_big_df[factor] = x_big.corrwith(y_big, axis=1)
        dic_small_df[factor] = x_small.corrwith(y_small, axis=1)
        dic_micro_df[factor] = x_micro.corrwith(y_micro, axis=1)
        
    dic_mp_ic_mega[i] = DataFrame(dic_mega_df)
    dic_mp_ic_big[i] = DataFrame(dic_big_df)
    dic_mp_ic_small[i] = DataFrame(dic_small_df)
    dic_mp_ic_micro[i] = DataFrame(dic_micro_df)
    
if __name__ == '__main__':
    
    n = 10
    y = pd.read_csv('%s/Data/r.csv'%gc.LABELBASE_PATH, index_col=[0], parse_dates=[0])

    stocks = tools.get_stocks()
    
    industrys = tools.get_industrys('L1', stocks)
    
    stocks = list(set(y.columns).intersection(set(stocks)))
    
    industrys = tools.get_industrys('L1', stocks)
    
    y = y.loc[:, stocks]
    y_s = tools.standardize(y)

    y_ind = DataFrame({ind:y.loc[:, industrys[ind]].mean(1) for ind in industrys.keys()})
    
    y_neutral_ind = tools.standardize_industry(y, industrys)
    
    mc = pd.read_csv('%s/Data/MC.csv'%(gc.FACTORBASE_PATH), index_col=[0], parse_dates=[0]).loc[:, stocks]
    mc = mc.loc[y.index.dropna(), stocks]
    mc = tools.standardize_industry(mc, industrys)
    beta = (y_neutral_ind * mc).sum(1) / (mc * mc).sum(1)
    
    y_neutral_mc = y_neutral_ind - mc.mul(beta, axis=0)
        
    # lag = 1
    #get factor
    files = os.listdir('%s/Data/'%gc.FACTORBASE_PATH)
    files = list(filter(lambda x:x[0] > '9', files))
    factors = {file[:-4]:pd.read_csv('%s/Data/%s'%(gc.FACTORBASE_PATH, file), index_col=[0], parse_dates=[0]).loc[:, stocks] for file in files}
    
    industry_list = ['MomentumInd']
    no_mc_neutral_list = ['MC']
    
    
    pool = mp.Pool(5)
    
    dic_mp_ic_mega = mp.Manager().dict()
    dic_mp_ic_big = mp.Manager().dict()
    dic_mp_ic_small = mp.Manager().dict()
    dic_mp_ic_micro = mp.Manager().dict()
    
    for i in range(1, n+1):
        print(i)
        pool.apply_async(func=f, args=(dic_mp_ic_mega, dic_mp_ic_big, dic_mp_ic_small, dic_mp_ic_micro, i, factors, industry_list, no_mc_neutral_list, y_s, y_ind, y_neutral_ind, y_neutral_mc, industrys, mc))
    
    pool.close()
    pool.join()
    
    ic_mega_list = []
    ic_big_list = []
    ic_small_list = []
    ic_micro_list = []
    for i in range(1, n+1):
        ic_mega_list.append(dic_mp_ic_mega[i])
        ic_big_list.append(dic_mp_ic_big[i])
        ic_small_list.append(dic_mp_ic_small[i])
        ic_micro_list.append(dic_mp_ic_micro[i])
    
    
    trade_cal = tools.get_trade_cal(start_date='20170701', end_date=datetime.datetime.today().strftime('%Y%m%d'))
    trade_cal = [pd.Timestamp(i) for i in trade_cal]
    dates = ic_mega_list[0].index
    dates = list(filter(lambda x:x in trade_cal, dates))
    
    ic_mega_list = [ic.loc[dates, :] for ic in ic_mega_list]
    ic_big_list = [ic.loc[dates, :] for ic in ic_big_list]
    ic_small_list = [ic.loc[dates, :] for ic in ic_small_list]
    ic_micro_list = [ic.loc[dates, :] for ic in ic_micro_list]
    
    ic_mega_sum = DataFrame(0, index=ic_mega_list[0].index, columns=ic_mega_list[0].columns)
    ic_big_sum = DataFrame(0, index=ic_big_list[0].index, columns=ic_big_list[0].columns)
    ic_small_sum = DataFrame(0, index=ic_small_list[0].index, columns=ic_small_list[0].columns)
    ic_micro_sum = DataFrame(0, index=ic_micro_list[0].index, columns=ic_micro_list[0].columns)
    
    for n in range((len(ic_mega_list))):
        ic_mega_list[n].to_csv('../Results/IC_MEGA_%s.csv'%n)
        ic_big_list[n].to_csv('../Results/IC_BIG_%s.csv'%n)
        ic_small_list[n].to_csv('../Results/IC_SMALL_%s.csv'%n)
        ic_micro_list[n].to_csv('../Results/IC_MICRO_%s.csv'%n)
        
        ic_mega_sum = ic_mega_sum + ic_mega_list[n]
        ic_big_sum = ic_big_sum + ic_big_list[n]
        ic_small_sum = ic_small_sum + ic_small_list[n]
        ic_micro_sum = ic_micro_sum + ic_micro_list[n]
        
    
    ic_mega_sum.to_csv('../Results/IC_mega_sum.csv')
    ic_big_sum.to_csv('../Results/IC_big_sum.csv')
    ic_small_sum.to_csv('../Results/IC_small_sum.csv')
    ic_micro_sum.to_csv('../Results/IC_micro_sum.csv')
        