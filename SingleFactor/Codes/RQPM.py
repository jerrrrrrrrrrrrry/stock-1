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

class RQPM(SingleFactor):
    def generate_factor(self):
        rqpm = pd.read_csv('%s/StockRQPMData/RQPMTHS.csv'%(gc.DATABASE_PATH), index_col=[0], parse_dates=[0])
        rqpm.fillna(method='ffill', inplace=True)
        rqpm.columns = [col+'.SZ' for col in rqpm.columns]
        a = rqpm
        a = a.loc[a.index >= self.start_date, :]
        a = a.loc[a.index <= self.end_date, :]
        self.factor = a



#%%
if __name__ == '__main__':
    #获取股票
    stocks = tools.get_stocks()

    a = RQPM('RQPM', stocks=stocks, start_date='20201201', end_date='20210416')
    
    a.generate_factor()
    
    a.factor_analysis(num_group=10)
    
    
