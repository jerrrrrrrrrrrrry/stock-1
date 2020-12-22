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



class Kurt(SingleFactor):
    def generate_factor(self):
        CLOSE = DataFrame({stock:pd.read_csv('%s/StockDailyData/Stock/%s.csv'%(gc.DATABASE_PATH, stock), index_col=[0], parse_dates=[0]).loc[:, 'close'] for stock in stocks})
        ADJ = DataFrame({stock:pd.read_csv('%s/StockDailyData/Stock/%s.csv'%(gc.DATABASE_PATH, stock), index_col=[0], parse_dates=[0]).loc[:, 'adj_factor'] for stock in stocks})
        CLOSE = CLOSE * ADJ
        r = np.log(CLOSE).diff()
        n = 20
        a = r.rolling(n).kurt()
        
        a = a.loc[a.index >= self.start_date, :]
        a = a.loc[a.index <= self.end_date, :]
        self.factor = a
        
        
#%%
if __name__ == '__main__':
    #获取股票
    stocks = tools.get_stocks()
    a = Kurt('Kurt', stocks=stocks, start_date='20200101', end_date='20201010')
    
    a.generate_factor()
    
    a.factor_analysis()
    
