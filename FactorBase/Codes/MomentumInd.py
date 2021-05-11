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

class MomentumInd(SingleFactor):
    def generate_factor(self):
        data = {stock:pd.read_csv('%s/StockDailyData/Stock/%s.csv'%(gc.DATABASE_PATH, stock), index_col=[0], parse_dates=[0]) for stock in self.stocks}
        
        CLOSE = DataFrame({stock:data[stock].loc[:, 'close'] for stock in self.stocks})
        ADJ = DataFrame({stock:data[stock].loc[:, 'adj_factor'] for stock in self.stocks})
        CLOSE = CLOSE * ADJ
        CLOSE.fillna(method='ffill', inplace=True)
        
        n_list = [1, 3, 5, 10, 20, 60, 120, 250]
        self.n_list = n_list
        a = []
        for n in n_list:
            r = np.log(CLOSE).diff(n)
            ind_files = os.listdir('%s/Data'%gc.FACTORBASE_PATH)
            ind_files = list(filter(lambda x:x[0]=='8', ind_files))
            
            m = DataFrame(0, index=r.index, columns=r.columns)
            for ind_file in ind_files:
                ind_df = pd.read_csv('%s/Data/%s'%(gc.FACTORBASE_PATH, ind_file), index_col=[0], parse_dates=[0])
                ind_df = ind_df.loc[r.index, r.columns]
                ind_df[ind_df==0] = np.nan
                m = m.add(ind_df.mul((r * ind_df).mean(1), axis=0), fill_value=0)
            a.append(m)
        
        for i in range(len(a)):
            a[i] = a[i].loc[a[i].index >= self.start_date, :]
            a[i] = a[i].loc[a[i].index <= self.end_date, :]
        self.factor = a
        
if __name__ == '__main__':
    
    #获取股票
    stocks = tools.get_stocks()
    
    a = MomentumInd('MomentumInd', stocks=stocks, start_date='20200101', end_date='20210101')
    
    a.generate_factor()
    
    a.factor_analysis(industry_neutral=False, size_neutral=False, num_group=5)
    
