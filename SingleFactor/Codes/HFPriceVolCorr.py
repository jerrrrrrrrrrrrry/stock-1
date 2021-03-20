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

class HFPriceVolCorr(SingleFactor):
    def generate_factor(self):
        
        trade_cal = tools.get_trade_cal(self.start_date, self.end_date)
        corr = DataFrame()
        for date in trade_cal:
            files = os.listdir('%s/StockSnapshootData/%s'%(gc.DATABASE_PATH, date))
            
            data_dic = {file.split('.')[1]:pd.read_csv('%s/StockSnapshootData/%s/%s'%(gc.DATABASE_PATH, date, file), index_col=[0], parse_dates=[0]) for file in files}
            keys = list(data_dic.keys())
            for key in keys:
                if len(data_dic[key]) == 0:
                    del data_dic[key]
            
            stocks = [stock + '.SH' if stock[0]=='6' else stock + '.SZ' for stock in keys]
            amount = DataFrame({stock:data_dic[stock[:6]].loc[:, 'last_amount'] for stock in stocks})
            amount.fillna(0, inplace=True)
            vol = DataFrame({stock:data_dic[stock[:6]].loc[:, 'last_volume'] for stock in stocks})
            vol.fillna(0, inplace=True)
            
            amount = amount.loc[amount.index>'%s100000'%(date.replace('-', '')), :]
            vol = vol.loc[vol.index>'%s100000'%(date.replace('-', '')), :]
            
            amount = amount.resample('5T').sum()
            vol = vol.resample('5T').sum()
            price = amount / vol
            corr_daily = price.corrwith(vol, axis=0)
            
            corr = pd.concat([corr, DataFrame({date:corr_daily}).T], axis=0)
            
        a = corr
        self.factor = a

#%%
if __name__ == '__main__':
    #获取股票
    stocks = tools.get_stocks()

    a = HFPriceVolCorr('HFPriceVolCorr', stocks=stocks, start_date='20200901', end_date='20210128')
    
    a.generate_factor()
    
    a.factor_analysis()
    
    
