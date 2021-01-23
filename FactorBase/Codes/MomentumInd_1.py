#!/usr/bin/env python
# coding: utf-8

#%%

import os
import sys
import time
import datetime
import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

import tushare as ts
import Config
sys.path.append(Config.GLOBALCONFIG_PATH)
from SingleFactor import SingleFactor
import Global_Config as gc
import tools

#%%

class MomentumInd(SingleFactor):
    def generate_factor(self):
        CLOSE = DataFrame({stock:pd.read_csv('%s/StockDailyData/Stock/%s.csv'%(gc.DATABASE_PATH, stock), index_col=[0], parse_dates=[0]).loc[:, 'close'] for stock in self.stocks})
        ADJ = DataFrame({stock:pd.read_csv('%s/StockDailyData/Stock/%s.csv'%(gc.DATABASE_PATH, stock), index_col=[0], parse_dates=[0]).loc[:, 'adj_factor'] for stock in self.stocks})
        CLOSE = CLOSE * ADJ
        CLOSE.fillna(method='ffill', inplace=True)
        r = np.log(CLOSE).diff(20)
        ind_files = os.listdir('%s/Data'%gc.FACTORBASE_PATH)
        ind_files = list(filter(lambda x:x[0]=='8', ind_files))
        
        a = DataFrame(0, index=r.index, columns=r.columns)
        for ind_file in ind_files:
            ind_df = pd.read_csv('%s/Data/%s'%(gc.FACTORBASE_PATH, ind_file), index_col=[0], parse_dates=[0])
            ind_df = ind_df.loc[r.index, r.columns]
            ind_df[ind_df==0] = np.nan
            a = a.add(ind_df.mul((r * ind_df).mean(1), axis=0), fill_value=0)
        a = a.loc[a.index >= self.start_date, :]
        a = a.loc[a.index <= self.end_date, :]
        self.factor = a
        
    def update_factor(self):
        self.generate_factor()
        #if 'industry' in self.neutral_list:
        if False:
            industrys = tools.get_industrys('L1', self.stocks)
            tmp = {}
            for k in industrys.keys():
                if len(industrys[k]) > 0:
                    tmp[k] = industrys[k]
            industrys = tmp
            factor = tools.standardize_industry(self.factor, industrys)
        #if 'market_capitalization' in self.neutral_list:
        if False:
            market_capitalization = DataFrame({stock: pd.read_csv('%s/StockTradingDerivativeData/Stock/%s.csv'%(gc.DATABASE_PATH, stock), index_col=[0], parse_dates=[0]).loc[:, 'TOTMKTCAP'] for stock in self.stocks})
            market_capitalization = np.log(market_capitalization)
            if self.start_date:
                market_capitalization = market_capitalization.loc[market_capitalization.index >= self.start_date, :]
            if self.end_date:
                market_capitalization = market_capitalization.loc[market_capitalization.index <= self.end_date, :]
            #if 'industry' in self.neutral_list:
            if True:
                market_capitalization = tools.standardize_industry(market_capitalization, industrys)
            beta = (factor * market_capitalization).sum(1) / (market_capitalization * market_capitalization).sum(1)
            factor = factor - market_capitalization.mul(beta, axis=0)
        self.factor.fillna(0, inplace=True)
        factor = tools.standardize(self.factor)
        if os.path.exists('%s/Data/%s.csv'%(gc.FACTORBASE_PATH, self.factor_name)):
            factor_old = pd.read_csv('%s/Data/%s.csv'%(gc.FACTORBASE_PATH, self.factor_name), index_col=[0])
            factor = pd.concat([factor_old, factor.loc[factor.index>factor.index[-1], :]], axis=0)
            factor.sort_index(axis=0, inplace=True)
            factor.sort_index(axis=1, inplace=True)
        factor.to_csv('%s/Data/%s.csv'%(gc.FACTORBASE_PATH, self.factor_name))
#%%


if __name__ == '__main__':
    
    #获取股票
    stocks = tools.get_stocks()
    
    a = MomentumInd('MomentumInd', stocks=stocks, start_date='20200101', end_date='20210101')
    
    a.generate_factor()
    
    a.factor_analysis(industry_neutral=False, size_neutral=False, num_group=5)
    
