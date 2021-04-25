import os
import sys
import datetime
import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import Config
sys.path.append(Config.GLOBALCONFIG_PATH)
import tools
import Global_Config as gc

def neutral_apply(y, x_list):
    date = y.name
    X = DataFrame(index=y.index)
    for x in x_list:
        X = pd.concat([X, x.loc[date, :]], axis=1)
    X.fillna(0, inplace=True)
    # X = sm.add_constant(X)
    res = y - X.dot(np.linalg.inv(X.T.dot(X)).dot(X.T).dot(y.fillna(0)))
    return res

if __name__ == '__main__':
    #声明风险
    risk_list = ['MC', 'BP']
    no_neutral_list = ['MC', 'BP']
    ind_list = ['MomentumInd']
    #获取风险
    risk_dic = {risk:pd.read_csv('%s/Data/%s.csv'%(gc.FACTORBASE_PATH, risk), index_col=[0], parse_dates=[0]) for risk in risk_list}
    stocks = list(risk_dic['MC'].columns)
    industrys = tools.get_industrys('L1', stocks)
    for risk in risk_dic.keys():
        risk_dic[risk] = tools.standardize_industry(risk_dic[risk], industrys)
    risk_df_list = [risk_df for risk_df in risk_dic.values()]
    #获取因子
    factor_list = os.listdir('%s/Data'%gc.FACTORBASE_PATH)
    factor_list = list(filter(lambda x:x[0]>'9', factor_list))
    factor_list = [f.split('.')[0] for f in factor_list]
    #遍历因子
    for factor in factor_list:
        #读取并判断风险
        #作风险中性
        #写入
        factor_df = pd.read_csv('%s/Data/%s.csv'%(gc.FACTORBASE_PATH, factor), index_col=[0], parse_dates=[0])
        na_df = factor_df.isna()
        if factor in ind_list:
            factor_df = tools.standardize(factor_df)
        elif factor in no_neutral_list:
            factor_df = tools.standardize_industry(factor_df, industrys)
        else:
            factor_df = tools.standardize_industry(factor_df, industrys)
            # factor_df = DataFrame(factor_df, index=factor_df.index, columns=stocks)
            factor_df = factor_df.apply(func=neutral_apply, args=(risk_df_list,), axis=1)
        factor_df[na_df] = np.nan
        factor_df.to_csv('%s/PreprocessData/%s.csv'%(gc.FACTORBASE_PATH, factor))
