# coding=utf-8
from __future__ import print_function, absolute_import
from gm.api import *
import Config
import os
import sys
import pandas as pd
sys.path.append(Config.GLOBALCONFIG_PATH)
import Global_Config as gc
import datetime


if __name__ == '__main__':
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    # 可以直接提取数据，掘金终端需要打开，接口取数是通过网络请求的方式，效率一般，行情数据可通过subscribe订阅方式
    # 设置token， 查看已有token ID,在用户-密钥管理里获取
    set_token('005bc7161f87579bc050fb3b0e74f9c94e136974')
    # 查询历史行情, 采用定点复权的方式， adjust指定前复权，adjust_end_time指定复权时间点
    fields_cashflow = 'ACCREXPEINCR, ACQUASSETCASH, ASSEDEPR, ASSEIMPA, BANKLOANNETINCR, BIZCASHINFL, BIZCASHOUTF, BIZNETCFLOW, CASHFINALBALA, CASHNETI, CASHNETR, CASHOPENBALA, CHARINTECASH, CHGEXCHGCHGS, DEBTINTOCAPI, DEBTPAYCASH, DEFEINCOINCR, DEFETAXASSETDECR, DEFETAXLIABINCR, DEPONETR, DISPFIXEDASSETLOSS, DISPTRADNETINCR, DIVIPROFPAYCASH, EQUFINALBALA, EQUOPENBALA, ESTIDEBTS, EXPICONVBD, FDSBORRNETR, FINALCASHBALA, FINCASHINFL, FINCASHOUTF, FINEXPE, FINFIXEDASSET, FININSTNETR, FINNETCFLOW, FINRELACASH, FIXEDASSESCRALOSS, FIXEDASSETNETC, INCRCASHPLED, INICASHBALA, INSNETC, INSPREMCASH, INTAASSEAMOR, INVCASHINFL, INVCASHOUTF, INVELOSS, INVEREDU, INVERETUGETCASH, INVNETCASHFLOW, INVPAYC, INVRECECASH, ISSBDRECECASH, LABOPAYC, LABORGETCASH, LOANNETR, LOANSNETR, LONGDEFEEXPENAMOR, MANANETR, MINYSHARRIGH, NETPROFIT, OTHER, PAYACTICASH, PAYAINCR, PAYCOMPGOLD, PAYDIVICASH, PAYINTECASH, PAYINVECASH, PAYTAX, PAYWORKCASH, PREPEXPEDECR, REALESTADEP, RECEFINCASH, RECEFROMLOAN, RECEINVCASH, RECEOTHERBIZCASH, RECEREDU, REDUCASHPLED, REPNETINCR, SAVINETR, SFORMATBIZCASHINFL, SFORMATBIZCASHOUTF, SFORMATBIZNETCFLOW, SFORMATCASHNETI, SFORMATCASHNETR, SFORMATFINALCASHBALA, SFORMATFINCASHINFL, SFORMATFINCASHOUTF, SFORMATINVCASHINFL, SFORMATINVCASHOUTF, SFORMATMANANETR, SMERGERBIZCASHINFL, SMERGERBIZCASHOUTF, SMERGERBIZNETCFLOW, SMERGERCASHNETI, SMERGERCASHNETR, SMERGERFINALCASHBALA, SMERGERFINCASHINFL, SMERGERFINCASHOUTF, SMERGERFINNETCFLOW, SMERGERINVCASHINFL, SMERGERINVCASHOUTF, SMERGERINVNETCASHFLOW, SMERGERMANANETR, SUBSNETC, SUBSPAYDIVID, SUBSPAYNETCASH, SUBSRECECASH, SUNEVENBIZCASHINFL, SUNEVENBIZCASHOUTF, SUNEVENBIZNETCFLOW, SUNEVENCASHNETI, SUNEVENCASHNETIMS, SUNEVENCASHNETR, SUNEVENFINALCASHBALA, SUNEVENFINCASHINFL, SUNEVENFINCASHOUTF, SUNEVENFINNETCFLOW, SUNEVENINVCASHINFL, SUNEVENINVCASHOUTF, SUNEVENINVNETCASHFLOW, SUNEVENMANANETR, SUNEVENMANANETRMS, TAXREFD, TRADEPAYMNETR, UNFIPARACHG, UNREINVELOSS, UNSEPARACHG, VALUECHGLOSS, WITHINVGETCASH'
    
    
    stocks = get_instruments(sec_types=1, fields='symbol', df=True)
    stocks = list(stocks.iloc[:, 0])
    stocks = filter(lambda x:x[6] == '0' or x[6] == '3' or x[6] == '6', stocks)
    for stock in stocks:
        cashflow = get_fundamentals(table='cashflow_statement', symbols=stock, start_date='2010-01-01', end_date=today, fields=fields_cashflow, filter=None, order_by=None, limit=1000, df=True)
        cashflow.to_csv('%s/StockFinanceData/Cashflow/%s.csv'%(gc.DATABASE_PATH, stock))
        