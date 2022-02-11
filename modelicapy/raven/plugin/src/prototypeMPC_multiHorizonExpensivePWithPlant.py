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
 
def _relativeToLast(lastVal,n,refLast,refTraj, gain = 1.0):
    result = []
    for i in range(n):
        result.append(lastVal*gain*(1.0+(refTraj[i]-refLast)/refTraj[i]))
    return result
           
                
def _objective(u, *args): 
    '''
    '''
    
    filename, start_time, output_interval, start_values, outputs, referenceTraj, dtype, time_control, weights, u_optimized, u1 = args

    # print('time_control {}'.format(len(time_control)))
    # print('np.concatenate((u_optimized, u)) {}'.format(len(np.concatenate((u_optimized, u)))))
    # print('u1 {}'.format(len(u1)))
    # Create inputs
    inputList = [time_control, np.concatenate((u_optimized, u)), u1]
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

def _compareRefTrajToPlant(results, time_control, referenceTraj, returnDiff=False):
    referenceTrajModified = {}
    for key in referenceTraj:
        if len(results['time']) > 1:
            _f = interp1d(results['time'],results[key])
            pred = _f(time_control)
        else:
            pred = results[key]
        ref = referenceTraj[key]
        referenceTrajModified[key] = ref - pred
        if not returnDiff:
            referenceTrajModified[key] = ref - referenceTrajModified
    return referenceTrajModified
     
def _sliceDict(dic,iSlice,left=True):
    result = {}
    for key in dic:
        if left:
            result[key] = dic[key][:-iSlice]
        else:
            result[key] = dic[key][-iSlice:]
    return result

def _fitError(x, y, xnew, order = 1, nDrop = 0, lim = None, limType = 'frac', scale = 1.0):
    fit = np.polyfit(x[nDrop:], y[nDrop:], order)
    _f = np.poly1d(fit)    
    ynew = _f(xnew)*scale
    
    if lim != None:
        if limType == 'frac':
            min_bounds = np.min(y)*lim
            max_bounds = np.max(y)*lim
            for i, val in enumerate(ynew):
                if val > max_bounds:
                    ynew[i] = max_bounds
                elif val < min_bounds:
                    ynew[i] = min_bounds
        elif limType == 'abs':
            min_bounds = lim[0]
            max_bounds = lim[1]
            for i, val in enumerate(ynew):
                if val > max_bounds:
                    ynew[i] = max_bounds
                elif val < min_bounds:
                    ynew[i] = min_bounds
        else:
            raise ValueError('Unsupported limit type')
            
    return ynew

       
