# -*- coding: utf-8 -*-
"""
Created on Fri Feb  4 10:55:12 2022

@author: Scott Greenwood

potential issues
- restart FMU? not possible? can't pause simulation either or rewind... requires resimulating entire timeframe'
"""

import prototypeMPC
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize
from fmpy import simulate_fmu
from scipy.interpolate import interp1d

def _refTrajSine(t, bias = 0.0, amplitude = 1.0, shift = 0.0, period = 10.0, scale = 1.0):
    return bias + amplitude*np.sin(scale*2*np.pi*(t-shift)/period)


def _timeControlPointBased(time_control, nC, nOverlap):
    dt = time_control[1]-time_control[0]
    time_control = np.concatenate((time_control[nC-nOverlap:],np.array([time_control[-1]+dt*(i+1) for i in range(nC-nOverlap)])))
    return time_control

def _timeControlFracBased(time_control, time_horizon, nC, fOverlap):
    t0 = fOverlap*time_horizon + time_control[0]
    tN = fOverlap*time_horizon + time_control[-1]
    time_control = np.linspace(t0,tN,nC)
    return time_control


# def _guessSolution(u0,c, referenceTraj):
#     # Correlate u0 to referenceTraj
#     _f = interp1d(interp1d(results[p]['time'],results[p][val])
#     start_values[key] = _f(time_control[0]),results[p][val])
#     start_values[key] = _f(time_control[0])
#     # Preduct u on new referen
#     u = 1
#     return u
    
    
#%%
if __name__ == '__main__':
    
    nHorizons = 4
    time_horizon = 5.0
    nC = 7
    nOverlap = 3 # point based overlap
    # fOverlap = 0.5 # fractional based overlap
    
    #%%
    # Path to FMU
    filename = '../tests/fmus/lotkaVolterra.fmu'
    # Start time
    start_time = 0.0
    # Stop time
    stop_time = time_horizon + start_time
    # Start values
    start_values = {'x_start':50,'y_start':50,'alpha':0.5,'beta':0.025,'gamma':0.5,'delta':0.005}
    # Outputs
    outputs = ['time','x','y','u']
    # Start/Output mapping
    startMap = {'x_start':'x','y_start':'y'}
    # Results output interval
    output_interval = 0.01
    
    #%% Test reference trajectories
    def _checkRefTrajSine(nC,start_time,stop_time,nHorizons):
        referenceTraj = {}
        fig, ax = plt.subplots()
        bias = start_values['x_start']
        amplitude = 0.5*bias
        shift = 0.0
        period = 10.0
        t = np.linspace(start_time,stop_time,nC)
        for p in range(nHorizons):
            referenceTraj['x'] = _refTrajSine(t, bias, amplitude, shift, period, scale = -1.0)
            ax.plot(t,referenceTraj['x'],'-.',label=p)
            
            # Fractional based overlap
            # t = _timeControlFracBased(time_control, time_horizon, nC, fOverlap)
            
            # Point based overlap (fixed dt)
            t = _timeControlPointBased(t, nC, nOverlap)

    _checkRefTrajSine(nC,start_time,stop_time,nHorizons)  
     
    
    #%%
    time_control = np.linspace(start_time,stop_time,nC)
    u0 = np.array([-100,100,-100,100,-100,100,-100])
    dtype = [('time', np.double), ('u', np.double)]
    inputList = [time_control, u0]
    inputs = prototypeMPC._createInputs(inputList,dtype)
        
    bias = start_values['x_start']
    amplitude = 0.5*bias
    
    referenceTraj = {}
    referenceTraj['x'] = _refTrajSine(time_control, bias, amplitude, 0.0, 10.0, -1.0)
    
    weights = {key:1.0 for key in referenceTraj}
    args = (filename, start_time, stop_time, output_interval, start_values, outputs, referenceTraj, dtype, time_control, weights)
    error = prototypeMPC._objective(u0, *args)

    bounds = tuple([(-200,200) for i in range(len(u0))])
 
    #%% Test simulation
    results0 = simulate_fmu(filename,
                            start_time=start_time,
                            stop_time=stop_time,
                            output_interval=output_interval,
                            start_values=start_values,
                            input=inputs,
                            output=outputs)
    prototypeMPC.simplePlot(['x','u'], results0, time_control, referenceTraj, 'Simulation Test')
    
    #%% Optimization loop
    results = {}
    fig, ax = plt.subplots()
    for p in range(nHorizons):
        # debugging
        ax.plot(time_control,referenceTraj['x'],'-.',label=p)
        ax.legend()
        
        prototypeMPC.tic()
        solution = scipy.optimize.minimize(prototypeMPC._objective,x0=u0,args=args,bounds=bounds)
        prototypeMPC.toc()

        
        # Test converged solution
        inputList = [time_control, solution.x]
        inputs = prototypeMPC._createInputs(inputList,dtype)
                
        results[p] = simulate_fmu(filename,
                                start_time=start_time,
                                stop_time=stop_time,
                                output_interval=output_interval,
                                start_values=start_values,
                                input=inputs,
                                output=outputs)
        prototypeMPC.simplePlot(['x','u'], results[p], time_control, referenceTraj, 'Solution Test')  


        
        # Update time
        time_control = _timeControlPointBased(time_control, nC, nOverlap)
        
        # Update start values
        for key, val in startMap.items():
            _f = interp1d(results[p]['time'],results[p][val])
            start_values[key] = _f(time_control[0])
        
        # Update reference
        referenceTraj['x'] = _refTrajSine(time_control, bias, amplitude, 0.0, 10.0, scale=-1.0)
        
        # Update guess values
        u0 = np.concatenate((solution.x[nC-nOverlap:],[100,-100,100,-100]))#solution.x #get solution for overlapped values and then guesstimate what the next might be from the trajectory...
        
        # Update inputs
        args = (filename, start_time, stop_time, output_interval, start_values, outputs, referenceTraj, dtype, time_control, weights)