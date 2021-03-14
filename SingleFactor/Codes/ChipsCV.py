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
class ChipsCV(SingleFactor):
    def generate_factor(self):
        CLOSE = DataFrame({stock:pd.read_csv('%s/StockDailyData/Stock/%s.csv'%(gc.DATABASE_PATH, stock), index_col=[0], parse_dates=[0]).loc[:, 'close'] for stock in self.stocks})
        amount = DataFrame({stock:pd.read_csv('%s/StockDailyData/Stock/%s.csv'%(gc.DATABASE_PATH, stock), index_col=[0], parse_dates=[0]).loc[:, 'amount'] for stock in self.stocks})
        volume = DataFrame({stock:pd.read_csv('%s/StockDailyData/Stock/%s.csv'%(gc.DATABASE_PATH, stock), index_col=[0], parse_dates=[0]).loc[:, 'vol'] for stock in self.stocks})

        average_price = amount / volume * 10
        
        ADJ = DataFrame({stock:pd.read_csv('%s/StockDailyData/Stock/%s.csv'%(gc.DATABASE_PATH, stock), index_col=[0], parse_dates=[0]).loc[:, 'adj_factor'] for stock in self.stocks})
        CLOSE = np.log(CLOSE * ADJ)
        average_price = np.log(average_price * ADJ)
        
        TURNRATE = DataFrame({stock:pd.read_csv('%s/StockTradingDerivativeData/Stock/%s.csv'%(gc.DATABASE_PATH, stock), index_col=[0], parse_dates=[0]).loc[:, 'TURNRATE'] for stock in self.stocks})
        TURNRATE[TURNRATE>0.99] = 0.99
        TURNRATE /= 64
        p = (1-TURNRATE).prod() / (1-TURNRATE).cumprod() * TURNRATE
        
        cum_p = p.cumsum()

        m1 = (average_price**1 * p).cumsum() / cum_p
        m2 = (average_price**2 * p).cumsum() / cum_p
        m3 = (average_price**3 * p).cumsum() / cum_p
        m4 = (average_price**4 * p).cumsum() / cum_p
        
        #v1 = 0
        v2 = m2 - m1**2
        v2[v2<1e-6] = np.nan
        v3 = m3 - 3*m2*m1 + 2*m1**3
        v4 = m4 - 4*m3*m1 + 6*m2*m1**2 - 3*m1**4
        
        #a = CLOSE / m1
        a = v2 / m1
        #a = np.log(a)
        #a = v3 / (v2**1.5)
        # a = v4 / (v2**3) - 3
        
        a = a.loc[a.index >= self.start_date, :]
        a = a.loc[a.index <= self.end_date, :]
        self.factor = a

#%%
if __name__ == '__main__':
    stocks = tools.get_stocks()
    stocks = list(filter(lambda x:x!='300950.SZ', stocks))
    a = ChipsCV('ChipsCV', stocks=stocks, start_date='20200101', end_date='20210228')
    
    a.generate_factor()
    
    a.factor_analysis()
    
