
import datetime
import os
import sys
import pickle
from scipy.stats import rankdata
import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import matplotlib.pyplot as plt
import tushare as ts
import tools
import Global_Config as gc

class SingleFactor:
    def __init__(self, factor_name, stocks=None, start_date=None, end_date=None):
        self.factor_name = factor_name
        self.stocks = stocks
        self.start_date = start_date
        self.end_date = end_date
        
        self.factor = None
        
        
    def generate_factor(self):
        self.factor = None
        
    def inf_to_nan(self, factor):
        factor[factor==np.inf] = np.nan
        factor[factor==-np.inf] = np.nan
        return factor
    
    def factor_analysis(self, industry_neutral=True, size_neutral=True, num_group=10):
        self.factor = self.inf_to_nan(self.factor)
        stocks = self.stocks
        start_date = self.start_date
        end_date = self.end_date
        y = pd.read_csv('%s/Data/y.csv'%gc.LABELBASE_PATH, index_col=[0], parse_dates=[0]).loc[:, stocks]
        if start_date:
            y = y.loc[y.index >= start_date, :]
        
        if end_date:
            y = y.loc[y.index <= end_date, :]
        
        ys = [y.shift(-n) for n in range(10)]
        
        if not os.path.exists('%s/Results/%s'%(gc.SINGLEFACTOR_PATH, self.factor_name)):
            os.mkdir('%s/Results/%s'%(gc.SINGLEFACTOR_PATH, self.factor_name))
        if isinstance(self.factor.index[0], type(y.index[0])):
            self.factor = self.factor.loc[y.index, :]
        else:
            ind = [i.strftime('%Y%m%d') for i in y.index]
            ind = list(filter(lambda x:x in self.factor.index, ind))
            self.factor = self.factor.loc[ind, :]
        factor = self.factor.copy()
        #行业中性
        if industry_neutral:
            industrys = tools.get_industrys('L1', self.stocks)
            tmp = {}
            for k in industrys.keys():
                if len(industrys[k]) > 0:
                    tmp[k] = industrys[k]
            industrys = tmp
            factor = tools.standardize_industry(self.factor, industrys)
            self.factor_industry_neutral = factor.copy()
        
        #市值中性
        if size_neutral:
            market_capitalization = DataFrame({stock: pd.read_csv('%s/StockTradingDerivativeData/Stock/%s.csv'%(gc.DATABASE_PATH, stock), index_col=[0], parse_dates=[0]).loc[:, 'TOTMKTCAP'] for stock in self.stocks})
            market_capitalization = np.log(market_capitalization)
            if self.start_date:
                market_capitalization = market_capitalization.loc[market_capitalization.index >= self.start_date, :]
            if self.end_date:
                market_capitalization = market_capitalization.loc[market_capitalization.index <= self.end_date, :]
            if industry_neutral:
                market_capitalization = tools.standardize_industry(market_capitalization, industrys)
            beta = (factor * market_capitalization).sum(1) / (market_capitalization * market_capitalization).sum(1)
            factor = factor - market_capitalization.mul(beta, axis=0)
            self.factor_industry_size_neutral = factor.copy()
        
        # self.factor_industry_neutral.fillna(0, inplace=True)
        # self.factor_industry_size_neutral.fillna(0, inplace=True)
        # factor.fillna(0, inplace=True)
        #因子分布
        plt.figure(figsize=(16,12))
        plt.hist(factor.fillna(0).values.flatten())
        plt.savefig('%s/Results/%s/hist.png'%(gc.SINGLEFACTOR_PATH, self.factor_name))
        
        #IC、IR、分组回测
        #ys = [y1, y2, y3, y4]
        IC = {}
        IR = {}
        group_backtest = {}
        group_pos = {}
        
        for i in range(len(ys)):
            if industry_neutral:
                y_neutral = tools.standardize_industry(ys[i], industrys)
            else:
                y_neutral = ys[i].copy()
            if size_neutral:
                y_neutral = y_neutral - market_capitalization.mul((y_neutral * market_capitalization).sum(1) / (market_capitalization * market_capitalization).sum(1), axis=0)
            if not (industry_neutral or size_neutral):
                y_neutral = ys[i].copy()
            IC[i] = (y_neutral * factor).mean(1) / factor.std(1) / y_neutral.std(1)
            IR[i] = IC[i].rolling(20).mean() / IC[i].rolling(20).std()
            factor_quantile = DataFrame(rankdata(factor, axis=1), index=factor.index, columns=factor.columns).div(factor.notna().sum(1), axis=0)# / len(factor.columns)
            factor_quantile[factor.isna()] = np.nan
            group_backtest[i] = {}
            group_pos[i] = {}
            for n in range(num_group):
                group_pos[i][n] = DataFrame((n/num_group <= factor_quantile) & (factor_quantile <= (n+1)/num_group))
                group_pos[i][n][~group_pos[i][n]] = np.nan
                group_pos[i][n] = 1 * group_pos[i][n]
                group_backtest[i][n] = ((group_pos[i][n] * ys[i]).mean(1) - ys[i].mean(1)).cumsum().rename('%s'%(n/num_group))
        self.IC = IC
        self.IR = IR
        self.group_pos = group_pos
        self.group_backtest = group_backtest
        
        plt.figure(figsize=(16,12))
        for i in range(len(ys)):
            IC[i].cumsum().plot()
        plt.legend(['%s'%i for i in range(len(ys))])
        plt.savefig('%s/Results/%s/IC.png'%(gc.SINGLEFACTOR_PATH, self.factor_name))
        
        plt.figure(figsize=(16,12))
        for i in range(len(ys)):
            IR[i].cumsum().plot()
        plt.legend(['%s'%i for i in range(len(ys))])
        plt.savefig('%s/Results/%s/IR.png'%(gc.SINGLEFACTOR_PATH, self.factor_name))
        
        for i in range(len(ys)):
            plt.figure(figsize=(16,12))
            for n in range(num_group):
                group_backtest[i][n].plot()
            plt.legend(['%s'%i for i in range(num_group)])
            plt.savefig('%s/Results/%s/groupbacktest%s.png'%(gc.SINGLEFACTOR_PATH, self.factor_name, i))
        
            
    def update_factor(self):
        self.generate_factor()
        self.factor = self.inf_to_nan(self.factor)
        #if 'industry' in self.neutral_list:
        if True:
            industrys = tools.get_industrys('L1', self.stocks)
            tmp = {}
            for k in industrys.keys():
                if len(industrys[k]) > 0:
                    tmp[k] = industrys[k]
            industrys = tmp
            factor = tools.standardize_industry(self.factor, industrys)
        #if 'market_capitalization' in self.neutral_list:
        if True:
            market_capitalization = DataFrame({stock: pd.read_csv('%s/StockTradingDerivativeData/Stock/%s.csv'%(gc.DATABASE_PATH, stock), index_col=[0], parse_dates=[0]).loc[:, 'TOTMKTCAP'] for stock in self.stocks})
            market_capitalization = np.log(market_capitalization)
            if self.start_date:
                market_capitalization = market_capitalization.loc[market_capitalization.index >= self.start_date, :]
            if self.end_date:
                market_capitalization = market_capitalization.loc[market_capitalization.index <= self.end_date, :]
            #if 'industry' in self.neutral_list:
            if True:
                market_capitalization = tools.standardize_industry(market_capitalization, industrys)
            beta = (factor * market_capitalization).sum(1) / (market_capitalization * market_capitalization).sum(1)
            factor = factor - market_capitalization.mul(beta, axis=0)
        # factor.fillna(0, inplace=True)
        if os.path.exists('%s/Data/%s.csv'%(gc.FACTORBASE_PATH, self.factor_name)):
            if isinstance(factor.index[0], str):
                factor_old = pd.read_csv('%s/Data/%s.csv'%(gc.FACTORBASE_PATH, self.factor_name), index_col=[0])
            else:
                factor_old = pd.read_csv('%s/Data/%s.csv'%(gc.FACTORBASE_PATH, self.factor_name), index_col=[0], parse_dates=[0])
            factor = pd.concat([factor_old, factor.loc[factor.index>factor_old.index[-1], :]], axis=0)
            factor.sort_index(axis=0, inplace=True)
        factor.sort_index(axis=1, inplace=True)
        factor.to_csv('%s/Data/%s.csv'%(gc.FACTORBASE_PATH, self.factor_name))