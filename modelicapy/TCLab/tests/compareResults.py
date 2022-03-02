# -*- coding: utf-8 -*-
"""
Created on Wed Mar  2 15:26:01 2022

@author: Scott Greenwood
"""
import matplotlib.pyplot as plt
import numpy as np
import os

import sys
sys.path.insert(0, '../src')
import helperFunctions as hf

#%% Main
if __name__ == "__main__":
    
    savePath = 'test_compareResults'
    plotPath = os.path.join(savePath,'plots')
    hf.createFolder(savePath)
    hf.createFolder(plotPath)
    
    pickles = {'fmu':'test_simulateFMU/results_fmu.pickle',
               'mod':'test_simulateTCLab/results_mod.pickle',
               'exp':'test_simulateTCLab/results_exp.pickle'}
    
    results = {}   
    for key in pickles:
        results[key] = hf.pickleResults(path=pickles[key], read=True)

    # Convert fmu temperatures from SI to degC
    results['fmu']['T1'] = results['fmu']['T1']-273.15
    results['fmu']['T2'] = results['fmu']['T2']-273.15
    
    keys = ['Q1','Q2','T1','T2'] 
    for key in keys:
        fig, ax = plt.subplots()
        ax.plot(results['fmu']['time']/60, results['fmu'][key], 'k-', label='FMU')
        ax.plot(np.array(results['mod']['time'])/60, results['mod'][key], 'b-.', label='Model')
        ax.plot(np.array(results['exp']['time'])/60, results['exp'][key], 'ro', label='Experiment')
        if 'T' in key:
            ax.set_ylabel('Temperature ({}C)'.format(hf.degree_sign))
        else:
            ax.set_ylabel('Heater Power (%)')
        ax.set_xlabel('Time (min)')
        ax.legend()
        ax.set_title(key)
        fig.savefig(os.path.join(plotPath,'{}.png'.format(key)))