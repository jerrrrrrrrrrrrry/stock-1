# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 23:38:30 2021

@author: admin
"""
import os
import sys
import datetime
import Config
sys.path.append(Config.GLOBALCONFIG_PATH)

import Global_Config as gc

import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import statsmodels.tsa.api as tsa
import statsmodels.api as sm
import matplotlib.pyplot as plt

if __name__ == '__main__':
    IC = pd.read_csv('../Results/IC.csv', index_col=[0], parse_dates=[0])
    factor = IC.loc[:, 'Beta']
    factor.plot()
    sm.graphics.tsa.plot_pacf(factor.dropna(), lags=20)
