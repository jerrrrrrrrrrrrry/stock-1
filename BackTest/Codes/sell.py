# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 22:53:44 2021

@author: admin
"""

import pandas as pd
import pickle
import datetime
def main():
    today = datetime.datetime.today().strftime('%Y%m%d')
    with open('./pos.pkl', 'rb') as f:
        position = pickle.load(f)
    position = [str(s) for s in position]
    position = ['300' + s if len(s)==3 else '3000' + s if len(s)==2 else s for s in position]
    
    buy_list = ['603488', '000401', '603339', '300190', '600987',
                '000690', '002217', '002277', '300034', '600345']
    sell_list= ['601169', '002546', '600688', '600583', '603111',
                '300393', '300095', '002538', '000716', ]
    
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
    date = '20210407'
    r_hat = pd.read_csv('../Results/r_hat.csv', index_col=[0], parse_dates=[0])
    
    rank = r_hat.loc[date, :].rank().loc[position].sort_values(ascending=False)
    print(rank)
    print('------')
    na_mask = pd.read_csv('../../LabelBase/Data/na_mask.csv', index_col=[0], parse_dates=[0]).loc[date, :]
    
    r_hat_rank = r_hat.loc[date, :].rank().sort_values(ascending=False)
    n = 10
    for i in r_hat_rank.index:
        if n == 0:
            break
        if i not in position and  not na_mask.loc[i]:
            print(i, r_hat_rank.loc[i])
            n = n - 1
                
    
if __name__ == '__main__':
    main()