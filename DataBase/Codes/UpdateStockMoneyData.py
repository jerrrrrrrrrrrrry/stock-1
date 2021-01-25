'''import tushare as ts
import os
import sys
import time
import datetime
import numpy as np
import pandas as pd
from pandas import Series, DataFrame

today = datetime.datetime.today().strftime('%Y%m%d')

start = today
end = today

pro = ts.pro_api()

#获取行业分类
stocks = pro.stock_basic(fields='ts_code').ts_code
df_daily = DataFrame()
for stock in stocks:
    df = pd.concat([
        pro.hk_hold(ts_code=stock, start_date=start, end_date=end).set_index('trade_date').sort_index().vol.rename('gt_vol'),
        pro.margin_detail(ts_code=stock, start_date=start, end_date=end).set_index('trade_date').loc[:, ['rzye', 'rqye']],
        pro.moneyflow(ts_code=stock, start_date=start, end_date=end, fields='trade_date, ts_code, buy_sm_amount, sell_sm_amount, buy_md_amount, sell_md_amount, buy_lg_amount, sell_lg_amount, buy_elg_amount, sell_elg_amount, net_mf_amount').set_index('trade_date'),
    ], axis=1, sort=False)
    df = df.sort_index()
    df.to_csv('../StockMoneyData/Stock/%s.csv'%stock, mode='a', header=False)
    if len(df) > 0:
        if df.notna().iloc[-1, :].any():
            df_daily = pd.concat([df_daily, df.iloc[-1:, :]], axis=0, sort=False)
df_daily.set_index('ts_code').to_csv('../StockMoneyData/Daily/%s.csv'%df.index[-1])'''

import tushare as ts
import os
import sys
import time
import datetime
import numpy as np
import pandas as pd
from pandas import Series, DataFrame

if len(sys.argv) == 2:
    today = sys.argv[1]
else:
    today = datetime.datetime.today().strftime('%Y%m%d')

start = today
end = today

pro = ts.pro_api()

#获取行业分类
stocks = pro.stock_basic(fields='ts_code').ts_code
hk_hold = pro.hk_hold(fields='ts_code', start_date=start, end_date=end, stocks).set_index('ts_code')
margin_detail = pro.margin_detail(fields='name, ts_code').set_index('ts_code')
moneyflow = pro.moneyflow(start_date=start, end_date=end, fields='ts_code, open, high, low, close, vol, amount').set_index('ts_code')

df_daily = DataFrame()

for stock in stocks:
    if (stock in list(hk_hold.index)) and (stock in list(margin_detail.index)) and (stock in list(moneyflow.index)):
        df = pd.concat([hk_hold.loc[[stock], :], margin_detail.loc[[stock], :], moneyflow.loc[[stock], :], ], axis=1, sort=False)
        
        df.index=[today]
        df = pd.concat([DataFrame(stock, index=df.index, columns=['ts_code']), df], axis=1, sort=False)
        if os.path.exists('../StockMoneyData/Stock/%s.csv'%stock):
            df.to_csv('../StockMoneyData/Stock/%s.csv'%stock, mode='a', header=False)
            df_daily = pd.concat([df_daily, df.iloc[-1:, :]], axis=0, sort=False)
        else:
            if len(df) > 0:
                df.to_csv('../StockMoneyData/Stock/%s.csv'%stock)
                df_daily = pd.concat([df_daily, df.iloc[-1:, :]], axis=0, sort=False)
    else:
        if os.path.exists('../StockMoneyData/Stock/%s.csv'%stock):
            DataFrame(index=[today]).to_csv('../StockMoneyData/Stock/%s.csv'%stock, mode='a', header=False)
df_daily.set_index('ts_code').to_csv('../StockDailyData/Daily/%s.csv'%df.index[-1])