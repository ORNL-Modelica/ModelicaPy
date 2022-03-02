# -*- coding: utf-8 -*-
"""
Created on Tue Mar  1 14:56:39 2022

@author: Scott Greenwood

Purpose:
    - Test running TCLab and TCModel
    - Accelerate TCLabModel test
"""

import matplotlib.pyplot as plt
import os

import sys
sys.path.insert(0, '../src')
import helperFunctions as hf

def dtUpdate(lab, T_ref = 50.0, T_scale = 10, use_T1 = True, minmax = [0.0,5.0], debug=False, speedup = 1.0):
    '''Decrease dt as the reference temperature is approched'''
    if use_T1:
        T = lab.T1
    else:
        T = lab.T2
    dt = max(minmax[0], min(minmax[1], abs(T_ref - T)/T_scale))
    if debug:
        print(dt)
    return dt/speedup 

#%% Main
if __name__ == "__main__":
    '''
    Example decreases the time between blinks as the temperature approaches the trip temperature.
    '''
    savePath = 'test_' + os.path.basename(__file__)[:-3]
    plotPath = os.path.join(savePath,'plots')
    
    tests = [False, True]    
    
    def updateResults(results, t, lab):
        results['time'].append(t)
        results['T1'].append(lab.T1)
        return results
    
    results = {}
    for test in tests:
        savePath = os.path.join(plotPath,str(test))
        hf.createFolder(savePath)
        results[str(test)] = {}
        results[str(test)]['time'] = []
        results[str(test)]['T1'] = []
        
        connected = test
        T_trip = 50.0
        speedup = 100
    
        # Connect to Arduino
        mlab = hf.connectLab(connected, speedup=speedup) # True (if hardware is available)
        a = mlab()
    
        if connected:
            speedup = 1.0
            
        fig, ax = plt.subplots()
        ax.set_ylim(0,50)
        t = 0.0
        style = 'ok'
        ax.set_xlabel('Time [s]')
        ax.set_ylabel('Temperature ({}C)'.format(hf.degree_sign))
        
        i = 0
        with a as lab:
            ax.plot(t,lab.T1,style)
            dt = dtUpdate(lab,speedup=speedup)
            hf.updateDisplay(fig, saveFig = True, saveName = os.path.join(savePath,'{}_{}.png'.format(test,i)))
            results[str(test)] = updateResults(results[str(test)], t, lab)
            lab.Q1(80)
            while lab.T1 < T_trip:
                i += 1
                hf.blink(lab,dt=dt)
                t += dt
                ax.plot(t*speedup,lab.T1,style)
                dt = dtUpdate(lab,speedup=speedup)
                hf.updateDisplay(fig, saveFig = True, saveName = os.path.join(savePath,'{}_{}.png'.format(test,i)))
                results[str(test)] = updateResults(results[str(test)], t, lab)
            lab.Q1(0)
            while lab.T1 > 30.0:
                i += 1
                hf.blink(lab,dt=dt)
                t += dt
                ax.plot(t*speedup,lab.T1,style)
                dt = dtUpdate(lab,speedup=speedup)
                hf.updateDisplay(fig, saveFig = True, saveName = os.path.join(savePath,'{}_{}.png'.format(test,i)))
                results[str(test)] = updateResults(results[str(test)], t, lab)
        hf.createGIF(plotName = str(test),path=savePath)