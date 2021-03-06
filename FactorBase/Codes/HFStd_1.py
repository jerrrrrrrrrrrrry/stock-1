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

class HFStd(SingleFactor):
    def generate_factor(self):
        
        trade_cal = tools.get_trade_cal(self.start_date, self.end_date)
        std = DataFrame()
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
            keys = list(data_dic.keys())
            stocks = [stock + '.SH' if stock[0]=='6' else stock + '.SZ' for stock in keys]
            price_dic = {}
            for stock in stocks:
                price_dic[stock] = data_dic[stock[:6]].loc[:, 'price']
                price_dic[stock] = price_dic[stock][~price_dic[stock].index.duplicated()]
                
            price = DataFrame(price_dic)
            price.fillna(method='ffill', inplace=True)
            price = price.loc[(price.index>='%s093000'%(date.replace('-', ''))) & (price.index<'%s150100'%(date.replace('-', ''))), :]
            r_daily = np.log(price).diff()
            r_daily.fillna(0, inplace=True)
            std_daily = r_daily.resample(rule='5T').sum().std()
            std = pd.concat([std, DataFrame({date:std_daily}).T], axis=0)
        
        a = std
        self.factor = a
    

#%%
if __name__ == '__main__':
    #????????????
    stocks = tools.get_stocks()

    a = HFStd('HFStd', stocks=stocks, start_date='20200901', end_date='20210228')
    
    a.generate_factor()
    
    a.factor_analysis()
    
    
