# -*- coding: utf-8 -*-
"""
Created on Tue Mar  8 15:21:10 2022

@author: Scott Greenwood
"""
import os
import pandas as pd
from gekko import GEKKO
import matplotlib.pyplot as plt
import numpy as np
import simulateTCLab as simTC
import tclab

import sys
sys.path.insert(0, '../src')
import helperFunctions as hf
      
def runExperiment(m, setpoints, time_update, stop_time, connected=False, speedup = 100, pLog = 10):
    if connected:
        speedup = 1.0
        p1 = 10; p2 = 1
    else:
        # print 20x less with emulator
        p1 = 200; p2 = 20   
        
    # Connect to Arduino
    mlab = hf.connectLab(connected, speedup=speedup) # True (if hardware is available)
    # a = mlab()
    
    # Instantiate results
    variables = ['time','Q1','Q2','T1','T2']
    results = {}
    for v in variables:
        results[v] = []
        
    with mlab() as lab:
        # Find current T1, T2
        print('Temperature 1: {0:0.2f} °C'.format(lab.T1))
        print('Temperature 2: {0:0.2f} °C'.format(lab.T2))
        
        i = 0
        for t in tclab.clock(stop_time, time_update): 
            Tsp1 = setpoints['T1'][i]
            Tsp2 = setpoints['T2'][i]
            
            # Read temperatures in Celcius 
            T1 = lab.T1
            T2 = lab.T2
    
            try:
                [Q1, Q2] = updateController(m,T1,Tsp1,T2,Tsp2)
            except:
                # catch any failure to converge
                Q1 = 0
                Q2 = 0 
                
            # Write heater output (0-100)
            lab.Q1(Q1)
            lab.Q2(Q2)
             
            results['time'].append(t)
            results['Q1'].append(Q1)
            results['Q2'].append(Q2)
            results['T1'].append(T1)
            results['T2'].append(T2)
            
            if i%p1==0:            
                print('  Time_____Q1___Tsp1_____T1______Q2____Tsp2_____T2')
            if i%p2==0:
                print(('{:6.1f} {:6.2f} {:6.2f} {:6.2f}  {:6.2f}  {:6.2f} {:6.2f}').format( \
                          t,Q1,Tsp1,T1,Q2,Tsp2,T2))
            i+=1
    return results

def updateController(m,T1,T1sp,T2,T2sp):    
    # Insert measurements
    m.TC1.MEAS = T1
    m.TC2.MEAS = T2

    # Adjust setpoints
    db1 = 0.1 # dead-band
    m.TC1.SP   = T1sp
    m.TC1.SPHI = T1sp + db1
    m.TC1.SPLO = T1sp - db1

    db2 = 0.1
    m.TC2.SP   = T2sp
    m.TC2.SPHI = T2sp + db2
    m.TC2.SPLO = T2sp - db2
    
    # Adjust heaters with MPC
    m.solve(disp=False) 

    if m.options.APPSTATUS == 1:
        # Retrieve new values
        Q1  = m.Q1.NEWVAL
        Q2  = m.Q2.NEWVAL
    else:
        # Solution failed
        Q1  = 0.0
        Q2  = 0.0    
    return [Q1,Q2]

def initializeController(p):
    m = GEKKO(remote=False)
    m.y = m.Array(m.CV,2)
    m.u = m.Array(m.MV,2)
    m.arx(p,m.y,m.u)
    
    # rename CVs
    m.TC1 = m.y[0]
    m.TC2 = m.y[1]
    
    # rename MVs
    m.Q1 = m.u[0]
    m.Q2 = m.u[1]
    
    # steady state initialization
    m.options.IMODE = 1
    m.solve(disp=False)
    
    # set up MPC
    m.options.IMODE   = 6 # MPC
    m.options.CV_TYPE = 2 # Objective type
    m.options.NODES   = 2 # Collocation nodes
    m.options.SOLVER  = 1 # APOPT
    m.options.MV_STEP_HOR = 1
    m.time=np.linspace(0,60,31)
    
    # Manipulated variables
    m.Q1.STATUS = 1  # manipulated
    m.Q1.FSTATUS = 0 # not measured
    m.Q1.DMAX = 100.0
    m.Q1.DCOST = 5
    m.Q1.UPPER = 100.0
    m.Q1.LOWER = 0.0
    
    m.Q2.STATUS = 1  # manipulated
    m.Q2.FSTATUS = 0 # not measured
    m.Q2.DMAX = 100.0
    m.Q2.DCOST = 5
    m.Q2.UPPER = 100.0
    m.Q2.LOWER = 0.0
    m.Q2.MEAS = 0    # set Q2=0
    
    # Controlled variables
    m.TC1.STATUS = 1     # drive to set point
    m.TC1.FSTATUS = 1    # receive measurement
    m.TC1.TAU = 20        # response speed (time constant)
    m.TC1.TR_INIT = 2    # reference trajectory
    m.TC1.TR_OPEN = 100  # for CV_TYPE=1
    m.TC1.WSPHI = 10
    m.TC1.WSPLO = 10
    m.TC1.WSP = 10
    
    m.TC2.STATUS = 1     # drive to set point
    m.TC2.FSTATUS = 1    # receive measurement
    m.TC2.TAU = 20        # response speed (time constant)
    m.TC2.TR_INIT = 2    # dead-band
    m.TC2.TR_OPEN = 100  # for CV_TYPE=1
    m.TC2.WSPHI = 10
    m.TC2.WSPLO = 10
    m.TC2.WSP = 10

    return m

