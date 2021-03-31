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


def f(dic_mp_ic, dic_mp_ic_pos, dic_mp_ic_neg, dic_mp_ic_big, dic_mp_ic_middle, dic_mp_ic_small, i, factors, no_industry_neutral_list, no_mc_neutral_list, y_s, y_neutral_ind, y_neutral_mc, industrys, mc):

    dic_df = {}
    
    dic_pos_df = {}
    dic_neg_df = {}
    
    # dic_big = {}
    # dic_middle = {}
    # dic_small = {}
    
    for factor in factors.keys():
        x = factors[factor].copy()
        if factor in no_industry_neutral_list:
            y = y_s.rolling(i).sum().shift(1-i)
            x = tools.standardize(x)
        elif factor in no_mc_neutral_list:
            y = y_neutral_ind.rolling(i).sum().shift(1-i)
            x = tools.standardize_industry(x, industrys)
        else:
            y = y_neutral_mc.rolling(i).sum().shift(1-i)
            x = tools.standardize_industry(x, industrys)
            x = x - mc.mul((x * mc).sum(1) / (mc * mc).sum(1), axis=0)
        
        
        big_mask = x.ge(x.quantile(0.975, 1), 0)
        small_mask = x.le(x.quantile(0.025, 1), 0)
        x[big_mask|small_mask] = np.nan
        
        y_pos = y.copy()
        y_neg = y.copy()
        
        # y_big = y.copy()
        # y_middle = y.copy()
        # y_small = y.copy()
        
        
        x_pos = x.copy()
        x_neg = x.copy()
        
        # x_big = x.copy()
        # x_middle = x.copy()
        # x_small = x.copy()
        
        pos_mask = x.ge(0, 0)
        neg_mask = x.le(0, 0)
        
        # big_mask = x.ge(x.quantile(2/3, 1), 0)
        # middle_mask = x.ge(x.quantile(1/3, 1), 0) & x.le(x.quantile(2/3, 1), 0)
        # small_mask = x.le(x.quantile(1/3, 1), 0)
        
        y_pos[neg_mask] = np.nan
        y_neg[pos_mask] = np.nan
        
        x_pos[neg_mask] = np.nan
        x_neg[pos_mask] = np.nan
        
        # y_big[middle_mask|small_mask] = np.nan
        # y_middle[big_mask|small_mask] = np.nan
        # y_small[big_mask|middle_mask] = np.nan
        
        # x_big[middle_mask|small_mask] = np.nan
        # x_middle[big_mask|small_mask] = np.nan
        # x_small[big_mask|middle_mask] = np.nan
        
        dic_df[factor] = x.corrwith(y, axis=1) * y.std(1) / x.std(1)
        dic_pos_df[factor] = x_pos.corrwith(y_pos, axis=1) * y_pos.std(1) / x_pos.std(1)
        dic_neg_df[factor] = x_neg.corrwith(y_neg, axis=1) * y_neg.std(1) / x_neg.std(1)
        # dic_big[factor] = x_big.corrwith(y_big, axis=1) * y.std(1) / x.std(1)
        # dic_middle[factor] = x_middle.corrwith(y_middle, axis=1) * y.std(1) / x.std(1)
        # dic_small[factor] = x_small.corrwith(y_small, axis=1) * y.std(1) / x.std(1)
    
    dic_mp_ic[i] = DataFrame(dic_df)
    dic_mp_ic_pos[i] = DataFrame(dic_pos_df)
    dic_mp_ic_neg[i] = DataFrame(dic_neg_df)
    # dic_mp_ic_big[i] = DataFrame(dic_big)
    # dic_mp_ic_middle[i] = DataFrame(dic_middle)
    # dic_mp_ic_small[i] = DataFrame(dic_small)
    
