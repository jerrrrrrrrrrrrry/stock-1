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
from MultiFactor import MultiFactor
import Global_Config as gc
import tools



#%%

class Reversal(MultiFactor):
    def set_factor(self):
        self.factor_list = ['Alpha', 'Bias', 'Donchian', 'Momentum', 'Sharpe', 'TSRegBeta']
        self.method = 'pca_0'

#%%
if __name__ == '__main__':
    #获取股票
    stocks = tools.get_stocks()
    
    a = Reversal('Reversal', stocks, start_date='20200101', end_date='20201225')
    
    a.set_factor()
    
    a.get_factor()
    
    a.multi_analysis()
    
    a.combine_factor()
    
    a.factor_analysis()
    
