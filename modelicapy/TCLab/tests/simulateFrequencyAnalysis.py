# -*- coding: utf-8 -*-
"""
Created on Mon Mar  7 15:30:28 2022

@author: Scott Greenwood
"""
import numpy as np
import simulateTCLab as simTC
import simulateFMU as simFMU
from fmpy import simulate_fmu

import sys
sys.path.insert(0, '../src')
import helperFunctions as hf
import frequencyAnalysisFunctions as fa

#%% Main
if __name__ == "__main__":
    ''' Switch between simulating or running the TCLab under the same scneario as simulateFMU'''
    
    method = 2
    startTime = 10*60
    # Input section    
    inputs_base = {}
    inputs_base['Q1'] = {}
    inputs_base['Q2'] = {}
    
    if method == 1:
        inputs_base['Q1']['time'], inputs_base['Q1']['u'] = fa.prbs(freqHz=0.1, amplitude = 20, offset=80, startTime = startTime, stopTime=2*startTime, bias=-0.5)   
        inputs_base['Q2']['time'], inputs_base['Q2']['u'] = fa.prbs(freqHz=0.1, amplitude = 20, offset=60, startTime = startTime+30, stopTime=2*startTime, bias=-0.5)
    elif method == 2:
        inputs_base['Q1']['time'], inputs_base['Q1']['u'] = fa.prts(freqHz=0.1, amplitude = 20, offset=80, startTime = startTime, stopTime=2*startTime)  
        inputs_base['Q2']['time'], inputs_base['Q2']['u'] = fa.prts(freqHz=0.1, amplitude = 20, offset=60, startTime = startTime+30, stopTime=2*startTime)
    else:
        inputs_base['Q1']['time'], inputs_base['Q1']['u'] = fa.mfbs(freqHz=16, amplitude = 20, offset=80, startTime = startTime, stopTime=2*startTime, bias=-0.5)   
        inputs_base['Q2']['time'], inputs_base['Q2']['u'] = fa.mfbs(freqHz=16, amplitude = 20, offset=60, startTime = startTime+30, stopTime=2*startTime, bias=-0.5)

    stop_time = 20*60
    time_update = 2 # time between querying
    connected = False
    speedup = 100
    
    # Run FMU
    filenameFMU = 'fmus/TCLab.fmu'
    output_interval = time_update
    parameters = {}
    outputs = ['Q1','Q2','T1','T2']
    inputs = simFMU.inputHelper(inputs_base)
    simFMU.simplePlotInputs(inputs)
    
    results = simulate_fmu(filenameFMU,
                        start_time=0,
                        stop_time=stop_time,
                        output_interval=output_interval,
                        output=outputs,
                        input=inputs,
                        start_values = parameters)
    hf.simplePlotResultsTwinned(results,['Q1','Q2'], ['T1','T2'])
    
    # Create structured input
    n = int(stop_time/time_update+1)
    time_setpoint = np.linspace(0.0,stop_time,n)
    
    inputs = simTC.inputHelper(inputs_base, time_setpoint)
    simTC.simplePlotInputs(inputs, time_setpoint)
    
    # Run experiment
    results = simTC.simulateExperiment(inputs, time_update, connected=connected, speedup=speedup)
    #%%
    fig =hf.simplePlotResultsTwinned(results,['Q1','Q2'], ['T1','T2'], xscale = 1/60, yscales=[1/100,1.0],xlabel='Time (s)', ylabels=['Power (W)','Temperature ({}C)'.format(hf.degree_sign)])