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

class Alpha(SingleFactor):
    def generate_factor(self):
        CLOSE = DataFrame({stock:pd.read_csv('%s/StockDailyData/Stock/%s.csv'%(gc.DATABASE_PATH, stock), index_col=[0], parse_dates=[0]).loc[:, 'close'] for stock in self.stocks})
        ADJ = DataFrame({stock:pd.read_csv('%s/StockDailyData/Stock/%s.csv'%(gc.DATABASE_PATH, stock), index_col=[0], parse_dates=[0]).loc[:, 'adj_factor'] for stock in self.stocks})
        CLOSE = CLOSE * ADJ
        CLOSE.fillna(method='ffill', inplace=True)
        r = np.log(CLOSE).diff()
        r_m = r.mean(1)
        
        n = 20
        
        def reg(y, x, n):
            lxx = (x**2).rolling(n).sum() - n * (x.rolling(n).mean()**2)
            lxy = (x * y).rolling(n).sum() - n * x.rolling(n).mean() * y.rolling(n).mean()
            beta = lxy / lxx
            alpha = y.rolling(n).mean() - beta * x.rolling(n).mean()

            return alpha, beta
        
        alpha, beta = reg(r, DataFrame({stock:r_m for stock in r.columns}), n)
        
        a = alpha
        a = a.loc[a.index >= self.start_date, :]
        a = a.loc[a.index <= self.end_date, :]
        self.factor = a



#%%
if __name__ == '__main__':
    #industry_list = ['801030.SI', '801080.SI', '801150.SI', '801730.SI', '801750.SI', '801760.SI', '801770.SI', '801890.SI']

    #industry_list = ['801010.SI', '801030.SI', '801080.SI', '801150.SI', '801160.SI', '801720.SI', '801730.SI', '801740.SI', '801750.SI', '801760.SI', '801770.SI', '801880.SI', '801890.SI']

    #获取股票
    stocks = tools.get_stocks()
    #获取行业
    industrys = tools.get_industrys(level='L1', stocks=stocks)
    
    
    industrys = {k:industrys[k] for k in industrys.keys()}
    stocks = []
    for v in industrys.values():
        stocks.extend(v)
    stocks.sort()

    a = Alpha('Alpha', stocks=stocks, start_date='20200101', end_date='20201130')
    
    a.generate_factor()
    
    a.factor_analysis()
    
    
