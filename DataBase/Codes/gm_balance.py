﻿# coding=utf-8
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
    fields_balance = 'ACCHELDFORS, ACCOPAYA, ACCORECE, ACCREXPE, ACCUDEPR, ACTITRADSECU, ACTIUNDESECU, ADVAPAYM, AVAISELLASSE, BDSPAYA, BDSPAYAPERBOND, BDSPAYAPREST, CAPISURP, CENBANKBORR, COMASSE, CONSPROG, COPEPOUN, COPEWITHREINRECE, COPEWORKERSAL, CURFDS, CURTRANDIFF, DEFEINCOTAXLIAB, DEFEREVE, DEFETAXASSET, DEPOSIT, DERIFINAASSET, DERILIAB, DEVEEXPE, DIVIDRECE, DIVIPAYA, DOMETICKSETT, DUENONCLIAB, ENGIMATE, EQUIINVE, EXPECURRLIAB, EXPENONCLIAB, EXPINONCURRASSET, EXPOTAXREBARECE, FDSBORR, FIXEDASSECLEA, FIXEDASSEIMMO, FIXEDASSEIMPA, FIXEDASSENET, FIXEDASSENETW, GENERISKRESE, GOODWILL, HOLDINVEDUE, HYDRASSET, INSUCONTRESE, INTAASSET, INTELPAY, INTELRECE, INTEPAYA, INTERECE, INTETICKSETT, INVE, INVEPROP, LCOPEWORKERSAL, LENDANDLOAN, LIABHELDFORS, LOGPREPEXPE, LONGBORR, LONGDEFEINCO, LONGPAYA, LONGRECE, MARGRECE, MARGREQU, MINYSHARRIGH, NOTESPAYA, NOTESRECE, OCL, OTHEQUIN, OTHERCURRASSE, OTHERCURRELIABI, OTHERFEEPAYA, OTHERLONGINVE, OTHERNONCASSE, OTHERNONCLIABI, OTHERPAY, OTHERRECE, PAIDINCAPI, PARESHARRIGH, PERBOND, PLAC, PREMRECE, PREP, PREPEXPE, PREST, PRODASSE, PURCRESAASSET, REINCONTRESE, REINRECE, RESE, RIGHAGGR, SELLREPASSE, SETTRESEDEPO, SFORMATCURRASSE, SFORMATCURRELIABI, SFORMATNONCASSE, SFORMATNONCLIAB, SFORMATPARESHARRIGH, SFORMATRIGHAGGR, SFORMATTOTASSET, SFORMATTOTLIAB, SFORMATTOTLIABSHAREQUI, SHORTTERMBDSPAYA, SHORTTERMBORR, SMERGERCURRASSE, SMERGERCURRELIABI, SMERGERNONCASSE, SMERGERNONCLIAB, SMERGERPARESHARRIGH, SMERGERRIGHAGGR, SMERGERTOTASSET, SMERGERTOTLIAB, SMERGERTOTLIABSHAREQUI, SPECPAYA, SPECRESE, SUBSRECE, SUNEVENASSETLIABEUQI, SUNEVENCURRASSE, SUNEVENCURRELIABI, SUNEVENNONCASSE, SUNEVENNONCLIAB, SUNEVENPARESHARRIGH, SUNEVENRIGHAGGR, SUNEVENTOTASSET, SUNEVENTOTLIAB, SUNEVENTOTLIABSHAREQUI, TAXESPAYA, TOPAYCASHDIVI, TOTALCURRLIAB, TOTALNONCASSETS, TOTALNONCLIAB, TOTASSET, TOTCURRASSET, TOTLIAB, TOTLIABSHAREQUI, TRADFINASSET, TRADFINLIAB, TRADSHARTRAD, TREASTK, UNDIPROF, UNREINVELOSS, UNSEG, WARLIABRESE'
    
    
    stocks = get_instruments(sec_types=1, fields='symbol', df=True)
    stocks = list(stocks.iloc[:, 0])
    stocks = filter(lambda x:x[6] == '0' or x[6] == '3' or x[6] == '6', stocks)
    for stock in stocks:
        balance = get_fundamentals(table='balance_sheet', symbols=stock, start_date='2010-01-01', end_date=today, fields=fields_balance, filter=None, order_by=None, limit=1000, df=True)
        balance.to_csv('%s/StockFinanceData/Balance/%s.csv'%(gc.DATABASE_PATH, stock))
        