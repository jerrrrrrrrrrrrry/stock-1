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

class HFReversal(SingleFactor):
    def generate_factor(self):
        
        trade_cal = tools.get_trade_cal(self.start_date, self.end_date)
        r = DataFrame()
        for date in trade_cal:
            if os.path.exists('%s/StockSnapshootData/%s'%(gc.DATABASE_PATH, date)):
                files = os.listdir('%s/StockSnapshootData/%s'%(gc.DATABASE_PATH, date))
            else:
                continue
            
            data_dic = {file.split('.')[1]:pd.read_csv('%s/StockSnapshootData/%s/%s'%(gc.DATABASE_PATH, date, file), index_col=[0], parse_dates=[0]) for file in files}
            keys = list(data_dic.keys())
            for key in keys:
                if len(data_dic[key]) == 0:
                    del data_dic[key]
            
            price = DataFrame({'%s.SZ'%stock:data_dic[stock].loc[:, 'price'] for stock in data_dic.keys()})
            price.fillna(method='ffill', inplace=True)
            r_daily = np.log(price).diff()
            r_daily.fillna(0, inplace=True)
            reversal_ind = (price.index>='%s100000'%(date.replace('-', ''))) & (price.index<'%s150100'%(date.replace('-', '')))
            momentum_ind = (price.index>='%s093000'%(date.replace('-', ''))) & (price.index<'%s100000'%(date.replace('-', '')))
            reversal = r_daily.loc[reversal_ind, :].sum()
            momentum = r_daily.loc[momentum_ind, :].sum()
            
            # price = price.loc[(price.index>='%s100000'%(date.replace('-', ''))) & (price.index<'%s150100'%(date.replace('-', ''))), :]
            # r_daily = np.log(price).diff()
            # r_daily.fillna(0, inplace=True)
            # r_daily = r_daily.sum()
            r = pd.concat([r, DataFrame({date:reversal - momentum}).T], axis=0)
        n = 20
        a = r.rolling(n).mean()
        self.factor = a



#%%
if __name__ == '__main__':
    #????????????
    stocks = tools.get_stocks()

    a = HFReversal('HFReversal', stocks=stocks, start_date='20200901', end_date='20210228')
    
    a.generate_factor()
    
    a.factor_analysis()
    
    
