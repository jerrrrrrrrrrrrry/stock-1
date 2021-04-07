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
    end_date = '20210401'
    # end_date = datetime.datetime.today().strftime('%Y%m%d')
    first = 1
    second = 1
    third = 0
    trade_cal = tools.get_trade_cal(begin_date, end_date)
    trade_cal = [pd.Timestamp(i) for i in trade_cal]
    factors = []
    factors.extend(['MC'])
    factors.extend(['TurnRate'])
    factors.extend(['ROE', 'EP', 'DEP', 'BP'])
    #factors.extend(['MomentumInd', 'MomentumBK'])
    #factors.extend(['Momentum', 'Alpha', 'Bias', 'Donchian', 'TSRegBeta'])
    factors.extend(['Jump', 'MomentumWeighted', 'CloseToAverage'])
    factors.extend(['CORRMarket'])
    factors.extend(['Sigma', 'ZF'])
    #factors.extend(['RQPM'])
    factors.extend(['HFStdMean', 'HFUID', 'HFReversalMean', 'HFSkewMean', 'HFVolMean'])
    #factors.extend(['HFStdMean', 'HFReversalMean', 'HFVolPowerMean', 'HFUID', 'HFSkewMean'])
    #y = pd.read_csv('%s/Data/y.csv'%gc.LABELBASE_PATH, index_col=[0], parse_dates=[0])
    r = pd.read_csv('%s/Data/y.csv'%gc.LABELBASE_PATH, index_col=[0], parse_dates=[0])
    #r_rinei = pd.read_csv('%s/Data/r_rinei.csv'%gc.LABELBASE_PATH, index_col=[0], parse_dates=[0])
    #r_geye = pd.read_csv('%s/Data/r_geye.csv'%gc.LABELBASE_PATH, index_col=[0], parse_dates=[0])

    
    
    mc = pd.read_csv('%s/Data/MC.csv'%(gc.FACTORBASE_PATH), index_col=[0], parse_dates=[0])
    stocks = list(mc.columns)
    industrys = tools.get_industrys('L1', stocks)
    #mc = mc.loc[y.index.dropna(), stocks]
    mc = tools.standardize_industry(mc, industrys)
    #beta = (y_neutral_ind * mc).sum(1) / (mc * mc).sum(1)
    
    r = r.loc[r.index>=begin_date, :]
    r = r.loc[r.index<=end_date, :]
    
    factors = list(set(factors))
    print(factors)
    
    halflife_mean_first = 120
    halflife_mean_second = 60
    halflife_mean_third = 20
    halflife_std_first = 120
    halflife_std_second = 60
    halflife_std_third = 20
    halflife_cov = 250
    lag = 5
    turn_rate = 0.1
    n = 5
    m = n
    if first:
        ic_list = []
    if second:
        ic_pos_list = []
        ic_neg_list = []
    if third:
        ic_big_list = []
        ic_middle_list = []
        ic_small_list = []
    print('-开始读ic-')
    for i in range(n):
        #print(i)
        if first:
            ic_list.append(pd.read_csv('%s/Results/IC_%s.csv'%(gc.IC_PATH, i), index_col=[0], parse_dates=[0]).loc[:, factors].fillna(0))
        if second:
            ic_pos_list.append(pd.read_csv('%s/Results/IC_POS_%s.csv'%(gc.IC_PATH, i), index_col=[0], parse_dates=[0]).loc[:, factors].fillna(0))
            ic_neg_list.append(pd.read_csv('%s/Results/IC_NEG_%s.csv'%(gc.IC_PATH, i), index_col=[0], parse_dates=[0]).loc[:, factors].fillna(0))
        # if third:
        #     ic_big_list.append(pd.read_csv('%s/Results/IC_BIG_%s.csv'%(gc.IC_PATH, i), index_col=[0], parse_dates=[0]).loc[:, factors].fillna(0))
        #     ic_middle_list.append(pd.read_csv('%s/Results/IC_MIDDLE_%s.csv'%(gc.IC_PATH, i), index_col=[0], parse_dates=[0]).loc[:, factors].fillna(0))
        #     ic_small_list.append(pd.read_csv('%s/Results/IC_SMALL_%s.csv'%(gc.IC_PATH, i), index_col=[0], parse_dates=[0]).loc[:, factors].fillna(0))
    
    print('-计算ic_mean_hat-')
    if first:
        ic_mean_hat_list = [ic_list[n].ewm(halflife=halflife_mean_first).mean().shift(n+lag) for n in range(len(ic_list))]
    if second:
        ic_pos_mean_hat_list = [ic_pos_list[n].ewm(halflife=halflife_mean_second).mean().shift(n+lag) for n in range(len(ic_pos_list))]
        ic_neg_mean_hat_list = [ic_neg_list[n].ewm(halflife=halflife_mean_second).mean().shift(n+lag) for n in range(len(ic_neg_list))]
    # if third:
    #     ic_big_mean_hat_list = [ic_big_list[n].ewm(halflife=halflife_mean_third).mean().shift(n+lag) for n in range(len(ic_big_list))]
    #     ic_middle_mean_hat_list = [ic_middle_list[n].ewm(halflife=halflife_mean_third).mean().shift(n+lag) for n in range(len(ic_middle_list))]
    #     ic_small_mean_hat_list = [ic_small_list[n].ewm(halflife=halflife_mean_third).mean().shift(n+lag) for n in range(len(ic_small_list))]
    
    print('-计算ic_std_hat-')
    if first:
        ic_std_hat_list = [ic_list[n].ewm(halflife=halflife_std_first).std().shift(n+lag) for n in range(len(ic_list))]
    
    if second:
        ic_pos_std_hat_list = [ic_pos_list[n].ewm(halflife=halflife_std_second).std().shift(n+lag) for n in range(len(ic_pos_list))]
        ic_neg_std_hat_list = [ic_neg_list[n].ewm(halflife=halflife_std_second).std().shift(n+lag) for n in range(len(ic_neg_list))]
    
    # if third:
    #     ic_big_std_hat_list = [ic_big_list[n].ewm(halflife=halflife_std_third).std().shift(n+lag) for n in range(len(ic_big_list))]
    #     ic_middle_std_hat_list = [ic_middle_list[n].ewm(halflife=halflife_std_third).std().shift(n+lag) for n in range(len(ic_middle_list))]
    #     ic_small_std_hat_list = [ic_small_list[n].ewm(halflife=halflife_std_third).std().shift(n+lag) for n in range(len(ic_small_list))]

    print('-计算ic_cov_hat-')
    if first:
        ic_cov_hat_list = [ic_list[n].ewm(halflife=halflife_cov).cov().shift(len(ic_list[0].columns)*(n+lag)).fillna(0) for n in range(len(ic_list))]
    
    # if second:
        # ic_pos_cov_hat_list = [ic_pos_list[n].ewm(halflife=halflife_cov).cov().shift(len(ic_pos_list[0].columns)*(n+lag)) for n in range(len(ic_pos_list))]
        # ic_neg_cov_hat_list = [ic_neg_list[n].ewm(halflife=halflife_cov).cov().shift(len(ic_neg_list[0].columns)*(n+lag)) for n in range(len(ic_neg_list))]
        
    # if third:
        # ic_big_cov_hat_list = [ic_big_list[n].ewm(halflife=halflife_cov).cov().shift(n+lag) for n in range(len(ic_big_list))]
        # ic_middle_cov_hat_list = [ic_middle_list[n].ewm(halflife=halflife_cov).cov().shift(n+lag) for n in range(len(ic_middle_list))]
        # ic_small_cov_hat_list = [ic_small_list[n].ewm(halflife=halflife_cov).cov().shift(n+lag) for n in range(len(ic_small_list))]
        
    
    # ic_corr_est = ic_list[0].ewm(halflife=halflife_cov).corr().shift(len(ic_list[0].columns)*(0+lag))
    # ic_corr_est.to_csv('../Results/IC_CORR.csv')
    
    if first:
        weight_list = [DataFrame(index=ic_mean_hat_list[n].index, columns=ic_mean_hat_list[n].columns) for n in range(len(ic_mean_hat_list))]
    if second:
        weight_pos_list = [DataFrame(index=ic_pos_mean_hat_list[n].index, columns=ic_pos_mean_hat_list[n].columns) for n in range(len(ic_pos_mean_hat_list))]
        weight_neg_list = [DataFrame(index=ic_neg_mean_hat_list[n].index, columns=ic_neg_mean_hat_list[n].columns) for n in range(len(ic_neg_mean_hat_list))]
    # if third:
    #     weight_big_list = [DataFrame(index=ic_big_mean_hat_list[n].index, columns=ic_big_mean_hat_list[n].columns) for n in range(len(ic_big_mean_hat_list))]
    #     weight_middle_list = [DataFrame(index=ic_middle_mean_hat_list[n].index, columns=ic_middle_mean_hat_list[n].columns) for n in range(len(ic_middle_mean_hat_list))]
    #     weight_small_list = [DataFrame(index=ic_small_mean_hat_list[n].index, columns=ic_small_mean_hat_list[n].columns) for n in range(len(ic_small_mean_hat_list))]
    
    print('-计算权重-')
    
    w_var_first = 0
    w_cov_first = 1 - w_var_first
    w_lambda_first = 0.0001
    w_var_second = 1
    w_cov_second = 1 - w_var_second
    w_lambda_second = 0.001
    w_var_third = 1
    w_cov_third = 1 - w_var_third
    print(w_var_first, w_var_second, w_var_third)
    w_lambda_third = 0.001
    
    for n in range(m):
        #print(n)
        for date in r.index:
            if first:
                weight_list[n].loc[date, :] = np.linalg.inv(np.diag(w_var_first*ic_std_hat_list[n].loc[date, :])**2 + w_cov_first*ic_cov_hat_list[n].loc[date, :, :].values + w_lambda_first*np.eye(len(ic_cov_hat_list[n].loc[date, :, :]))).dot(ic_mean_hat_list[n].loc[date, :].values)
            if second:
                # weight_pos_list[n].loc[date, :] = np.linalg.inv(np.diag(w_var_second*ic_pos_std_hat_list[n].loc[date, :])**2 + w_cov_second*ic_pos_cov_hat_list[n].loc[date, :, :].values + w_lambda_second*np.eye(len(ic_pos_cov_hat_list[n].loc[date, :, :]))).dot(ic_pos_mean_hat_list[n].loc[date, :].values)
                # weight_neg_list[n].loc[date, :] = np.linalg.inv(np.diag(w_var_second*ic_neg_std_hat_list[n].loc[date, :])**2 + w_cov_second*ic_neg_cov_hat_list[n].loc[date, :, :].values + w_lambda_second*np.eye(len(ic_neg_cov_hat_list[n].loc[date, :, :]))).dot(ic_neg_mean_hat_list[n].loc[date, :].values)
            
                weight_pos_list[n].loc[date, :] = np.linalg.inv(np.diag(w_var_second*ic_pos_std_hat_list[n].loc[date, :])**2  + w_lambda_second*np.eye(len(factors))).dot(ic_pos_mean_hat_list[n].loc[date, :].values)
                weight_neg_list[n].loc[date, :] = np.linalg.inv(np.diag(w_var_second*ic_neg_std_hat_list[n].loc[date, :])**2  + w_lambda_second*np.eye(len(factors))).dot(ic_neg_mean_hat_list[n].loc[date, :].values)
            # if third:
                # weight_big_list[n].loc[date, :] = np.linalg.inv(np.diag(w_var_third*ic_big_std_hat_list[n].loc[date, :])**2 + w_cov_third*ic_big_cov_hat_list[n].loc[date, :, :].values + w_lambda_third*np.eye(len(ic_big_cov_hat_list[n].loc[date, :, :]))).dot(ic_big_mean_hat_list[n].loc[date, :].values)
                # weight_middle_list[n].loc[date, :] = np.linalg.inv(np.diag(w_var_third*ic_middle_std_hat_list[n].loc[date, :])**2 + w_cov_third*ic_middle_cov_hat_list[n].loc[date, :, :].values + w_lambda_third*np.eye(len(ic_middle_cov_hat_list[n].loc[date, :, :]))).dot(ic_middle_mean_hat_list[n].loc[date, :].values)
                # weight_small_list[n].loc[date, :] = np.linalg.inv(np.diag(w_var_third*ic_small_std_hat_list[n].loc[date, :])**2 + w_cov_third*ic_small_cov_hat_list[n].loc[date, :, :].values + w_lambda_third*np.eye(len(ic_small_cov_hat_list[n].loc[date, :, :]))).dot(ic_small_mean_hat_list[n].loc[date, :].values)
                
                # weight_big_list[n].loc[date, :] = np.linalg.inv(np.diag(w_var_third*ic_big_std_hat_list[n].loc[date, :])**2 + w_cov_third*ic_cov_hat_list[n].loc[date, :, :].values + w_lambda_third*np.eye(len(ic_cov_hat_list[n].loc[date, :, :]))).dot(ic_big_mean_hat_list[n].loc[date, :].values)
                # weight_middle_list[n].loc[date, :] = np.linalg.inv(np.diag(w_var_third*ic_middle_std_hat_list[n].loc[date, :])**2 + w_cov_third*ic_cov_hat_list[n].loc[date, :, :].values + w_lambda_third*np.eye(len(ic_cov_hat_list[n].loc[date, :, :]))).dot(ic_middle_mean_hat_list[n].loc[date, :].values)
                # weight_small_list[n].loc[date, :] = np.linalg.inv(np.diag(w_var_third*ic_small_std_hat_list[n].loc[date, :])**2 + w_cov_third*ic_cov_hat_list[n].loc[date, :, :].values + w_lambda_third*np.eye(len(ic_cov_hat_list[n].loc[date, :, :]))).dot(ic_small_mean_hat_list[n].loc[date, :].values)
       
        # if first:
        #     weight_list[n] = tools.standardize(weight_list[n])
        # if second:
        #     weight_pos_list[n] = tools.standardize(weight_pos_list[n])
        #     weight_neg_list[n] = tools.standardize(weight_neg_list[n])
        # if third:
        #     weight_big_list[n] = tools.standardize(weight_big_list[n])
        #     weight_middle_list[n] = tools.standardize(weight_middle_list[n])
        #     weight_small_list[n] = tools.standardize(weight_small_list[n])
            
            
    # ic_cov_hat_list[0].to_csv('../Results/ic_cov.csv')
    
    print('权重求和')
    def f(df_list, turn_rate=0.2):
        # s = 1 - (1 - turn_rate) ** len(df_list)
        mean = DataFrame(0, index=df_list[0].index, columns=df_list[0].columns)
        for i in range(len(df_list)):
            mean = mean + df_list[i] * ((1 - turn_rate)**i + (1 - i * turn_rate)) / 2
        # mean = mean / s
        ret = mean
        return ret
    if first:
        weight = f(weight_list, turn_rate)
        weight = weight.loc[weight.index>=begin_date, :]
        weight = weight.loc[weight.index<=end_date, :]
        weight.to_csv('../Results/weight.csv')
    
    if second:
        weight_pos = f(weight_pos_list, turn_rate)
        weight_pos = weight_pos.loc[weight_pos.index>=begin_date, :]
        weight_pos = weight_pos.loc[weight_pos.index<=end_date, :]
        weight_pos.to_csv('../Results/weight_pos.csv')
        
        weight_neg = f(weight_neg_list, turn_rate)
        weight_neg = weight_neg.loc[weight_neg.index>=begin_date, :]
        weight_neg = weight_neg.loc[weight_neg.index<=end_date, :]
        weight_neg.to_csv('../Results/weight_neg.csv')
    
    # if third:
    #     weight_big = f(weight_big_list, turn_rate)
    #     weight_big = weight_big.loc[weight_big.index>=begin_date, :]
    #     weight_big = weight_big.loc[weight_big.index<=end_date, :]
    #     weight_big.to_csv('../Results/weight_big.csv')
        
    #     weight_middle = f(weight_middle_list, turn_rate)
    #     weight_middle = weight_middle.loc[weight_middle.index>=begin_date, :]
    #     weight_middle = weight_middle.loc[weight_middle.index<=end_date, :]
    #     weight_middle.to_csv('../Results/weight_middle.csv')
        
    #     weight_small = f(weight_small_list, turn_rate)
    #     weight_small = weight_small.loc[weight_small.index>=begin_date, :]
    #     weight_small = weight_small.loc[weight_small.index<=end_date, :]
    #     weight_small.to_csv('../Results/weight_small.csv')
    
    r_hat = DataFrame(0, index=trade_cal, columns=r.columns)
    
    no_industry_neutral_list = ['MomentumInd', 'MomentumBK']
    no_mc_neutral_list = ['MC']
    
    print('-计算r_hat-')
    for factor in factors:
        d = DataFrame(0, index=trade_cal, columns=r.columns)
        #print('factor: %s 预处理'%factor)
        factor_df = pd.read_csv('%s/Data/%s.csv'%(gc.FACTORBASE_PATH, factor), index_col=[0], parse_dates=[0])
        factor_df = factor_df.loc[factor_df.index>=begin_date, :]
        factor_df = factor_df.loc[factor_df.index<=end_date, :]
        factor_df.fillna(method='ffill', inplace=True)
        
        
        
        stocks = list(set(factor_df.columns).intersection(set(mc.columns)))
        industrys = tools.get_industrys('L1', stocks)
        mc_df = mc.loc[:, stocks]
        
        if factor in no_industry_neutral_list:
            factor_df = tools.standardize(factor_df)
        elif factor in no_mc_neutral_list:
            factor_df = tools.standardize_industry(factor_df, industrys)
        else:
            factor_df = tools.standardize_industry(factor_df, industrys)
            beta = (factor_df * mc).sum(1) / (mc * mc).sum(1)
            factor_df = factor_df - mc_df.mul(beta, axis=0)
        print('factor: %s 贡献r_hat'%factor)
        
        big_mask = factor_df.ge(factor_df.quantile(0.975, 1), 0)
        small_mask = factor_df.le(factor_df.quantile(0.025, 1), 0)
        factor_df[big_mask|small_mask] = 0
        
        if first:
            d_first = factor_df.mul(weight.loc[:, factor], axis=0)
            d = d.add(d_first, fill_value=0)
            
        if second:
            knot_1 = 0
            
            indicative_2 = factor_df.ge(knot_1, 0)
            
            d_second_1 = factor_df.mul(weight_neg.loc[:, factor], axis=0)
            d_second_2 = indicative_2 * factor_df.sub(knot_1, axis=0).mul(weight_pos.sub(weight_neg).loc[:, factor], axis=0)
            d = d.add(d_second_1, fill_value=0)
            d = d.add(d_second_2, fill_value=0)
            
        # if third:
        #     knot_1 = factor_df.quantile(1/3, 1)
        #     knot_2 = factor_df.quantile(2/3, 1)
            
        #     indicative_2 = factor_df.ge(knot_1, 0)
        #     indicative_3 = factor_df.ge(knot_2, 0)
            
        #     d_third_1 = factor_df.mul(weight_small.loc[:, factor], axis=0)
        #     d_third_2 = indicative_2 * factor_df.sub(knot_1, axis=0).mul(weight_middle.sub(weight_small).loc[:, factor], axis=0)
        #     d_third_3 = indicative_3 * factor_df.sub(knot_2, axis=0).mul(weight_big.sub(weight_middle).loc[:, factor], axis=0)
            
        #     d = d.add(d_third_1, fill_value=0)
        #     d = d.add(d_third_2, fill_value=0)
        #     d = d.add(d_third_3, fill_value=0)
            
        # d = tools.standardize(d)
        r_hat = r_hat + d
    
    print('回测')
    stock_num = 50
    trade_num = int(stock_num * turn_rate)
    
    num_group = 80
    
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
