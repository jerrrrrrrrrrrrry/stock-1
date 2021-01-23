import time
import datetime
import os
import sys
import numpy as np
import pandas as pd
from pandas import Series, DataFrame
sys.path.append('../../Codes')
import tools


def main(stocks=None, args=[1, 2, 3, 4, 5]):
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
    no_liquid = (AMOUNT.lt(AMOUNT.rolling(20).mean().quantile(0.00, axis=1), axis=0)).shift()
    
    tingpai = (CLOSE == np.nan) | (AMOUNT == 0)
    
    CLOSE = (np.log(CLOSE * ADJ)).fillna(method='ffill')
    OPEN = (np.log(OPEN * ADJ)).fillna(value=CLOSE)
    HIGH = (np.log(HIGH * ADJ)).fillna(value=CLOSE)
    LOW = (np.log(LOW * ADJ)).fillna(value=CLOSE)
    
    
    yiziban = (HIGH == LOW) & (HIGH > CLOSE.shift())
    
    y1 = OPEN.shift(-2) - OPEN.shift(-1)
    y2 = OPEN.shift(-3) - OPEN.shift(-2)
    y3 = OPEN.shift(-4) - OPEN.shift(-3)
    y4 = OPEN.shift(-5) - OPEN.shift(-4)
    y5 = OPEN.shift(-6) - OPEN.shift(-5)
    
    def list_n_na(s, n):
        for i in range(n):
            s.loc[s.first_valid_index()] = np.nan
        return s
    y1 = y1.apply(func=list_n_na, args=(20,), axis=0, result_type='expand')
    y2 = y2.apply(func=list_n_na, args=(20,), axis=0, result_type='expand')
    y3 = y3.apply(func=list_n_na, args=(20,), axis=0, result_type='expand')
    y4 = y4.apply(func=list_n_na, args=(20,), axis=0, result_type='expand')
    y5 = y5.apply(func=list_n_na, args=(20,), axis=0, result_type='expand')
    y1[st|no_liquid|yiziban|tingpai] = np.nan
    y2[st|no_liquid|yiziban|tingpai] = np.nan
    y3[st|no_liquid|yiziban|tingpai] = np.nan
    y4[st|no_liquid|yiziban|tingpai] = np.nan
    y5[st|no_liquid|yiziban|tingpai] = np.nan
    
    y1.to_csv('../Data/y1.csv')
    y2.to_csv('../Data/y2.csv')
    y3.to_csv('../Data/y3.csv')
    y4.to_csv('../Data/y4.csv')
    y5.to_csv('../Data/y5.csv')


if __name__ == '__main__':
    main()