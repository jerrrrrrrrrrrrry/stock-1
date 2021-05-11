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

class TurnRate(SingleFactor):
    def generate_factor(self):
        tr = DataFrame({stock: pd.read_csv('%s/StockTradingDerivativeData/Stock/%s.csv'%(gc.DATABASE_PATH, stock), index_col=[0], parse_dates=[0]).loc[:, 'TURNRATE'] for stock in self.stocks})
        tr = np.log(tr)
        n_list = [1, 3, 5, 10, 20, 60, 120]
        self.n_list = n_list
        a = []
        for n in n_list:
            a.append(tr.rolling(n).mean())
        
        for i in range(len(a)):
            a[i] = a[i].loc[a[i].index >= self.start_date, :]
            a[i] = a[i].loc[a[i].index <= self.end_date, :]
        self.factor = a


#%%
if __name__ == '__main__':
    #获取股票
    stocks = tools.get_stocks()
    
    a = TurnRate('TurnRate', stocks=stocks, start_date='20200101', end_date='20201010')
    
    a.generate_factor()
    
    a.factor_analysis()
    