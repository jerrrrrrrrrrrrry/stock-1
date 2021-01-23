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

class Value(MultiFactor):
    def set_factor(self):
        self.factor_list = ['BP', 'CP', 'EP', 'SP']
        self.method = 'ew'
        self.quantile_nl = None

#%%
if __name__ == '__main__':
    #获取股票
    stocks = tools.get_stocks()
    
    a = Value('Value', stocks, start_date='20200101', end_date='20201231')
    
    a.set_factor()
    
    a.get_factor()
    
    a.multi_analysis()
    
    a.combine_factor()
    
    a.factor_analysis()
    
