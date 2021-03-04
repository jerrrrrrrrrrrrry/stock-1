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

class STTGRN(SingleFactor):
    def generate_factor(self):
        dates = tools.get_trade_cal(self.start_date, self.end_date)
        tr = DataFrame({stock: pd.read_csv('%s/StockTradingDerivativeData/Stock/%s.csv'%(gc.DATABASE_PATH, stock), index_col=[0], parse_dates=[0]).loc[:, 'TURNRATE'] for stock in self.stocks})
        OPEN = DataFrame({stock:pd.read_csv('%s/StockDailyData/Stock/%s.csv'%(gc.DATABASE_PATH, stock), index_col=[0], parse_dates=[0]).loc[:, 'open'] for stock in self.stocks})
        CLOSE = DataFrame({stock:pd.read_csv('%s/StockDailyData/Stock/%s.csv'%(gc.DATABASE_PATH, stock), index_col=[0], parse_dates=[0]).loc[:, 'close'] for stock in self.stocks})
        ADJ = DataFrame({stock:pd.read_csv('%s/StockDailyData/Stock/%s.csv'%(gc.DATABASE_PATH, stock), index_col=[0], parse_dates=[0]).loc[:, 'adj_factor'] for stock in self.stocks})
        OPEN = OPEN * ADJ
        OPEN.fillna(method='ffill', inplace=True)
        CLOSE = CLOSE * ADJ
        CLOSE.fillna(method='ffill', inplace=True)
        r_rinei = np.log(CLOSE / OPEN)
        
        n = 20
        def f(r_rolling, tr):
            ind = r_rolling.index
            tr_tmp = tr.loc[ind].rank()
            return (r_rolling * tr_tmp).mean()
        dates = [datetime.datetime.strptime(date, '%Y%m%d') for date in dates]
        sttg = DataFrame(index=dates, columns=CLOSE.columns)
        for stock in sttg.columns:
            r_rinei_tmp = r_rinei.loc[:, stock]
            tr_tmp = tr.loc[:, stock]
            sttg.loc[:, stock] = r_rinei_tmp.rolling(n).apply(func=f, args=(tr_tmp.shift(),))
        
        #tr = tr - tr.rolling(n).mean()
        
        #sttg_rinei = (r_rinei.rolling(n) * tr.rolling(n)).mean()
        #sttg_geye = (r_geye.rolling(n) * tr.rolling(n)).mean()
        #sttg_rinei = r_rinei.rolling(n).apply(func=f)
        #sttg_geye = r_geye.rolling(n).apply(func=f)
        #sttg = sttg_geye - sttg_rinei
        a = sttg    
        a = a.loc[a.index >= self.start_date, :]
        a = a.loc[a.index <= self.end_date, :]
        self.factor = a


#%%
if __name__ == '__main__':
    #获取股票
    stocks = tools.get_stocks()
    
    a = STTGRN('STTGRN', stocks=stocks, start_date='20200101', end_date='20210228')
    
    a.generate_factor()
    
    a.factor_analysis()
    