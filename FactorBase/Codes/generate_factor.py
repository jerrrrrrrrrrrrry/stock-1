import os
import sys
import time
import datetime
import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import Config
sys.path.append(Config.GLOBALCONFIG_PATH)
import tools
import Global_Config as gc
import multiprocessing as mp

def f(p, stocks, start_date, end_date):
    exec('from %s import %s'%(p.split('.')[0], p.split('.')[0][:-2]))
    factor = eval('%s("%s", stocks, start_date, end_date)'%(p.split('.')[0][:-2], p.split('.')[0][:-2]))
    factor.update_factor()
        
if __name__ == '__main__':
    #获取时间
    t = datetime.datetime.today().strftime('%H%M%S')
    start_date = datetime.datetime.today().strftime('%Y%m%d')
    end_date = datetime.datetime.today().strftime('%Y%m%d')
    # start_date = '20210423'
    # end_date = '20210423'
    # t = '20210423'
    if t < '200000':
        time_delta = datetime.timedelta(days=1)
    else:
        time_delta = datetime.timedelta(days=0)
    start_date = datetime.datetime.strptime(start_date, '%Y%m%d') - time_delta
    end_date = datetime.datetime.strptime(end_date, '%Y%m%d') - time_delta
    start_date = start_date.strftime('%Y%m%d')
    end_date = end_date.strftime('%Y%m%d')
    trade_cal = tools.get_trade_cal(start_date=start_date, end_date=end_date)
    if len(trade_cal) == 0:
        sys.exit()
    #获取股票
    stocks = tools.get_stocks()
    #获取行业
    industrys = tools.get_industrys(level='L1', stocks=stocks)
    
    print(start_date, end_date)
    
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
            
    files = os.listdir('./')
    files = list(filter(lambda x:len(x)>4, files))
    factors_1 = list(filter(lambda x:x[-5:]=='_1.py', files))
    factors_2 = list(filter(lambda x:x[-5:]=='_2.py', files))
    # factors_1 = ['STR_1.py']
    # factors_2 = []
    #生成单因子
    pool = mp.Pool(4)
    for p in factors_1:
        flag = 0
        if not os.path.exists('%s/Data/%s.csv'%(gc.FACTORBASE_PATH, p.split('.')[0][:-2])):
            start_date_tmp = start_date
            if p[:2] == 'HF':
                # continue
                start_date = '20201214'
            else:
                start_date = '20170101'
            flag = 1
        pool.apply_async(func=f, args=(p, stocks, start_date, end_date))
        if flag == 1:
            start_date = start_date_tmp
    pool.close()
    pool.join()
    #生成合成因子
    for p in factors_2:
        flag = 0
        if not os.path.exists('%s/Data/%s.csv'%(gc.FACTORBASE_PATH, p.split('.')[0][:-2])):
            start_date_tmp = start_date
            if p[:2] == 'HF':
                # continue
                start_date = '20201214'
            else:
                start_date = '20170101'
            flag = 1
        exec('from %s import %s'%(p.split('.')[0], p.split('.')[0][:-2]))
        factor = eval('%s("%s", stocks, start_date, end_date)'%(p.split('.')[0][:-2], p.split('.')[0][:-2]))
        factor.update_factor()
        if flag == 1:
            start_date = start_date_tmp
    
    os.system('python ./preprocess_factor.py')