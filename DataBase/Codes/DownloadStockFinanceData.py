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
    start = sys.argv[1]
else:
    start = '20170101'
end = today

pro = ts.pro_api()

#获取行业分类
stocks = list(pro.stock_basic(fields='ts_code').ts_code)
df_daily = DataFrame()
fields = ', '.join(list(pro.fina_indicator(ts_code=stocks[0]).columns))
fields = fields + ', update_flag'
for stock in stocks:
    time.sleep(1)
    df = pro.fina_indicator(ts_code=stock, fields=fields)
    if len(df) > 0:
        df.to_csv('../StockFinanceData/Stock/%s.csv'%stock)