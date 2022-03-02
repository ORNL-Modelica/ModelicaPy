# -*- coding: utf-8 -*-
"""
Created on Wed Mar  2 08:53:11 2022

@author: Scott Greenwood
"""

from fmpy import simulate_fmu
import numpy as np
import matplotlib.pyplot as plt

import sys
sys.path.insert(0, '../src')
import helperFunctions as hf

def linear(t_array,u_array):
    '''Default to linear assumed in FFMPY simulate_fmu'''
    return t_array, u_array

def step(t_array,u_array):
    '''Format values to enforce step'''
    time = []; u = []
    for i in range(len(t_array)):
        time.append(t_array[i])
        u.append(u_array[i])
        if i < len(t_array)-1:
            time.append(t_array[i+1])
            u.append(u_array[i])
    return time, u

def indices(a,b):
    '''Find all matching indices of b values in list a'''
    result = []
    for val in b:
        iMatch = []
        for i in range(len(a)):
            if a[i] == val:
                iMatch.append(i)
        result.append(iMatch)
    return result

def removeDuplicates(a):
    '''Remove duplicate entries in list'''
    result = []
    [result.append(x) for x in a if x not in result]
    return result

def inputHelper(inputs_base, dtype = None):
    '''
    Simplify the mapping of simple independent input to FMPy formatted for simulate_fmu
    
    dtype = [('time', np.double), ('Q1', np.double), ('Q2', np.double)]
    
    # Original signal setpoints
    inputs_base = {}
    inputs_base['Q1'] = {'time':[0,20,200,400,600,800,1000],
                         'u':[0,80,20,70,50,100,0]}
    inputs_base['Q2'] = {'time':[0,100,300,500,700,900,1100],
                         'u':[0,35,95,25,100,45,0]}
    
    inputs = inputHelper(inputs_base, dtype)
    simulate_fmu(..., input=inputs, ...)
    '''
    if dtype == None:
        dtype = []
        dtype.append(('time', np.double))
        for key in inputs_base:
            dtype.append((key, np.double)) # this can be changed to handle boolean (that may or may not work in the rest of the code)
 
    # Behavior at each datapoint (do nothing = linear - linear not coded
    inputs_individual = {}
    for key in inputs_base:
        t_array = inputs_base[key]['time']
        u_array = inputs_base[key]['u']
        time, u = step(t_array, u_array)
        inputs_individual[key] = {'time':time,'u':u} 

    # Combine arrays into a single time array
    time = []   
    for key in inputs_individual:
        t = inputs_individual[key]['time']
        for i, val in enumerate(t):
            if time.count(val) != 2:
                time.append(val)
        time.sort()
        
    # Remove extra initial time values
    while time.count(time[0]) > 1:
        time.pop(0)

    # Create value arrays (assumes step behavior and not linear)
    inputs_combined = {}
    for key in inputs_individual:
        time_key = inputs_individual[key]['time']
        inputs_combined[key] = np.zeros(len(time))
        iMatches = indices(time,time_key)
        iMatches = removeDuplicates(iMatches)
        
        for i, iM in enumerate(iMatches):
            if i == 0:
                inputs_combined[key][0] = inputs_base[key]['u'][i]
            else:
                if i == 1:
                    inputs_combined[key][0:iM[1]] = inputs_base[key]['u'][i-1]
                else:
                    inputs_combined[key][iMatches[i-1][1]:iM[1]] = inputs_base[key]['u'][i-1]
                inputs_combined[key][iM[1]] = inputs_base[key]['u'][i]

    # Generate required output format
    inputList = []
    for val in dtype:
        if val[0] == 'time':
            inputList.append(time)
        else:
            inputList.append(inputs_combined[val[0]].tolist())
    inputs = hf.createInputs(inputList,dtype)
    return inputs

#%% Plotting
def simplePlotInputsBase(inputs_base):
    fig, ax = plt.subplots()
    for key in inputs_base:
        ax.plot(inputs_base[key]['time'],inputs_base[key]['u'],label=key)
    ax.legend()

def simplePlotInputs(inputs):
    fig, ax = plt.subplots()
    for key in inputs.dtype.names:
        if key != 'time':
            ax.plot(inputs['time'],inputs[key],label=key)
    ax.legend()
        
#%% Main
if __name__ == "__main__":
    
    filenameFMU = 'fmus/TCLab.fmu'
    
    inputs_base = {}
    inputs_base['Q1'] = {'time':[0,20,200,400,600,800,1000],
                    'u':[0,80,20,70,50,100,0]}
    inputs_base['Q2'] = {'time':[0,100,300,500,700,900,1100],
                    'u':[0,35,95,25,100,45,0]}

    inputs = inputHelper(inputs_base)
    simplePlotInputs(inputs)

    # Setup
    start_time = 0
    stop_time = 20*60
    output_interval = 2
    parameters = {}
    outputs = ['Q1','Q2','T1','T2']
         
    results = simulate_fmu(filenameFMU,
                        start_time=start_time,
                        stop_time=stop_time,
                        output_interval=output_interval,
                        output=outputs,
                        input=inputs,
                        start_values = parameters)

    hf.simplePlotResultsTwinned(results,['Q1','Q2'], ['T1','T2'])