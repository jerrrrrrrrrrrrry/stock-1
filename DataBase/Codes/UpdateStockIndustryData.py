# -*- coding: utf-8 -*-

import Config
import sys
sys.path.append(Config.GLOBALCONFIG_PATH)

import Global_Config as gc
import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import datetime
import os
import tushare as ts

def main(start_date, end_date):
    pro = ts.pro_api()
    
    dates = pro.trade_cal(exchange='SZSE', start_date=start_date, end_date=end_date)
    dates = list(dates.loc[dates.is_open==1, :].cal_date)
    
    stocks_list = pro.stock_basic(fields='symbol, list_date, market')
    stocks_list = list(stocks_list.loc[stocks_list.market=='创业板', :].symbol)
    stocks_list = [stock+'.SZ' for stock in stocks_list]
    df = DataFrame(columns=stocks_list, index=dates)
    
    index_list = list(pro.index_classify(level='L1', src='SW').sort_values('index_code').index_code)
    
    for index in index_list:
        ind_stock = list(pro.index_member(index_code=index).con_code.sort_values())
        ind_stock = list(filter(lambda x:x[0]=='3', ind_stock))
        ind_stock = list(filter(lambda x:x in df.columns, ind_stock))
        df.loc[:,ind_stock] = index
    
    if os.path.exists(gc.DATABASE_PATH+'/StockIndustryData/StockIndustry.csv'):
        df.to_csv(gc.DATABASE_PATH+'/StockIndustryData/StockIndustry.csv', mode='a', header=False)
    else:
        df.to_csv(gc.DATABASE_PATH+'/StockIndustryData/StockIndustry.csv')
if __name__ == '__main__':
    if len(sys.argv) == 3:
        start_date = sys.argv[1]
        end_date = sys.argv[2]
    elif len(sys.argv) == 2:
        start_date = sys.argv[1]
        end_date = sys.argv[1]
    else:
        start_date = datetime.datetime.today().strftime('%Y%m%d')
        end_date = start_date
    main(start_date, end_date)