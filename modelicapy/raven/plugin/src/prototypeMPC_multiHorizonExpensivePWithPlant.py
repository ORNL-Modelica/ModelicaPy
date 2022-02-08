# -*- coding: utf-8 -*-
"""
Created on Fri Feb  4 10:55:12 2022

@author: Scott Greenwood


"""

import prototypeMPC
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize
from fmpy import simulate_fmu
from scipy.interpolate import interp1d
import sklearn.metrics as sklm
import pandas as pd


def _refTrajSine(t, bias = 0.0, amplitude = 1.0, shift = 0.0, period = 10.0, scale = 1.0):
    return bias + amplitude*np.sin(scale*2*np.pi*(t-shift)/period)

def _refTrajConstant(t, bias = 0.0):
    return np.ones(len(t))*bias

def _refTrajRamp(t, bias = 0.0, amplitude = 0.0, tChange = 0.0):
    result = np.ones(len(t))*bias
    for i, val in enumerate(t):
        if val >= tChange:
            result[i] += amplitude
    return result

def _timeControlPointBased(time_control, nC, nOverlap):
    dt = time_control[1]-time_control[0]
    time_control = np.concatenate((time_control,np.array([time_control[-1]+dt*(i+1) for i in range(nC-nOverlap)])))
    return time_control

def _alternatingValue(vals,n,iStart=0):
    result = []
    j = iStart
    for i in range(n):
        result.append(vals[j])
        j += 1
        if j >= len(vals):
            j = 0
    return result
            
                
def _objective(u, *args): 
    '''
    '''
    
    filename, start_time, output_interval, start_values, outputs, referenceTraj, dtype, time_control, weights, u_optimized = args

    # Create inputs
    inputList = [time_control, np.concatenate((u_optimized, u))]
    inputs = prototypeMPC._createInputs(inputList,dtype)

    # Simulate       
    results = simulate_fmu(filename,
                           start_time=start_time,
                           stop_time=time_control[-1],
                           output_interval=output_interval,
                           start_values=start_values,
                           input=inputs,
                           output=outputs)
    
    # Calculate error
    summary = {}
    summary['error'] = 0.0
    for key in referenceTraj:
        _f = interp1d(results['time'],results[key])
        summary[key] = {}
        ref = referenceTraj[key]
        pred = _f(time_control)
        summary[key]['MSE'] = sklm.mean_squared_error(ref,pred,squared=True)
        summary['error'] += summary[key]['MSE']*weights[key]
    return summary['error']



    
