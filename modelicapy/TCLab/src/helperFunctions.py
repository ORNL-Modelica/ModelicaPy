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
    
degree_sign = u'\N{DEGREE SIGN}'

def connectLab(connected=False, speedup = 100):
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
    
def updateDisplay(fig, saveFig = False, saveName = ''):
    ''' Clear and update output'''
    display(fig)
    if saveFig:
        fig.savefig(saveName)
    clear_output(wait = True)
    
def blink(lab,vals=[100,0],dt=5.0):
    '''Blink LED from [max,min] value holding the max value for dt seconds'''
    lab.LED(vals[0])
    time.sleep(dt)
    lab.LED(vals[1]) 
    
def createFolder(folderPath):
    if not os.path.exists(folderPath):
        os.makedirs(folderPath)
    else:
        shutil.rmtree(folderPath)
        
def _createGIF(plotName = 'controlSolution',path='plots',iStart=0):
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