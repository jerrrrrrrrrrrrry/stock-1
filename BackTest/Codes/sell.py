# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 22:53:44 2021

@author: admin
"""

import numpy as np
import pandas as pd
import datetime

def main():
    position = [16, 34, 47, 68, 88, 92]
    position.extend([147, 154, 184, 193])
    position.extend([246, 259, 284])
    position.extend([306, 308, 320, 371, 375, 394, 395, 396])
    position.extend([423, 427, 462, 463])
    position.extend([511, 547, 575, 580])
    position.extend([625, 660, 684])
    position.extend([709, 732, 735, 739, 766, 767, 829])

    position = [str(s) for s in position]
    position = ['300' + s + '.SZ' if len(s)==3 else '3000' + s + '.SZ'  for s in position]
    
    print(position)
    print(len(position))
    date =  '20210310'
    r_hat = pd.read_csv('../Results/r_hat.csv', index_col=[0], parse_dates=[0])
    
    rank = r_hat.loc[date, :].rank().loc[position].sort_values(ascending=False)
    print(rank)
    
if __name__ == '__main__':
    main()