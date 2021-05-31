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
import tools

today = datetime.datetime.today().strftime('%Y%m%d')

if len(sys.argv) > 1:
    start_date = sys.argv[1]
else:
    start_date = '20100101'
end = today
pro = ts.pro_api()

#获取行业分类
stocks = list(pro.stock_basic(fields='ts_code').ts_code)

fields_balance = ', '.join(list(pro.balancesheet(ts_code=stocks[0]).columns))
fields_balance = fields_balance + ', update_flag'

fields_income = ', '.join(list(pro.income(ts_code=stocks[0]).columns))
fields_income = fields_income + ', update_flag'

fields_cashflow = ', '.join(list(pro.cashflow(ts_code=stocks[0]).columns))
fields_cashflow = fields_cashflow + ', update_flag'

fields_indicator = ', '.join(list(pro.fina_indicator(ts_code=stocks[0]).columns))
fields_indicator = fields_indicator + ', update_flag'

fields_date = ', '.join(list(pro.disclosure_date(ts_code=stocks[0]).columns))
fields_date = fields_date + ', modify_date'


for stock in stocks:
    time.sleep(0.3)
    df_balance = pro.balancesheet(ts_code=stock, fields=fields_balance, start_date=start_date)
    df_income = pro.income(ts_code=stock, fields=fields_income, start_date=start_date)
    df_cashflow = pro.cashflow(ts_code=stock, fields=fields_cashflow, start_date=start_date)
    
    
    df_indicator = pro.fina_indicator(ts_code=stock, fields=fields_indicator, start_date=start_date)
    df_audit = pro.fina_audit(ts_code=stock, start_date=start_date)
    df_date = pro.disclosure_date(ts_code=stock, fields=fields_date, start_date=start_date)
    if len(df_balance) > 0:
        df_balance.to_csv('../StockFinanceData/Balance/%s.csv'%stock)
    if len(df_income) > 0:
        df_income.to_csv('../StockFinanceData/Income/%s.csv'%stock)
    if len(df_cashflow) > 0:
        df_cashflow.to_csv('../StockFinanceData/Cashflow/%s.csv'%stock)
    if len(df_indicator) > 0:
        df_indicator.to_csv('../StockFinanceData/Indicator/%s.csv'%stock)
    if len(df_audit) > 0:
        df_audit.to_csv('../StockFinanceData/Audit/%s.csv'%stock)
    if len(df_date) > 0:
        df_date.to_csv('../StockFinanceData/Date/%s.csv'%stock)