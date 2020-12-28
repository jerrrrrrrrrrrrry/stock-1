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

class ResidualSkew(SingleFactor):
    def generate_factor(self):
        CLOSE = DataFrame({stock:pd.read_csv('%s/StockDailyData/Stock/%s.csv'%(gc.DATABASE_PATH, stock), index_col=[0], parse_dates=[0]).loc[:, 'close'] for stock in self.stocks})
        ADJ = DataFrame({stock:pd.read_csv('%s/StockDailyData/Stock/%s.csv'%(gc.DATABASE_PATH, stock), index_col=[0], parse_dates=[0]).loc[:, 'adj_factor'] for stock in self.stocks})
        CLOSE = CLOSE * ADJ
        CLOSE.fillna(method='ffill', inplace=True)
        r = np.log(CLOSE).diff()
        r_m = r.mean(1)
        r_m = DataFrame({stock:r_m for stock in r.columns})
        n = 20
        
        def reg(y, x, n):
            lxx = (x**2).rolling(n).sum() - n * (x.rolling(n).mean()**2)
            lxy = (x * y).rolling(n).sum() - n * x.rolling(n).mean() * y.rolling(n).mean()
            beta = lxy / lxx
            alpha = y.rolling(n).mean() - beta * x.rolling(n).mean()

            return alpha, beta
        
        alpha, beta = reg(r, r_m, n)
        e = r.subtract(alpha, 1) - r_m.mul(beta, 1)
        
        m = n
        a = e.rolling(m).skew()
        a = a.loc[a.index >= self.start_date, :]
        a = a.loc[a.index <= self.end_date, :]

        self.factor = a

#%%
if __name__ == '__main__':
    #获取股票
    stocks = tools.get_stocks()
    
    a = ResidualSkew('ResidualSkew', stocks=stocks, start_date='20200101', end_date='20201010')
    
    a.generate_factor()
    
    a.factor_analysis()