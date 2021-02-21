import time
import datetime
import os
import sys
import numpy as np
import pandas as pd
from pandas import Series, DataFrame
sys.path.append('../../Codes')
import tools


def main(stocks=None):
    if stocks == None:
        stocks = tools.get_stocks()
    data = {stock: pd.read_csv('../../DataBase/StockDailyData/Stock/%s.csv'%stock, index_col=[0], parse_dates=[0]) for stock in stocks}
    
    OPEN = DataFrame({stock: data[stock].loc[:, 'open'] for stock in stocks})
    HIGH = DataFrame({stock: data[stock].loc[:, 'high'] for stock in stocks})
    LOW = DataFrame({stock: data[stock].loc[:, 'low'] for stock in stocks})
    CLOSE = DataFrame({stock: data[stock].loc[:, 'close'] for stock in stocks})
    ADJ = DataFrame({stock: data[stock].loc[:, 'adj_factor'] for stock in stocks})
    st = DataFrame({stock: data[stock].loc[:, 'st'] for stock in stocks})
    AMOUNT = DataFrame({stock: data[stock].loc[:, 'amount'] for stock in stocks})
    
    st = st.shift()
    no_liquid = (AMOUNT.lt(AMOUNT.ewm(halflife=20).mean().quantile(0.05, axis=1), axis=0)).shift()
    
    tingpai = (CLOSE == np.nan) | (AMOUNT == 0)
    
    CLOSE = (np.log(CLOSE * ADJ)).fillna(method='ffill')
    OPEN = (np.log(OPEN * ADJ)).fillna(value=CLOSE)
    HIGH = (np.log(HIGH * ADJ)).fillna(value=CLOSE)
    LOW = (np.log(LOW * ADJ)).fillna(value=CLOSE)
    
    
    yiziban = (HIGH == LOW) & (HIGH > CLOSE.shift())
    
    y = OPEN.shift(-2) - OPEN.shift(-1)
    r = OPEN.shift(-2) - OPEN.shift(-1)
    def list_n_na(s, n):
        for i in range(n):
            s.loc[s.first_valid_index()] = np.nan
        return s
    n = 20
    y = y.apply(func=list_n_na, args=(n,), axis=0, result_type='expand')
    
    y[st|no_liquid|yiziban|tingpai] = np.nan
    
    y.to_csv('../Data/y.csv')
    r.to_csv('../Data/r.csv')
    

if __name__ == '__main__':
    main()