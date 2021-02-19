import os
import sys
import datetime
import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import Config
sys.path.append(Config.GLOBALCONFIG_PATH)
import tools
import Global_Config as gc

def main(start_date, end_date):
    #获取股票
    stocks = tools.get_stocks()
    #获取行业
    industrys = tools.get_industrys(level='L1', stocks=stocks)
    #获取时间
    t = datetime.datetime.today().strftime('%H%M%S')
    if t < '150000':
        time_delta = datetime.timedelta(days=1)
    else:
        time_delta = datetime.timedelta(days=0)
        
    industrys = {k:industrys[k] for k in industrys.keys()}
    stocks = []
    for v in industrys.values():
        stocks.extend(v)
    stocks.sort()
    
    CLOSE = DataFrame({stock:pd.read_csv('%s/StockDailyData/Stock/%s.csv'%(gc.DATABASE_PATH, stock), index_col=[0], parse_dates=[0]).loc[:, 'close'] for stock in stocks})
    dates = CLOSE.index
    for ind in industrys.keys():
        if len(industrys[ind]) > 0:
            df = DataFrame(0, index=dates, columns=stocks)
            df.loc[:, industrys[ind]] = 1
            if os.path.exists('%s/Data/%s.csv'%(gc.FACTORBASE_PATH, ind)):
                df_old = pd.read_csv('%s/Data/%s.csv'%(gc.FACTORBASE_PATH, ind), index_col=[0], parse_dates=[0])
                df = pd.concat([df_old, df.loc[df.index> df_old.index[-1]]], axis=0)
                df.sort_index(0, inplace=True)
            df.sort_index(1, inplace=True)
            df.to_csv('%s/Data/%s.csv'%(gc.FACTORBASE_PATH, ind))
    #遍历取pickle
    files = os.listdir('./')
    files = list(filter(lambda x:len(x)>4, files))
    factors_1 = list(filter(lambda x:x[-5:]=='_1.py', files))
    factors_2 = list(filter(lambda x:x[-5:]=='_2.py', files))
    #生成单因子
    for p in factors_1:
        flag = 0
        if not os.path.exists('%s/Data/%s.csv'%(gc.FACTORBASE_PATH, p.split('.')[0][:-2])):
            start_date_tmp = start_date
            start_date = '20200901'
            flag = 1
        exec('from %s import %s'%(p.split('.')[0], p.split('.')[0][:-2]))
        factor = eval('%s("%s", stocks, start_date, end_date)'%(p.split('.')[0][:-2], p.split('.')[0][:-2]))
        factor.update_factor()
        if flag:
            start_date = start_date_tmp
    #生成合成因子
    for p in factors_2:
        flag = 0
        if not os.path.exists('%s/Data/%s.csv'%(gc.FACTORBASE_PATH, p.split('.')[0][:-2])):
            start_date_tmp = start_date
            start_date = '20200901'
            flag = 1
        exec('from %s import %s'%(p.split('.')[0], p.split('.')[0][:-2]))
        factor = eval('%s("%s", stocks, start_date, end_date)'%(p.split('.')[0][:-2], p.split('.')[0][:-2]))
        factor.update_factor()
        if flag:
            start_date = start_date_tmp
            
            
if __name__ == '__main__':
    if len(sys.argv) == 3:
        start_date = sys.argv[1]
        end_date = sys.argv[2]
    elif len(sys.argv) == 2:
        start_date = sys.argv[1]
        end_date = sys.argv[1]
    elif len(sys.argv) == 1:
        start_date = datetime.datetime.today().strftime('%Y%m%d')
        end_date = datetime.datetime.today().strftime('%Y%m%d')
    else:
        print('date?')
        exit()
    main(start_date, end_date)