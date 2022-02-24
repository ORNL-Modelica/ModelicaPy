# -*- coding: utf-8 -*-
"""
Created on Thu Feb 24 09:38:05 2022

@author: Scott Greenwood
"""

import fmpy
import numpy as np
import matplotlib.pyplot as plt
from fmpy import simulate_fmu

def _createInputs(inputList,dtype):
    '''Format the input into FMPY simulate_fmu'''
    # verify length of arrays in inputList are equal
    refLength = len(inputList[0])
    for i in range(len(inputList)-1):
        if len(inputList[i+1]) != refLength:
            raise ValueError('Input arrays of inputList must be equal.')
            
    # Create formatted input per FMPy requirements
    tupleList = []
    for i in range(refLength):
        tupleItem = []
        for val in inputList:
            tupleItem.append(val[i])
        tupleList.append(tuple(tupleItem))
    return np.array(tupleList, dtype)


def _linear(t_array,u_array):
    '''Default to linear assumed in FFMPY simulate_fmu'''
    return t_array, u_array

def _step(t_array,u_array):
    '''Format values to enforce step'''
    time = []; u = []
    for i in range(len(t_array)):
        time.append(t_array[i])
        u.append(u_array[i])
        if i < len(t_array)-1:
            time.append(t_array[i+1])
            u.append(u_array[i])
    return time, u

def _indices(a,b):
    '''Find all matching indices of b values in list a'''
    result = []
    for val in b:
        iMatch = []
        for i in range(len(a)):
            if a[i] == val:
                iMatch.append(i)
        result.append(iMatch)
    return result

def _inputHelper(inputs_base, dtype):
    '''
    The commented below was trying to simplofy the method for input signals for simulate_fmu.
    However, the way simulate_fmu does inputs (forcing them to be all be based on a single time vector is unworkable)
    This helper would be ok except that there will be issues with derivatives and unbounded simulations etc. so this 
    effort is paused at the point of trying to create a new time_new variable that combines everything appropriately
    
    dtype = [('time', np.double), ('Q1', np.double), ('Q2', np.double)]
    
    # Original signal setpoints
    # inputs_base = {}
    # inputs_base['Q1'] = {'time':[0,20,200,400,600,800,1000],
    #                 'u':[0,80,20,70,50,100,0]}
    # inputs_base['Q2'] = {'time':[0,100,300,500,700,900,1100],
    #                 'u':[0,35,95,25,100,45,0]}
    '''



    # #%% Behavior at each datapoint (do nothing = linear)
    # inputs = {}
    # for key in inputs_base:
    #     t_array = inputs_base[key]['time']
    #     u_array = inputs_base[key]['u']
    #     time, u = _step(t_array, u_array)
    #     inputs[key] = {'time':time,'u':u} 
    # # inputList = [time_u, u]
    # # inputs = _createInputs(inputList,dtype)
    
    # #%% Plot   
    # simplePlot(inputs)
    
    # # Gather unique time values and sort in increasing order
    # time_unique = []
    # keys = inputs.keys()
    # for key in inputs:
    #     for val in inputs[key]['time']:
    #         if not val in time_unique:
    #             time_unique.append(val)
    # time_unique.sort()

    # #%%
    # for key in inputs:
    #     fig, ax = plt.subplots()
    #     iMatches = _indices(inputs[key]['time'],time_unique)
    
    #     u = inputs[key]['u']
    #     u_new = []
    #     j = 0
    #     for val in iMatches:
    #         if len(val) == 1:
    #             u_new.append(u[j])
    #             j += 1
    #         if len(val) == 0:
    #             u_new.append(u[j])
    #         if len(val) == 2:
    #             u_new.append(u[j])
    #             j += 1
    #             u_new.append(u[j])
    pass

#%% Plotting Section
def simplePlot(d):
    fig, ax = plt.subplots()
    for key in inputs:
        ax.plot(d[key]['time'],d[key]['u'],label=key)
    ax.legend()

def simplePlotResults(results,keys):
    fig, ax = plt.subplots()
    for key in keys:
        ax.plot(results['time'],results[key], label=key)
    ax.legend()
    
def simplePlotResultsTwinned(results,keys1, keys2):
    fig, ax = plt.subplots()
    for key in keys1:
        ax.plot(results['time'],results[key], label=key)
    
    ax2 = ax.twinx()
    for key in keys2:
        ax2.plot(results['time'],results[key], '-.', label=key)
    fig.legend()
    
#%%
if __name__ == '__main__':

    
    #%% Inputs
    dtype = [('time', np.double), ('Q1', np.double), ('Q2', np.double)]
    
    time = [0,20,20,100,100,200,200,300,300,400,400,500,500,600,600,700,700,800,800,900,900,1000,1000,1100,1100]
    Q1s = [0,0,80,80,80,80,20,20,20,20,70,70,70,70,50,50,50,50,100,100,100,100,0,0,0]
    Q2s = [0,0,0,0,35,35,35,35,95,95,95,95,25,25,25,25,100,100,100,100,45,45,45,45,0]

    inputList = [time, Q1s, Q2s]
    inputs = _createInputs(inputList,dtype)
    
    #%%
    filenameFMU = r'C:\Users\greems\Documents\Dymola\TCLab.fmu'

    # Setup
    start_time = 0
    stop_time = 20*60
    output_interval = 2
    parameters = {'Q1_scale':50}
    outputs = ['Q1','Q2','T1','T2']
    
    #%% Simulate
    results = simulate_fmu(filenameFMU,
                            start_time=start_time,stop_time=stop_time,output_interval=output_interval,output=outputs,input=inputs, start_values = parameters)
    
    simplePlotResults(results,['Q1','Q2'])
    simplePlotResults(results,['T1','T2'])

    simplePlotResultsTwinned(results,['Q1','Q2'], ['T1','T2'])