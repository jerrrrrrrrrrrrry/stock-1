# -*- coding: utf-8 -*-
"""
Created on Tue May  4 21:49:12 2021

@author: admin
"""

import multiprocessing as mp

if __name__ == '__main__':
    factors = []
    # factors.extend(['MC', 'BP'])
    factors.extend(['TurnRate1', 'TurnRate5', 'TurnRate20', 'TurnRate60'])
    # factors.extend(['DEP'])
    # factors.extend(['ROE', 'EP', 'DEP'])
    #factors.extend(['MomentumInd', 'MomentumBK'])
    
    factors.extend(['Momentum5', 'Momentum20'])
    factors.extend(['Bias20', 'Bias60'])
    factors.extend(['TSRegBeta60', 'TSRegBeta120'])
    factors.extend(['Donchian120', 'Donchian250'])
    factors.extend(['CloseToAverage1', 'CloseToAverage5', 'CloseToAverage20'])
    factors.extend(['Jump1', 'Jump5', 'Jump20'])
    factors.extend(['CORRMarket20', 'CORRMarket60'])
    factors.extend(['Sigma20', 'Sigma60'])
    factors.extend(['ZF20', 'ZF60'])
    factors.extend(['Skew20', 'Skew60'])
    
    # factors.extend(['RQPM'])
    factors.extend(['HFReversalMean20', 'HFReversalMean60'])
    factors.extend(['HFStdMean20', 'HFStdMean60'])
    factors.extend(['HFUID20', 'HFUID60'])
    factors.extend(['HFSkewMean20', 'HFSkewMean60'])
    factors.extend(['HFVolMean20', 'HFVolMean60'])
    # factors.extend(['HFVolPowerMean20'])
    
    pool = mp.Pool(4)
    models = ['beta_1', 'beta_2', 'beta_3']
    for model in models:
        exec('import %s'%model)
        exec('pool.apply_async(func=%s.main, args=(factors, ))'%model)
    pool.close()
    pool.join()