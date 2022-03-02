# -*- coding: utf-8 -*-
"""
Created on Tue Mar  1 15:54:01 2022

@author: Scott Greenwood
"""

import tclab
from IPython.display import display, clear_output
import time
import os, shutil
import imageio
import re
import numpy as np
import matplotlib.pyplot as plt
import pickle
  
degree_sign = u'\N{DEGREE SIGN}'

#%% TCLab
def connectLab(connected=False, speedup = 100):
    '''Connect to the TCLab hardware or emulator. Speedup only impacts the emulator'''
    if connected:
        mlab = tclab.TCLab      # Physical hardware
    else:
        mlab = tclab.setup(connected=False, speedup = speedup) # Emulator
    return mlab

def safeShutdown(lab):
    '''Safely shutdown the arduino'''    
    lab.Q1(0)
    lab.Q2(0)
    print('Shutting down')
    lab.close()
        
def blink(lab,vals=[100,0],dt=5.0):
    '''Blink LED from [max,min] value holding the max value for dt seconds'''
    lab.LED(vals[0])
    time.sleep(dt)
    lab.LED(vals[1]) 

#%% FMU - FMPy
def createInputs(inputList,dtype):
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

#%% Miscellaneous
def createFolder(folderPath, clear = False):
    '''Create path if exists else clear path if enabled'''
    if not os.path.exists(folderPath):
        os.makedirs(folderPath)
    else:
        if clear:
            shutil.rmtree(folderPath)
  
def pickleResults(results = None, path='plots/results.pickle', read=True):
    '''Write or read pickle of dictionary of results'''
    if read:
        with open(path, 'rb') as handle:
            return pickle.load(handle)
    else:
        with open(path, 'wb') as handle:
            pickle.dump(results, handle, protocol=pickle.HIGHEST_PROTOCOL)
            
#%% Plotting
def updateDisplay(fig, saveFig = False, saveName = ''):
    ''' Clear and update output'''
    display(fig)
    if saveFig:
        fig.savefig(saveName)
    clear_output(wait = True)
    
def createGIF(plotName = 'image',path='plots',iStart=0):
    ''' Create a GIF from images with plotName followed by numbering (e.g., image_0.png, image_1.png, etc.)'''
    # Get the list of all files and directories
    dirList = os.listdir(path)
    fileREGEX = plotName + '_\d*.png'
    # Get only result files and record the simulation order
    files = []
    for file in dirList:
        if re.match(fileREGEX,file):
            order = int(re.search('\d+', file[iStart:]).group())
            files.append((os.path.join(path,file),order))
    # Sort in ascending order
    files.sort(key=lambda tup: tup[1])

    images = []
    for file in files:
        images.append(imageio.imread(file[0]))
    imageio.mimsave(os.path.join(path,plotName+'.gif'), images)
    
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