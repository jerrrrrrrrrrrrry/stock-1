# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 22:53:44 2021

@author: admin
"""

import numpy as np
import pandas as pd
import datetime

def main():
    position = [300278, '300049', 300071, 300094, 300106, 300108, 300146, 300193, 300194, 300221, 300289, 300301, 300312, 300405, 300424, 300489, 300506, 300654, 300660, 300736, 300742]
    position = [str(s)+'.SZ' for s in position]
    date =  '20210224'
    r_hat = pd.read_csv('../Results/r_hat.csv', index_col=[0], parse_dates=[0])
    
    rank = r_hat.loc[date, :].rank().loc[position].sort_values(ascending=False)
    print(rank)
    
if __name__ == '__main__':
    main()