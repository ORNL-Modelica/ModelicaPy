# -*- coding: utf-8 -*-
"""
Created on Wed Mar  2 16:12:14 2022

@author: Scott Greenwood
"""

from gekko import GEKKO
import os
import pandas as pd
import matplotlib.pyplot as plt
import copy

import sys
sys.path.insert(0, '../src')
import helperFunctions as hf

#%% Main
if __name__ == "__main__":

    savePath = 'test_' + os.path.basename(__file__)[:-3]
    plotPath = os.path.join(savePath,'plots')
    hf.createFolder(savePath)
    hf.createFolder(plotPath)
    
    resampledName = 'test_compareResults/results_resampled.pickle'
    residualName = 'test_compareResults/residuals.pickle'
    results_resampled = hf.pickleResults(path=resampledName, read=True)
    residuals = hf.pickleResults(path=residualName, read=True)

    # Time series predictive model
    keys = ['fmu', 'mod']
    variables = ['T1','T2']
    results_corrected = copy.deepcopy(results_resampled)
    for key in keys:
        data = pd.DataFrame.from_dict(results_resampled[key])
        data_residuals = pd.DataFrame.from_dict(residuals[key])
        
        # Get data
        t = data['time']
        u = data[['Q1','Q2']]
        y = data_residuals[['T1','T2']]
        
        # Generate time-series model
        m = GEKKO(remote=False)
    
        # System identification
        na = 2 # output coefficients
        nb = 2 # input coefficients
        yp,p,K = m.sysid(t,u,y,na,nb,objf=10000,scale=False,diaglevel=1)
        
        # Correct results
        for i, v in enumerate(variables):
            results_corrected[key][v] = results_corrected[key][v] + yp[:,i]
        
        # Plot residual prediction
        fig, ax = plt.subplots()
        ax.plot(t/60,y,'o',markersize=2)
        ax.plot(t/60, yp, zorder=5)
        ax.legend([r'$T_{1meas}$',r'$T_{2meas}$',\
                    r'$T_{1pred}$',r'$T_{2pred}$'])
        ax.set_xlabel('Time (min)')
        ax.set_ylabel('Residual ({}C)'.format(hf.degree_sign))
        fig.savefig(os.path.join(plotPath,'prediction_residuals_{}.png'.format(key)))
        
        # Plot corrected prediction
        fig, ax = plt.subplots()
        for i, v in enumerate(variables):
            x_pred = results_corrected[key]['time']/60
            y_pred = results_corrected[key][v]
            x_meas = results_resampled['exp']['time']/60
            y_meas = results_resampled['exp'][v]
            ax.plot(x_pred,y_pred,zorder=5,label='{}'.format(v)+r'$_{pred}$')
            ax.plot(x_meas,y_meas,'o',markersize=2,label='{}'.format(v)+r'$_{meas}$')
        ax.legend()
        ax.set_xlabel('Time (min)')
        ax.set_ylabel('Temperature ({}C)'.format(hf.degree_sign))
        fig.savefig(os.path.join(plotPath,'prediction_corrected_{}.png'.format(key)))
        
        # Save results
        pickleName = os.path.join(savePath,'results_corrected.pickle')
        hf.pickleResults(results_corrected, path=pickleName, read=False)