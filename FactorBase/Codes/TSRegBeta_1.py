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

class TSRegBeta(SingleFactor):
    def generate_factor(self):
        data = {stock:pd.read_csv('%s/StockDailyData/Stock/%s.csv'%(gc.DATABASE_PATH, stock), index_col=[0], parse_dates=[0]) for stock in self.stocks}
        
        CLOSE = DataFrame({stock:data[stock].loc[:, 'close'] for stock in self.stocks})
        ADJ = DataFrame({stock:data[stock].loc[:, 'adj_factor'] for stock in self.stocks})
        CLOSE = CLOSE * ADJ
        CLOSE = np.log(CLOSE)
        def reg_ts(df, n):
            x = np.arange(n)
            x = x - x.mean()
            b = df.rolling(n).apply(lambda y:(y*x).sum() / (x*x).sum(), raw=True)
            a = df.rolling(n).mean()
            y_hat = a + b * x[-1]
            e = df - y_hat

            return b, e
        n_list = [5, 10, 20, 60, 120, 250]
        self.n_list = n_list
        a = []
        for n in n_list:
            b, e = reg_ts(CLOSE, n)
            a.append(b)
        
        for i in range(len(a)):
            a[i] = a[i].loc[a[i].index >= self.start_date, :]
            a[i] = a[i].loc[a[i].index <= self.end_date, :]
        self.factor = a


#%%
if __name__ == '__main__':
    #获取股票
    stocks = tools.get_stocks()
    
    a = TSRegBeta('TSRegBeta', stocks=stocks, start_date='20200101', end_date='20201010')
    
    a.generate_factor()
    
    a.factor_analysis()
    
    