import tushare as ts
import os
import sys
import time
import datetime
import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import Config
sys.path.append(Config.GLOBALCONFIG_PATH)
import Global_Config as gc



if len(sys.argv) == 3:
    start = sys.argv[1]
    end = sys.argv[2]
elif len(sys.argv) == 2:
    today = sys.argv[1]
    start = today
    end = today
else:
    today = datetime.datetime.today().strftime('%Y%m%d')
    start = today
    end = today

pro = ts.pro_api()

#获取行业分类
stocks = pro.stock_basic(fields='ts_code').ts_code

trade_cal = pd.read_csv('%s/TradeCalData/TradeCal.csv'%gc.DATABASE_PATH)

trade_cal.loc[:, 'cal_date'] = [str(i) for i in trade_cal.loc[:, 'cal_date']]

trade_cal = trade_cal.loc[trade_cal.loc[:, 'is_open']==1, 'cal_date']

if start == end:
    trade_cal = trade_cal.loc[trade_cal < end].iloc[-1:]
else:
    trade_cal = trade_cal.loc[trade_cal >= start]
    trade_cal = trade_cal.loc[trade_cal <= end]

df = DataFrame()
for trade_date in trade_cal:
    hk_hold = pro.hk_hold(fields='ts_code, vol', start_date=trade_date, end_date=trade_date).set_index('ts_code')
    hk_hold.columns = [trade_date]
    df = pd.concat([df, hk_hold.T], axis=0)
    
if os.path.exists('%s/StockMoneyData/hk.csv'%gc.DATABASE_PATH):
    df_old = pd.read_csv('%s/StockMoneyData/hk.csv'%gc.DATABASE_PATH, index_col=[0])
    df = pd.concat([df_old, df.loc[df.index>str(df_old.index[-1]), :]], axis=0)
    df.to_csv('%s/StockMoneyData/hk.csv'%gc.DATABASE_PATH)
else:
    if len(df) > 0:
        df.to_csv('%s/StockMoneyData/hk.csv'%gc.DATABASE_PATH)