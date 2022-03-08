# -*- coding: utf-8 -*-
"""
Created on Fri Mar  4 12:43:32 2022

@author: Scott Greenwood
"""
import os

import sys
sys.path.insert(0, '../src')
import helperFunctions as hf

#%%

picklePath = 'test_residualPredictionGEKKO/m.pickle'
m = hf.pickleResults(path=picklePath, read=True)