# -*- coding: utf-8 -*-
"""
Created on Sat Nov 21 12:54:11 2020

@author: 王佳欢
"""
import os
import sys
import datetime
import re
from selenium import webdriver
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
    hour = datetime.datetime.now().strftime('%H')
    date = datetime.datetime.today().strftime('%Y%m%d')
    pro = ts.pro_api()
    #获取股票
    stocks = pro.stock_basic(fields='symbol, list_date, market')
    stocks = stocks.loc[stocks.market=='创业板', :]
    codes = stocks.loc[:, 'symbol']
    data = {}
    ept = []
    option = webdriver.ChromeOptions()
    option.add_argument('headless')
    driver = webdriver.Chrome(options=option)
    for code in codes:
        #time.sleep(np.random.exponential(0.05))
        times_max = 10
        while times_max > 0:
            try:
                driver.get('http://guba.eastmoney.com/list,%s.html'%code)
                xpath = "//div[@id='popularity_rank']"
                a = driver.find_element_by_xpath(xpath)
                rank = re.sub('\\D', "", a.text)
                data[code] = rank
                print(code, rank)
                break
            except:
                time.sleep(5)
                times_max -= 1
        if times_max == 0:
            winsound.Beep(600,10000)
            DataFrame(Series([code])).to_csv('D:/stock/DataBase/StockRQPMData/DFCF%s_error%s.csv'%(date, hour))
    df = DataFrame(data, index=[int(datetime.datetime.today().strftime('%Y%m%d'))])
    if os.path.exists('D:/stock/DataBase/StockRQPMData/DFCF%s.csv'%hour):
        df_old = pd.read_csv('D:/stock/DataBase/StockRQPMData/DFCF%s.csv'%hour, index_col=[0])
        print(type(df_old.index[-1]))
        if df_old.index[-1] < int(datetime.datetime.today().strftime('%Y%m%d')):
            df = pd.concat([df_old, df], axis=0)
            df.sort_index(axis=0, inplace=True)
            df.sort_index(axis=1, inplace=True)
    df.to_csv('D:/stock/DataBase/StockRQPMData/DFCF%s.csv'%hour)