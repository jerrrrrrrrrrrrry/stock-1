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


class MC(SingleFactor):
    def generate_factor(self):
        a = DataFrame({stock: pd.read_csv('%s/StockTradingDerivativeData/Stock/%s.csv'%(gc.DATABASE_PATH, stock), index_col=[0], parse_dates=[0]).loc[:, 'TOTMKTCAP'] for stock in self.stocks})
        a = np.log(a)
        
        a = a.loc[a.index >= self.start_date, :]
        a = a.loc[a.index <= self.end_date, :]
        self.factor = a
        
    def update_factor(self):
        self.generate_factor()
        #if 'industry' in self.neutral_list:
        if True:
            industrys = tools.get_industrys('L1', self.stocks)
            tmp = {}
            for k in industrys.keys():
                if len(industrys[k]) > 0:
                    tmp[k] = industrys[k]
            industrys = tmp
            factor = tools.standardize_industry(self.factor, industrys)
        # #if 'market_capitalization' in self.neutral_list:
        # if False:
        #     market_capitalization = DataFrame({stock: pd.read_csv('%s/StockTradingDerivativeData/Stock/%s.csv'%(gc.DATABASE_PATH, stock), index_col=[0], parse_dates=[0]).loc[:, 'TOTMKTCAP'] for stock in self.stocks})
        #     market_capitalization = np.log(market_capitalization)
        #     if self.start_date:
        #         market_capitalization = market_capitalization.loc[market_capitalization.index >= self.start_date, :]
        #     if self.end_date:
        #         market_capitalization = market_capitalization.loc[market_capitalization.index <= self.end_date, :]
        #     #if 'industry' in self.neutral_list:
        #     if True:
        #         market_capitalization = tools.standardize_industry(market_capitalization, industrys)
        #     beta = (factor * market_capitalization).sum(1) / (market_capitalization * market_capitalization).sum(1)
        #     factor = factor - market_capitalization.mul(beta, axis=0)
        factor.fillna(0, inplace=True)
        if os.path.exists('%s/Data/%s.csv'%(gc.FACTORBASE_PATH, self.factor_name)):
            if isinstance(factor.index[0], str):
                factor_old = pd.read_csv('%s/Data/%s.csv'%(gc.FACTORBASE_PATH, self.factor_name), index_col=[0])
            else:
                factor_old = pd.read_csv('%s/Data/%s.csv'%(gc.FACTORBASE_PATH, self.factor_name), index_col=[0], parse_dates=[0])
            factor = pd.concat([factor_old, factor.loc[factor.index>factor_old.index[-1], :]], axis=0)
            factor.sort_index(axis=0, inplace=True)
        factor.to_csv('%s/Data/%s.csv'%(gc.FACTORBASE_PATH, self.factor_name))

#%%


if __name__ == '__main__':
    
    #获取股票
    stocks = tools.get_stocks()
    
    a = MC('MC', stocks=stocks, start_date='20200101', end_date='20201201')
    
    a.generate_factor()
    
    a.factor_analysis(size_neutral=False)
    
