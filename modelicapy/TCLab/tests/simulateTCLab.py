# -*- coding: utf-8 -*-
"""
Created on Wed Mar  2 13:06:05 2022

@author: Scott Greenwood
"""
import numpy as np
import matplotlib.pyplot as plt
import time
import os

import sys
sys.path.insert(0, '../src')
import helperFunctions as hf

def inputHelper(inputs_base, time):
    inputs = {}
    for key in inputs_base:
        time_key = inputs_base[key]['time']
        value_key = inputs_base[key]['u']
        inputs[key] = np.zeros(len(time))
        
        j = 1
        for i, t in enumerate(time):
            if j < len(time_key):
                if t >= time_key[j]:
                    j += 1
            inputs[key][i] = value_key[j-1]
    return inputs
      
#%% Plots
def simplePlotInputsBase(inputs_base):
    fig, ax = plt.subplots()
    for key in inputs_base:
        ax.plot(inputs_base[key]['time'],inputs_base[key]['u'],label=key)
    ax.legend()

def simplePlotInputs(inputs, time):
    fig, ax = plt.subplots()
    for key in inputs:
        ax.plot(time,inputs[key],label=key)
    ax.legend()

    
#%% Experiment      
def simulateExperiment(inputs, time_update, connected=False, speedup = 100):
    '''Simple experiment which follows input heater values for a period of time'''
    
    if connected:
        speedup = 1.0
        
    # Connect to Arduino
    mlab = hf.connectLab(connected, speedup=speedup) # True (if hardware is available)
    a = mlab()

    # Instantiate results
    variables = ['time','Q1','Q2','T1','T2']
    results = {}
    for v in variables:
        results[v] = []
    
    # Run experiment
    try:
        for i in range(n):
            # set heater values
            a.Q1(inputs['Q1'][i])
            a.Q2(inputs['Q2'][i])
            print('time: ' + str(time_update*i) + \
                  ' Q1: ' + str(inputs['Q1'][i]) + \
                  ' Q2: ' + str(inputs['Q2'][i]) + \
                  ' T1: ' + str(a.T1)   + \
                  ' T2: ' + str(a.T2))

            results['time'].append(time_update*i)
            results['Q1'].append(inputs['Q1'][i])
            results['Q2'].append(inputs['Q2'][i])
            results['T1'].append(a.T1)
            results['T2'].append(a.T2)

            # wait specified seconds
            time.sleep(time_update/speedup)

        a.close()
        return results
    
    except KeyboardInterrupt:
        hf.safeShutdown(a)
    except:    
        hf.safeShutdown(a)
        raise
        
#%% Main
if __name__ == "__main__":
    ''' Switch between simulating or running the TCLab under the same scneario as simulateFMU'''
    # Input section
    inputs_base = {}
    inputs_base['Q1'] = {'time':[0,20,200,400,600,800,1000],
                          'u':[0,80,20,70,50,100,0]}
    inputs_base['Q2'] = {'time':[0,100,300,500,700,900,1100],
                         'u':[0,35,95,25,100,45,0]}

    stop_time = 20*60
    time_update = 2 # time between querying
    connected = False
    speedup = 100
    
    # Create structured input
    n = int(stop_time/time_update+1)
    time_setpoint = np.linspace(0.0,stop_time,n)
    
    inputs = inputHelper(inputs_base, time_setpoint)
    simplePlotInputs(inputs, time_setpoint)
    
    # Run experiment
    results = simulateExperiment(inputs, time_update, connected=connected, speedup=speedup)
    hf.simplePlotResultsTwinned(results,['Q1','Q2'], ['T1','T2'])
    
    #%% Save results
    savePath = 'test_' + os.path.basename(__file__)[:-3]
    hf.createFolder(savePath)
    
    if connected:
        pickleName = os.path.join(savePath,'results_exp.pickle')
    else:
        pickleName = os.path.join(savePath,'results_mod.pickle')
    hf.pickleResults(results, path=pickleName, read=False)