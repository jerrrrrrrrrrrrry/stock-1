# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 22:53:44 2021

@author: admin
"""

import pandas as pd
import pickle
import datetime
                
    
if __name__ == '__main__':
    today = datetime.datetime.today().strftime('%Y%m%d')
    with open('./pos.pkl', 'rb') as f:
        position = pickle.load(f)
    position = [str(s) for s in position]
    position = ['300' + s if len(s)==3 else '3000' + s if len(s)==2 else s for s in position]
    
    buy_list = ['000590', '603997', '002206', '300307', '002297',
                '688168', '002637', '603567', '300679']
    sell_list= ['002443', '600323', '600742', '603606', '000898',
                '603609', '603063', '002025', '002067', '603686']
    
    position.extend(buy_list)
    position = list(set(position) - set(sell_list))
    with open('./pos.pkl', 'wb') as f:
        pickle.dump(position, f)
    with open('./pos%s.pkl'%today, 'wb') as f:
        pickle.dump(position, f)
    position = [str(s) for s in position]
    position = ['300' + s if len(s)==3 else '3000' + s if len(s)==2 else s for s in position]
    
    position = [s+'.SH' if s[0]=='6' else s+'.SZ' for s in position]
    pd.set_option('display.max_row', None)
    position.sort()
    print(position)
    print(len(position))
    
    date = today
    date = '20210514'
    r_hat = pd.read_csv('../Results/r_hat.csv', index_col=[0], parse_dates=[0])
    
    na_mask = pd.read_csv('../../LabelBase/Data/na_mask.csv', index_col=[0], parse_dates=[0]).loc[date, :]
    
    rank = r_hat.loc[date, :].rank().loc[position].sort_values(ascending=False)
    # print(rank)
    for stock in rank.index:
        print(stock, rank.loc[stock], na_mask.loc[stock])
    print('---%s---'%rank.name)
    r_hat_rank = r_hat.loc[date, :].rank().sort_values(ascending=False)
    n = 10
    for i in r_hat_rank.index:
        if n == 0:
            break
        # print(i)
        # print(i not in position)
        # print(not na_mask.loc[i])
        
        # print(i not in position and  not na_mask.loc[i])
        
        if i not in position and not na_mask.loc[i]:
            print(i, r_hat_rank.loc[i])
            n = n - 1
