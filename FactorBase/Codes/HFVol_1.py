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

class HFVol(SingleFactor):
    def generate_factor(self):
        
        trade_cal = tools.get_trade_cal(self.start_date, self.end_date)
        vol_rate = DataFrame()
        for date in trade_cal:
            files = os.listdir('%s/StockSnapshootData/%s'%(gc.DATABASE_PATH, date))
            
            data_dic = {file.split('.')[1]:pd.read_csv('%s/StockSnapshootData/%s/%s'%(gc.DATABASE_PATH, date, file), index_col=[0], parse_dates=[0]) for file in files}
            keys = list(data_dic.keys())
            for key in keys:
                if len(data_dic[key]) == 0:
                    del data_dic[key]
            keys = list(data_dic.keys())
            stocks = [stock + '.SH' if stock[0]=='6' else stock + '.SZ' for stock in keys]
            
            vol_dic = {}
            for stock in stocks:
                vol_dic[stock] = data_dic[stock[:6]].loc[:, 'last_volume']
                vol_dic[stock] = vol_dic[stock][~vol_dic[stock].index.duplicated()]
                
            vol = DataFrame(vol_dic)
            vol.fillna(0, inplace=True)
            vol1 = vol.loc[vol.index<'%s094500'%(date.replace('-', '')), :]
            vol2 = vol.loc[vol.index>'%s145500'%(date.replace('-', '')), :]
            vol_rate_daily = (vol1.sum() + vol2.sum()) / vol.sum()
            
            vol_rate = pd.concat([vol_rate, DataFrame({date:vol_rate_daily}).T], axis=0)

        a = vol_rate
        self.factor = a

#%%
if __name__ == '__main__':
    #获取股票
    stocks = tools.get_stocks()

    a = HFVol('HFVol', stocks=stocks, start_date='20200901', end_date='20210128')
    
    a.generate_factor()
    
    a.factor_analysis()
    
    
