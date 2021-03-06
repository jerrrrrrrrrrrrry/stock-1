# -*- coding: utf-8 -*-
"""
Created on Tue Feb  9 23:09:23 2021

@author: admin
"""

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

class HFSkewMean(SingleFactor):
    def generate_factor(self):
        skew = pd.read_csv('%s/Data/HFSkew.csv'%gc.FACTORBASE_PATH, index_col=[0], parse_dates=[0])
        skew.fillna(method='ffill', inplace=True)
        n = 20
        skew_mean = skew.rolling(n).mean()
        a = skew_mean
        a = a.loc[a.index >= self.start_date, :]
        a = a.loc[a.index <= self.end_date, :]
        self.factor = a



#%%
if __name__ == '__main__':
    #获取股票
    stocks = tools.get_stocks()

    a = HFSkewMean('HFSkewMean', stocks=stocks, start_date='20200901', end_date='20210128')
    
    a.generate_factor()
    
    a.factor_analysis()
    
    
