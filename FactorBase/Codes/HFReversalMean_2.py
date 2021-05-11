#!/usr/bin/env python
# coding: utf-8

#%%
import sys
import datetime
import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import matplotlib.pyplot as plt
import tushare as ts
import os
import Config
sys.path.append(Config.GLOBALCONFIG_PATH)
from SingleFactor import SingleFactor
import Global_Config as gc
import tools
#%%

class HFReversalMean(SingleFactor):
    def generate_factor(self):
        reversal = pd.read_csv('%s/Data/HFReversal.csv'%gc.FACTORBASE_PATH, index_col=[0], parse_dates=[0])
        reversal.fillna(method='ffill', inplace=True)
        n_list = [3, 5, 10, 20, 60]
        self.n_list = n_list
        a = []
        for n in n_list:
            a.append(reversal.rolling(n).mean())
        for i in range(len(a)):
            a[i] = a[i].loc[a[i].index >= self.start_date, :]
            a[i] = a[i].loc[a[i].index <= self.end_date, :]
        self.factor = a



#%%
if __name__ == '__main__':
    #获取股票
    stocks = tools.get_stocks()

    a = HFReversalMean('HFReversalMean', stocks=stocks, start_date='20200901', end_date='20210128')
    
    a.generate_factor()
    
    a.factor_analysis()
    
    
