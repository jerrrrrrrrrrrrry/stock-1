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



if len(sys.argv) == 3:
    start = sys.argv[1]
    end = sys.argv[2]
elif len(sys.argv) == 2:
    today = sys.argv[1]
    start = today
    end = today
else:
    today = datetime.datetime.today().strftime('%Y%m%d')
    start = today
    end = today

pro = ts.pro_api()

#获取行业分类
stocks = pro.stock_basic(fields='ts_code').ts_code

trade_cal = pd.read_csv('%s/TradeCalData/TradeCal.csv'%gc.DATABASE_PATH)

trade_cal.loc[:, 'cal_date'] = [str(i) for i in trade_cal.loc[:, 'cal_date']]

trade_cal = trade_cal.loc[trade_cal.loc[:, 'is_open']==1, 'cal_date']

trade_cal = trade_cal.loc[trade_cal >= start]
trade_cal = trade_cal.loc[trade_cal <= end]

df_margin_detail = DataFrame()
df_sm_trade = DataFrame()
df_sm_mf = DataFrame()
df_md_trade = DataFrame()
df_md_mf = DataFrame()
df_lg_trade = DataFrame()
df_lg_mf = DataFrame()
df_elg_trade = DataFrame()
df_elg_mf = DataFrame()
df_net_mf = DataFrame()
for trade_date in trade_cal:
    margin_detail = pro.margin_detail(fields='rzye, ts_code', trade_date=trade_date).set_index('ts_code')
    margin_detail.columns = [trade_date]
    df_margin_detail = pd.concat([df_margin_detail, margin_detail.T], axis=0)
    
    moneyflow = pro.moneyflow(trade_date=trade_date).set_index('ts_code')
    
    sm_trade = moneyflow.loc[:, ['buy_sm_amount']].values + moneyflow.loc[:, ['sell_sm_amount']].values
    sm_mf = moneyflow.loc[:, ['buy_sm_amount']].values - moneyflow.loc[:, ['sell_sm_amount']].values
    md_trade = moneyflow.loc[:, ['buy_md_amount']].values + moneyflow.loc[:, ['sell_md_amount']].values
    md_mf = moneyflow.loc[:, ['buy_md_amount']].values + moneyflow.loc[:, ['sell_md_amount']].values
    lg_trade = moneyflow.loc[:, ['buy_lg_amount']].values + moneyflow.loc[:, ['sell_lg_amount']].values
    lg_mf = moneyflow.loc[:, ['buy_lg_amount']].values + moneyflow.loc[:, ['sell_lg_amount']].values
    elg_trade = moneyflow.loc[:, ['buy_elg_amount']].values + moneyflow.loc[:, ['sell_elg_amount']].values
    elg_mf = moneyflow.loc[:, ['buy_elg_amount']].values + moneyflow.loc[:, ['sell_elg_amount']].values
    net_mf = moneyflow.loc[:, ['net_mf_amount']].values
    
    
    sm_trade = DataFrame(sm_trade, index=moneyflow.index, columns = [trade_date])
    sm_mf = DataFrame(sm_mf, index=moneyflow.index, columns = [trade_date])
    md_trade = DataFrame(md_trade, index=moneyflow.index, columns = [trade_date])
    md_mf = DataFrame(md_mf, index=moneyflow.index, columns = [trade_date])
    lg_trade = DataFrame(lg_trade, index=moneyflow.index, columns = [trade_date])
    lg_mf = DataFrame(lg_mf, index=moneyflow.index, columns = [trade_date])
    elg_trade = DataFrame(elg_trade, index=moneyflow.index, columns = [trade_date])
    elg_mf = DataFrame(elg_mf, index=moneyflow.index, columns = [trade_date])
    net_mf = DataFrame(net_mf, index=moneyflow.index, columns = [trade_date])
    
    df_sm_trade = pd.concat([df_sm_trade, sm_trade.T], axis=0)
    df_sm_mf = pd.concat([df_sm_mf, sm_mf.T], axis=0)
    df_md_trade = pd.concat([df_md_trade, md_trade.T], axis=0)
    df_md_mf = pd.concat([df_md_mf, md_mf.T], axis=0)
    df_lg_trade = pd.concat([df_lg_trade, lg_trade.T], axis=0)
    df_lg_mf = pd.concat([df_lg_mf, lg_mf.T], axis=0)
    df_elg_trade = pd.concat([df_elg_trade, elg_trade.T], axis=0)
    df_elg_mf = pd.concat([df_elg_mf, elg_mf.T], axis=0)
    df_net_mf = pd.concat([df_net_mf, net_mf.T], axis=0)

data_list = ['margin_detail',
             'sm_trade', 'sm_mf',
             'md_trade', 'md_mf',
             'lg_trade', 'lg_mf',
             'elg_trade', 'elg_mf',
             'net_mf']

for data in data_list:
    if os.path.exists('%s/StockMoneyData/%s.csv'%(gc.DATABASE_PATH, data)):
        df_old = pd.read_csv('%s/StockMoneyData/%s.csv'%(gc.DATABASE_PATH, data), index_col=[0])
        df = eval('pd.concat([df_old.loc[df_old.index<%s, :], df_%s], axis=0).sort_index(1)'%(start, data))
        df.to_csv('%s/StockMoneyData/%s.csv'%(gc.DATABASE_PATH, data))
    else:
        if eval('len(df_%s)'%data) > 0:
            exec('df_%s.sort_index(1).to_csv("%s/StockMoneyData/%s.csv")'%(data, gc.DATABASE_PATH, data))
