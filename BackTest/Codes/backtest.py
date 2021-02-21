# -*- coding: utf-8 -*-
"""
Created on Fri Jan 22 22:19:18 2021

@author: admin
"""

import os
import sys
import Config
sys.path.append(Config.GLOBALCONFIG_PATH)

import Global_Config as gc
import tools
import datetime

import numpy as np
import pandas as pd
from pandas import Series, DataFrame

import matplotlib.pyplot as plt

def main():
    begin_date = '20200209'
    end_date = '20210220'
    
    trade_cal = tools.get_trade_cal(begin_date, end_date)
    trade_cal = [pd.Timestamp(i) for i in trade_cal]
    factors = []
    factors.extend(['ChipsCV', 'CloseToAverage', 'HK', 'MC', 'RQPM', 'Sigma', 'TurnRate', 'EP'])
    factors.extend(['HFPriceVolCorr', 'HFReversalMean', 'HFSkewMean', 'HFVolMean'])

    factors = list(set(factors))
    print(factors)
    #获取股票超额收益的预测值
    IC_hat = pd.read_csv('%s/Results/IC_hat.csv'%gc.IC_PATH, index_col=[0], parse_dates=[0])
    IC_hat = IC_hat.loc[IC_hat.index>begin_date, :]
    IC_hat = IC_hat.loc[IC_hat.index<end_date, :]
    
    r = pd.read_csv('%s/Data/y.csv'%gc.LABELBASE_PATH, index_col=[0], parse_dates=[0])

    r = r.loc[r.index>=begin_date, :]
    r = r.loc[r.index<=end_date, :]
    
    r_hat = DataFrame(0, index=trade_cal, columns=r.columns)
    for factor in factors:
        factor_df = pd.read_csv('%s/Data/%s.csv'%(gc.FACTORBASE_PATH, factor), index_col=[0], parse_dates=[0])
        factor_df = factor_df.loc[factor_df.index>=begin_date, :]
        factor_df = factor_df.loc[factor_df.index<=end_date, :]
        r_hat = r_hat.add(factor_df.mul(IC_hat.loc[:, factor], axis=0), fill_value=0)
    
    stock_num = 30
    turn_rate = 0.1
    trade_num = int(stock_num * turn_rate)
    
    df_position = DataFrame(index=trade_cal, columns=list(range(stock_num)))
    df_position.iloc[0, :] = list(r_hat.iloc[0, :].sort_values(ascending=False).iloc[:stock_num].index)

    df_pnl = DataFrame(0, index=trade_cal, columns=list(range(stock_num)))
    df_stock_sort = DataFrame(index=trade_cal, columns=r_hat.columns)
    
    pre_date = df_position.index[0]
    for date in df_position.index[1:]:
        pre_position = list(df_position.loc[pre_date, :])
        position = list(r_hat.loc[date, pre_position].sort_values(ascending=False).dropna().iloc[:(stock_num-trade_num)].index)
        
        stocks = r_hat.loc[date, :].sort_values(ascending=False).index
        df_stock_sort.loc[date, :] = stocks.values
        for stock in stocks:
            if stock not in position:
                if (date in df_position.index[-2:]) or pd.notnull(r.loc[date, stock]):
                    position.append(stock)
                    if len(position) >= stock_num:
                        break
        position.sort()
        df_position.loc[date, :] = position
        df_pnl.loc[date, :] = r.loc[date, position].values
        pre_date = date
    pnl = df_pnl.mean(1)
    df_stock_sort.to_csv('%s/Results/df_stock_sort.csv'%gc.BACKTEST_PATH)
    df_position.to_csv('%s/Results/df_position.csv'%gc.BACKTEST_PATH)
    df_pnl.to_csv('%s/Results/df_pnl.csv'%gc.BACKTEST_PATH)
    pnl.to_csv('%s/Results/pnl.csv'%gc.BACKTEST_PATH)
    
    plt.figure(figsize=(16,12))
    pnl.cumsum().plot()
    r.mean(1).cumsum().plot()
    
    (pnl - r.mean(1)).cumsum().plot()
    plt.legend(['PNL', 'BENCHMARK', 'ALPHA'])
    plt.savefig('%s/Results/backtest.png'%gc.BACKTEST_PATH)
    #begin end
    #股票排序
    #按换手率生成持仓
    #生成日收益率
    #plot和统计分析
if __name__ == '__main__':
    main()