if __name__ == '__main__':
    
    n = 5
    y = pd.read_csv('%s/Data/y.csv'%gc.LABELBASE_PATH, index_col=[0], parse_dates=[0])

    stocks = tools.get_stocks()
    
    industrys = tools.get_industrys('L1', stocks)
    
    stocks = list(set(y.columns).intersection(set(stocks)))
    
    industrys = tools.get_industrys('L1', stocks)
    
    y = y.loc[:, stocks]
    y_s = tools.standardize(y)
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
    
    
    no_industry_neutral_list = ['MomentumInd', 'MomentumBK']
    no_mc_neutral_list = ['MC']
    
    
    pool = mp.Pool(5)
    
    dic_mp_ic = mp.Manager().dict()
    dic_mp_ic_pos = mp.Manager().dict()
    dic_mp_ic_neg = mp.Manager().dict()
    dic_mp_ic_big = mp.Manager().dict()
    dic_mp_ic_middle = mp.Manager().dict()
    dic_mp_ic_small = mp.Manager().dict()
    
    for i in range(1, n+1):
        print(i)
        pool.apply_async(func=f, args=(dic_mp_ic, dic_mp_ic_pos, dic_mp_ic_neg, dic_mp_ic_big, dic_mp_ic_middle, dic_mp_ic_small, i, factors, no_industry_neutral_list, no_mc_neutral_list, y_s, y_neutral_ind, y_neutral_mc, industrys, mc))
    
    pool.close()
    pool.join()
    
    ic_list = []
    ic_pos_list = []
    ic_neg_list = []
    # ic_big_list = []
    # ic_middle_list = []
    # ic_small_list = []
    for i in range(1, n+1):
        ic_list.append(dic_mp_ic[i])
        ic_pos_list.append(dic_mp_ic_pos[i])
        ic_neg_list.append(dic_mp_ic_neg[i])
        # ic_big_list.append(dic_mp_ic_big[i])
        # ic_middle_list.append(dic_mp_ic_middle[i])
        # ic_small_list.append(dic_mp_ic_small[i])
    
    
    trade_cal = tools.get_trade_cal(start_date='20170701', end_date=datetime.datetime.today().strftime('%Y%m%d'))
    trade_cal = [pd.Timestamp(i) for i in trade_cal]
    dates = ic_list[0].index
    dates = list(filter(lambda x:x in trade_cal, dates))
    ic_list = [ic.loc[dates, :] for ic in ic_list]
    ic_pos_list = [ic.loc[dates, :] for ic in ic_pos_list]
    ic_neg_list = [ic.loc[dates, :] for ic in ic_neg_list]
    # ic_big_list = [ic.loc[dates, :] for ic in ic_big_list]
    # ic_middle_list = [ic.loc[dates, :] for ic in ic_middle_list]
    # ic_small_list = [ic.loc[dates, :] for ic in ic_small_list]
    
    ic_sum = DataFrame(0, index=ic_list[0].index, columns=ic_list[0].columns)
    ic_pos_sum = DataFrame(0, index=ic_list[0].index, columns=ic_list[0].columns)
    ic_neg_sum = DataFrame(0, index=ic_list[0].index, columns=ic_list[0].columns)
    # ic_big_sum = DataFrame(0, index=ic_list[0].index, columns=ic_list[0].columns)
    # ic_middle_sum = DataFrame(0, index=ic_list[0].index, columns=ic_list[0].columns)
    # ic_small_sum = DataFrame(0, index=ic_list[0].index, columns=ic_list[0].columns)
    
    for n in range((len(ic_list))):
        ic_list[n].to_csv('../Results/IC_%s.csv'%n)
        ic_pos_list[n].to_csv('../Results/IC_POS_%s.csv'%n)
        ic_neg_list[n].to_csv('../Results/IC_NEG_%s.csv'%n)
        # ic_big_list[n].to_csv('../Results/IC_BIG_%s.csv'%n)
        # ic_middle_list[n].to_csv('../Results/IC_MIDDLE_%s.csv'%n)
        # ic_small_list[n].to_csv('../Results/IC_SMALL_%s.csv'%n)
        
        ic_sum = ic_sum + ic_list[n]
        ic_pos_sum = ic_pos_sum + ic_pos_list[n]
        ic_neg_sum = ic_neg_sum + ic_neg_list[n]
        # ic_big_sum = ic_big_sum + ic_big_list[n]
        # ic_middle_sum = ic_middle_sum + ic_middle_list[n]
        # ic_small_sum = ic_small_sum + ic_small_list[n]
        
    
    ic_sum.to_csv('../Results/IC_sum.csv')
    ic_pos_sum.to_csv('../Results/IC_pos_sum.csv')
    ic_neg_sum.to_csv('../Results/IC_neg_sum.csv')
    # ic_big_sum.to_csv('../Results/IC_big_sum.csv')
    # ic_middle_sum.to_csv('../Results/IC_middle_sum.csv')
    # ic_small_sum.to_csv('../Results/IC_small_sum.csv')
        