#%%
if __name__ == '__main__':

    nHorizons = 25
    time_horizon = 5.0
    nC = 7
    nOverlap = 4 # point based overlap

    #%%
    # Path to FMU
    filename = '../tests/fmus/lotkaVolterra.fmu'
    # Start time
    start_time = 0.0
    # Stop time
    # stop_time = time_horizon + start_time
    # Start values
    start_values = {'x_start':50,'y_start':50,'alpha':0.5,'beta':0.025,'gamma':0.5,'delta':0.005}
    # Outputs
    outputs = ['time','x','y','u']
    # Results output interval
    output_interval = 0.01
    # Controlled variable
    varControl = 'y'
    
    #%% Test reference trajectories
    def _checkRefTrajSine(nC,start_time,time_horizon,nHorizons):
        referenceTraj = {}
        fig, ax = plt.subplots()
        bias = start_values['x_start']
        amplitude = 0.5*bias
        shift = 0.0
        period = 10.0
        time_control = np.linspace(start_time,time_horizon + start_time,nC)
        for p in range(nHorizons):
            referenceTraj[varControl] = _refTrajSine(time_control, bias, amplitude, shift, period, scale = -1.0)
            ax.plot(time_control,referenceTraj[varControl]+p,'-.',label=p)
            # Point based overlap (fixed dt)
            time_control = _timeControlPointBased(time_control, nC, nOverlap)
            
        ax.legend()
        ax.set_xlabel('Time')
        ax.set_ylabel('Variable \n+ Small Offset for Visibility')
        
    _checkRefTrajSine(nC,start_time,time_horizon,nHorizons)  
     
    def _checkRefTrajConstant(nC,start_time,time_horizon,nHorizons):
        referenceTraj = {}
        fig, ax = plt.subplots()
        bias = start_values['x_start']
        time_control = np.linspace(start_time,time_horizon + start_time,nC)
        for p in range(nHorizons):
            referenceTraj[varControl] = _refTrajConstant(time_control, bias)
            ax.plot(time_control,referenceTraj[varControl]+p,'-.',label=p)
            # Point based overlap (fixed dt)
            time_control = _timeControlPointBased(time_control, nC, nOverlap)
            
        ax.legend()
        ax.set_xlabel('Time')
        ax.set_ylabel('Variable \n+ Small Offset for Visibility')
        
    _checkRefTrajConstant(nC,start_time,time_horizon,nHorizons)  
    
    #%%
    time_control = np.linspace(start_time,time_horizon + start_time,nC)
    u_optimized = []

    u0 = np.array([-10,-5,0,5,10,5,0])
    dtype = [('time', np.double), ('u', np.double)]
    inputList = [time_control, np.concatenate((u_optimized, u0))]
    inputs = prototypeMPC._createInputs(inputList,dtype)
        
    # bias = start_values['x_start']
    # amplitude = 0.5*bias
    bias = start_values['alpha']/start_values['beta']
    
    referenceTraj = {}
    # referenceTraj['x'] = _refTrajSine(time_control, bias, amplitude, 0.0, 10.0, -1.0)
    # referenceTraj[varControl] = _refTrajConstant(time_control, bias)
    referenceTraj[varControl] = _refTrajRamp(time_control, bias, amplitude = bias*0.25, tChange = 10.0)
    
    weights = {key:1.0 for key in referenceTraj}
    args = (filename, start_time, output_interval, start_values, outputs, referenceTraj, dtype, time_control, weights, u_optimized)
    error = _objective(u0, *args)

    bounds = tuple([(-200,200) for i in range(len(u0))])
 
    #%% Test simulation
    results0 = simulate_fmu(filename,
                            start_time=start_time,
                            stop_time=time_control[-1],
                            output_interval=output_interval,
                            start_values=start_values,
                            input=inputs,
                            output=outputs)
    prototypeMPC.simplePlot([varControl,'u'], results0, time_control, referenceTraj, 'Simulation Test')
    
    
    #%% Plant info
    filenamePlant = '../tests/fmus/lotkaVolterraWithControl_NoiseDrift.fmu'
    
    
    #%% Optimization loop
    results = {}

    for p in range(nHorizons):
        print('Horizon: {}, Time: {}'.format(p, time_control[-1]))
        
        # Get data from plant for last time horizon
        if p > 0:
            
        # Calculate error between result and plant
        
        
        # Optimize control
        prototypeMPC.tic()
        solution = scipy.optimize.minimize(_objective,x0=u0,args=args,bounds=bounds)
        prototypeMPC.toc()

        
        # Test converged solution
        inputList = [time_control, np.concatenate((u_optimized, solution.x))]
        inputs = prototypeMPC._createInputs(inputList,dtype)
                
        results[p] = simulate_fmu(filename,
                                start_time=start_time,
                                stop_time=time_control[-1],
                                output_interval=output_interval,
                                start_values=start_values,
                                input=inputs,
                                output=outputs)
        prototypeMPC.simplePlot([varControl,'u'], results[p], time_control, referenceTraj,save=True, saveName = 'temp/controlSolution_{}.png'.format(p))  
        
        
            
        if p < nHorizons-1:
            # Update time
            time_control = _timeControlPointBased(time_control, nC, nOverlap)
    
            # Update reference
            # referenceTraj['x'] = _refTrajSine(time_control, bias, amplitude, 0.0, 10.0, scale=-1.0)
            # referenceTraj[varControl] = _refTrajConstant(time_control, bias)
            referenceTraj[varControl] = _refTrajRamp(time_control, bias, amplitude = bias*0.25, tChange = 10.0)
            
            # Update solution
            u_optimized = np.concatenate((u_optimized,solution.x[:nC-nOverlap]))
            
            # Update guess values
            u0 = np.concatenate((solution.x[nC-nOverlap:],_alternatingValue([10,0],nC-nOverlap,0)))
            
            # Update inputs
            args = (filename, start_time, output_interval, start_values, outputs, referenceTraj, dtype, time_control, weights, u_optimized)
        else:
            # Update final solution
            u_optimized = np.concatenate((u_optimized,solution.x))
            
    #%% Output Results
    print('Optimized solution:\ntime =\n{}\nu =\n{}'.format(time_control, u_optimized))
    df = pd.DataFrame({'time':time_control, 'u':u_optimized})
    df.set_index('time',inplace=True)
    df.to_csv('temp/control.csv')
    
    #%% Create GIF of solution process
    import imageio
    import os
    import re
    
    path = 'temp'
    file_list=os.listdir(path)
    print (file_list)
             
    # Get the list of all files and directories
    dirList = os.listdir(path)
    fileREGEX = 'controlSolution_\d*.png'

    # Get only result files and record the simulation order
    files = []
    for file in dirList:
        if re.match(fileREGEX,file):
            order = int(re.search('\d+', file).group())
            files.append((os.path.join(path,file),order))
    # Sort in ascending order
    files.sort(key=lambda tup: tup[1])

    images = []
    for file in files:
        images.append(imageio.imread(file[0]))
    imageio.mimsave(os.path.join(path,'controlSolution.gif'), images)