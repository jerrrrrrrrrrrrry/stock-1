import datetime
import os
import sys
import time
import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import sklearn
import Config
sys.path.append(Config.GLOBALCONFIG_PATH)
from Model import Model


class IC(Model):
    def fit(self, y, X):
        """
        

        Parameters
        ----------
        y : TYPE
            DESCRIPTION.序列n*1
        X : TYPE
            DESCRIPTION.表n*p

        Returns
        -------
        ic : Series p*1

        """
        self.ic = X.mul(y, axis=1).mean(0)
        
        return self.ic
    
    
    def predict(self, X):
        """
        

        Parameters
        ----------
        X : TYPE
            DESCRIPTION.表n*p

        Returns
        -------
        None.

        """
        return X.dot(self.ic)
    
if __name__ == '__main__':
    label_weight = [0.6, 0.4, 0, 0, 0]
    factor_list = ['Amount', 'Beta', 'ChipsCV', 'Close', 'CloseToAverage', 'Jump', 'MC', 'Reversal', 'Sigma', 'TurnRate', 'Value']
    start_date = '20200901'
    end_date = '20201131'
    model = IC('IC', label_weight=[], factor_list=, start_date=, end_date=)
    
    model.fit()
    
    