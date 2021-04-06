# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import Config
import sys
sys.path.append(Config.GLOBALCONFIG_PATH)

import Global_Config as gc
import tools
import datetime
if __name__ == '__main__':
    today = datetime.datetime.today().strftime('%Y%m%d')
    start_date = '20180101'
    end_date = today
    factors = []
    factors.extend(['MC'])
    factors.extend(['TurnRate'])
    factors.extend(['ROE', 'DEP'])
    # factors.extend(['ROE', 'EP', 'DEP', 'BP'])
    #factors.extend(['MomentumInd', 'MomentumBK'])
    #factors.extend(['Momentum', 'Alpha', 'Bias', 'Donchian', 'TSRegBeta'])
    factors.extend(['Jump', 'MomentumWeighted', 'CloseToAverage'])
    factors.extend(['CORRMarket'])
    factors.extend(['Sigma', 'ZF', 'Skew'])
    #factors.extend(['RQPM'])
    factors.extend(['HFStdMean', 'HFUID', 'HFReversalMean', 'HFSkewMean', 'HFVolMean'])
    #factors.extend(['HFStdMean', 'HFReversalMean', 'HFVolPowerMean', 'HFUID', 'HFSkewMean'])
    
    mc = pd.read_csv('%s/Data/MC.csv'%(gc.FACTORBASE_PATH), index_col=[0], parse_dates=[0])
    dates = mc.index[(mc.index>=start_date) & (mc.index<=end_date)]
    stocks = list(mc.columns)
    industrys = tools.get_industrys('L1', stocks)
    mc = mc.loc[dates, stocks]
    mc = tools.standardize_industry(mc, industrys)
    r = pd.read_csv('%s/Data/r_jiaoyi.csv'%gc.LABELBASE_PATH, index_col=[0], parse_dates=[0])
    
    r_hat = DataFrame(0, index=dates, columns=r.columns)
    
    #行业轮动因子列表
    industry_list = ['MomentumInd']
    #不做市值中性因子列表
    no_mc_neutral_list = ['MC']
    
    factor_df_dic = {}
    for factor in factors:
        print(factor)
        factor_df = pd.read_csv('%s/Data/%s.csv'%(gc.FACTORBASE_PATH, factor), index_col=[0], parse_dates=[0])
        stocks = list(set(stocks).intersection(set(factor_df.columns)))
        stocks.sort()
        industrys = tools.get_industrys('L1', stocks)
        factor_df = factor_df.loc[:, stocks]
        factor_df = factor_df.loc[factor_df.index>=start_date, :]
        factor_df = factor_df.loc[factor_df.index<=end_date, :]
        mc_df = mc.loc[dates, stocks]
        if factor in industry_list:
            factor_df = tools.standardize(factor_df)
        elif factor in no_mc_neutral_list:
            factor_df = tools.standardize_industry(factor_df, industrys)
        else:
            factor_df = tools.standardize_industry(factor_df, industrys)
            beta = (factor_df * mc_df).sum(1) / (mc_df * mc_df).sum(1)
            factor_df = factor_df - mc_df.mul(beta, 0)
        big_mask = factor_df.ge(factor_df.quantile(0.975, 1), 0)
        small_mask = factor_df.le(factor_df.quantile(0.025, 1), 0)
        factor_df[big_mask|small_mask] = 0
        factor_df_dic[factor] = factor_df

    beta_big = pd.read_csv('%s/Results/beta_big.csv'%gc.IC_PATH, index_col=[0], parse_dates=[0])
    beta_middle = pd.read_csv('%s/Results/beta_middle.csv'%gc.IC_PATH, index_col=[0], parse_dates=[0])
    beta_small = pd.read_csv('%s/Results/beta_small.csv'%gc.IC_PATH, index_col=[0], parse_dates=[0])
    beta_big = beta_big.loc[:, factors]
    beta_middle = beta_middle.loc[:, factors]
    beta_small = beta_small.loc[:, factors]
    beta_big.fillna(method='ffill', inplace=True)
    beta_middle.fillna(method='ffill', inplace=True)
    beta_small.fillna(method='ffill', inplace=True)
    beta_big.fillna(0, inplace=True)
    beta_middle.fillna(0, inplace=True)
    beta_small.fillna(0, inplace=True)
    
    halflife_mean = 20
    halflife_std = 120
    halflife_cov = 250
    lamb = 1e-4
    n = 5
    lag = n + 1
    
    beta_big_mean_hat = beta_big.ewm(halflife=halflife_mean).mean().shift(lag)
    beta_middle_mean_hat = beta_middle.ewm(halflife=halflife_mean).mean().shift(lag)
    beta_small_mean_hat = beta_small.ewm(halflife=halflife_mean).mean().shift(lag)
    
    beta_big_std_hat = beta_big.ewm(halflife=halflife_std).std().shift(lag)
    beta_middle_std_hat = beta_middle.ewm(halflife=halflife_std).std().shift(lag)
    beta_small_std_hat = beta_small.ewm(halflife=halflife_std).std().shift(lag)
    
    beta_big_cov_hat = beta_big.ewm(halflife=halflife_cov).cov().shift(lag*len(factors))
    beta_middle_cov_hat = beta_middle.ewm(halflife=halflife_cov).cov().shift(lag*len(factors))
    beta_small_cov_hat = beta_small.ewm(halflife=halflife_cov).cov().shift(lag*len(factors))
    beta_cov_hat = (beta_big_cov_hat + beta_middle_cov_hat + beta_small_cov_hat) / 3
    
    weight_big = DataFrame(index=beta_big.index, columns=beta_big.columns)
    weight_middle = DataFrame(index=beta_big.index, columns=beta_big.columns)
    weight_small = DataFrame(index=beta_big.index, columns=beta_big.columns)
    
    for date in weight_big.index:
        weight_big.loc[date, :] = np.linalg.inv(beta_cov_hat.loc[date, :, :].values + lamb*np.eye(len(factors))).dot(beta_big_mean_hat.loc[date, :].values)
        weight_middle.loc[date, :] = np.linalg.inv(beta_cov_hat.loc[date, :, :].values + lamb*np.eye(len(factors))).dot(beta_middle_mean_hat.loc[date, :].values)
        weight_small.loc[date, :] = np.linalg.inv(beta_cov_hat.loc[date, :, :].values + lamb*np.eye(len(factors))).dot(beta_small_mean_hat.loc[date, :].values)
        
    for factor in factors:
        factor_df = factor_df_dic[factor]
        knot_1 = factor_df.quantile(1/3, 1)
        knot_2 = factor_df.quantile(2/3, 1)
        middle_mask = factor_df.ge(knot_1, 0)
        big_mask = factor_df.ge(knot_2, 0)
        
        r_hat = r_hat.add(factor_df.mul(weight_small.loc[:, factor], 0), fill_value=0)
        r_hat = r_hat.add(middle_mask * factor_df.sub(knot_1, 0).mul(weight_middle.loc[:, factor] - weight_small.loc[:, factor], 0), fill_value=0)
        r_hat = r_hat.add(big_mask * factor_df.sub(knot_2, 0).mul(weight_big.loc[:, factor] - weight_middle.loc[:, factor], 0), fill_value=0)
        
    r_hat.to_csv('../Results/r_hat_beta_3.csv')