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
import statsmodels.tsa.api as tsa

if __name__ == '__main__':
    begin_date = '20180101'
    end_date = '20210402'
    # end_date = datetime.datetime.today().strftime('%Y%m%d')
    
    trade_cal = tools.get_trade_cal(begin_date, end_date)
    trade_cal = [pd.Timestamp(i) for i in trade_cal]
    
    r = pd.read_csv('%s/Data/r_jiaoyi.csv'%gc.LABELBASE_PATH, index_col=[0], parse_dates=[0])
    y = pd.read_csv('%s/Data/y.csv'%gc.LABELBASE_PATH, index_col=[0], parse_dates=[0])
    
    r = r.loc[r.index>=begin_date, :]
    r = r.loc[r.index<=end_date, :]
    
    # r_hat_name_list = ['r_hat_betacov_0',]
    r_hat_name_list = ['r_hat_betacov_1',
                       'r_hat_beta_2', 'r_hat_beta_3']
    # r_hat_name_list = ['r_hat_beta_0']
    r_hat_dic = {r_hat_name : pd.read_csv('%s/Results/%s.csv'%(gc.PREDICT_PATH, r_hat_name), index_col=[0], parse_dates=[0]) for r_hat_name in r_hat_name_list}
    
    for r_hat_name in r_hat_name_list:
        r_hat_dic[r_hat_name] = tools.standardize(r_hat_dic[r_hat_name])
    
    ic = DataFrame(index=r_hat_dic[r_hat_name_list[0]].index, columns=r_hat_name_list)
    y = y.loc[r_hat_dic[r_hat_name_list[0]].index, r_hat_dic[r_hat_name_list[0]].columns]
    
    halflife_mean = 250
    halflife_cov = 250
    lamb = 1e-2
    n = 5
    lag = n + 1
    
    for r_hat_name in r_hat_name_list:
        ic.loc[:, r_hat_name] = y.corrwith(r_hat_dic[r_hat_name], 1)
    ic.to_csv('../Results/ic.csv')
    
    ic_mean_hat = ic.ewm(halflife=halflife_mean).mean().shift(lag)
    ic_cov_hat = ic.ewm(halflife=halflife_cov).cov().shift(lag*len(r_hat_name_list))
    weight = DataFrame(index=ic.index, columns=ic.columns)
    for date in weight.index:
        weight.loc[date, :] = np.linalg.inv(ic_cov_hat.loc[date, :, :].values + lamb*np.eye(len(r_hat_name_list))).dot(ic_mean_hat.loc[date, :].values)
    
    ic_mean_hat.to_csv('../Results/ic_mean_hat.csv')
    ic_cov_hat.to_csv('../Results/ic_cov_hat.csv')
    weight.to_csv('../Results/weight.csv')
    
    r_hat = DataFrame(0, index=r_hat_dic[r_hat_name_list[0]].index, columns=r_hat_dic[r_hat_name_list[0]].columns)
    for r_hat_name in r_hat_name_list:
        r_hat = r_hat.add(r_hat_dic[r_hat_name].mul(weight.loc[:, r_hat_name], 0), fill_value=0)
    # r_hat = DataFrame(0, index=r_hat_dic[r_hat_name_list[0]].index, columns=r_hat_dic[r_hat_name_list[0]].columns)
    # for r_hat_name in r_hat_name_list:
    #     r_hat = r_hat.add(r_hat_dic[r_hat_name], fill_value=0)
        
    print('回测')
    turn_rate = 0.2
    stock_num = 100
    trade_num = int(stock_num * turn_rate)
    
    num_group = 40
    
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
        
        #buy = list(set(position) - set(pre_position))
        #sell = list(set(pre_position) - set(position))
        #zuocang = list(set(position) - set(buy))
        
        df_position.loc[date, :] = position
        #df_pnl.loc[date, :] = r.loc[date, position].values
        #df_pnl.loc[date, buy] = r_rinei.loc[date, buy].values
        #df_pnl.loc[date, zuocang] = r.loc[date, zuocang].values
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
    IC = r_hat.corrwith(y, axis=1)
    IC.cumsum().plot()
    plt.savefig('../Results/IC.png')
    
    plt.figure(figsize=(16, 12))
    factor_quantile = DataFrame(r_hat.rank(axis=1), index=r.index, columns=r.columns).div(r_hat.notna().sum(1), axis=0)# / len(factor.columns)
    #factor_quantile[r.isna()] = np.nan
    group_backtest = {}
    group_pos = {}
    for n in range(num_group):
        group_pos[n] = DataFrame((n/num_group <= factor_quantile) & (factor_quantile <= (n+1)/num_group))
        group_pos[n][~group_pos[n]] = np.nan
        group_pos[n] = 1 * group_pos[n]
        group_backtest[n] = ((group_pos[n] * r).mean(1) - 1*r.mean(1)).cumsum().rename('%s'%(n/num_group))
        group_backtest[n].plot()
    plt.legend(['%s'%i for i in range(num_group)])
    plt.savefig('../Results/groupbacktest.png')
    
    plt.figure(figsize=(16, 12))
    group_hist = [group_backtest[i].iloc[np.where(group_backtest[i].notna())[0][-1]] for i in range(num_group)]
    plt.bar(range(num_group), group_hist)
    plt.savefig('../Results/grouphist.png')
    
    # plt.figure(figsize=(16,12))
    # r.mad(1).cumsum().plot()
    # plt.legend(['DIV'])
    # plt.savefig('%s/Results/DIV.png'%gc.BACKTEST_PATH)
    
    plt.figure(figsize=(16,12))
    pnl.cumsum().plot()
    r.mean(1).cumsum().plot()
    (pnl - r.mean(1)).cumsum().plot()
    alpha = pnl - r.mean(1)
    print('日均')
    print(alpha.mean())
    print('夏普')
    print(alpha.mean()/alpha.std() * np.sqrt(250))
    print('胜率')
    print((alpha>0).mean())
    print('盈亏比')
    print((alpha[alpha>0].mean()/alpha[alpha<0].mean()))
    plt.legend(['PNL', 'BENCHMARK', 'ALPHA'])
    plt.savefig('%s/Results/backtest_sum.png'%gc.BACKTEST_PATH)
    
    plt.figure(figsize=(16,12))
    (1+pnl).cumprod().plot()
    (1+r.mean(1)).cumprod().plot()
    ((1+pnl).cumprod() / (1+r.mean(1)).cumprod()).plot()
    plt.legend(['PNL', 'BENCHMARK', 'ALPHA'])
    plt.savefig('%s/Results/backtest_prod.png'%gc.BACKTEST_PATH)
    #begin end
    #股票排序
    #按换手率生成持仓
    #生成日收益率
    #plot和统计分析
