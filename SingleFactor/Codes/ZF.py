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
        dates = tools.get_trade_cal(self.start_date, self.end_date)
        OPEN = DataFrame({stock:pd.read_csv('%s/StockDailyData/Stock/%s.csv'%(gc.DATABASE_PATH, stock), index_col=[0], parse_dates=[0]).loc[:, 'open'] for stock in self.stocks})
        HIGH = DataFrame({stock:pd.read_csv('%s/StockDailyData/Stock/%s.csv'%(gc.DATABASE_PATH, stock), index_col=[0], parse_dates=[0]).loc[:, 'high'] for stock in self.stocks})
        LOW = DataFrame({stock:pd.read_csv('%s/StockDailyData/Stock/%s.csv'%(gc.DATABASE_PATH, stock), index_col=[0], parse_dates=[0]).loc[:, 'low'] for stock in self.stocks})
        CLOSE = DataFrame({stock:pd.read_csv('%s/StockDailyData/Stock/%s.csv'%(gc.DATABASE_PATH, stock), index_col=[0], parse_dates=[0]).loc[:, 'close'] for stock in self.stocks})
        ADJ = DataFrame({stock:pd.read_csv('%s/StockDailyData/Stock/%s.csv'%(gc.DATABASE_PATH, stock), index_col=[0], parse_dates=[0]).loc[:, 'adj_factor'] for stock in self.stocks})
        OPEN = OPEN * ADJ
        OPEN.fillna(method='ffill', inplace=True)
        HIGH = HIGH * ADJ
        HIGH.fillna(method='ffill', inplace=True)
        LOW = LOW * ADJ
        LOW.fillna(method='ffill', inplace=True)
        CLOSE = CLOSE * ADJ
        CLOSE.fillna(method='ffill', inplace=True)
        
        # SYX = HIGH - (OPEN + CLOSE + np.abs(OPEN-CLOSE)) / 2
        # XYX = (OPEN + CLOSE - np.abs(OPEN-CLOSE)) / 2 - LOW
        
        # SYX = SYX / SYX.rolling(20).mean()
        # XYX = XYX / XYX.rolling(20).mean()
        
        # a = (SYX + XYX).rolling(20).std() / (SYX + XYX).rolling(20).mean()
        a = (HIGH - LOW).rolling(20).std() / (HIGH - LOW).rolling(20).mean()
        a = a.loc[a.index >= self.start_date, :]
        a = a.loc[a.index <= self.end_date, :]
        self.factor = a


#%%
if __name__ == '__main__':
    #获取股票
    stocks = tools.get_stocks()
    
    a = ZF('ZF', stocks=stocks, start_date='20200101', end_date='20210228')
    
    a.generate_factor()
    
    a.factor_analysis()
    