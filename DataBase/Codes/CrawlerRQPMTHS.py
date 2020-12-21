# -*- coding: utf-8 -*-
"""
Created on Sat Nov 21 12:54:11 2020

@author: 王佳欢
"""
import os
import sys
import datetime
from lxml import etree
import requests
import json
import os
import pickle
import random
import time
import numpy as np
import tushare as ts
import pandas as pd
from pandas import Series, DataFrame
import winsound

if __name__ == '__main__':
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:00')
    hour = datetime.datetime.now().strftime('%H')
    date = datetime.datetime.today().strftime('%Y-%m-%d')
    pro = ts.pro_api()
    #获取股票
    stocks = pro.stock_basic(fields='symbol, list_date, market')
    stocks = stocks.loc[stocks.market=='创业板', :]
    codes = stocks.loc[:, 'symbol']
    data = {}
    ept = []
    for code in codes:
        time.sleep(np.random.exponential(0.05))
        times_max = 10
        while times_max > 0:
            try:
                header = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.'+str(random.randint(0,999))+' Safari/537.36'
                ua_headers = {'User-Agent':header}
                url = 'http://basic.10jqka.com.cn/mapp/%s/a_stock_foucs.json'%code
                html = requests.get(url, headers=ua_headers)
                dic = json.loads(html.content)
                rank = dic['data']['all_rank'] / dic['data']['all_num']
                data[code] = rank
                print(code, rank)
                break
            except:
                time.sleep(5)
                times_max -= 1
        if times_max == 0:
            winsound.Beep(600,10000)
            DataFrame(Series([code])).to_csv('D:/stock/DataBase/StockRQPMData/THS%s_error%s.csv'%(date, hour))
    df = DataFrame(data, index=[now])
    if os.path.exists('D:/stock/DataBase/StockRQPMData/RQPMTHS.csv'):
        df_old = pd.read_csv('D:/stock/DataBase/StockRQPMData/RQPMTHS.csv', index_col=[0])
        print(type(df_old.index[-1]))
        if df_old.index[-1] < now:
            df = pd.concat([df_old, df], axis=0)
            df.sort_index(axis=0, inplace=True)
            df.sort_index(axis=1, inplace=True)
    df.to_csv('D:/stock/DataBase/StockRQPMData/RQPMTHS.csv')