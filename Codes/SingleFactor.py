
import datetime
import os
import sys
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
        r_jiaoyi = pd.read_csv('%s/Data/r_jiaoyi.csv'%gc.LABELBASE_PATH, index_col=[0], parse_dates=[0]).loc[:, stocks]
        
        if start_date:
            y = y.loc[y.index >= start_date, :]
            r_jiaoyi = r_jiaoyi.loc[r_jiaoyi.index >= start_date, :]
        
        if end_date:
            y = y.loc[y.index <= end_date, :]
            r_jiaoyi = r_jiaoyi.loc[r_jiaoyi.index <= end_date, :]
        
        ys = [y.shift(-n) for n in range(10)]
        
        if not os.path.exists('%s/Results/%s'%(gc.SINGLEFACTOR_PATH, self.factor_name)):
            os.mkdir('%s/Results/%s'%(gc.SINGLEFACTOR_PATH, self.factor_name))
        self.factor = self.factor.loc[y.index, :]
        factor = self.factor.copy()
        #行业中性
        if industry_neutral:
            industrys = tools.get_industrys('L1', self.stocks)
            factor = tools.standardize_industry(self.factor, industrys)
            self.factor_industry_neutral = factor.copy()
        else:
            factor = tools.standardize(self.factor)
            self.factor_industry_neutral = None
        #市值中性
        if size_neutral:
            market_capitalization = DataFrame({stock: pd.read_csv('%s/StockTradingDerivativeData/Stock/%s.csv'%(gc.DATABASE_PATH, stock), index_col=[0], parse_dates=[0]).loc[:, 'TOTMKTCAP'] for stock in self.stocks})
            market_capitalization = np.log(market_capitalization)
            if self.start_date:
                market_capitalization = market_capitalization.loc[market_capitalization.index >= self.start_date, :]
            if self.end_date:
                market_capitalization = market_capitalization.loc[market_capitalization.index <= self.end_date, :]
            market_capitalization = tools.standardize_industry(market_capitalization, industrys)
            beta = (factor * market_capitalization).sum(1) / (market_capitalization * market_capitalization).sum(1)
            factor = factor - market_capitalization.mul(beta, axis=0)
            self.factor_industry_size_neutral = factor.copy()
        
        #因子分布
        plt.figure(figsize=(16,12))
        plt.hist(factor.fillna(0).values.flatten())
        plt.savefig('%s/Results/%s/hist.png'%(gc.SINGLEFACTOR_PATH, self.factor_name))
        
        #IC、IR、分组回测
        #ys = [y1, y2, y3, y4]
        IC = {}
        IR = {}
        
        for i in range(len(ys)):
            if industry_neutral:
                y_neutral = tools.standardize_industry(ys[i], industrys)
            else:
                y_neutral = tools.standardize(ys[i])
            if size_neutral:
                y_neutral = y_neutral - market_capitalization.mul((y_neutral * market_capitalization).sum(1) / (market_capitalization * market_capitalization).sum(1), axis=0)

            IC[i] = (y_neutral * factor).mean(1) / factor.std(1) / y_neutral.std(1)
            IR[i] = IC[i].rolling(20).mean() / IC[i].rolling(20).std()
            factor_quantile = DataFrame(factor.rank(axis=1), index=factor.index, columns=factor.columns).div(factor.notna().sum(1), axis=0)# / len(factor.columns)
            factor_quantile[factor.isna()] = np.nan
            
            group_pos = {}
            for n in range(num_group):
                group_pos[n] = DataFrame((n/num_group <= factor_quantile) & (factor_quantile <= (n+1)/num_group))
                group_pos[n][~group_pos[n]] = np.nan
                group_pos[n] = 1 * group_pos[n]
            
            plt.figure(figsize=(16, 12))
            group_mean = {}
            for n in range(num_group):
                group_mean[n] = ((group_pos[n] * ys[i]).mean(1) - 1*ys[i].mean(1)).cumsum().rename('%s'%(n/num_group))
                group_mean[n].plot()
            plt.legend(['%s'%i for i in range(num_group)])
            plt.savefig('%s/Results/%s/group_mean%s.png'%(gc.SINGLEFACTOR_PATH, self.factor_name, i))
            plt.figure(figsize=(16, 12))
            group_hist = [group_mean[i].iloc[np.where(group_mean[i].notna())[0][-1]] for i in range(num_group)]
            plt.bar(range(num_group), group_hist)
            plt.savefig('%s/Results/%s/group_mean_hist%s.png'%(gc.SINGLEFACTOR_PATH, self.factor_name, i))
            
            plt.figure(figsize=(16, 12))
            group_std = {}
            for n in range(num_group):
                group_std[n] = (group_pos[n] * ys[i]).std(1).cumsum().rename('%s'%(n/num_group))
                group_std[n].plot()
            plt.legend(['%s'%i for i in range(num_group)])
            plt.savefig('%s/Results/%s/group_std%s.png'%(gc.SINGLEFACTOR_PATH, self.factor_name, i))
            plt.figure(figsize=(16, 12))
            group_hist = [group_std[i].iloc[np.where(group_std[i].notna())[0][-1]] for i in range(num_group)]
            plt.bar(range(num_group), group_hist)
            plt.savefig('%s/Results/%s/group_std_hist%s.png'%(gc.SINGLEFACTOR_PATH, self.factor_name, i))
            
            plt.figure(figsize=(16, 12))
            group_skew = {}
            for n in range(num_group):
                group_skew[n] = (group_pos[n] * ys[i]).skew(1).cumsum().rename('%s'%(n/num_group))
                group_skew[n].plot()
            plt.legend(['%s'%i for i in range(num_group)])
            plt.savefig('%s/Results/%s/group_skew%s.png'%(gc.SINGLEFACTOR_PATH, self.factor_name, i))
            plt.figure(figsize=(16, 12))
            group_hist = [group_skew[i].iloc[np.where(group_skew[i].notna())[0][-1]] for i in range(num_group)]
            plt.bar(range(num_group), group_hist)
            plt.savefig('%s/Results/%s/group_skew_hist%s.png'%(gc.SINGLEFACTOR_PATH, self.factor_name, i))
            
            plt.figure(figsize=(16, 12))
            group_kurt = {}
            for n in range(num_group):
                group_kurt[n] = (group_pos[n] * ys[i]).kurt(1).cumsum().rename('%s'%(n/num_group))
                group_kurt[n].plot()
            plt.legend(['%s'%i for i in range(num_group)])
            plt.savefig('%s/Results/%s/group_kurt%s.png'%(gc.SINGLEFACTOR_PATH, self.factor_name, i))
            plt.figure(figsize=(16, 12))
            group_hist = [group_kurt[i].iloc[np.where(group_kurt[i].notna())[0][-1]] for i in range(num_group)]
            plt.bar(range(num_group), group_hist)
            plt.savefig('%s/Results/%s/group_kurt_hist%s.png'%(gc.SINGLEFACTOR_PATH, self.factor_name, i))
        
        self.IC = IC
        self.IR = IR
        
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
        
            
    def update_factor(self):
        self.generate_factor()
        factor = self.inf_to_nan(self.factor)
        if os.path.exists('%s/Data/%s.csv'%(gc.FACTORBASE_PATH, self.factor_name)):
            # if isinstance(factor.index[0], str):
            #     factor_old = pd.read_csv('%s/Data/%s.csv'%(gc.FACTORBASE_PATH, self.factor_name), index_col=[0])
            #     factor_old.index = [str(i) for i in factor_old.index]
            # else:
            #     factor_old = pd.read_csv('%s/Data/%s.csv'%(gc.FACTORBASE_PATH, self.factor_name), index_col=[0], parse_dates=[0])
            factor_old = pd.read_csv('%s/Data/%s.csv'%(gc.FACTORBASE_PATH, self.factor_name), index_col=[0], parse_dates=[0])
            
            factor = pd.concat([factor_old.loc[factor_old.index<factor.index[0], :], factor], axis=0)
        factor.to_csv('%s/Data/%s.csv'%(gc.FACTORBASE_PATH, self.factor_name))