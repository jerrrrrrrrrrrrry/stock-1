import time
import datetime
import os
import sys
import numpy as np
import pandas as pd
from pandas import Series, DataFrame
sys.path.append('../../Codes')
import Config
sys.path.append(Config.GLOBALCONFIG_PATH)

import Global_Config as gc
import tools


if __name__ == '__main__':
    stocks = os.listdir('../../DataBase/StockDailyData/Stock/')
    stocks = [stock[:-4] for stock in stocks]
    data = {stock: pd.read_csv('../../DataBase/StockDailyData/Stock/%s.csv'%stock, index_col=[0], parse_dates=[0]) for stock in stocks}
    
    OPEN = DataFrame({stock: data[stock].loc[:, 'open'] for stock in stocks})
    HIGH = DataFrame({stock: data[stock].loc[:, 'high'] for stock in stocks})
    LOW = DataFrame({stock: data[stock].loc[:, 'low'] for stock in stocks})
    CLOSE = DataFrame({stock: data[stock].loc[:, 'close'] for stock in stocks})
    ADJ = DataFrame({stock: data[stock].loc[:, 'adj_factor'] for stock in stocks})
    st = DataFrame({stock: data[stock].loc[:, 'st'] for stock in stocks})
    AMOUNT = DataFrame({stock: data[stock].loc[:, 'amount'] for stock in stocks})
    
    # mc = pd.read_csv('%s/PreprocessData/MC.csv'%(gc.FACTORBASE_PATH), index_col=[0], parse_dates=[0])
    # MC = DataFrame(index=OPEN.index, columns=OPEN.columns)
    # MC.loc[:,:] = mc
    
    bp = pd.read_csv('%s/PreprocessData/BP.csv'%gc.FACTORBASE_PATH, index_col=[0], parse_dates=[0])
    BP = DataFrame(index=OPEN.index, columns=OPEN.columns)
    BP.loc[:,:] = bp
    
    ep = pd.read_csv('%s/PreprocessData/EP.csv'%gc.FACTORBASE_PATH, index_col=[0], parse_dates=[0])
    EP = DataFrame(index=OPEN.index, columns=OPEN.columns)
    EP.loc[:,:] = ep
    
    cp = pd.read_csv('%s/PreprocessData/CP.csv'%gc.FACTORBASE_PATH, index_col=[0], parse_dates=[0])
    CP = DataFrame(index=OPEN.index, columns=OPEN.columns)
    CP.loc[:,:] = cp
    
    sp = pd.read_csv('%s/PreprocessData/SP.csv'%gc.FACTORBASE_PATH, index_col=[0], parse_dates=[0])
    SP = DataFrame(index=OPEN.index, columns=OPEN.columns)
    SP.loc[:,:] = sp
    
    dy = pd.read_csv('%s/PreprocessData/DY.csv'%gc.FACTORBASE_PATH, index_col=[0], parse_dates=[0])
    DY = DataFrame(index=OPEN.index, columns=OPEN.columns)
    DY.loc[:,:] = dy
    
    # eps = pd.read_csv('%s/PreprocessData/EPS.csv'%gc.FACTORBASE_PATH, index_col=[0], parse_dates=[0])
    # EPS = DataFrame(index=OPEN.index, columns=OPEN.columns)
    # EPS.loc[:,:] = eps
    
    dep = pd.read_csv('%s/PreprocessData/DEP.csv'%gc.FACTORBASE_PATH, index_col=[0], parse_dates=[0])
    DEP = DataFrame(index=OPEN.index, columns=OPEN.columns)
    DEP.loc[:,:] = dep
    
    roe = pd.read_csv('%s/PreprocessData/ROE.csv'%gc.FACTORBASE_PATH, index_col=[0], parse_dates=[0])
    ROE = DataFrame(index=OPEN.index, columns=OPEN.columns)
    ROE.loc[:,:] = roe
    
    # droe = roe.diff(60)
    # DROE = DataFrame(index=OPEN.index, columns=OPEN.columns)
    # DROE.loc[:,:] = droe
    
    qt = 0.75
    #dep0.3,dy0.4,ep0.5,cp0.2,sp0.05,roe0.4
    f = 4*BP + 5*EP + 5*CP + 1*SP + 1*DY + 5*DEP + 6*ROE
    # ic = f.corrwith(y, axis=1)
    # print(ic.sum()/ic.std())
    # f.corrwith(y, axis=1).cumsum().plot()
    
    low_f = f.lt(f.quantile(qt, 1), 0)
    
    low_liquid = AMOUNT.lt(AMOUNT.ewm(halflife=60).mean().quantile(0.1, 1), 0)
    
    low_price = CLOSE.le(1, 0)
    
    # low_bp = BP.lt(BP.ewm(halflife=20).mean().quantile(0.7, 1), 0)
    
    # blacklist = low_f|low_liquid|low_price|low_bp|low_mc
    blacklist = low_f|low_liquid|low_price
    
    tingpai = (CLOSE.shift(-1) == np.nan) | (AMOUNT.shift(-1) == 0)
    
    CLOSE = (np.log(CLOSE * ADJ)).fillna(method='ffill')
    OPEN = (np.log(OPEN * ADJ)).fillna(value=CLOSE)
    HIGH = (np.log(HIGH * ADJ)).fillna(value=CLOSE)
    LOW = (np.log(LOW * ADJ)).fillna(value=CLOSE)
    
    
    yiziban = (HIGH.shift(-1) == LOW.shift(-1)) & (HIGH.shift(-1) > CLOSE)
    
    
    def list_n_na(s, n):
        if s.any():
            ind = np.where(s)[0][0]
            ind_end = min(ind + n, len(s))
            s.iloc[ind:ind_end] = False
        return s
    n = 60
    list_mask = CLOSE.fillna(method='ffill').fillna(0).astype('bool')
    list_mask = list_mask.apply(func=list_n_na, args=(n,), axis=0, result_type='expand')
    list_mask = (1 - list_mask).astype('bool')
    
    industrys = tools.get_industrys('L1', stocks)
    stocks_fina = []
    stocks_fina.extend(list(industrys['801230.SI']))
    stocks_fina.extend(list(industrys['801780.SI']))
    stocks_fina.extend(list(industrys['801790.SI']))
    
    na_mask = st|yiziban|tingpai|blacklist|list_mask
    na_mask.loc[:, stocks_fina] = True
    
    print((1-na_mask).sum(1))
    
    r = CLOSE.shift(-1) - CLOSE
    r_jiaoyi = OPEN.shift(-2) - OPEN.shift(-1)
    r_rinei = CLOSE.shift(-1) - OPEN.shift(-1)
    r_geye = OPEN.shift(-1) - CLOSE
    
    
    turn_rate = 0.2
    n = 5
    measure1 = np.array([(1 - turn_rate)**i for i in range(n)])
    measure2 = np.array([1 - i * turn_rate for i in range(n)])
    measure = 0*measure1 + measure2
    y = DataFrame(0, index=r_jiaoyi.index, columns=r_jiaoyi.columns)
    for i in range(n):
        y = y + measure[i] * r_jiaoyi.rolling(1+i).sum().shift(-i)
    # y = OPEN.shift(-n-1) - OPEN.shift(-1)
    
    industrys = tools.get_industrys('L1', list(y.columns))
    
    y_ind = DataFrame({ind:y.loc[:, industrys[ind]].mean(1) for ind in industrys.keys()})
    
    
    y[na_mask] = np.nan
    # r_jiaoyi[na_mask] = np.nan
    # r[na_mask] = np.nan
    # r_rinei[na_mask] = np.nan
    # r_geye[na_mask] = np.nan
    
    r_plot = r_jiaoyi.copy()
    r_plot[na_mask] = np.nan
    print(r_plot.mean(1).sum())
    r_plot.mean(1).cumsum().plot()
    
    f.to_csv('../Data/f.csv')
    low_f.to_csv('../Data/low_f.csv')
    low_liquid.to_csv('../Data/low_liquid.csv')
    low_price.to_csv('../Data/low_price.csv')
    st.to_csv('../Data/st.csv')
    yiziban.to_csv('../Data/yiziban.csv')
    tingpai.to_csv('../Data/tingpai.csv')
    blacklist.to_csv('../Data/blacklist.csv')
    list_mask.to_csv('../Data/list_mask.csv')
    na_mask.to_csv('../Data/na_mask.csv')
    y.to_csv('../Data/y.csv')
    y_ind.to_csv('../Data/y_ind.csv')
    r.to_csv('../Data/r.csv')
    r_rinei.to_csv('../Data/r_rinei.csv')
    r_geye.to_csv('../Data/r_geye.csv')
    r_jiaoyi.to_csv('../Data/r_jiaoyi.csv')
    
