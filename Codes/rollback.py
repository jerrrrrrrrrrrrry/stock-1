# -*- coding: utf-8 -*-
"""
Created on Fri Feb 19 19:51:46 2021

@author: admin
"""

import os
import sys
import datetime
import pandas as pd
from pandas import Series, DataFrame
import multiprocessing as mp

def f(file, date, d):
    data = pd.read_csv('%s/%s'%(d, file), index_col=[0], parse_dates=[0])
    data = data.loc[data.index != date, :]
    data.to_csv('%s/%s'%(d, file))

if __name__ == '__main__':
    if len(sys.argv) == 2:
        date = sys.argv[1]
    else:
        date = datetime.datetime.today().strftime('%Y%m%d')
    d = '../FactorBase/PreprocessData/'
    files = os.listdir(d)
    pool = mp.Pool(8)
    
    for file in files:
        pool.apply_async(func=f, args=(file, date, d))
    pool.close()
    pool.join()