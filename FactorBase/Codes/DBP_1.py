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

class DBP(SingleFactor):
    def generate_factor(self):
        a = DataFrame({stock: pd.read_csv('%s/StockTradingDerivativeData/Stock/%s.csv'%(gc.DATABASE_PATH, stock), index_col=[0], parse_dates=[0]).loc[:, 'PB'] for stock in self.stocks})
        a = 1 / a
        a = a.diff(20)
        a = a.loc[a.index >= self.start_date, :]
        a = a.loc[a.index <= self.end_date, :]
        self.factor = a

#%%
#获取股票
if __name__ == '__main__':
    stocks = tools.get_stocks()
    
    
    a = DBP('DBP', stocks=stocks, start_date='20200101', end_date='20210221')
    
    a.generate_factor()
    
    a.factor_analysis()
    
