# -*- coding: utf-8 -*-
"""
Created on Mon Mar  7 15:30:28 2022

@author: Scott Greenwood
"""
import numpy as np
import simulateTCLab as simTC

import sys
sys.path.insert(0, '../src')
import helperFunctions as hf
import frequencyAnalysisFunctions as fa

#%% Main
if __name__ == "__main__":
    ''' Switch between simulating or running the TCLab under the same scneario as simulateFMU'''
    
    method = 'prts'
    startTime = 10*60
    # Input section    
    inputs_base = {}
    inputs_base['Q1'] = {}
    inputs_base['Q1']['time'], inputs_base['Q1']['u'] = fa.prts(freqHz=0.1, amplitude = 20, offset=80, startTime = startTime, stopTime=2*startTime)#, bias=-0.5)

    inputs_base['Q2'] = {}
    inputs_base['Q2']['time'], inputs_base['Q2']['u'] = fa.prts(freqHz=0.1, amplitude = 20, offset=60, startTime = startTime+30, stopTime=2*startTime)#, bias=-0.5)

    stop_time = 20*60
    time_update = 2 # time between querying
    connected = False
    speedup = 100
    
    # Create structured input
    n = int(stop_time/time_update+1)
    time_setpoint = np.linspace(0.0,stop_time,n)
    
    inputs = simTC.inputHelper(inputs_base, time_setpoint)
    simTC.simplePlotInputs(inputs, time_setpoint)
    
    # Run experiment
    results = simTC.simulateExperiment(inputs, time_update, connected=connected, speedup=speedup)
    hf.simplePlotResultsTwinned(results,['Q1','Q2'], ['T1','T2'])
    
    # #%% Save results
    # savePath = 'test_' + os.path.basename(__file__)[:-3]
    # hf.createFolder(savePath)
    
    # if connected:
    #     pickleName = os.path.join(savePath,'results_exp.pickle')
    # else:
    #     pickleName = os.path.join(savePath,'results_mod.pickle')
    # hf.pickleResults(results, path=pickleName, read=False)