def identifySystem(pickleName=None,dictionary=None,key='fmu'):
    
    if pickleName != None:
        results_corrected = hf.pickleResults(path=pickleName, read=True)
        if key != None:
            data = pd.DataFrame.from_dict(results_corrected[key])
        else:
            data = pd.DataFrame.from_dict(results_corrected)
    else:
        data = pd.DataFrame.from_dict(dictionary)
        
    # Time series predictive model
    t = data['time']
    u = data[['Q1','Q2']]
    y = data[['T1','T2']]

    # Generate time-series model
    m = GEKKO(remote=False)
    
    # System identification
    na = np.shape(u)[1] # output coefficients
    nb = np.shape(y)[1] # input coefficients
    print('Identify model')
    yp,p,K = m.sysid(t,u,y,na,nb,objf=10000,scale=False,diaglevel=1)
       
    # Plot prediction
    fig, ax = plt.subplots()
    ax.plot(t/60,y,'o',markersize=2)
    ax.plot(t/60, yp, zorder=5)
    ax.legend([r'$T_{1meas}$',r'$T_{2meas}$',\
               r'$T_{1pred}$',r'$T_{2pred}$'])
    ax.set_xlabel('Time (min)')
    ax.set_ylabel('Temperature ({}C)'.format(hf.degree_sign))
    return p
    
#%% Main
if __name__ == "__main__":
    savePath = 'test_' + os.path.basename(__file__)[:-3]
    plotPath = os.path.join(savePath,'plots')
    hf.createFolder(savePath)
    hf.createFolder(plotPath)

    # pickleName = 'test_residualPredictionGEKKO/results_corrected.pickle'
    pickleName = 'test_compareResults/results_resampled.pickle'
    
    # Input section
    setpoints_base = {}
    setpoints_base['T1'] = {'time':[0,60,120,200,400,550],
                          'u':[20,40,25,40,25,40]}
    setpoints_base['T2'] = {'time':[0,100,300,500],
                         'u':[20,30,25,35]}
    
    stop_time = 10*60
    time_update = 2 # time between querying
    connected = False
    speedup = 100
    
    # Create structured input
    n = int(stop_time/time_update+1)
    time_setpoint = np.linspace(0.0,stop_time,n)
    
    setpoints = simTC.inputHelper(setpoints_base, time_setpoint)
    simTC.simplePlotInputs(setpoints, time_setpoint)
    
    # System identification
    p = identifySystem(pickleName=pickleName,key='exp')
    
    # # Create control ARX model
    m = initializeController(p)
    
    results = runExperiment(m, setpoints, time_update = time_update, stop_time = stop_time, connected=connected, speedup = speedup)

    #%%
    fig =hf.simplePlotResultsTwinned(results,['Q1','Q2'], ['T1','T2'], xscale = 1/60, yscales=[1/100,1.0],xlabel='Time (s)', ylabels=['Power (W)','Temperature ({}C)'.format(hf.degree_sign)])
    ax_list = fig.axes
    ax_list[1].plot(time_setpoint/60,setpoints['T1'],'k-.',label='T1sp')
    ax_list[1].plot(time_setpoint/60,setpoints['T2'],'r-.',label='T2sp')
    ax_list[1].legend(loc='upper right')
    
    
    
    
    
    
    
    