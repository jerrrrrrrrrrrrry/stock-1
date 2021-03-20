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

class MomentumBK(SingleFactor):
    def generate_factor(self):
        data = {stock:pd.read_csv('%s/StockDailyData/Stock/%s.csv'%(gc.DATABASE_PATH, stock), index_col=[0], parse_dates=[0]) for stock in self.stocks}
        
        CLOSE = DataFrame({stock:data[stock].loc[:, 'close'] for stock in self.stocks})
        ADJ = DataFrame({stock:data[stock].loc[:, 'adj_factor'] for stock in self.stocks})
        
        CLOSE.fillna(method='ffill', inplace=True)
        ADJ.fillna(method='ffill', inplace=True)
        
        CLOSE = CLOSE * ADJ
        r = np.log(CLOSE).diff(20)
        
        
        cols = list(r.columns)
        bk_list = ['00', '30', '60', '68']
        bks = {bk: list(filter(lambda x:x[:2]==bk, cols)) for bk in bk_list}
        
        a = DataFrame({col: r.loc[:, bks[col[:2]]].mean(1) + np.random.randn(len(r))/1000 for col in cols})
        
        a = a.loc[a.index >= self.start_date, :]
        a = a.loc[a.index <= self.end_date, :]
        self.factor = tools.standardize(a)
        
#%%


if __name__ == '__main__':
    
    #获取股票
    stocks = tools.get_stocks()
    
    a = MomentumBK('MomentumBK', stocks=stocks, start_date='20180101', end_date='20210224')
    
    a.generate_factor()
    
    a.factor_analysis(industry_neutral=False, size_neutral=False, num_group=10)
    
