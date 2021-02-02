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


class MF(SingleFactor):
    def generate_factor(self):
        elg_mf = pd.read_csv('%s/StockMoneyData/elg_mf.csv'%gc.DATABASE_PATH, index_col=[0], parse_dates=[0])
        lg_mf = pd.read_csv('%s/StockMoneyData/lg_mf.csv'%gc.DATABASE_PATH, index_col=[0], parse_dates=[0])
        md_mf = pd.read_csv('%s/StockMoneyData/md_mf.csv'%gc.DATABASE_PATH, index_col=[0], parse_dates=[0])
        sm_mf = pd.read_csv('%s/StockMoneyData/sm_mf.csv'%gc.DATABASE_PATH, index_col=[0], parse_dates=[0])
        net_mf = pd.read_csv('%s/StockMoneyData/net_mf.csv'%gc.DATABASE_PATH, index_col=[0], parse_dates=[0])
        
        elg_mf.fillna(0, inplace=True)
        lg_mf.fillna(0, inplace=True)
        md_mf.fillna(0, inplace=True)
        sm_mf.fillna(0, inplace=True)
        net_mf.fillna(0, inplace=True)
        
        mf = sm_mf + 0.33*md_mf - 0.33*lg_mf - elg_mf
        cols = list(filter(lambda x:x[0]=='3', mf.columns))
        mf = mf.loc[:, cols]
        
        a = mf
        a = a.loc[a.index >= self.start_date, :]
        a = a.loc[a.index <= self.end_date, :]
        self.factor = a
#%%


if __name__ == '__main__':
    
    #获取股票
    stocks = tools.get_stocks()
    
    a = MF('MF', stocks=stocks, start_date='20200101', end_date='20201230')
    
    a.generate_factor()
    
    a.factor_analysis()
    