#%%
if __name__ == '__main__':

    nHorizons = 15
    time_horizon = 5.0
    nC = 7
    nOverlap = 4 # point based overlap

    # Include plant feedback
    useFeedbackPlant = True
    
    #%%
    # Path to FMU
    filename = '../tests/fmus/lotkaVolterraWithControl.fmu'
    # Start time
    start_time = 0.0
    # Stop time
    # stop_time = time_horizon + start_time
    # Start values
    start_values = {'x_start':50,'y_start':50,'alpha':0.5,'beta':0.025,'gamma':0.5,'delta':0.005}
    # Outputs
    outputs = ['time','x','y','u_x','u_y']
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

    u0 = np.array([-10,-5,0,5,10,5,0])#,-5,0,5])
    u1 = np.zeros(len(u0))
    dtype = [('time', np.double), ('u_y', np.double), ('u_x', np.double)]
    inputList = [time_control, np.concatenate((u_optimized, u0)), u1]
    inputs = prototypeMPC._createInputs(inputList,dtype)
        
    # bias = start_values['x_start']
    # amplitude = 0.5*bias
    bias = start_values['alpha']/start_values['beta']
    
    referenceTraj = {}
    # referenceTraj['x'] = _refTrajSine(time_control, bias, amplitude, 0.0, 10.0, -1.0)
    # referenceTraj[varControl] = _refTrajConstant(time_control, bias)
    referenceTraj[varControl] = _refTrajRamp(time_control, bias, amplitude = bias*0.25, tChange = 15.0)
    
    weights = {key:1.0 for key in referenceTraj}
    args = (filename, start_time, output_interval, start_values, outputs, referenceTraj, dtype, time_control, weights, u_optimized, u1)
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
    prototypeMPC.simplePlot([varControl,'u_y'], results0, time_control, referenceTraj, 'Simulation Test')
    
    
    #%% Plant info
    import copy

    plant = {}
    plant['filename'] = '../tests/fmus/lotkaVolterraWithControl_NoiseDrift.fmu'
    plant['start_values'] = copy.deepcopy(start_values)
    plant['start_values']['drift[1]'] = 5
    plant['results'] = {}
    plant['inputs'] = None
    plant['outputs'] = ['time','x','y', 'u_x', 'u_y']
    plant['dtype'] = [('time', np.double), ('u_y', np.double), ('u_x', np.double)]
    
    #%% Test plant "input"
    plant['results'][0] = simulate_fmu(plant['filename'],
                            start_time=start_time,
                            stop_time=time_control[-1],
                            output_interval=output_interval,
                            start_values=plant['start_values'],
                            input=plant['inputs'],
                            output=plant['outputs']) 
    prototypeMPC.simplePlot([varControl,'u_y'], plant['results'][0], time_control, referenceTraj, 'Plant Test')
    
    #%% Optimization loop
    results = {}
    error = []
    error_t = []
    fig, ax = plt.subplots()
    error = []
    error_t = []
    error_p = []
    for p in range(nHorizons):
        print('Horizon: {}, Time: {}'.format(p, time_control[-1]))
             
        if p > 0:
            # Create modified trajectory based on plant feedback
            referenceTraj_plant = _sliceDict(referenceTraj,nOverlap+(nC-nOverlap))
            referenceTraj_error = _compareRefTrajToPlant(plant['results'][p-1], time_control[:-nOverlap-(nC-nOverlap)], referenceTraj_plant, returnDiff=True)
            # error.append(referenceTraj_error)
            # error_t.append(time_control[:-nOverlap-(nC-nOverlap)])
            
            xtemp = time_control[:-nOverlap-(nC-nOverlap)]
            x = xtemp[-(nC-nOverlap):] # Get the last points which will not be optimized again
            xnew = time_control
            referenceTraj_errorPredict = {}
            referenceTrajModified = {}
            for key in referenceTraj:
                y = referenceTraj_error[key][-(nC-nOverlap):]
                referenceTraj_errorPredict[key] = _fitError(x, y, xnew, order = 1, nDrop=1, lim = 4, scale = 0.5)
                # referenceTrajModified[key] = np.array([referenceTraj[key][i] + (0.0 if i < 3*p else referenceTraj_errorPredict[key][i]) for i in range(len(referenceTraj[key]))])
                referenceTrajModified[key] = referenceTraj[key] + np.average(referenceTraj_error[key])
                
            error.append(y)
            error_t.append(x)
            error_p.append(referenceTraj_errorPredict[key])
            ax.plot(x,y,'*')
            ax.plot(xnew,referenceTraj_errorPredict[key],'-')
    
            if useFeedbackPlant:
                args = (filename, start_time, output_interval, start_values, outputs, referenceTrajModified, dtype, time_control, weights, u_optimized, u1)

        # Optimize control
        prototypeMPC.tic()
        solution = scipy.optimize.minimize(_objective,x0=u0,args=args,bounds=bounds)
        prototypeMPC.toc()

        
        # Test converged solution
        inputList = [time_control, np.concatenate((u_optimized, solution.x)), u1]
        inputs = prototypeMPC._createInputs(inputList,dtype)
                
        results[p] = simulate_fmu(filename,
                                start_time=start_time,
                                stop_time=time_control[-1],
                                output_interval=output_interval,
                                start_values=start_values,
                                input=inputs,
                                output=outputs)
        prototypeMPC.simplePlot([varControl,'u_y'], results[p], time_control, referenceTraj,save=True, saveName = 'temp/controlSolution_{}.png'.format(p))  
                    
        # Get plant performance based on optimized control
        inputList_plant = [time_control[:-nOverlap], np.concatenate((u_optimized,solution.x[:nC-nOverlap])), u1[:-nOverlap]]
        plant['inputs'] = prototypeMPC._createInputs(inputList_plant,plant['dtype'])
        plant['results'][p] = simulate_fmu(plant['filename'],
                                start_time=start_time,
                                stop_time=time_control[-nOverlap-1],
                                output_interval=output_interval,
                                start_values=plant['start_values'],
                                input=plant['inputs'],
                                output=plant['outputs']) 
        # referenceTraj_plant = copy.deepcopy(referenceTraj)
        referenceTraj_plant = _sliceDict(referenceTraj,nOverlap) 
        prototypeMPC.simplePlot([varControl,'u_y'], plant['results'][p], time_control[:-nOverlap], referenceTraj_plant,save=True, saveName = 'temp/plantSolution_{}.png'.format(p)) 
        
        if p > 0:
            referenceTrajModified_sliced = _sliceDict(referenceTrajModified,nOverlap) 
            prototypeMPC.simplePlotExtra([varControl,'u_y'], plant['results'][p], time_control[:-nOverlap], referenceTraj_plant,save=True, saveName = 'temp/plantSolutionWithMod_{}.png'.format(p), yExtra = referenceTrajModified_sliced) 
        
        # Update
        if p < nHorizons-1:
            # Update time
            time_control = _timeControlPointBased(time_control, nC, nOverlap)
    
            # Update reference
            refLast = {}
            for key in referenceTraj:
                refLast[key] = referenceTraj[key][-1]
            # referenceTraj['x'] = _refTrajSine(time_control, bias, amplitude, 0.0, 10.0, scale=-1.0)
            # referenceTraj[varControl] = _refTrajConstant(time_control, bias)
            referenceTraj[varControl] = _refTrajRamp(time_control, bias, amplitude = bias*0.25, tChange = 10.0)
            
            # Update solution
            u_optimized = np.concatenate((u_optimized,solution.x[:nC-nOverlap]))
            u1 = np.concatenate((u1,np.zeros(nC-nOverlap)))
            # Update guess values
            # u0 = np.concatenate((solution.x[nC-nOverlap:],_relativeToLast(solution.x[-1],nC-nOverlap,refLast['y'],referenceTraj['y'][nC-nOverlap:], gain = 1.0)))
            u0 = np.concatenate((solution.x[nC-nOverlap:],_alternatingValue([10,0],nC-nOverlap,0)))
            
            # Update inputs
            args = (filename, start_time, output_interval, start_values, outputs, referenceTraj, dtype, time_control, weights, u_optimized, u1)
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
    
    def _createGIF(plotName = 'controlSolution',path='temp',):
        # Get the list of all files and directories
        dirList = os.listdir(path)
        fileREGEX = plotName + '_\d*.png'
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
        imageio.mimsave(os.path.join(path,plotName+'.gif'), images)
    
    _createGIF(plotName = 'controlSolution')
    _createGIF(plotName = 'plantSolution')
    
    
    # #%%
    # fig, ax = plt.subplots()
    # for i in range(4):
    #     order = 1
    #     x = error_t[i][-(nC-nOverlap):]
    #     y = error[i]['y'][-(nC-nOverlap):]
        
    #     z = np.polyfit(x, y, order)
    #     _f = np.poly1d(z)
        
    #     ynew = _f(x)
    #     xnew =  _timeControlPointBased(x, nC, nOverlap)
    #     ynew2 = _f(xnew)
    #     ax.plot(x,y,'*')
    #     ax.plot(xnew,ynew2,'-')
    #     # ax.plot(x,ynew,'-')
    #     # input("Press Enter to continue...")
        
    # #%%
    # key = 'y'
    # for i in range(len(referenceTraj[key])):
    #     c =  referenceTraj[key][i]
    #     if i < 3*p:
    #         a = 0.0
    #     else:
    #         a = referenceTraj_errorPredict[key][i]
            
    #     c += a
    #     print(c)
    
    # d = np.array([referenceTraj[key][i] + (0.0 if i < 3*p else referenceTraj_errorPredict[key][i]) for i in range(len(referenceTraj[key]))])
    #%%
    fig, ax = plt.subplots()
    for i in range(4):
        x = error_t[i]
        y = error[i]
        yp = error_p[i]
        # ax.plot(x,y,'o')
        ax.plot(yp,'o')