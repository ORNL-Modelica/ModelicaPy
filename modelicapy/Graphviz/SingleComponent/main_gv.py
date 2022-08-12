# -*- coding: utf-8 -*-
"""
Created on Tue Aug  9 09:50:01 2022

@author: ScottGreenwood
"""
import os
import glob
from SearchMOFile_gv import searchFile
import graphviz 

directories = [r'C:/Users/ScottGreenwood/Documents/Projects/Modelon/SVN/P509-ML',
             r'C:/Users/ScottGreenwood/Documents/Projects/Modelon/SVN/P504-TPL']
# directory = '.'
DIRNames = ['Modelon','ThermalPower']
colors = {'Modelon':'#FFC633',
          'ThermalPower':'#ADE11D'}

useDIRName = True
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
componentList = [(0,'Modelon.ThermoFluid.FlowChannels.StaticPipe'),
                 (0,'Modelon.ThermoFluid.FlowChannels.SimplePipe'),
                 (0,'Modelon.ThermoFluid.FlowChannels.DistributedChannel'),
                 (0,'Modelon.ThermoFluid.FlowChannels.DistributedPipe'),
                 (0,'Modelon.ThermoFluid.FlowChannels.DistributedTwoPhase'),
                 (0,'Modelon.ThermoFluid.FlowChannels.DistributedTwoPhaseMB'),
                 (0,'Modelon.ThermoFluid.FlowChannels.DistributedDelayPipe'),
                 (0,'Modelon.ThermoFluid.FlowChannels.AnalyticMoistAirChannel'),
                 (0,'Modelon.ThermoFluid.FlowChannels.ParallelChannels'),
                 (0,'Modelon.ThermoFluid.FlowChannels.ParallelAnalyticMoistAirChannels'),
                 (0,'Modelon.ThermoFluid.FlowChannels.PipeDiscreteTLumpedP'),
                 (0,'Modelon.ThermoFluid.FlowChannels.StaticHeatTransfer'),
                 (0,'Modelon.ThermoFluid.FlowChannels.TransportDelayPipe'),
                 (0,'Modelon.ThermoFluid.FlowChannels.StaticHeatTransferMoistAir'),
                 (0,'Modelon.ThermoFluid.FlowChannels.DistributedTwoPhaseMetaStable'),
                 (1,'ThermalPower.FlueGas.FlowChannels.Pipe'),
                 (1,'ThermalPower.FlueGas.FlowChannels.Pipe_lumpedP'),
                 (1,'ThermalPower.TwoPhase.FlowChannels.LongLineMOC'),
                 (1,'ThermalPower.TwoPhase.FlowChannels.DualPipe_dynamicDelay'),
                 (1,'ThermalPower.TwoPhase.FlowChannels.Pipe'),
                 (1,'ThermalPower.TwoPhase.FlowChannels.Pipe_bends'),
                 (1,'ThermalPower.TwoPhase.FlowChannels.Pipe_dynamicDelay'),
                 (1,'ThermalPower.TwoPhase.FlowChannels.Pipe_lumpedP'),
                 (1,'ThermalPower.SeparationProcess.Pipes.Pipe'),
                 (1,'ThermalPower.SeparationProcess.Pipes.StaticPipeWithDelay')]
fileList = []
for component in componentList:
    fileList.append(os.path.join(directories[component[0]],component[1].replace('.','/')+'.mo'))
    
fileList_orig = fileList
itMax = 10
it = 0
dot = graphviz.Digraph(comment='Parent to Daughter Decay',engine='dot',format='png')

while it < itMax:
    fileList_new = []
    for file in fileList:
        if file not in fileList_new:
            fileList_new.append(file)
            
        DIRName = file.split('\\')[1].split('/')[0]
        
        attributes_edge={}
        attributes_edge['constraint']='true'
        
        attributes_node={}
        if file in fileList_orig:
            attributes_node['fillcolor'] = colors[DIRName]
            attributes_node['style'] = 'filled'
            # attributes_node['rank'] = 'same'
        # attributes_node['label'] = file.split('/')[-1].split('.')[0]
        
        resultName, dot = searchFile(dot, attributes_edge, attributes_node, file, useDIRName, DIRName, usePeriod, resultFolder)
        
        newFiles = []
        for val in resultName:
            directory = directories[DIRNames.index(val.split('.')[0])]                
            file_new = os.path.join(directory,'{}.mo'.format(val.replace('.','/')))
            if file_new not in fileList_new:
                fileList_new.append(file_new)
    if fileList==fileList_new:
        print('Completed in {} iterations'.format(it))
        break
    else:
       fileList=fileList_new 
       dot.clear()
    it += 1    
    
#%%
dot.render('temp/graph', view=False)

# #%% Condense information to one master file
# list_of_files = glob.glob(resultFolder+'/*.txt')
# with open('DepMaster.gv', 'w') as outputFile:
#     outputFile.write('digraph DepMaster { \n')
#     # print('size="6,6";', file=outputFile)
#     outputFile.write('node [color=lightblue2, style=filled];\n')

#     outputFile.write('')  # add a blank line for visual separation

#     for fileName in list_of_files:
#         with open(fileName, 'r') as f:
#             lines = f.read().splitlines()
#             for i in range(0, len(lines)):
#                 outputFile.write(lines[i]+'\n')

#     outputFile.write('\n}')