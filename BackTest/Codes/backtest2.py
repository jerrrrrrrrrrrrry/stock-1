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
    end_date = '20210329'
    # end_date = datetime.datetime.today().strftime('%Y%m%d')
    
    trade_cal = tools.get_trade_cal(begin_date, end_date)
    trade_cal = [pd.Timestamp(i) for i in trade_cal]
    factors = []
    factors.extend(['MC'])
    factors.extend(['TurnRate'])
    factors.extend(['ROE', 'EP', 'DEP', 'BP'])
    #factors.extend(['MomentumInd'])
    #factors.extend(['Momentum', 'Alpha', 'Bias', 'Donchian', 'TSRegBeta'])
    factors.extend(['Jump', 'MomentumWeighted', 'CloseToAverage'])
    factors.extend(['CORRMarket'])
    factors.extend(['Sigma', 'ZF'])
    #factors.extend(['RQPM'])
    factors.extend(['HFStdMean', 'HFUID', 'HFReversalMean', 'HFSkewMean', 'HFVolMean'])
    #factors.extend(['HFStdMean', 'HFReversalMean', 'HFVolPowerMean', 'HFUID', 'HFSkewMean'])
    #y = pd.read_csv('%s/Data/y.csv'%gc.LABELBASE_PATH, index_col=[0], parse_dates=[0])
    r = pd.read_csv('%s/Data/r.csv'%gc.LABELBASE_PATH, index_col=[0], parse_dates=[0])
    #r_rinei = pd.read_csv('%s/Data/r_rinei.csv'%gc.LABELBASE_PATH, index_col=[0], parse_dates=[0])
    #r_geye = pd.read_csv('%s/Data/r_geye.csv'%gc.LABELBASE_PATH, index_col=[0], parse_dates=[0])

    
    
    mc = pd.read_csv('%s/Data/MC.csv'%(gc.FACTORBASE_PATH), index_col=[0], parse_dates=[0])
    stocks = list(mc.columns)
    industrys = tools.get_industrys('L1', stocks)
    #mc = mc.loc[y.index.dropna(), stocks]
    mc = tools.standardize_industry(mc, industrys)
    mc = mc.loc[mc.index>=begin_date, :]
    mc = mc.loc[mc.index<=end_date, :]
    #beta = (y_neutral_ind * mc).sum(1) / (mc * mc).sum(1)
    
    r = r.loc[r.index>=begin_date, :]
    r = r.loc[r.index<=end_date, :]
    
    factors = list(set(factors))
    print(factors)
    
    halflife_mean_nl = 60
    halflife_mean = 60
    halflife_cov = 250
    lag = 1
    turn_rate = 0.1
    n = 5
    # ic_mega_list = []
    # ic_big_list = []
    # ic_small_list = []
    # ic_micro_list = []
    ic_pos_list = []
    ic_neg_list = []
    print('-开始读ic-')
    for i in range(n):
        # ic_mega_list.append(pd.read_csv('%s/Results/IC_MEGA_%s.csv'%(gc.IC_PATH, i), index_col=[0], parse_dates=[0]).loc[:, factors].fillna(0))
        # ic_big_list.append(pd.read_csv('%s/Results/IC_BIG_%s.csv'%(gc.IC_PATH, i), index_col=[0], parse_dates=[0]).loc[:, factors].fillna(0))
        # ic_small_list.append(pd.read_csv('%s/Results/IC_SMALL_%s.csv'%(gc.IC_PATH, i), index_col=[0], parse_dates=[0]).loc[:, factors].fillna(0))
        # ic_micro_list.append(pd.read_csv('%s/Results/IC_MICRO_%s.csv'%(gc.IC_PATH, i), index_col=[0], parse_dates=[0]).loc[:, factors].fillna(0))
        ic_pos_list.append(pd.read_csv('%s/Results/IC_POS_%s.csv'%(gc.IC_PATH, i), index_col=[0], parse_dates=[0]).loc[:, factors].fillna(0))
        ic_neg_list.append(pd.read_csv('%s/Results/IC_NEG_%s.csv'%(gc.IC_PATH, i), index_col=[0], parse_dates=[0]).loc[:, factors].fillna(0))
        
    print('-计算ic_mean_hat-')
    # ic_mega_mean_hat_list = [ic_mega_list[i].ewm(halflife=halflife_mean_nl).mean().shift(i+lag) for i in range(n)]
    # ic_big_mean_hat_list = [ic_big_list[i].ewm(halflife=halflife_mean_nl).mean().shift(i+lag) for i in range(n)]
    # ic_small_mean_hat_list = [ic_small_list[i].ewm(halflife=halflife_mean_nl).mean().shift(i+lag) for i in range(n)]
    # ic_micro_mean_hat_list = [ic_micro_list[i].ewm(halflife=halflife_mean_nl).mean().shift(i+lag) for i in range(n)]
    ic_pos_mean_hat_list = [ic_pos_list[i].ewm(halflife=halflife_mean_nl).mean().shift(i+lag) for i in range(n)]
    ic_neg_mean_hat_list = [ic_neg_list[i].ewm(halflife=halflife_mean_nl).mean().shift(i+lag) for i in range(n)]

    print('权重求和')
    def f(df_list, turn_rate=0.1):
        mean = DataFrame(0, index=df_list[0].index, columns=df_list[0].columns)
        for i in range(len(df_list)):
            mean = mean + df_list[i] * ((1 - turn_rate)**i + (1 - i * turn_rate)) / 2
        mean = mean
        ret = mean
        return ret
    ic_pos_mean_hat = f(ic_pos_mean_hat_list, turn_rate)
    ic_neg_mean_hat = f(ic_neg_mean_hat_list, turn_rate)
    # ic_small_mean_hat = f(ic_small_mean_hat_list, turn_rate)
    # ic_micro_mean_hat = f(ic_micro_mean_hat_list, turn_rate)
    ic_pos_mean_hat = ic_pos_mean_hat.loc[ic_pos_mean_hat.index>=begin_date, :]
    ic_pos_mean_hat = ic_pos_mean_hat.loc[ic_pos_mean_hat.index<=end_date, :]
    ic_neg_mean_hat = ic_neg_mean_hat.loc[ic_neg_mean_hat.index>=begin_date, :]
    ic_neg_mean_hat = ic_neg_mean_hat.loc[ic_neg_mean_hat.index<=end_date, :]
    # ic_small_mean_hat = ic_small_mean_hat.loc[ic_small_mean_hat.index>=begin_date, :]
    # ic_small_mean_hat = ic_small_mean_hat.loc[ic_small_mean_hat.index<=end_date, :]
    # ic_micro_mean_hat = ic_micro_mean_hat.loc[ic_micro_mean_hat.index>=begin_date, :]
    # ic_micro_mean_hat = ic_micro_mean_hat.loc[ic_micro_mean_hat.index<=end_date, :]
    industry_list = ['MomentumInd']
    no_mc_neutral_list = ['MC']
    
    
    print('-因子非线性转换-')
    factor_nl_dic = {}
    IC_dic = {}
    for i in range(n):
        IC_dic[i] = DataFrame(columns=factors)
    for factor in factors:
        print('factor: %s 预处理'%factor)
        factor_df = pd.read_csv('%s/Data/%s.csv'%(gc.FACTORBASE_PATH, factor), index_col=[0], parse_dates=[0])
        factor_df = factor_df.loc[factor_df.index>=begin_date, :]
        factor_df = factor_df.loc[factor_df.index<=end_date, :]
        factor_df.fillna(method='ffill', inplace=True)
        
        stocks = list(set(factor_df.columns).intersection(set(mc.columns)))
        industrys = tools.get_industrys('L1', stocks)
        factor_df = factor_df.loc[:, stocks]
        mc_df = mc.loc[:, stocks]
        
        if factor in industry_list:
            factor_df = tools.standardize(factor_df)
        elif factor in no_mc_neutral_list:
            factor_df = tools.standardize_industry(factor_df, industrys)
        else:
            factor_df = tools.standardize_industry(factor_df, industrys)
            beta = (factor_df * mc).sum(1) / (mc * mc).sum(1)
            factor_df = factor_df - mc_df.mul(beta, axis=0)
        
        print('factor: %s 非线性转换'%factor)
        # knot_1 = factor_df.quantile(0.25, 1)
        knot = factor_df.quantile(0.5, 1)
        # knot_3 = factor_df.quantile(0.75, 1)
        
        # mega_mask = factor_df.ge(knot_3, 0)
        # big_mask = factor_df.ge(knot_2, 0)
        # small_mask = factor_df.ge(knot_1, 0)
        pos_mask = factor_df.ge(knot, 0)
        factor_nl = DataFrame(0, index=factor_df.index, columns=factor_df.columns)
        factor_nl = factor_nl.add(factor_df.mul(ic_neg_mean_hat.loc[:, factor], 0), fill_value=0)
        
        factor_nl = factor_nl.add(pos_mask * (factor_df.sub(knot, 0)).mul(ic_pos_mean_hat.loc[:, factor].sub(ic_neg_mean_hat.loc[:, factor], 0), 0), fill_value=0)
        # factor_nl = factor_nl.add(big_mask * (factor_df.sub(knot_2, 0)).mul(ic_big_mean_hat.loc[:, factor].sub(ic_small_mean_hat.loc[:, factor], 0), 0), fill_value=0)
        # factor_nl = factor_nl.add(mega_mask * (factor_df.sub(knot_3, 0)).mul(ic_mega_mean_hat.loc[:, factor].sub(ic_big_mean_hat.loc[:, factor], 0), 0), fill_value=0)
        
        factor_nl_dic[factor] = factor_nl.copy()
        print('factor: %s IC'%factor)
        for i in range(1, n+1):
            IC_dic[i-1].loc[:, factor] = factor_nl.corrwith(r.rolling(i).sum().shift(1-i), 1).fillna(0)
    ic_list = []
    for i in range(n):
        ic_list.append(IC_dic[i])
    ic_mean_hat_list = [ic_list[i].ewm(halflife=halflife_mean).mean().shift(i+lag) for i in range(n)]
    ic_cov_hat_list = [ic_list[i].ewm(halflife=halflife_cov).cov().shift(len(factors)*(i+lag)) for i in range(n)]
    
    v_list = [DataFrame(index=ic_mean_hat_list[i].index, columns=ic_mean_hat_list[i].columns) for i in range(n)]
    
    lamb = 0.0001
    for i in range(n):
        for date in r.index:
            v_list[i].loc[date, :] = np.linalg.inv(0*ic_cov_hat_list[i].loc[date, :, :].values + lamb*np.eye(len(factors))).dot(ic_mean_hat_list[i].loc[date, :].values)
            
    v = f(v_list, turn_rate)
    v.to_csv('../Results/v.csv')
    weight = DataFrame(0, index=trade_cal, columns=r.columns)
    for factor in factors:
        print('factor: %s 贡献权重'%factor)
        factor_df = factor_nl_dic[factor]
        factor_df = factor_df.loc[factor_df.index>=begin_date, :]
        factor_df = factor_df.loc[factor_df.index<=end_date, :]
        factor_df.fillna(method='ffill', inplace=True)
        
        stocks = list(set(factor_df.columns).intersection(set(mc.columns)))
        industrys = tools.get_industrys('L1', stocks)
        factor_df = factor_df.loc[:, stocks]
        mc_df = mc.loc[:, stocks]
        
        if factor in industry_list:
            factor_df = tools.standardize(factor_df)
        elif factor in no_mc_neutral_list:
            factor_df = tools.standardize_industry(factor_df, industrys)
        else:
            factor_df = tools.standardize_industry(factor_df, industrys)
            beta = (factor_df * mc).sum(1) / (mc * mc).sum(1)
            factor_df = factor_df - mc_df.mul(beta, axis=0)
        weight = weight.add(factor_df.mul(v.loc[:, factor], axis=0), fill_value=0)
    weight.to_csv('../Results/weight.csv')
    # ic_corr_est = ic_list[0].ewm(halflife=halflife_cov).corr().shift(len(ic_list[0].columns)*(0+lag))
    # ic_corr_est.to_csv('../Results/IC_CORR.csv')
    r_hat = weight
    print('回测')
    stock_num = 100
    trade_num = int(stock_num * turn_rate)
    
    num_group = 10
    
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
    IC = r_hat.fillna(0).corrwith(r.fillna(0), axis=1)
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
    print(alpha.mean()/alpha.std() * np.sqrt(250))
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