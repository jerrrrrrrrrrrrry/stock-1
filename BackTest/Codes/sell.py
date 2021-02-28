# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 22:53:44 2021

@author: admin
"""

import numpy as np
import pandas as pd
import datetime

def main():
    position = ['049', '074', '094', 106, 146, 147, 163, 184, 194, 246, 261, 280, 284, 326, 375, 395, 405, 424, 437, 462, 464, 511, 611, 653, 684, 735, 736, 739, 767, 875]
    
    position = ['300'+str(s)+'.SZ' for s in position]
    print(position)
    print(len(position))
    date =  '20210226'
    r_hat = pd.read_csv('../Results/r_hat.csv', index_col=[0], parse_dates=[0])
    
    rank = r_hat.loc[date, :].rank().loc[position].sort_values(ascending=False)
    print(rank)
    
if __name__ == '__main__':
    main()