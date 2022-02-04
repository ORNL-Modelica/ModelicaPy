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

import sklearn.metrics as sklm
import dtaidistance as dta


def createDirectory(path):
    if not os.path.isdir(path):
        os.makedirs(path)
    
def gatherData(filename, path = '.', filetype = 'csv'):
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
    return resultFiles
    

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
    
    resultFiles = gatherData(filename = filename, path = path, filetype = filetype)
    
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
    plt.close('all')  
    
    
def sampleSpacePlot(variables, filename, path = '.'):
    
    sampleSpace = pd.read_csv(os.path.join(path,filename)+'.csv')
    
    pathPlot = os.path.join(path,'plots')
    createDirectory(pathPlot)
    
    fig, ax = plt.subplots(len(variables), sharex=True)
    for i, var in enumerate(variables):
        ax[i].plot(sampleSpace[var].values,'bo-',linewidth=1, markersize=2)
        ax[i].set_ylabel(var)
    ax[-1].set_xlabel('RAVEN Sample Number')
    fig.align_ylabels(ax[:])
    fig.savefig(os.path.join(pathPlot,'sampleSpace.png'), bbox_inches='tight')
    plt.close('all')  
    
    
def historyComparisonPlot(variables, filenames, path = '.', filetype = 'csv', iRef = 0, plotInterval = 0, pivotParameter = 'time', xlabel = 'Time', plotPathAdd=''):
    
    if not len(filenames) == 2:
        raise ValueError('filenames must contain a list of exactly two names.')  
        
    resultFiles = {}
    for filename in filenames:
        resultFiles[filename] = gatherData(filename = filename, path = path, filetype = filetype)
    
    # Verify have matching length and indices
    if len(resultFiles[filenames[0]]) != len(resultFiles[filenames[1]]):
        raise ValueError('The number of result files for each filename are not equal.')
    
    for i in range(len(resultFiles[filenames[0]])):
        if resultFiles[filenames[0]][i][1] != resultFiles[filenames[1]][i][1]:
            raise ValueError('The files found do not have matching orders.')
    
    pathPlot = os.path.join(path,'plots',plotPathAdd)
    createDirectory(pathPlot)
    
    summary = {}
    for iFile in range(len(resultFiles[filenames[0]])):
        results = {}
        results['ref'] = pd.read_csv(resultFiles[filenames[iRef]][iFile][0])
        results['pred'] = pd.read_csv(resultFiles[filenames[1-iRef]][iFile][0])
        
        if plotInterval==0 or np.mod(iFile, plotInterval)==0:
            for var in variables:
                summary[iFile] = {}
                
                ref = results['ref'][var]
                pred = results['pred'][var]
                
                # Simple Plots
                fig, ax = plt.subplots()
                ax1 = ax.twinx()
                ax.plot(results['ref'][pivotParameter], ref,'k-',label='Reference')
                ax.plot(results['pred'][pivotParameter], pred,'r-.',label='Predicted')
                ax1.plot(results['ref'][pivotParameter], (ref-pred)/ref, 'b:',  label='Normalized Difference')
                ax.set_ylabel(var)
                ax1.set_ylabel('Difference (-)')
                ax.set_xlabel(xlabel)
                # fig.legend()
                fig.legend(bbox_to_anchor=(0.5, 1),loc='lower center',ncol=3)
                fig.savefig(os.path.join(pathPlot,'comparison_{}_{}.png'.format(iFile,var)), bbox_inches='tight')
                
                # Metrics
                summary[iFile]['RMSE'] = sklm.mean_squared_error(ref,pred,squared=False)

                # Time warping
                # path_RP = dta.dtw.warping_path(ref, pred)
                # dta.dtw_visualisation .plot_warping(ref, pred, path_RP, filename=os.path.join(pathPlot,'warp_{}_{}.png'.format(iFile,var)))
                summary[iFile]['distance'] = dta.dtw.distance(ref, pred, use_pruning=True)
                
    plt.close('all')    
    return summary
    
    
if __name__ == '__main__':
    
    path = '../tests/test_sampleROM'
    variables = ['x','y']
    filename = 'history'
    historyPlot(variables, filename, path, showLegend = True, plotInterval = 2, xlabel = 'Time (s)')
    
    variables = ['alpha','beta','gamma','delta']
    filename = 'pointValues'
    sampleSpacePlot(variables, filename, path)
    
    path = '../tests/test_createROM_V'
    variables = ['x','y']
    filenames = ['history','historyROM']
    summary = historyComparisonPlot(variables, filenames, path, plotInterval=4)