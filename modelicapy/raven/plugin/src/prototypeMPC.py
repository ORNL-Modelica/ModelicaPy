# -*- coding: utf-8 -*-
"""
Created on Fri Feb  4 10:55:12 2022

@author: Scott Greenwood
"""

from fmpy import simulate_fmu
import numpy as np
import scipy.optimize
import matplotlib.pyplot as plt
import sklearn.metrics as sklm
from scipy.interpolate import interp1d

history_x = []
history_u = []

#%%
import time

def TicTocGenerator():
    # Generator that returns time differences
    ti = 0           # initial time
    tf = time.time() # final time
    while True:
        ti = tf
        tf = time.time()
        yield tf-ti # returns the time difference

TicToc = TicTocGenerator() # create an instance of the TicTocGen generator

# This will be the main function through which we define both tic() and toc()
def toc(tempBool=True):
    # Prints the time difference yielded by generator instance TicToc
    tempTimeInterval = next(TicToc)
    if tempBool:
        print( "Elapsed time: %f seconds.\n" %tempTimeInterval )

def tic():
    # Records a time in TicToc, marks the beginning of a time interval
    toc(False)
#%%
  
def _createInputs(inputList,dtype):
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


def _objective(u, *args): 
    '''
    '''
    
    filename, start_time, stop_time, output_interval, start_values, outputs, referenceTraj, dtype, time_control, weights = args

    # Create inputs
    inputList = [time_control, u]
    inputs = _createInputs(inputList,dtype)
    
    # Simulate       
    results = simulate_fmu(filename,
                           start_time=start_time,
                           stop_time=stop_time,
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
    # print(summary['error'])
    history_x.append(results['x'])
    history_u.append(u)
    return summary['error']


def simplePlot(tags, results, time_control, referenceTraj, figTitle = '', showLegend=True):
    fig, ax = plt.subplots()
    ax.plot(results['time'],results[tags[0]],'k-', label='sim')
    ax.plot(time_control,referenceTraj[tags[0]],'ro--',label='ref')
    ax1 = ax.twinx()
    ax1.plot(results['time'],results[tags[1]],'b:',label='control')
    ax.set_xlabel('Time')
    
    if showLegend:
        fig.legend(bbox_to_anchor=(0.7, 0.85),loc='upper left')
        
    if figTitle != '':
        fig.suptitle(figTitle)
    return fig
        
def simplePlotBeforeAfter(tags, results0, results, time_control, referenceTraj, figTitle = ''):
    
    fig = simplePlot(tags, results, time_control, referenceTraj, figTitle = figTitle, showLegend=False)
    ax_list = fig.axes
    ax_list[0].plot(results0['time'],results0[tags[0]],'m-', label='sim0', alpha=0.5)
    ax_list[1].plot(results0['time'],results0[tags[1]],'g:',label='control0', alpha=0.5)
    fig.legend(bbox_to_anchor=(0.7, 0.85),loc='upper left')
    
    
if __name__ == '__main__':
    
    #%%
    # Path to FMU
    filename = '../tests/fmus/lotkaVolterra.fmu'
    # Start time
    start_time = 0.0
    # Start values
    start_values = {'x_start':50,'y_start':50,'alpha':0.5,'beta':0.025,'gamma':0.5,'delta':0.005}
    # Outputs
    outputs = ['time','x','y','u']
    # Interval at which control should be optimized
    output_interval = 0.01
    control_interval = 100*output_interval
    #%% Select which input as base, the other will ve overwritten
    use_nPredictions = False
    nPredictions = 20
    stop_time = 6

    if use_nPredictions:
        # Calculate simulation time based on inputs
        stop_time = output_interval*nPredictions
    else:
        # Calculate the numpber of predictions
        nPredictions = int((stop_time-start_time)/control_interval)
      
    #%% Determine method of how controller will function (e.g., step changes, linear changes between points, etc.)
    time_control = np.linspace(0,stop_time,nPredictions+1)
    # Provide inital guess of control signal(s)
    u0 = np.array([-100,100,-100,100,-100,100,-100])
    # Specify formatting and generate FMPy inputs
    dtype = [('time', np.double), ('u', np.double)]
    inputList = [time_control, u0]
    inputs = _createInputs(inputList,dtype)
    
    #%% Create reference trajectory to be used in optimization
    referenceTraj = {}
    referenceTraj['x'] = start_values['x_start']*(1+0.5*np.sin(-time_control/2))

    #%% Test simulation
    results0 = simulate_fmu(filename,
                            start_time=start_time,
                            stop_time=stop_time,
                            output_interval=output_interval,
                            start_values=start_values,
                            input=inputs,
                            output=outputs)
    simplePlot(['x','u'], results0, time_control, referenceTraj, 'Simulation Test')

    #%% Test objective function format
    weights = {key:1.0 for key in referenceTraj}
    args = (filename, start_time, stop_time, output_interval, start_values, outputs, referenceTraj, dtype, time_control, weights)
    error = _objective(u0, *args)
    # simplePlot(['x','u'], results, referenceTraj, 'Objective Test')
    
    #%%
    bounds = tuple([(-200,200) for i in range(len(u0))])

    tic()
    solution = scipy.optimize.minimize(_objective,x0=u0,args=args,bounds=bounds)
    # solution = scipy.optimize.least_squares(_objective,x0=u0,args=args,bounds=(0,10))
    toc()
    
    #%% Test converged solution
    inputList = [time_control, solution.x]
    inputs = _createInputs(inputList,dtype)
    
    results = simulate_fmu(filename,
                            start_time=start_time,
                            stop_time=stop_time,
                            output_interval=output_interval,
                            start_values=start_values,
                            input=inputs,
                            output=outputs)
    simplePlotBeforeAfter(['x','u'], results0, results, time_control, referenceTraj, 'Simulation Test')