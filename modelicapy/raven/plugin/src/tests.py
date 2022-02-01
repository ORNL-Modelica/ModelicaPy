# -*- coding: utf-8 -*-
"""
Created on Tue Feb  1 12:44:30 2022

@author: Scott Greenwood
"""

import plotRAVEN

path = '../tests/test_sampleROM_V'
variables = ['x','y']
filenames = ['historyFMU','history']
summary = plotRAVEN.historyComparisonPlot(variables, filenames, path, plotInterval=4,plotPathAdd='IDW')