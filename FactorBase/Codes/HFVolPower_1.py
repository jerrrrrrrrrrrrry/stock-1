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

class HFVolPower(SingleFactor):
    def generate_factor(self):
        
        trade_cal = tools.get_trade_cal(self.start_date, self.end_date)
        power = DataFrame()
        
        def estimate_power(s, n=10):
            y = np.log(np.arange(1,n)/n)
            x = np.log(np.array([s.quantile(i) for i in np.arange(1,n)/n]))
            y = y - y.mean()
            x = x - x.mean()
            power = (x * y).sum() / (x * x).sum()
            return power
        
        for date in trade_cal:
            files = os.listdir('%s/StockSnapshootData/%s'%(gc.DATABASE_PATH, date))
            
            data_dic = {file.split('.')[1]:pd.read_csv('%s/StockSnapshootData/%s/%s'%(gc.DATABASE_PATH, date, file), index_col=[0], parse_dates=[0]) for file in files}
            keys = list(data_dic.keys())
            for key in keys:
                if len(data_dic[key]) == 0:
                    del data_dic[key]
            
            vol = DataFrame({'%s.SZ'%stock:data_dic[stock].loc[:, 'last_volume'] for stock in data_dic.keys()})
            vol.fillna(0, inplace=True)
            vol = vol.loc[vol.index>='%s093000'%(date.replace('-', '')), :]
            vol = vol.resample('1T').sum()
            vol[vol==0] = 1
            
            power_daily = vol.apply(func=estimate_power, axis=0)
            
            power = pd.concat([power, DataFrame({date:power_daily}).T], axis=0)

        a = power
        self.factor = a



#%%
if __name__ == '__main__':
    #获取股票
    stocks = tools.get_stocks()

    a = HFVolPower('HFVolPower', stocks=stocks, start_date='20200901', end_date='20210128')
    
    a.generate_factor()
    
    a.factor_analysis()
    
    
