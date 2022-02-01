# -*- coding: utf-8 -*-
"""
Created on Fri Jan 28 10:51:04 2022

@author: Scott Greenwood
"""

# pip install buildingspy

import matplotlib.pyplot as plt
import os
import re
import pandas as pd
import numpy as np

    
def historyPlot(variables, filename, path = '.', filetype = 'csv', showLegend = False, plotInterval = 0, pivotParameter = 'time', xlabel = 'Time'):
    '''

    Parameters
    ----------
    variables : TYPE
        DESCRIPTION.
    filename : TYPE
        DESCRIPTION.
    path : TYPE, optional
        DESCRIPTION. The default is '.'.
    filetype : TYPE, optional
        DESCRIPTION. The default is 'csv'.
    showLegend : TYPE, optional
        DESCRIPTION. The default is False.
    plotInterval : TYPE, optional
        Plot every nth simulation result or 0 to plot all simulations. The default is 0.

    Returns
    -------
    None.

    '''
    fileREGEX = filename + '_\d*.' + filetype
    
     
    # Get the list of all files and directories
    dirList = os.listdir(path)
    
    # Get only result files and record the simulation order
    resultFiles = []
    for file in dirList:
        if re.match(fileREGEX,file):
            order = int(re.search('\d+', file).group())
            resultFiles.append((os.path.join(path,file),order))
    
    # Sort in ascending order
    resultFiles.sort(key=lambda tup: tup[1])
    
    # Create figures loading data only once
    figList = []
    for var in variables:
        fig, ax = plt.subplots()
        figList.append((fig, ax))
    
    prop_cycle = plt.rcParams['axes.prop_cycle']
    colors = prop_cycle.by_key()['color']
    nColors = len(colors)
    iColor = 0

    iInterval = 0   
    for iFile, file in enumerate(resultFiles):
        result = pd.read_csv(file[0])

        options = {'linestyle':'-','marker':None}
        if len(result[pivotParameter]) == 1:
            options['linestyle'] = 'None'
            options['marker'] = 'o'

        if plotInterval==0 or np.mod(iFile, plotInterval)==0:
            for i, var in enumerate(variables):
                figList[i][1].plot(result[pivotParameter].values,result[var].values,color=colors[iColor],label=iFile,**options)
                figList[i][1].set_xlabel(xlabel)
                figList[i][1].set_ylabel(var)
            iColor += 1
            if iColor > nColors-1:
                iColor = 0
            iInterval += 1
        
    if showLegend:
        for i, var in enumerate(variables):
            fig, ax = figList[i]
            ax.legend(bbox_to_anchor=(0.5, 1),loc='lower center',ncol=int(np.ceil(np.sqrt(len(ax.lines)))))
 

def sampleSpacePlot(variables, filename, path = '.'):
    
    sampleSpace = pd.read_csv(os.path.join(path,filename)+'.csv')
    
    fig, ax = plt.subplots(len(variables), sharex=True)
    for i, var in enumerate(variables):
        ax[i].plot(sampleSpace[var].values,'bo-',linewidth=1, markersize=2)
        ax[i].set_ylabel(var)
    ax[-1].set_xlabel('RAVEN Sample Number')
    fig.align_ylabels(ax[:])
    

if __name__ == '__main__':
    
    path = '../tests/test_sampleROM'
    
    variables = ['x','y']
    filename = 'history'
    historyPlot(variables, filename, path, filetype = 'csv', showLegend = True, plotInterval = 2, xlabel = 'Time (s)')
    
    variables = ['alpha','beta','gamma','delta']
    filename = 'pointValues'
    sampleSpacePlot(variables, filename, path)