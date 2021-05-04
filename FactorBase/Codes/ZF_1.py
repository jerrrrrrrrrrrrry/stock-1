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

class ZF(SingleFactor):
    def generate_factor(self):
        data = {stock:pd.read_csv('%s/StockDailyData/Stock/%s.csv'%(gc.DATABASE_PATH, stock), index_col=[0], parse_dates=[0]) for stock in self.stocks}
        
        HIGH = DataFrame({stock:data[stock].loc[:, 'high'] for stock in self.stocks})
        LOW = DataFrame({stock:data[stock].loc[:, 'low'] for stock in self.stocks})
        
        HIGH.fillna(method='ffill', inplace=True)
        LOW.fillna(method='ffill', inplace=True)
        
        # # SYX = HIGH - (OPEN + CLOSE + np.abs(OPEN-CLOSE)) / 2
        # # XYX = (OPEN + CLOSE - np.abs(OPEN-CLOSE)) / 2 - LOW
        
        # # SYX = SYX / SYX.rolling(20).mean()
        # # XYX = XYX / XYX.rolling(20).mean()
        
        # # a = (SYX + XYX).rolling(20).std() / (SYX + XYX).rolling(20).mean()
        # a = (HIGH - LOW).rolling(20).std() / (HIGH - LOW).rolling(20).mean()
        # a = a.loc[a.index >= self.start_date, :]
        # a = a.loc[a.index <= self.end_date, :]
        
        n_list = [3, 5, 10, 20, 60, 120, 250]
        self.n_list = n_list
        a = []
        for n in n_list:
            a.append((HIGH - LOW).rolling(n).std() / (HIGH - LOW).rolling(n).mean())
        
        
        for i in range(len(a)):
            a[i] = a[i].loc[a[i].index >= self.start_date, :]
            a[i] = a[i].loc[a[i].index <= self.end_date, :]
        self.factor = a


#%%
if __name__ == '__main__':
    #获取股票
    stocks = tools.get_stocks()
    
    a = ZF('ZF', stocks=stocks, start_date='20200101', end_date='20210228')
    
    a.generate_factor()
    
    a.factor_analysis()
    