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
    end_date = datetime.datetime.today().strftime('%Y%m%d')
    end_date = '20210226'
    trade_cal = tools.get_trade_cal(begin_date, end_date)
    trade_cal = [pd.Timestamp(i) for i in trade_cal]
    factors = []
    factors.extend(['Beta', 'CORRMarket', 'MC', 'DEP', 'CloseToAverage', 'Sigma', 'EP'])
    factors.extend(['HFPriceVolCorrMean', 'HFReversalMean', 'HFSkewMean', 'HFVolMean', 'HFVolPowerMean'])

    r = pd.read_csv('%s/Data/y.csv'%gc.LABELBASE_PATH, index_col=[0], parse_dates=[0])

    r = r.loc[r.index>=begin_date, :]
    r = r.loc[r.index<=end_date, :]
    
    factors = list(set(factors))
    print(factors)
    
    halflife = 20
    lag = 1
    turn_rate = 0.2
    n = int(1 / turn_rate)
    ic_list = []
    for i in range(n):
        ic_list.append(pd.read_csv('%s/Results/IC_%s.csv'%(gc.IC_PATH, i), index_col=[0], parse_dates=[0]).loc[:, factors].fillna(0))
    
    ic_mean_hat_list = [ic_list[n].ewm(halflife=halflife).mean().shift(n+lag) for n in range(len(ic_list))]
    #ic_std_hat_list = [ic_list[n].ewm(halflife=halflife).std().shift(n+lag) for n in range(len(ic_list))]
    ic_cov_hat_list = [ic_list[n].ewm(halflife=halflife).cov().shift(len(ic_list[0].columns)*(n+lag)) for n in range(len(ic_list))]
    
    weight_list = [DataFrame(index=ic_mean_hat_list[n].index, columns=ic_mean_hat_list[n].columns) for n in range(len(ic_mean_hat_list))]
    for date in r.index:
        for n in range(len(weight_list)):
            weight_list[n].loc[date, :] = np.linalg.inv(0.001*np.eye(len(ic_cov_hat_list[n].loc[date, :, :])) + ic_cov_hat_list[n].loc[date, :, :].values).dot(ic_mean_hat_list[n].loc[date, :].values)
    ic_cov_hat_list[0].to_csv('../Results/ic_cov.csv')
            # print(ic_cov_hat_list[n].loc[date,:,:])
            # print(date, n)
            # print(np.linalg.inv(ic_cov_hat_list[n].loc[date, :, :]))
            # print(ic_mean_hat_list[n].loc[date, :])
            # print(weight_list[n].loc[date, :])
            # print('---------------------')
    
    def f(df_list, turn_rate=0.2):
        s = 1 / turn_rate * (1 + turn_rate) / 2
        # s = 1 - (1 - turn_rate) ** 10
        mean = DataFrame(0, index=df_list[0].index, columns=df_list[0].columns)
        
        for i in range(len(df_list)):
            mean = mean + df_list[i] * (1 - i * turn_rate)
            # mean = mean + df_list[i] * (1 - turn_rate)**i
            
        mean = mean / s
        
        ret = mean
        return ret
    
    weight = f(weight_list, turn_rate)
    weight = weight.loc[weight.index>=begin_date, :]
    weight = weight.loc[weight.index<=end_date, :]
    weight.to_csv('../Results/weight.csv')
    
    r_hat = DataFrame(0, index=trade_cal, columns=r.columns)
    for factor in factors:
        factor_df = pd.read_csv('%s/Data/%s.csv'%(gc.FACTORBASE_PATH, factor), index_col=[0], parse_dates=[0])
        factor_df = factor_df.loc[factor_df.index>=begin_date, :]
        factor_df = factor_df.loc[factor_df.index<=end_date, :]
        r_hat = r_hat.add(factor_df.mul(weight.loc[:, factor], axis=0), fill_value=0)
    
    stock_num = 30
    trade_num = int(stock_num * turn_rate)
    
    df_position = DataFrame(index=trade_cal, columns=list(range(stock_num)))
    df_position.iloc[0, :] = list(r_hat.iloc[0, :].sort_values(ascending=False).iloc[:stock_num].index)

    df_pnl = DataFrame(index=trade_cal, columns=list(range(stock_num)))
    df_stock_sort = DataFrame(index=trade_cal, columns=list(range(len(r_hat.columns))))
    
    df_rank_stock = r_hat.rank(axis=1)
    
    df_rank_pre_position = DataFrame(index=trade_cal, columns=list(range(stock_num)))
    df_rank_position = DataFrame(index=trade_cal, columns=list(range(stock_num)))
    
    df_sell = DataFrame(index=trade_cal, columns=list(range(trade_num)))
    
    pre_date = df_position.index[0]
    for date in df_position.index[1:]:
        pre_position = list(df_position.loc[pre_date, :])
        position = list(r_hat.loc[date, pre_position].sort_values(ascending=False).iloc[:(stock_num-trade_num)].index)
        df_sell.loc[date, :] = list(r_hat.loc[date, pre_position].sort_values(ascending=True).iloc[:trade_num].index)
        stocks = r_hat.loc[date, :].sort_values(ascending=False).index
        df_stock_sort.loc[date, :] = stocks.values
        for stock in stocks:
            if stock not in position:
                if (date in df_position.index[-2:]) or pd.notnull(r.loc[date, stock]):
                    position.append(stock)
                    if len(position) >= stock_num:
                        break
        pre_rank = r_hat.loc[date, :].rank().loc[pre_position].sort_values(ascending=False)
        rank = r_hat.loc[date, :].rank().loc[position].sort_values(ascending=False)
        
        df_rank_pre_position.loc[date, :] = [{stock:pre_rank.loc[stock]} for stock in pre_rank.index]
        df_rank_position.loc[date, :] = [{stock:rank.loc[stock]} for stock in rank.index]

        position.sort()
        df_position.loc[date, :] = position
        df_pnl.loc[date, :] = r.loc[date, position].values
        pre_date = date
    
    pnl = df_pnl.mean(1)
    
    pnl.fillna(r.mean(1), inplace=True)
    r_hat.to_csv('%s/Results/r_hat.csv'%gc.BACKTEST_PATH)
    
    df_rank_stock.to_csv('%s/Results/df_rank_stock.csv'%gc.BACKTEST_PATH)
    df_rank_pre_position.to_csv('%s/Results/df_rank_pre_position.csv'%gc.BACKTEST_PATH)
    df_rank_position.to_csv('%s/Results/df_rank_position.csv'%gc.BACKTEST_PATH)
    
    df_stock_sort.to_csv('%s/Results/df_stock_sort.csv'%gc.BACKTEST_PATH)
    df_sell.to_csv('%s/Results/df_sell.csv'%gc.BACKTEST_PATH)
    df_position.to_csv('%s/Results/df_position.csv'%gc.BACKTEST_PATH)
    df_pnl.to_csv('%s/Results/df_pnl.csv'%gc.BACKTEST_PATH)
    pnl.to_csv('%s/Results/pnl.csv'%gc.BACKTEST_PATH)
    
    r_hat = r_hat.loc[r.index, r.columns]
    
    plt.figure(figsize=(16,12))
    IC = r_hat.corrwith(r, method='pearson', axis=1)
    IC.cumsum().plot()
    plt.savefig('../Results/IC.png')
    
    plt.figure(figsize=(16, 12))
    num_group = 50
    factor_quantile = DataFrame(r_hat.rank(axis=1), index=r.index, columns=r.columns).div(r_hat.notna().sum(1), axis=0)# / len(factor.columns)
    #factor_quantile[r.isna()] = np.nan
    group_backtest = {}
    group_pos = {}
    for n in range(num_group):
        group_pos[n] = DataFrame((n/num_group <= factor_quantile) & (factor_quantile <= (n+1)/num_group))
        group_pos[n][~group_pos[n]] = np.nan
        group_pos[n] = 1 * group_pos[n]
        group_backtest[n] = ((group_pos[n] * r).mean(1) - r.mean(1)).cumsum().rename('%s'%(n/num_group))
        group_backtest[n].plot()
    plt.legend(['%s'%i for i in range(num_group)])
    plt.savefig('../Results/groupbacktest.png')
    
    plt.figure(figsize=(16, 12))
    group_hist = [group_backtest[i].iloc[np.where(group_backtest[i].notna())[0][-1]] for i in range(num_group)]
    plt.bar(range(num_group), group_hist)
    plt.savefig('../Results/grouphist.png')
    
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