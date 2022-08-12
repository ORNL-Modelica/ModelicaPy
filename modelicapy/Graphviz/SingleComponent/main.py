# -*- coding: utf-8 -*-
"""
Created on Tue Aug  9 09:50:01 2022

@author: ScottGreenwood
"""
import os
import glob
from SearchMOFile import searchFile

directory = r'C:/Users/ScottGreenwood/Documents/Projects/Modelon/SVN/P509-ML'
# directory = '.'
useDIRName = True
DIRName = 'Modelon'
usePeriod = False

# Clear and create result folder
resultFolder = 'dependencies'
if not os.path.exists(resultFolder):
    os.mkdir(resultFolder)

for the_file in os.listdir(resultFolder):
    file_path = os.path.join(resultFolder, the_file)
    try:
        if os.path.isfile(file_path):
            os.unlink(file_path)
        # elif os.path.isdir(file_path): shutil.rmtree(file_path)
    except Exception as e:
        print(e)

#%%        
depFiles = os.listdir(resultFolder)
depFiles_new = []
itMax = 5

#%%
componentList = ['Modelon.ThermoFluid.FlowChannels.StaticPipe',
                 'Modelon.ThermoFluid.FlowChannels.SimplePipe',
                 'Modelon.ThermoFluid.FlowChannels.DistributedChannel',
                 'Modelon.ThermoFluid.FlowChannels.DistributedPipe',
                 'Modelon.ThermoFluid.FlowChannels.DistributedTwoPhase',
                 'Modelon.ThermoFluid.FlowChannels.DistributedTwoPhaseMB',
                 'Modelon.ThermoFluid.FlowChannels.DistributedDelayPipe',
                 'Modelon.ThermoFluid.FlowChannels.AnalyticMoistAirChannel',
                 'Modelon.ThermoFluid.FlowChannels.ParallelChannels',
                 'Modelon.ThermoFluid.FlowChannels.ParallelAnalyticMoistAirChannels',
                 'Modelon.ThermoFluid.FlowChannels.PipeDiscreteTLumpedP',
                 'Modelon.ThermoFluid.FlowChannels.StaticHeatTransfer',
                 'Modelon.ThermoFluid.FlowChannels.TransportDelayPipe',
                 'Modelon.ThermoFluid.FlowChannels.StaticHeatTransferMoistAir',
                 'Modelon.ThermoFluid.FlowChannels.DistributedTwoPhaseMetaStable',
                 ]
fileList = []
for component in componentList:
    fileList.append(os.path.join(directory,component.replace('.','/')+'.mo'))
itMax = 10
it = 0
while it < itMax:
    fileList_new = []
    for file in fileList:
        if file not in fileList_new:
            fileList_new.append(file)
        resultName = searchFile(file, useDIRName, DIRName, usePeriod, resultFolder)
        newFiles = []
        for val in resultName:
            file_new = os.path.join(directory,'{}.mo'.format(val.replace('.','/')))
            if file_new not in fileList_new:
                fileList_new.append(file_new)
    if fileList==fileList_new:
        print('Completed in {} iterations'.format(it))
        break
    else:
       fileList=fileList_new 
    it += 1    
    
#%% Condense information to one master file
list_of_files = glob.glob(resultFolder+'/*.txt')
with open('DepMaster.gv', 'w') as outputFile:
    outputFile.write('digraph DepMaster { \n')
    # print('size="6,6";', file=outputFile)
    outputFile.write('node [color=lightblue2, style=filled];\n')

    outputFile.write('')  # add a blank line for visual separation

    for fileName in list_of_files:
        with open(fileName, 'r') as f:
            lines = f.read().splitlines()
            for i in range(0, len(lines)):
                outputFile.write(lines[i]+'\n')

    outputFile.write('\n}')