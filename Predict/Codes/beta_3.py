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

def main(factors):
    today = datetime.datetime.today().strftime('%Y%m%d')
    start_date = '20180101'
    end_date = today
    # factors = []
    # # factors.extend(['MC', 'BP'])
    # factors.extend(['TurnRate1'])
    # # factors.extend(['DEP'])
    # # factors.extend(['ROE', 'EP', 'DEP'])
    # #factors.extend(['MomentumInd', 'MomentumBK'])
    
    # factors.extend(['Bias20'])
    # factors.extend(['TSRegBeta60'])
    # factors.extend(['Donchian120'])
    # factors.extend(['CloseToAverage1'])
    # factors.extend(['Jump1'])
    # factors.extend(['CORRMarket20'])
    # factors.extend(['Sigma20'])
    # factors.extend(['ZF20'])
    # factors.extend(['Skew20'])
    
    # # factors.extend(['RQPM'])
    # factors.extend(['HFReversalMean20'])
    # factors.extend(['HFStdMean20'])
    # factors.extend(['HFUID20'])
    # factors.extend(['HFSkewMean20'])
    # factors.extend(['HFVolMean20'])
    # # factors.extend(['HFVolPowerMean20'])
    
    r = pd.read_csv('%s/Data/r_jiaoyi.csv'%gc.LABELBASE_PATH, index_col=[0], parse_dates=[0])
    dates = r.index[(r.index>=start_date) & (r.index<=end_date)]
    
    r_hat = DataFrame(0, index=dates, columns=r.columns)
    
    na_mask = pd.read_csv('%s/Data/na_mask.csv'%gc.LABELBASE_PATH, index_col=[0], parse_dates=[0])
    
    factor_df_dic = {}
    for factor in factors:
        print(factor)
        factor_df = pd.read_csv('%s/PreprocessData/%s.csv'%(gc.FACTORBASE_PATH, factor), index_col=[0], parse_dates=[0])
        factor_df = DataFrame(factor_df, index=na_mask.index, columns=na_mask.columns)
        factor_df[na_mask.isna()] = np.nan
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
    
    halflife_mean = 60
    halflife_cov = 250
    a = 0.8
    lamb = 1e-3
    n = 5
    lag = n + 1
    
    beta_big_mean_hat = beta_big.ewm(halflife=halflife_mean).mean().shift(lag)
    beta_middle_mean_hat = beta_middle.ewm(halflife=halflife_mean).mean().shift(lag)
    beta_small_mean_hat = beta_small.ewm(halflife=halflife_mean).mean().shift(lag)
    
    beta_big_cov_hat = beta_big.ewm(halflife=halflife_cov).cov().shift(lag*len(factors))
    beta_middle_cov_hat = beta_middle.ewm(halflife=halflife_cov).cov().shift(lag*len(factors))
    beta_small_cov_hat = beta_small.ewm(halflife=halflife_cov).cov().shift(lag*len(factors))
    beta_cov_hat = (beta_big_cov_hat + beta_middle_cov_hat + beta_small_cov_hat) / 3
    
    weight_big = DataFrame(index=beta_big.index, columns=beta_big.columns)
    weight_middle = DataFrame(index=beta_big.index, columns=beta_big.columns)
    weight_small = DataFrame(index=beta_big.index, columns=beta_big.columns)
    
    for date in weight_big.index:
        sigma_inv = np.linalg.inv((1 + a*np.eye(len(factors))) * beta_cov_hat.loc[date, :, :].values + lamb*np.eye(len(factors)))
        weight_big.loc[date, :] = sigma_inv.dot(beta_big_mean_hat.loc[date, :].values)
        weight_middle.loc[date, :] = sigma_inv.dot(beta_middle_mean_hat.loc[date, :].values)
        weight_small.loc[date, :] = sigma_inv.dot(beta_small_mean_hat.loc[date, :].values)
        
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
    
if __name__ == '__main__':
    main()