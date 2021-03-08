# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 22:53:44 2021

@author: admin
"""

import numpy as np
import pandas as pd
import datetime

def main():
    position = ['016', '034', '047', '068', 146, 147, 184, 193, 246, 259, 280, 284, 306, 308, 320, 375, 394, 395, 396, 423, 427, 463, 511, 547, 562, 575, 580, 660, 684, 709, 732, 735, 739, 766, 767, 829]

    position = ['300'+str(s)+'.SZ' for s in position]
    print(position)
    print(len(position))
    date =  '20210308'
    r_hat = pd.read_csv('../Results/r_hat.csv', index_col=[0], parse_dates=[0])
    
    rank = r_hat.loc[date, :].rank().loc[position].sort_values(ascending=False)
    print(rank)
    
if __name__ == '__main__':
    main()