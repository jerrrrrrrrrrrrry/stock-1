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


class DHK(SingleFactor):
    def generate_factor(self):
        CLOSE = DataFrame({stock: pd.read_csv('%s/StockDailyData/Stock/%s.csv'%(gc.DATABASE_PATH, stock), index_col=[0], parse_dates=[0]).loc[:, 'close'] for stock in self.stocks})
        
        hk = pd.read_csv('%s/StockMoneyData/HK.csv'%gc.DATABASE_PATH, index_col=[0], parse_dates=[0])
        hk.fillna(method='ffill', inplace=True)
        hk.fillna(0, inplace=True)
        hk = DataFrame(hk, index=CLOSE.index, columns=hk.columns)
        CLOSE = CLOSE.loc[CLOSE.index >= self.start_date, :]
        CLOSE = CLOSE.loc[CLOSE.index <= self.end_date, :]
        
        hk = hk.shift().loc[CLOSE.index, :]
        hk_hold = DataFrame(0, index=CLOSE.index, columns=self.stocks)
        hk_hold.loc[hk.index, hk.columns] = hk
        
        hk_amount = hk_hold * CLOSE
        hk_amount = hk_amount.sub(hk_amount.mean(1), axis=0)
        hk_amount.fillna(0, inplace=True)
        hk_amount = hk_amount.div(hk_amount.std(1), axis=0)
        
        dhk = hk_amount.diff(20)
        dhk = dhk.sub(dhk.mean(1), axis=0)
        dhk.fillna(0, inplace=True)
        dhk = dhk.div(dhk.std(1), axis=0)
        def f(y, x):
            beta = y.corrwith(x, axis=1) * y.std(1) / x.std(1)
            alpha = y.mean(1) - x.mean(1) * beta
            e = y.sub(x.mul(beta, axis=0).add(alpha, axis=0), axis=0)
            return e
        a = f(dhk, hk_amount)
        a = a.loc[a.index >= self.start_date, :]
        a = a.loc[a.index <= self.end_date, :]
        self.factor = a
#%%


if __name__ == '__main__':
    
    #获取股票
    stocks = tools.get_stocks()
    
    a = DHK('DHK', stocks=stocks, start_date='20180101', end_date='20210301')
    
    a.generate_factor()
    
    a.factor_analysis()
    
