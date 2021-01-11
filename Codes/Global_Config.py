import os
import sys
import time
import datetime

import numpy as np
import pandas as pd
from pandas import Series, DataFrame

#字段名

#路径名
PROJECT_PATH = 'D:/stock'
GLOBALCONFIG_PATH = PROJECT_PATH + '/Codes'
DATABASE_PATH = PROJECT_PATH + '/DataBase'
FACTORBASE_PATH = PROJECT_PATH + '/FactorBase'
LABELBASE_PATH = PROJECT_PATH + '/LabelBase'
SINGLEFACTOR_PATH = PROJECT_PATH + '/SingleFactor'
MULTIFACTOR_PATH = PROJECT_PATH + '/MultiFactor'
MODEL_PATH = PROJECT_PATH + '/Model'

#常量
OPEN = 'OPEN'
HIGH = 'HIGH'
LOW = 'LOW'
CLOSE = 'CLOSE'
VOLUME = 'VOLUME'
AMOUNT = 'AMOUNT'
ADJ_FACTOR = 'ADJ_FACTOR'
TURNOVER_RATE = 'TURNOVER_RATE'



PE = 'PE'
PB = 'PB'
PS = 'PS'
DY = 'DY'
TMC = 'TMC'
CMC = 'CMC'
ST = 'ST'
