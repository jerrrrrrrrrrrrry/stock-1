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

class MomentumWeighted(SingleFactor):
    def generate_factor(self):
        data = {stock:pd.read_csv('%s/StockDailyData/Stock/%s.csv'%(gc.DATABASE_PATH, stock), index_col=[0], parse_dates=[0]) for stock in self.stocks}
        
        CLOSE = DataFrame({stock:data[stock].loc[:, 'close'] for stock in self.stocks})
        ADJ = DataFrame({stock:data[stock].loc[:, 'adj_factor'] for stock in self.stocks})
        CLOSE = np.log(CLOSE * ADJ)
        CLOSE.fillna(method='ffill', inplace=True)
        r = CLOSE.diff()
        r.fillna(method='ffill', inplace=True)
        r.fillna(0, inplace=True)
        w = np.arange(250) / 250
        w = w - w[120]
        w = 1 / (1 + np.exp(-w)) - 0.5
        def f(r, w):
            ret = (r.values.flatten() * w[-len(r):]).sum()
            return ret
        a = r.rolling(250).apply(func=f, args=(w,))
        a = a
        # n0 = 0
        # n1 = 5
        # n2 = 20
        # n3 = 60
        # n4 = 120
        # n5 = 250
        # r1 = CLOSE.diff(n1-n0).shift(n0) / (n1-n0)
        # r2 = CLOSE.diff(n2-n1).shift(n1) / (n2-n1)
        # r3 = CLOSE.diff(n3-n2).shift(n2) / (n3-n2)
        # r4 = CLOSE.diff(n4-n3).shift(n3) / (n4-n3)
        # r5 = CLOSE.diff(n5-n4).shift(n4) / (n5-n4)
        # a = r4
        a = a.loc[a.index >= self.start_date, :]
        a = a.loc[a.index <= self.end_date, :]
        self.factor = a

#%%


if __name__ == '__main__':
    
    #获取股票
    stocks = tools.get_stocks()
    
    a = MomentumWeighted('MomentumWeighted', stocks=stocks, start_date='20200101', end_date='20210301')
    
    a.generate_factor()
    
    a.factor_analysis()
    
