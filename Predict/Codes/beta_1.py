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
        big_mask = factor_df.ge(factor_df.quantile(0.975, 1), 0)
        small_mask = factor_df.le(factor_df.quantile(0.025, 1), 0)
        factor_df[na_mask.isna()] = np.nan
        factor_df[big_mask|small_mask] = 0
        factor_df_dic[factor] = factor_df

    beta = pd.read_csv('%s/Results/beta.csv'%gc.IC_PATH, index_col=[0], parse_dates=[0])
    beta = beta.loc[:, factors]
    beta.fillna(method='ffill', inplace=True)
    beta.fillna(0, inplace=True)
    
    halflife_mean = 120
    halflife_cov = 250
    a = 0.1
    lamb = 1e-4
    n = 5
    lag = n + 1
    beta_mean_hat = beta.ewm(halflife=halflife_mean).mean().shift(lag)
    beta_cov_hat = beta.ewm(halflife=halflife_cov).cov().shift(lag*len(factors))
    weight = DataFrame(index=beta.index, columns=beta.columns)
    for date in weight.index:
        weight.loc[date, :] = np.linalg.inv((1 + a*np.eye(len(factors))) * beta_cov_hat.loc[date, :, :].values + lamb*np.eye(len(factors))).dot(beta_mean_hat.loc[date, :].values)
            
    for factor in factors:
        r_hat = r_hat.add(factor_df_dic[factor].mul(weight.loc[:, factor], 0), fill_value=0)
    
    r_hat.to_csv('../Results/r_hat_beta_1.csv')
    # m3 = np.random.rand(400).reshape(20,20)
    # m4 = np.random.rand(625).reshape(25,25)
    # m4[:20,:20]=m3
    # m4[20:,:]=0
    # m4[:,20:]=0
    # inv1 = np.linalg.inv(m3)
    # inv2 = np.linalg.inv(m4+1e-6*np.eye(25))
    # inv2_11 = inv2[:20, :20]
    # d = inv1-inv2_11
if __name__ == '__main__':
    main()