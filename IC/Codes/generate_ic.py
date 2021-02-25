# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 21:47:43 2021

@author: admin
"""

import os
import sys
import datetime
import Config
sys.path.append(Config.GLOBALCONFIG_PATH)

import Global_Config as gc
import tools
import numpy as np
import pandas as pd
from pandas import Series, DataFrame

import datetime
def main():
    halflife = 1
    turn_rate = 0.1
    n = 20
    #get y
    #y = pd.read_csv('%s/Data/y.csv'%gc.LABELBASE_PATH, index_col=[0], parse_dates=[0])
    y = pd.read_csv('%s/Data/r.csv'%gc.LABELBASE_PATH, index_col=[0], parse_dates=[0])
    
    #get factor
    files = os.listdir('%s/Data/'%gc.FACTORBASE_PATH)
    files = list(filter(lambda x:x[0] > '9', files))
    factors = {file[:-4]:pd.read_csv('%s/Data/%s'%(gc.FACTORBASE_PATH, file), index_col=[0], parse_dates=[0]) for file in files}
    
    ic_list = [DataFrame({factor:factors[factor].corrwith(y.shift(-n), method='pearson', axis=1) for factor in factors.keys()}) for n in range(n)]
    
    trade_cal = tools.get_trade_cal(start_date='20200101', end_date=datetime.datetime.today().strftime('%Y%m%d'))
    trade_cal = [pd.Timestamp(i) for i in trade_cal]
    dates = ic_list[0].index
    dates = list(filter(lambda x:x in trade_cal, dates))
    ic_list = [ic.loc[dates, :] for ic in ic_list]
    
    ic_hat_list = [ic.ewm(halflife=halflife).mean().shift(2) for ic in ic_list]
    
    ir_hat_list = [(ic.ewm(halflife=halflife).mean() / ic.ewm(halflife=halflife).std()).shift(2) for ic in ic_list]
    def f(df_list, turn_rate=0.1):
        q = 1 - turn_rate
        q_sum = (1 - q**len(df_list)) / (1 - q)
        
        mean = DataFrame(0, index=df_list[0].index, columns=df_list[0].columns)
        #var = DataFrame(0, index=df_list[0].index, columns=df_list[0].columns)
        
        for i in range(len(df_list)):
            mean = mean + df_list[i] * q**i
        mean = mean / q_sum
        
        #for i in range(len(df_list)):
        #    var = var + (df_list[i] - mean)**2 * q**i
        #var = var / q_sum
        #std = np.sqrt(var)
        #t = mean
        ret = mean
        return ret
    
    ic_hat = f(ic_hat_list, turn_rate)
    ic_hat.to_csv('%s/Results/IC_hat.csv'%gc.IC_PATH)
    ir_hat = f(ir_hat_list, turn_rate)
    ir_hat.to_csv('%s/Results/IR_hat.csv'%gc.IC_PATH)
    '''
    for i in range(len(ic_list)):
        ic_list[i].to_csv('%s/Results/IC_%s.csv'%(gc.IC_PATH, i))
        ic_hat_list[i].to_csv('%s/Results/IC_hat_%s.csv'%(gc.IC_PATH, i))
    '''
    '''
    #get y
    y1 = pd.read_csv('%s/Data/y1.csv'%gc.LABELBASE_PATH, index_col=[0], parse_dates=[0])
    y2 = pd.read_csv('%s/Data/y2.csv'%gc.LABELBASE_PATH, index_col=[0], parse_dates=[0])
    y3 = pd.read_csv('%s/Data/y3.csv'%gc.LABELBASE_PATH, index_col=[0], parse_dates=[0])
    y4 = pd.read_csv('%s/Data/y4.csv'%gc.LABELBASE_PATH, index_col=[0], parse_dates=[0])
    y5 = pd.read_csv('%s/Data/y5.csv'%gc.LABELBASE_PATH, index_col=[0], parse_dates=[0])
    y6 = pd.read_csv('%s/Data/y6.csv'%gc.LABELBASE_PATH, index_col=[0], parse_dates=[0])
    y7 = pd.read_csv('%s/Data/y7.csv'%gc.LABELBASE_PATH, index_col=[0], parse_dates=[0])
    y8 = pd.read_csv('%s/Data/y8.csv'%gc.LABELBASE_PATH, index_col=[0], parse_dates=[0])
    y9 = pd.read_csv('%s/Data/y9.csv'%gc.LABELBASE_PATH, index_col=[0], parse_dates=[0])
    y10 = pd.read_csv('%s/Data/y10.csv'%gc.LABELBASE_PATH, index_col=[0], parse_dates=[0])
    
    #get factor
    files = os.listdir('%s/Data/'%gc.FACTORBASE_PATH)
    files = list(filter(lambda x:x[0] > '9', files))
    factors = {file[:-4]:pd.read_csv('%s/Data/%s'%(gc.FACTORBASE_PATH, file), index_col=[0], parse_dates=[0]) for file in files}
    
    #y = y1 + 0.7 * y2.shift() + 0.49 * y3.shift(2) + 0.49*0.7 * y4.shift(3) + 0.49*0.49 * y5.shift(4)
    
    ic1 = DataFrame({factor:factors[factor].corrwith(y1, method='spearman', axis=1) for factor in factors.keys()})
    ic2 = DataFrame({factor:factors[factor].corrwith(y2, method='spearman', axis=1) for factor in factors.keys()})
    ic3 = DataFrame({factor:factors[factor].corrwith(y3, method='spearman', axis=1) for factor in factors.keys()})
    ic4 = DataFrame({factor:factors[factor].corrwith(y4, method='spearman', axis=1) for factor in factors.keys()})
    ic5 = DataFrame({factor:factors[factor].corrwith(y5, method='spearman', axis=1) for factor in factors.keys()})
    ic6 = DataFrame({factor:factors[factor].corrwith(y6, method='spearman', axis=1) for factor in factors.keys()})
    ic7 = DataFrame({factor:factors[factor].corrwith(y7, method='spearman', axis=1) for factor in factors.keys()})
    ic8 = DataFrame({factor:factors[factor].corrwith(y8, method='spearman', axis=1) for factor in factors.keys()})
    ic9 = DataFrame({factor:factors[factor].corrwith(y9, method='spearman', axis=1) for factor in factors.keys()})
    ic10 = DataFrame({factor:factors[factor].corrwith(y10, method='spearman', axis=1) for factor in factors.keys()})
    trade_cal = tools.get_trade_cal(start_date='20200101', end_date=datetime.datetime.today().strftime('%Y%m%d'))
    trade_cal = [pd.Timestamp(i) for i in trade_cal]
    dates = ic1.index
    dates = list(filter(lambda x:x in trade_cal, dates))
    ic1 = ic1.loc[dates, :]
    ic2 = ic2.loc[dates, :]
    ic3 = ic3.loc[dates, :]
    ic4 = ic4.loc[dates, :]
    ic5 = ic5.loc[dates, :]
    ic6 = ic6.loc[dates, :]
    ic7 = ic7.loc[dates, :]
    ic8 = ic8.loc[dates, :]
    ic9 = ic9.loc[dates, :]
    ic10 = ic10.loc[dates, :]
    
    #ic = DataFrame({factor:factors[factor].corrwith(y, method='spearman', axis=1) for factor in factors.keys()})
    
    turn_rate = 0.2
    w = 1 - turn_rate
    m = ic1 + w * ic2.shift() + w**2 * ic3.shift(2) + w**3 * ic4.shift(3) + w**4 * ic5.shift(4) + w**5 * ic6.shift(5) + w**6 * ic7.shift(6) + w**7 * ic8.shift(7) + w**8 * ic9.shift(8) + w**9 * ic10.shift(9)
    s = np.sqrt((ic1-m)**2 + w * (ic2.shift()-m)**2 + w**2 * (ic3.shift(2)-m)**2 + w**3 * (ic4.shift(3)-m)**2 + w**4 * (ic5.shift(4)-m)**2 + w**5 * (ic6.shift(5)-m)**2 + w**6 * (ic7.shift(6)-m)**2 + w**7 * (ic8.shift(7)-m)**2 + w**8 * (ic9.shift(8)-m)**2 + w**9 * (ic10.shift(9)-m)**2)
    ic = m / s
    #ic1_hat = ic1.ewm(halflife=20).mean().shift(2)
    #ic2_hat = ic2.ewm(halflife=20).mean().shift(3)
    #ic3_hat = ic3.ewm(halflife=20).mean().shift(4)
    #ic4_hat = ic4.ewm(halflife=20).mean().shift(5)
    #ic5_hat = ic5.ewm(halflife=20).mean().shift(6)
    
    #ic = ic1.add(0.7 * ic2, fill_value=0).add(0.7**2 * ic3, fill_value=0).add(0.7**3 * ic4, fill_value=0).add(0.7**4 * ic5, fill_value=0)
    #ic = ic1
    ic1.to_csv('%s/Results/IC1.csv'%gc.IC_PATH)
    ic2.to_csv('%s/Results/IC2.csv'%gc.IC_PATH)
    ic3.to_csv('%s/Results/IC3.csv'%gc.IC_PATH)
    ic4.to_csv('%s/Results/IC4.csv'%gc.IC_PATH)
    ic5.to_csv('%s/Results/IC5.csv'%gc.IC_PATH)
    ic.to_csv('%s/Results/IC.csv'%gc.IC_PATH)
    
    ic_hat = ic.ewm(halflife=20).mean().shift(2) / ic.ewm(halflife=20).std().shift(2)
    #ic_hat = ic.ewm(halflife=20).mean().shift(2)
    #ic_hat = ic1_hat + 0.7 * ic2_hat + 0.7**2 * ic3_hat + 0.7**3 * ic4_hat + 0.7**4 * ic5_hat
    
    #ic_hat = ic.rolling(60).mean().shift(6)
    ic_hat.to_csv('%s/Results/IC_hat.csv'%gc.IC_PATH)
    '''
if __name__ == '__main__':
    main()