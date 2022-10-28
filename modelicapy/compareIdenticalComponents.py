# -*- coding: utf-8 -*-
"""
Created on Fri Oct 28 14:31:12 2022

@author: ScottGreenwood
"""

import matplotlib.pyplot as plt
import os
from buildingspy.io.outputfile import Reader
import numpy as np
import copy

# Path to .mat file
resultPath = r'C:\PATHTOMATFILE'
experiment = 'EXPERIMENTNAME'
iControlName = 0 # index of control component name
componentNames = ['pipe','pipe_multiSurface','pipe_geometry']
controlName = componentNames[iControlName]

#%% Define control variable at get all variables with the same name
resultName = '{}.mat'.format(experiment)
result = os.path.join(resultPath,resultName)
r = Reader(result,'dymola')
variables = r.varNames(controlName+'\.')

results = {}

# Save the order in which the results will be stored
results['order'] = [controlName] + componentNames[:iControlName] + componentNames[iControlName+1:]

# Get and save variables compared to control
varsRemoved = []
for var in variables:
    varName = var[var.find('.')+1:]
    time, tempControl = r.values(var)
    vals = {}
    vals[0]=tempControl

    i = 1
    for component in componentNames:
        try:
            if component != controlName:
                _, temp = r.values(component+'.'+varName)
                if len(temp) == len(tempControl):
                    vals[i] = temp
                    i += 1
                else:
                    if varName not in varsRemoved:
                        varsRemoved.append(varName)
        except:
            pass
    
    results[varName] = vals
    
# Remove all unmatched variables across tests (excluding control)
def removeNonConforming(results,varsRemoved=[]):
    resultsNew = copy.deepcopy(results)
    
    # Variables that are not common between non-control components
    for key in results.keys():
        if len(results[key]) != len(componentNames):
            del resultsNew[key]
            if key not in varsRemoved:
                varsRemoved.append(key)
    return resultsNew, varsRemoved

results, varsRemoved = removeNonConforming(results,varsRemoved)

#%% Number of matching variables
nVars = len(variables)
nVarsNew = len(results.keys())-1
percentMatch = nVarsNew/nVars*100
print('Variables found = {}\n Variables saved = {}\n Percent Match = {}%'.format(nVars,nVarsNew,percentMatch))

#%% Compare results
summary = {}

summary['order'] = componentNames[:iControlName] + componentNames[iControlName+1:]
summary['error'] = {}
summary['errorAbsolute'] = {}
summary['errorRelative'] = {}
for key in results.keys():
    if key != 'order':
        error = {}
        errorAbsolute = {}
        errorRelative = {}
        for i in range(len(componentNames)-1):
            val_control = results[key][0]
            val_compare = results[key][i+1]
            error[i] = np.subtract(val_control,val_compare)
            errorAbsolute[i] = np.abs(error[i])
            errorRelative[i] = np.divide(errorAbsolute[i],np.abs(val_control))
        summary['error'][key] = error
        summary['errorAbsolute'][key] = errorAbsolute
        summary['errorRelative'][key] = errorRelative
    
#%% Find keys which dominate the error

# errorType = 'errorAbsolute'
# limits = [0,1]

errorType = 'errorRelative'
limits = [0,0.0001]

#%% All  
keys = []
for key, item in summary[errorType].items():
    for i in item.keys():
        for val in item[i]:
            if val > limits[0] and val > limits[1]:
                if key not in keys:
                    keys.append(key)
print(keys)


#%% Index
keys = []
index = 1#-1
for key, item in summary[errorType].items():
    for i in item.keys():
        if item[i][index] > limits[0] and item[i][index] > limits[1]:
            if key not in keys:
                keys.append(key)
print(keys)

#%%
# import re
# pat = re.compile(r'^((?!--).)*$')
# filtered = [i for i in keys if pat.match(i)]
filtered = []
ignoreString = ['sat','der','Q_s','.h']
for key in keys:
    found = False
    for string in ignoreString:
        if string in key:
            found = True
    if not found:
        filtered.append(key)
print(filtered)

#%% Plot variable
varPlot = 'drhodx[2]'

style = ['k','r--','b-.']
fig, ax = plt.subplots()
ax1 = ax.twinx()
for i, component in enumerate(results['order']):
    ax.plot(time, results[varPlot][i],style[i],label=component,markerfacecolor="None")

style = ['rx','bo']
for i in range(len(componentNames)-1):
    ax1.plot(time, summary['errorRelative'][varPlot][i],style[i],alpha=0.1,label=component,markerfacecolor="None")
ax1.set_ylabel('Relative Error')
ax.legend()
