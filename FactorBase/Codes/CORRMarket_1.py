#!/usr/bin/env python
# coding: utf-8

#%%
import sys
import datetime
import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import matplotlib.pyplot as plt
import tushare as ts

import Config
sys.path.append(Config.GLOBALCONFIG_PATH)
from SingleFactor import SingleFactor
import Global_Config as gc
import tools

#%%
class CORRMarket(SingleFactor):
    def generate_factor(self):
        data = {stock:pd.read_csv('%s/StockDailyData/Stock/%s.csv'%(gc.DATABASE_PATH, stock), index_col=[0], parse_dates=[0]) for stock in self.stocks}
        
        CLOSE = DataFrame({stock:data[stock].loc[:, 'close'] for stock in self.stocks})
        ADJ = DataFrame({stock:data[stock].loc[:, 'adj_factor'] for stock in self.stocks})
        CLOSE = CLOSE * ADJ
        CLOSE.fillna(method='ffill', inplace=True)
        r = np.log(CLOSE).diff()
        r_m = r.mean(1)
        n_list = [5, 20, 60, 120, 250]
        self.n_list = n_list
        a = []
        for n in n_list:
            corrmarket = r.rolling(n).corr(r_m)
            
            a.append(corrmarket)
        
        for i in range(len(a)):
            a[i] = a[i].loc[a[i].index >= self.start_date, :]
            a[i] = a[i].loc[a[i].index <= self.end_date, :]
        self.factor = a

#%%
if __name__ == '__main__':
    industry_list = ['801030.SI', '801080.SI', '801150.SI', '801730.SI', '801750.SI', '801760.SI', '801770.SI', '801890.SI']
    
    
    #获取股票
    stocks = tools.get_stocks()
    #获取行业
    industrys = tools.get_industrys(level='L1', stocks=stocks)
    
    
    industrys = {k:industrys[k] for k in industrys.keys()}
    stocks = []
    for v in industrys.values():
        stocks.extend(v)
    stocks.sort()
    
    a = CORRMarket('CORRMarket', stocks=stocks, start_date='20200101', end_date='20210222')
    
    a.generate_factor()
    
    a.factor_analysis()
    
    
