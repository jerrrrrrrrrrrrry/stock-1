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
    factors.extend(['ROE', 'EP', 'DEP', 'BP'])
    #factors.extend(['MomentumInd', 'MomentumBK'])
    #factors.extend(['Momentum', 'Alpha', 'Bias', 'Donchian', 'TSRegBeta'])
    factors.extend(['Jump', 'MomentumWeighted', 'CloseToAverage'])
    factors.extend(['CORRMarket'])
    factors.extend(['Sigma', 'ZF'])
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
        big_mask = factor_df.ge(factor_df.quantile(0.99, 1), 0)
        small_mask = factor_df.le(factor_df.quantile(0.01, 1), 0)
        factor_df[big_mask|small_mask] = 0
        factor_df_dic[factor] = factor_df

    ic = pd.read_csv('%s/Results/ic.csv'%gc.IC_PATH, index_col=[0], parse_dates=[0])
    beta = pd.read_csv('%s/Results/beta.csv'%gc.IC_PATH, index_col=[0], parse_dates=[0])
    
    halflife_mean = 60
    halflife_std = 120
    halflife_cov = 250
    n = 5
    lag = n + 1
    ic_mean_hat = ic.ewm(halflife=halflife_mean).mean().shift(lag)
    beta_mean_hat = beta.ewm(halflife=halflife_mean).mean().shift(lag)
    for factor in factors:
        print(factor)
        print(r_hat)
        r_hat = r_hat.add(factor_df_dic[factor].mul(ic_mean_hat.loc[:, factor], 0), fill_value=0)
    
    r_hat.to_csv('../Results/r_hat_ic_0.csv')