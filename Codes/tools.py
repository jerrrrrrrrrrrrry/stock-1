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
    return industrys


def get_stocks(cond=None):
    if cond == None:
        def cond(stock):
            return stock[0] == '3'
    pro = ts.pro_api()
    stocks = pro.stock_basic(fields='symbol').iloc[:,0]
    stocks = [stock + '.SZ' if (stock[0]=='0' or stock[0]=='3') else stock + '.SH' for stock in stocks]
    return list(filter(cond, stocks))


def get_stock_daily_data(stocks=None, industrys=None, industry=None, fields=['open',
                                 'high',
                                 'low',
                                 'close',
                                 'vol',
                                 'amount',
                                 'adj_factor']):
    data = {}
        
    if not stocks:
        if industry == 'all':
            stocks = [j for i in industrys.values() for j in i]
        else:
            stocks = [j for i in industry for j in industrys[i]]
    
    for field in fields:
        data[field] = DataFrame({stock: pd.read_csv('../DataBase/StockDailyData/Stock/%s.csv'%stock, index_col=[0], parse_dates=[0]).loc[:, field] for stock in stocks})
        
    return data


def group_backtest(factor, r, n):
    l = [(((factor.ge(factor.quantile(i/n, 1), 0)) & (factor.le(factor.quantile(i/n+1/n, 1), 0))) * n * r).mean(1).cumsum().rename('%s'%(i/n)) for i in range(n)]
    for i in l:
        (i - r.mean(1).cumsum()).plot()
    plt.legend(['alpha %s'%i.name for i in l])
    '''for i in l:
        i.plot()
    for i in l:
        (i - r.mean(1).cumsum()).plot()
    r.mean(1).cumsum().plot()
    plt.legend([i.name for i in l]+['alpha %s'%i.name for i in l]+['benchmark'])'''
    '''
    for i in range(n):
        q = i / n
        position = (factor.gt(factor.quantile(q, 1), 0)) & (factor.lt(factor.quantile(q+1/n, 1), 0))
        r_backtest = position * r
        daily_r_backtest = r_backtest.mean(1)
        daily_cumsum_r_backtest = daily_r_backtest.cumsum()
    '''
    
    return


def icir(factor, r, n=20, rank=False):
    if rank:
        x1 = DP.standardize(rankdata(factor))
    else:
        x1 = DP.standardize(factor)
    x2 = DP.standardize(r)
    ic = (x1 * x2).mean(1).fillna(0)
    ir = ic.rolling(20).mean() / ic.rolling(20).std()
    
    return ic, ir


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


def normalize(df):
    return df.subtract(df.min(1), 0).divide(df.max(1) - df.min(1), 0)

def centralize(data):
    return data.subtract(data.mean(1), 0)

def standardize(data):
    return data.subtract(data.mean(1), 0).divide(data.std(1), 0)

def ma_ratio(data, ma_short, ma_long):
    return data.rolling(ma_short).mean() / data.rolling(ma_long).mean()

def normalize_industry(data, industrys, industry):
    data_dic = {i:normalize(data.loc[:, industrys[i]]) for i in industry}
    ret = pd.concat([df for df in data_dic.values()], axis=1)
    
    return ret

def standardize_industry(data, industrys):
    data_dic = {k:standardize(data.loc[:, industrys[k]]) for k in industrys.keys()}
    ret = pd.concat([df for df in data_dic.values()], axis=1)
    
    return ret

def truncate_outliers(df, percent=0.05):
    tmp = df.copy()
    tmp[tmp.le(tmp.quantile(percent, 1), 0) | tmp.ge(tmp.quantile(1-percent, 1), 0)] = 0
    
    return tmp