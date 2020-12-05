import os
import sys
import datetime
import tushare as ts
from contextlib import closing
from tqsdk import TqApi, TqAuth, TqSim
from tqsdk.tools import DataDownloader


def main(start_date, end_date):
    pro = ts.pro_api()
    api = TqApi(auth=TqAuth('shengyiqing', 'chenYiYi0517'))
    download_tasks = {}
    
    stocks = pro.stock_basic(fields='symbol, list_date, market')
    stocks = stocks.loc[stocks.market=='创业板', :]
    
    df = pro.trade_cal(exchange='SZSE', start_date=start_date, end_date=end_date)
    dates = df.cal_date[df.is_open==1]
    
    for date in dates:
        if not os.path.exists('../StockHFData/StockSnapshootData/%s'%date):
            os.mkdir('../StockHFData/StockSnapshootData/%s'%date)
        for i in stocks.index:
            if stocks.loc[i, 'list_date'] < date:
                stock = 'SZSE.' + stocks.loc[i, 'symbol']
                download_tasks[date+stock] = DataDownloader(api, symbol_list=[stock], dur_sec=0, start_dt=datetime.datetime.strptime(date, '%Y%m%d'),
                                                          end_dt=(datetime.datetime.strptime(date, '%Y%m%d')+datetime.timedelta(1)), csv_file_name="../StockHFData/StockSnapshootData/%s/%s.csv"%(date, stock))
    with closing(api):
        while not all([v.is_finished() for v in download_tasks.values()]):
            api.wait_update()
            #print("progress: ", { k:("%.2f%%" % v.get_progress()) for k,v in download_tasks.items() })
if __name__ == '__main__':
    #获取交易日
    #获取股票代码
    #遍历交易日，股票代码，下载
    start_date = sys.argv[1]
    end_date = sys.argv[2]
    main(start_date, end_date)