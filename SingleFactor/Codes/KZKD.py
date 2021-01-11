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

import Config
sys.path.append(Config.GLOBALCONFIG_PATH)
from SingleFactor import SingleFactor
import Global_Config as gc
import tools
#%%

class KZKD(SingleFactor):
    def generate_factor(self):
        kzkd = pd.read_csv('%s/StockKZKDData/KZKDDFCF.csv'%(gc.DATABASE_PATH), index_col=[0])
        kzkd.loc[:, 'time'] = [ind.split(' ')[1] for ind in kzkd.index]
        kzkd = kzkd.loc[kzkd.time=='23:00:00', :]
        kzkd.index = [ind.split(' ')[0].replace('-', '') for ind in kzkd.index]
        kzkd.drop('time', axis=1, inplace=True)
        kzkd.columns = [col+'.SZ' for col in kzkd.columns]
        a = kzkd.diff()
        a = a.loc[a.index >= self.start_date, :]
        a = a.loc[a.index <= self.end_date, :]
        self.factor = a



#%%
if __name__ == '__main__':
    #获取股票
    stocks = tools.get_stocks()

    a = KZKD('KZKD', stocks=stocks, start_date='20201201', end_date='20201230')
    
    a.generate_factor()
    
    a.factor_analysis()
    
    
