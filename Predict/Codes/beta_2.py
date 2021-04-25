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
    # factors.extend(['MC', 'BP'])
    factors.extend(['TurnRate'])
    # factors.extend(['DEP'])
    factors.extend(['ROE', 'EP', 'DEP'])
    #factors.extend(['MomentumInd', 'MomentumBK'])
    factors.extend(['Momentum', 'Alpha', 'Bias', 'Donchian', 'TSRegBeta'])
    factors.extend(['Jump', 'MomentumWeighted', 'CloseToAverage'])
    factors.extend(['CORRMarket'])
    factors.extend(['Sigma', 'ZF', 'Skew'])
    #factors.extend(['RQPM'])
    factors.extend(['HFStdMean', 'HFUID', 'HFReversalMean', 'HFSkewMean', 'HFVolMean'])
    #factors.extend(['HFStdMean', 'HFReversalMean', 'HFVolPowerMean', 'HFUID', 'HFSkewMean'])
    
    r = pd.read_csv('%s/Data/r_jiaoyi.csv'%gc.LABELBASE_PATH, index_col=[0], parse_dates=[0])
    dates = r.index[(r.index>=start_date) & (r.index<=end_date)]
    
    r_hat = DataFrame(0, index=dates, columns=r.columns)
    
    factor_df_dic = {}
    for factor in factors:
        print(factor)
        factor_df = pd.read_csv('%s/Data/%s.csv'%(gc.FACTORBASE_PATH, factor), index_col=[0], parse_dates=[0])
        
        big_mask = factor_df.ge(factor_df.quantile(0.975, 1), 0)
        small_mask = factor_df.le(factor_df.quantile(0.025, 1), 0)
        factor_df[big_mask|small_mask] = 0
        factor_df_dic[factor] = factor_df

    beta_pos = pd.read_csv('%s/Results/beta_pos.csv'%gc.IC_PATH, index_col=[0], parse_dates=[0])
    beta_neg = pd.read_csv('%s/Results/beta_neg.csv'%gc.IC_PATH, index_col=[0], parse_dates=[0])
    beta_pos = beta_pos.loc[:, factors]
    beta_neg = beta_neg.loc[:, factors]
    beta_pos.fillna(method='ffill', inplace=True)
    beta_neg.fillna(method='ffill', inplace=True)
    beta_pos.fillna(0, inplace=True)
    beta_neg.fillna(0, inplace=True)
    halflife_mean = 60
    halflife_std = 120
    halflife_cov = 250
    a = 0.5
    lamb = 5e-4
    n = 5
    lag = n + 1
    
    beta_pos_mean_hat = beta_pos.ewm(halflife=halflife_mean).mean().shift(lag)
    beta_neg_mean_hat = beta_neg.ewm(halflife=halflife_mean).mean().shift(lag)
    
    beta_pos_std_hat = beta_pos.ewm(halflife=halflife_std).std().shift(lag)
    beta_neg_std_hat = beta_neg.ewm(halflife=halflife_std).std().shift(lag)
    
    beta_pos_cov_hat = beta_pos.ewm(halflife=halflife_cov).cov().shift(lag*len(factors))
    beta_neg_cov_hat = beta_neg.ewm(halflife=halflife_cov).cov().shift(lag*len(factors))
    beta_cov_hat = (beta_pos_cov_hat + beta_neg_cov_hat) / 2
    
    weight_pos = DataFrame(index=beta_pos.index, columns=beta_pos.columns)
    weight_neg = DataFrame(index=beta_neg.index, columns=beta_neg.columns)
    
    for date in weight_pos.index:
        sigma_inv = np.linalg.inv((1 + a*np.eye(len(factors))) * beta_cov_hat.loc[date, :, :].values + lamb*np.eye(len(factors)))
        weight_pos.loc[date, :] = sigma_inv.dot(beta_pos_mean_hat.loc[date, :].values)
        weight_neg.loc[date, :] = sigma_inv.dot(beta_neg_mean_hat.loc[date, :].values)
        
    for factor in factors:
        factor_df = factor_df_dic[factor]
        knot_1 = factor_df.quantile(0.5, 1)
        pos_mask = factor_df.ge(knot_1, 0)
        
        r_hat = r_hat.add(factor_df.mul(weight_neg.loc[:, factor], 0), fill_value=0)
        r_hat = r_hat.add(pos_mask * factor_df.sub(knot_1, 0).mul(weight_pos.loc[:, factor] - weight_neg.loc[:, factor], 0), fill_value=0)
        
    r_hat.to_csv('../Results/r_hat_beta_2.csv')