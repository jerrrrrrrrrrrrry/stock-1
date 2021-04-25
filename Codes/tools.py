import os
import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import matplotlib.pyplot as plt
import datetime
import time
import DataProcessor as DP
from scipy.stats import rankdata
import tushare as ts
import Global_Config as gc

def get_trade_cal(start_date='20200101', end_date='20201231'):
    trade_cal = pd.read_csv('%s/TradeCalData/TradeCal.csv'%gc.DATABASE_PATH, index_col=[0], parse_dates=[0])
    trade_cal = trade_cal.loc[(trade_cal.index>=start_date) & (trade_cal.index<=end_date), :]
    trade_cal = list(trade_cal.loc[trade_cal.is_open==1, :].index.astype('str'))
    trade_cal = [s.replace('-', '') for s in trade_cal]
    return trade_cal

def get_industrys(level='L1', stocks=None):
    #获取行业分类
    file_list = os.listdir(gc.DATABASE_PATH+'/StockIndustryData')
    file_list.sort()
    file = file_list[-1]
    df = pd.read_csv(gc.DATABASE_PATH+'/StockIndustryData/%s'%file, dtype=str)
    df.dropna(inplace=True)
    
    ind_name_code_dict = {'农林牧渔':'801010.SI',
                          '采掘':'801020.SI',
                          '化工':'801030.SI',
                          '钢铁':'801040.SI',
                          '有色金属':'801050.SI',
                          '电子':'801080.SI',
                          '家用电器':'801110.SI',
                          '食品饮料':'801120.SI',
                          '纺织服装':'801130.SI',
                          '轻工制造':'801140.SI',
                          '医药生物':'801150.SI',
                          '公用事业':'801160.SI',
                          '交通运输':'801170.SI',
                          '房地产':'801180.SI',
                          '商业贸易':'801200.SI',
                          '休闲服务':'801210.SI',
                          '综合':'801230.SI',
                          '建筑材料':'801710.SI',
                          '建筑装饰':'801720.SI',
                          '电气设备':'801730.SI',
                          '国防军工':'801740.SI',
                          '计算机':'801750.SI',
                          '传媒':'801760.SI',
                          '通信':'801770.SI',
                          '银行':'801780.SI',
                          '非银金融':'801790.SI',
                          '汽车':'801880.SI',
                          '机械设备':'801890.SI',
                          }
    industrys = {}
    for ind_name in ind_name_code_dict.keys():
        industrys[ind_name_code_dict[ind_name]] = list(df.loc[df.loc[:,'行业名称']==ind_name, '股票代码'])
        industrys[ind_name_code_dict[ind_name]] = [stock + '.SZ' if (stock[0]=='0' or stock[0]=='3') else stock + '.SH' for stock in industrys[ind_name_code_dict[ind_name]]]
    
    if stocks:
        def cond(stock):
            return stock in stocks
        industrys = {i:list(filter(cond, industrys[i])) for i in industrys.keys()}
    
        stocks.clear()
        for v in industrys.values():
            stocks.extend(v)
        stocks.sort()
    return industrys


def get_stocks(cond=None):
    if cond == None:
        def cond(stock):
            return True
    pro = ts.pro_api()
    stocks = pro.stock_basic(fields='ts_code, list_date')
    stocks = stocks.loc[stocks.list_date < datetime.datetime.today().strftime('%Y%m%d'), 'ts_code']
    stocks = list(filter(lambda x:x!='689009.SH', stocks))
    stocks = list(filter(lambda x:x!="600086.SH", stocks))
    stocks = list(filter(lambda x:x!="600634.SH", stocks))
    return list(filter(cond, stocks))


def sharpe_ratio_ts(df, n):
    return df.rolling(n).mean() / df.rolling(n).std()

def reg_ts(df, n):
    x = np.arange(n)
    x = x - x.mean()
    b = df.rolling(n).apply(lambda y:(y*x).sum() / (x*x).sum(), raw=True)
    a = df.rolling(n).mean()
    y_hat = a + b * x[-1]
    e = df - y_hat
    
    return b, e

def centralize(data):
    return data.subtract(data.mean(1), 0)

def standardize(data):
    if len(data.columns) > 1:
        if (data.std(1) == 0).any():
            return data.subtract(data.mean(1), 0)
        else:
            return data.subtract(data.mean(1), 0).divide(data.std(1), 0)
    else:
        return data.subtract(data.mean(1), 0)

def ma_ratio(data, ma_short, ma_long):
    return data.rolling(ma_short).mean() / data.rolling(ma_long).mean()

def standardize_industry(data, industrys):
    data_dic = {k:standardize(DataFrame(data, columns=industrys[k])) for k in industrys.keys()}
    ret = pd.concat([df for df in data_dic.values()], axis=1)
    
    return ret

def truncate(df, percent=0.05):
    tmp = df.copy()
    q1 = tmp.quantile(percent, 1)
    q2 = tmp.quantile(1-percent, 1)
    tmp[tmp.le(q1, 0)] = np.nan
    tmp[tmp.ge(q2, 0)] = np.nan
    
    return tmp

def winsorize(df, percent=0.05):
    tmp = df.copy()
    def f(s):
        q1 = s.quantile(percent)
        q2 = s.quantile(1-percent)
        s[s<q1] = q1
        s[s>q2] = q2
        return s
    tmp = tmp.apply(func=f, axis=1, result_type='expand')
    
    return tmp