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

class TSRegRSquare(SingleFactor):
    def generate_factor(self):
        CLOSE = DataFrame({stock:pd.read_csv('%s/StockDailyData/Stock/%s.csv'%(gc.DATABASE_PATH, stock), index_col=[0], parse_dates=[0]).loc[:, 'close'] for stock in self.stocks})
        ADJ = DataFrame({stock:pd.read_csv('%s/StockDailyData/Stock/%s.csv'%(gc.DATABASE_PATH, stock), index_col=[0], parse_dates=[0]).loc[:, 'adj_factor'] for stock in self.stocks})
        CLOSE = CLOSE * ADJ
        CLOSE = np.log(CLOSE)
        CLOSE.fillna(method='ffill', inplace=True)
        def reg_ts(df, n):
            x = np.arange(n)
            x = x - x.mean()
            b = df.rolling(n).apply(lambda y:(y*x).sum() / (x*x).sum(), raw=True)
            a = df.rolling(n).mean()
            y_hat = a + b * x[-1]
            e = df - y_hat
            r2 = 1 - (e)**2.sum() / ((df - df.mean(0))**2).sum()
            return b, e
        n = 20
        b, e = reg_ts(CLOSE, n)
        a = b
        a = a.loc[a.index >= self.start_date, :]
        a = a.loc[a.index <= self.end_date, :]
        self.factor = a


#%%
if __name__ == '__main__':
    #获取股票
    stocks = tools.get_stocks()
    
    a = TSRegRSquare('TSRegRSquare', stocks=stocks, start_date='20200101', end_date='20201230')
    
    a.generate_factor()
    
    a.factor_analysis()
    
    