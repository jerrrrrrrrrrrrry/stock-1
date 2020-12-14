#!/usr/bin/env python
# coding: utf-8

# In[1]:


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

sys.path.append('../Codes')
import tools
from SingleFactor import SingleFactor


# In[2]:


industry_list = ['801030.SI', '801080.SI', '801150.SI', '801730.SI', '801750.SI', '801760.SI', '801770.SI', '801890.SI']


# In[3]:


#获取股票
stocks = tools.get_stocks()
#获取行业
industrys = tools.get_industrys(level='L1', stocks=stocks)


# In[4]:


industrys = {k:industrys[k] for k in industry_list}
stocks = []
for v in industrys.values():
    stocks.extend(v)
stocks.sort()


# In[ ]:





# In[25]:


class A(SingleFactor):
    def generate_factor(self):
        CLOSE = DataFrame({stock:pd.read_csv('../../DataBase/StockDailyData/Stock/%s.csv'%stock, index_col=[0], parse_dates=[0]).loc[:, 'close'] for stock in stocks})
        ADJ = DataFrame({stock:pd.read_csv('../../DataBase/StockDailyData/Stock/%s.csv'%stock, index_col=[0], parse_dates=[0]).loc[:, 'adj_factor'] for stock in stocks})
        CLOSE = CLOSE * ADJ
        CLOSE = np.log(CLOSE)
        def reg_ts(df, n):
            x = np.arange(n)
            x = x - x.mean()
            b = df.rolling(n).apply(lambda y:(y*x).sum() / (x*x).sum(), raw=True)
            a = df.rolling(n).mean()
            y_hat = a + b * x[-1]
            e = df - y_hat

            return b, e
        n = 20
        b, e = reg_ts(CLOSE, n)
        a = e
        a = a.loc[a.index >= self.start_date, :]
        a = a.loc[a.index <= self.end_date, :]
        self.factor = a


# In[26]:


a = A('TSRegRes', stocks=stocks, start_date='20200101', end_date='20201010')


# In[27]:


a.generate_factor()


# In[28]:


a.factor_analysis()


# In[ ]:




