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

class CloseToAverage(SingleFactor):
    def generate_factor(self):
        CLOSE = DataFrame({stock:pd.read_csv('%s/StockDailyData/Stock/%s.csv'%(gc.DATABASE_PATH, stock), index_col=[0], parse_dates=[0]).loc[:, 'close'] for stock in self.stocks})
        amount = DataFrame({stock:pd.read_csv('%s/StockDailyData/Stock/%s.csv'%(gc.DATABASE_PATH, stock), index_col=[0], parse_dates=[0]).loc[:, 'amount'] for stock in self.stocks})
        volume = DataFrame({stock:pd.read_csv('%s/StockDailyData/Stock/%s.csv'%(gc.DATABASE_PATH, stock), index_col=[0], parse_dates=[0]).loc[:, 'vol'] for stock in self.stocks})
        average_price = amount / volume * 10
        a = np.log(CLOSE / average_price)
        
        a = a.loc[a.index >= self.start_date, :]
        a = a.loc[a.index <= self.end_date, :]
        self.factor = a

#%%
if __name__ == '__main__':
    #获取股票
    stocks = tools.get_stocks()
    
    a = CloseToAverage('CloseToAverage', stocks=stocks, start_date='20200101', end_date='20201130')
    
    a.generate_factor()
    
    a.factor_analysis()
    
