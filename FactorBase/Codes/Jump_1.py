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
class Jump(SingleFactor):
    def generate_factor(self):
        data = {stock:pd.read_csv('%s/StockDailyData/Stock/%s.csv'%(gc.DATABASE_PATH, stock), index_col=[0], parse_dates=[0]) for stock in self.stocks}
        
        OPEN = DataFrame({stock:data[stock].loc[:, 'open'] for stock in self.stocks})
        CLOSE = DataFrame({stock:data[stock].loc[:, 'close'] for stock in self.stocks})
        ADJ = DataFrame({stock:data[stock].loc[:, 'adj_factor'] for stock in self.stocks})
        
        OPEN = OPEN * ADJ
        CLOSE = CLOSE * ADJ
        jump = np.log(OPEN / CLOSE.shift())
        n_list = [1, 3, 5, 10, 20]
        self.n_list = n_list
        a = []
        for n in n_list:
            a.append(jump.rolling(n).mean())
        
        for i in range(len(a)):
            a[i] = a[i].loc[a[i].index >= self.start_date, :]
            a[i] = a[i].loc[a[i].index <= self.end_date, :]
        self.factor = a

#%%
if __name__ == '__main__':
    #获取股票
    stocks = tools.get_stocks()
    
    a = Jump('Jump', stocks=stocks, start_date='20200101', end_date='20201201')
    
    a.generate_factor()
    
    a.factor_analysis()
