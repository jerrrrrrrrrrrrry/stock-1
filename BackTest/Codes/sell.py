# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 22:53:44 2021

@author: admin
"""

import pandas as pd

def main():
    position = [26]
    position.extend([147, 154, 184, 193, 300393])
    position.extend([209, 230, 246, 259, 284])
    position.extend([306, 308, 349, 360, 371, 375, 394, 396])
    position.extend([423, 427, 462])
    position.extend([547, 580])
    position.extend([660, 684])
    position.extend([709, 735, 739])
    position.extend(['002726', '002661', 601186, 603887,  600260, '002869', '002441', 603301, 603920, 600580, 603985])
    
    position = [str(s) for s in position]
    position = ['300' + s if len(s)==3 else '3000' + s if len(s)==2 else s for s in position]
    
    position = [s+'.SH' if s[0]=='6' else s+'.SZ' for s in position]
    print(position)
    print(len(position))
    date =  '20210318'
    r_hat = pd.read_csv('../Results/r_hat.csv', index_col=[0], parse_dates=[0])
    
    rank = r_hat.loc[date, :].rank().loc[position].sort_values(ascending=False)
    print(rank)
    
if __name__ == '__main__':
    main()