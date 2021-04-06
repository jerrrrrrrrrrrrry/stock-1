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
    
    
    stocks_2 = os.listdir('../../DataBase/StockTradingDerivativeData/Stock/')
    stocks_2 = [stock[:-4] for stock in stocks_2]
    stocks_2 = list(set(stocks).intersection(set(stocks_2)))
    
    mc = pd.read_csv('%s/Data/MC.csv'%(gc.FACTORBASE_PATH), index_col=[0], parse_dates=[0])
    # stocks = list(mc.columns)
    # industrys = tools.get_industrys('L1', stocks)
    # mc = tools.standardize_industry(mc, industrys)
    mc = tools.standardize(mc)
    MC = DataFrame(index=OPEN.index, columns=OPEN.columns)
    MC.loc[:,:] = mc
    
    ep = pd.read_csv('%s/Data/EP.csv'%gc.FACTORBASE_PATH, index_col=[0], parse_dates=[0])
    stocks = list(ep.columns)
    industrys = tools.get_industrys('L1', stocks)
    ep = tools.standardize_industry(ep, industrys)
    EP = DataFrame(index=OPEN.index, columns=OPEN.columns)
    EP.loc[:,:] = ep
    
    eps = pd.read_csv('%s/Data/EPS.csv'%gc.FACTORBASE_PATH, index_col=[0], parse_dates=[0])
    stocks = list(eps.columns)
    industrys = tools.get_industrys('L1', stocks)
    eps = tools.standardize_industry(eps, industrys)
    EPS = DataFrame(index=OPEN.index, columns=OPEN.columns)
    EPS.loc[:,:] = eps
    
    bp = pd.read_csv('%s/Data/BP.csv'%gc.FACTORBASE_PATH, index_col=[0], parse_dates=[0])
    stocks = list(bp.columns)
    industrys = tools.get_industrys('L1', stocks)
    bp = tools.standardize_industry(bp, industrys)
    BP = DataFrame(index=OPEN.index, columns=OPEN.columns)
    BP.loc[:,:] = bp
    
    dep = pd.read_csv('%s/Data/DEP.csv'%gc.FACTORBASE_PATH, index_col=[0], parse_dates=[0])
    stocks = list(dep.columns)
    industrys = tools.get_industrys('L1', stocks)
    dep = tools.standardize_industry(dep, industrys)
    DEP = DataFrame(index=OPEN.index, columns=OPEN.columns)
    DEP.loc[:,:] = dep
    
    roe = pd.read_csv('%s/Data/ROE.csv'%gc.FACTORBASE_PATH, index_col=[0], parse_dates=[0])
    stocks = list(roe.columns)
    industrys = tools.get_industrys('L1', stocks)
    roe = tools.standardize_industry(roe, industrys)
    ROE = DataFrame(index=OPEN.index, columns=OPEN.columns)
    ROE.loc[:,:] = roe
    
    
    st = st.shift()
    
    qt = 0.75
    
    f = EP + DEP + BP + ROE
    
    low_f = (f.lt(f.ewm(halflife=20).mean().quantile(qt, 1), 0)).shift()
    
    low_liquid = (AMOUNT.lt(AMOUNT.ewm(halflife=20).mean().quantile(0.1, 1), 0)).shift()
    low_price = CLOSE.le(1, 0).shift()
    low_mc = (MC.lt(MC.ewm(halflife=20).mean().quantile(0.1, 1), 0)).shift()
    
    # low_ep = (EP.lt(EP.ewm(halflife=20).mean().quantile(qt, 1), 0)).shift()
    # low_eps = (EPS.lt(EPS.ewm(halflife=20).mean().quantile(qt, 1), 0)).shift()
    # low_dep = (DEP.lt(DEP.ewm(halflife=20).mean().quantile(qt, 1), 0)).shift()
    # low_bp = (BP.lt(BP.ewm(halflife=20).mean().quantile(qt, 1), 0)).shift()
    # low_roe = (ROE.lt(ROE.ewm(halflife=20).mean().quantile(qt, 1), 0)).shift()
    
    blacklist = low_liquid|low_price|low_mc|low_f
    # blacklist = low_price|low_mc
    
    tingpai = (CLOSE == np.nan) | (AMOUNT == 0)
    
    CLOSE = (np.log(CLOSE * ADJ)).fillna(method='ffill')
    OPEN = (np.log(OPEN * ADJ)).fillna(value=CLOSE)
    HIGH = (np.log(HIGH * ADJ)).fillna(value=CLOSE)
    LOW = (np.log(LOW * ADJ)).fillna(value=CLOSE)
    
    
    yiziban = (HIGH == LOW) & (HIGH > CLOSE.shift())
    
    r = CLOSE.shift(-1) - CLOSE
    r_jiaoyi = OPEN.shift(-2) - OPEN.shift(-1)
    r_rinei = CLOSE.shift(-1) - OPEN.shift(-1)
    r_geye = OPEN.shift(-1) - CLOSE
    
    turn_rate = 0.2
    n = 5
    measure = np.array([(1-turn_rate)**i for i in range(n)])
    
    # y = DataFrame(0, index=r_jiaoyi.index, columns=r_jiaoyi.columns)
    # for i in range(n):
    #     y = y + measure[i] * r_jiaoyi.rolling(1+i).sum().shift(-i)
    y = OPEN.shift(-n-1) - OPEN.shift(-1)
    def list_n_na(s, n):
        if s.notna().any():
            ind = np.where(s.notna())[0][0]
            ind_end = min(ind + n, len(s))
            s.iloc[ind:ind_end] = np.nan
        
        # for i in range(n):
        #     s.loc[s.first_valid_index()] = np.nan
        return s
    n = 60
    r = r.apply(func=list_n_na, args=(n,), axis=0, result_type='expand')
    r_jiaoyi[r.isna()] = np.nan
    r_rinei[r.isna()] = np.nan
    r_geye[r.isna()] = np.nan
    y[r.isna()] = np.nan
    
    
    
    
    na_mask = st|yiziban|tingpai|blacklist
    
    y[na_mask] = np.nan
    r_jiaoyi[na_mask] = np.nan
    r[na_mask] = np.nan
    r_rinei[na_mask] = np.nan
    r_geye[na_mask] = np.nan
    
    print(r_jiaoyi.mean(1).sum())
    r_jiaoyi.mean(1).cumsum().plot()
    
    na_mask.to_csv('../Data/na_mask.csv')
    y.to_csv('../Data/y.csv')
    r.to_csv('../Data/r.csv')
    r_rinei.to_csv('../Data/r_rinei.csv')
    r_geye.to_csv('../Data/r_geye.csv')
    r_jiaoyi.to_csv('../Data/r_jiaoyi.csv')
    
