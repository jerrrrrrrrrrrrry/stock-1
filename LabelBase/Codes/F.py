#!/usr/bin/env python
# coding: utf-8

#%%
import os
import sys
import time
import datetime
import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

import tushare as ts

import Config
sys.path.append(Config.GLOBALCONFIG_PATH)
from SingleFactor import SingleFactor
import Global_Config as gc
import tools


#%%


class F(SingleFactor):
    def generate_factor(self):
        
        mc = pd.read_csv('%s/Data/MC.csv'%(gc.FACTORBASE_PATH), index_col=[0], parse_dates=[0])
        
        bp = pd.read_csv('%s/Data/BP.csv'%gc.FACTORBASE_PATH, index_col=[0], parse_dates=[0])
        
        ep = pd.read_csv('%s/Data/EP.csv'%gc.FACTORBASE_PATH, index_col=[0], parse_dates=[0])
        
        cp = pd.read_csv('%s/Data/CP.csv'%gc.FACTORBASE_PATH, index_col=[0], parse_dates=[0])
        
        sp = pd.read_csv('%s/Data/SP.csv'%gc.FACTORBASE_PATH, index_col=[0], parse_dates=[0])
        
        # dy = pd.read_csv('%s/Data/DY.csv'%gc.FACTORBASE_PATH, index_col=[0], parse_dates=[0])
        
        # dep = pd.read_csv('%s/PreprocessData/DEP.csv'%gc.FACTORBASE_PATH, index_col=[0], parse_dates=[0])
        
        # roe = pd.read_csv('%s/PreprocessData/ROE.csv'%gc.FACTORBASE_PATH, index_col=[0], parse_dates=[0])
        
        #dep0.3,dy0.4,ep0.5,cp0.2,sp0.05,roe0.4
        f = (3*ep + 2*cp + 1*sp)/bp
        a = f
        a = a.loc[a.index >= self.start_date, :]
        a = a.loc[a.index <= self.end_date, :]
        self.factor = a

#%%
if __name__ == '__main__':
    #获取股票
    stocks = tools.get_stocks()
    
    a = F('F', stocks=stocks, start_date='20180101', end_date='20210506')
    
    a.generate_factor()
    
    a.factor_analysis()
    
