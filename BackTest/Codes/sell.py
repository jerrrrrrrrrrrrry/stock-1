# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 22:53:44 2021

@author: admin
"""

import numpy as np
import pandas as pd
import datetime

def main():
    position = ['049', '074', '094', 106, 163, 169, 184, 194, 221, 281, 289, 301, 312, 326, 375, 405, 424, 437, 462, 489, 506, 611, 736, 742, 859]
    position = ['300'+str(s)+'.SZ' for s in position]
    date =  '20210225'
    r_hat = pd.read_csv('../Results/r_hat.csv', index_col=[0], parse_dates=[0])
    
    rank = r_hat.loc[date, :].rank().loc[position].sort_values(ascending=False)
    print(rank)
    
if __name__ == '__main__':
    main()