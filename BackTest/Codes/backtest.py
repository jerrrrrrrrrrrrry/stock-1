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
import datetime

import numpy as np
import pandas as pd
from pandas import Series, DataFrame

import matplotlib.pyplot as plt

def main():
    begin_date = '20200401'
    end_date = '20210110'
    factors = ['Amount', 'Beta', 'ChipsCV', 'Close', 'CloseToAverage', 'Value', 'Jump', 'MC', 'MCNL', 'MomentumInd', 'Sigma', 'Skew', 'TurnRate', 'Reversal']

    #获取股票超额收益的预测值
    IC_hat = pd.read_csv('%s/Results/IC_hat.csv'%gc.IC_PATH, index_col=[0], parse_dates=[0])
    IC_hat = IC_hat.loc[IC_hat.index>begin_date, :]
    IC_hat = IC_hat.loc[IC_hat.index<end_date, :]
    
    y = pd.read_csv('%s/Data/y1.csv'%gc.LABELBASE_PATH, index_col=[0], parse_dates=[0])
    y = y.loc[y.index>begin_date, :]
    y = y.loc[y.index<end_date, :]
    
    y_hat = DataFrame(0, index=y.index, columns=y.columns)
    for factor in factors:
        factor_df = pd.read_csv('%s/Data/%s.csv'%(gc.FACTORBASE_PATH, factor), index_col=[0], parse_dates=[0])
        factor_df = factor_df.loc[factor_df.index>begin_date, :]
        factor_df = factor_df.loc[factor_df.index<end_date, :]
        y_hat = y_hat.add(factor_df.mul(IC_hat.loc[:, factor], axis=0), fill_value=0)
    
    stock_num = 20
    turn_rate = 0.2
    trade_num = int(stock_num * turn_rate)
    
    df_position = DataFrame(index=y.index, columns=list(range(stock_num)))
    df_position.iloc[0, :] = list(y_hat.iloc[0, :].sort_values(ascending=False).iloc[:stock_num].index)

    df_pnl = DataFrame(0, index=y.index, columns=list(range(stock_num)))

    pre_date = df_position.index[0]
    for date in df_position.index[1:]:
        pre_position = list(df_position.loc[pre_date, :])
        position = list(y_hat.loc[date, pre_position].sort_values(ascending=False).dropna().iloc[:(stock_num-trade_num)].index)
        
        stocks = y_hat.loc[date, :].sort_values(ascending=False).index
        for stock in stocks:
            if stock not in position:
                if pd.notna(y.loc[date, stock]):
                    position.append(stock)
                    if len(position) >= stock_num:
                        break
        position.sort()
        df_position.loc[date, :] = position
        df_pnl.loc[date, :] = y.loc[date, position].values
        pre_date = date
    pnl = df_pnl.mean(1)
    df_position.to_csv('%s/Results/df_position.csv'%gc.BACKTEST_PATH)
    df_pnl.to_csv('%s/Results/df_pnl.csv'%gc.BACKTEST_PATH)
    pnl.to_csv('%s/Results/pnl.csv'%gc.BACKTEST_PATH)
    
    plt.figure(figsize=(16,12))
    pnl.cumsum().plot()
    y.mean(1).cumsum().plot()
    
    (pnl - y.mean(1)).cumsum().plot()
    plt.legend(['PNL', 'BENCHMARK', 'ALPHA'])
    plt.savefig('%s/Results/backtest.png'%gc.BACKTEST_PATH)
    #begin end
    #股票排序
    #按换手率生成持仓
    #生成日收益率
    #plot和统计分析
if __name__ == '__main__':
    main()