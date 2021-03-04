# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 22:53:44 2021

@author: admin
"""

import numpy as np
import pandas as pd
import datetime

def main():
    position = ['034', '068', 115, 146, 147, 184, 192, 246, 280, 284, 306, 308, 375, 378, 394, 395, 427, 449, 462, 463, 511, 562, 575, 603, 684, 735, 739, 766, 767, 829]

    position = ['300'+str(s)+'.SZ' for s in position]
    print(position)
    print(len(position))
    date =  '20210304'
    r_hat = pd.read_csv('../Results/r_hat.csv', index_col=[0], parse_dates=[0])
    
    rank = r_hat.loc[date, :].rank().loc[position].sort_values(ascending=False)
    print(rank)
    
if __name__ == '__main__':
    main()