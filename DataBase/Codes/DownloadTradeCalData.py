# -*- coding: utf-8 -*-
"""
Created on Sun Jan 10 10:47:16 2021

@author: admin
"""
import tushare as ts
import Config
import sys
sys.path.append(Config.GLOBALCONFIG_PATH)
import Global_Config as gc

if __name__ == '__main__':
    pro = ts.pro_api()
    df = pro.trade_cal(exchange='', start_date='20100101', end_date='20221231').set_index('cal_date').loc[:, ['is_open']]
    df.to_csv('%s/TradeCalData/TradeCal.csv'%gc.DATABASE_PATH)