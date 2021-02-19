# -*- coding: utf-8 -*-
"""
Created on Fri Feb 19 19:51:46 2021

@author: admin
"""

import os
import sys
import pandas as pd
from pandas import Series, DataFrame

def main(date):
    d = '../FactorBase/Data/'
    files = os.listdir(d)
    for file in files:
        data = pd.read_csv('%s/%s'%(d, file), index_col=[0], parse_dates=[0])
        data = data.loc[data.index != date, :]
        data.to_csv('%s/%s'%(d, file))

if __name__ == '__main__':
    date = '20210218'
    main(date)