import os
import sys
import datetime
import pickle
import Config
sys.path.append(Config.GLOBALCONFIG_PATH)
import tools
import Global_Config as gc

def main(start_date, end_date):
    industry_list = ['801030.SI', '801080.SI', '801150.SI', '801730.SI', '801750.SI', '801760.SI', '801770.SI', '801890.SI']

    #获取股票
    stocks = tools.get_stocks()
    #获取行业
    industrys = tools.get_industrys(level='L1', stocks=stocks)
    
    industrys = {k:industrys[k] for k in industry_list}
    stocks = []
    for v in industrys.values():
        stocks.extend(v)
    stocks.sort()
    
    #遍历取pickle
    files = os.listdir('./')
    files = list(filter(lambda x:len(x)>4, files))
    factors_1 = list(filter(lambda x:x[-4:]=='1.py', files))
    factors_2 = list(filter(lambda x:x[-4:]=='2.py', files))
    
    #生成单因子
    for p in factors_1:
        if os.path.exists('%s/Base/%s.csv'%(gc.FACTORBASE_PATH, p.split('.')[0][:-2])):
            start_date = datetime.datetime.today().strftime('%Y%m%d')
            end_date = datetime.datetime.today().strftime('%Y%m%d')
        else:
            start_date = '20200101'
            end_date = datetime.datetime.today().strftime('%Y%m%d')
        exec('from %s import %s'%(p.split('.')[0], p.split('.')[0][:-2]))
        factor = eval('%s("%s", stocks, start_date, end_date)'%(p.split('.')[0][:-2], p.split('.')[0][:-2]))
        factor.update_factor()
    #生成合成因子
    for p in factors_2:
        if os.path.exists('%s/Base/%s.csv'%(gc.FACTORBASE_PATH, p.split('.')[0][:-2])):
            start_date = datetime.datetime.today().strftime('%Y%m%d')
            end_date = datetime.datetime.today().strftime('%Y%m%d')
        else:
            start_date = '20200101'
            end_date = datetime.datetime.today().strftime('%Y%m%d')
        exec('from %s import %s'%(p.split('.')[0], p.split('.')[0][:-2]))
        factor = eval('%s("%s", stocks, start_date, end_date)'%(p.split('.')[0][:-2], p.split('.')[0][:-2]))
        factor.update_factor()
            
            
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