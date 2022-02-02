# -*- coding: utf-8 -*-
"""
Created on Tue Feb  1 12:44:30 2022

@author: Scott Greenwood
"""

import plotRAVEN

summary = {}
path = '../tests/test_sampleROM_V'
variables = ['x','y']

methods = ['IDW','DMD','SVM','DMDho']
for method in methods:
    filenames = ['historyFMU','history{}'.format(method)]
    summary[method] = plotRAVEN.historyComparisonPlot(variables, filenames, path, plotInterval=4,plotPathAdd=method)
    
from beeprint import pp
pp(summary)
