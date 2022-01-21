# -*- coding: utf-8 -*-
"""
Created on Fri Dec  4 11:39:25 2020

@author: vmg

Note - FMU optimization requires binary export license and for it to be enabled
"""
import os
from dymola.dymola_interface import DymolaInterface
import re
import shutil, errno
import os
import numpy as np
from collections import OrderedDict
'''
TODO
- path names are wonky. will need to address proper way to place "problem" when not at highest level of packge. This will also reduce the packagename+problem issue
- using Dymola to optimize (instead of FMU) is not working as there is some strange python to modelica conversion issues with the dymola python package (or so it seems)
- parallelize optimization
- cleanup directory option
'''

def copyAnything(src, dst):
    try:
        shutil.copytree(src, dst)
    except OSError as exc: # python >2.5
        if exc.errno == errno.ENOTDIR:
            shutil.copy(src, dst)
        else: raise



def createDirectory(tempDir):
    '''
    # Create temporary directory.
    '''
    if not os.path.exists(tempDir):
        os.makedirs(tempDir)


def copyPackageToTemp(PackagePath,PackageName,tempDir):
    '''
    # Copy package of interest. This will be the working copy of the package
    '''
    # Remove existing package for optimization
    shutil.rmtree(os.path.join(tempDir,PackageName), ignore_errors=True)
    
    # Copy package for optimization
    copyAnything(os.path.join(PackagePath,PackageName),os.path.join(tempDir,PackageName))


def readProblemMO(PackageName,tempDir,problem):
    '''
    Read model and gather values to be changed
    '''
    # Read file
    with open(os.path.join(tempDir,PackageName,problem+'.mo'),'r')as fil:
       lines = fil.readlines()
    lines = [l.replace('\n','') for l in lines]
    
    # Locate and extract parameters for consideration
    for i,l in enumerate(lines):
        if '// Optimize' in l:
            i_start = i
        elif '// End Optimize' in l:
            i_end = i
    
    # Get content between markers
    lines_opt = lines[i_start+1:i_end]
    
    # Combine into single string
    lines_opt_combined = re.sub(' +', ' ', ''.join(lines_opt))
    
    # Convert to dictionary based on delimiters
    optDict = {}
    for l in lines_opt_combined.split(';'):
        temp = l.split('=')
        if len(temp) > 1:
            optDict[temp[0].strip()] = temp[1].strip()
    return optDict, i_start, i_end, lines


def createNewModels(varName,optDict,i_start,i_end,lines):
    '''
    '''
    modelList = {}
    for i, o in enumerate(options):
        fileName = problem+'_{}'.format(i)
        optDict[varName]=o
        
        # Recreate the new optimization section
        lines_opt_new = []
        for key, val in optDict.items():
            lines_opt_new.append(key+' = '+val+';')
        
        # Find model and rename
        i_modelName = lines.index('model '+ problem)
        i_modelEnd = lines.index('end '+ problem+';')
        
        # Create the lines for the new model
        lines_new = []
        for l in lines[0:i_modelName]:
            lines_new.append(l)
        lines_new.append('model '+fileName)
        for l in lines[i_modelName+1:i_start+1]:
            lines_new.append(l)
        for l in lines_opt_new:
            lines_new.append(l)
        for l in lines[i_end:i_modelEnd]:
            lines_new.append(l)
        lines_new.append('end '+fileName+';')
        
        # Create the new model
        with open(os.path.join(tempDir,PackageName,fileName+'.mo'),'w') as fil:
            fil.writelines('\n'.join(lines_new))
            
        # Add new model to package.order
        with open(os.path.join(tempDir,PackageName,'package.order'),'a') as fil:
            fil.write('\n'+fileName)
        modelList[fileName] = {}
        modelList[fileName]['varName'] = varName
        modelList[fileName]['option'] = o
        modelList[fileName]['identifier'] = i 
    return modelList
   
def modelCreationWorkflow(PackagePath,PackageName,tempDir,problem,varName,options):
    '''
    '''
    createDirectory(tempDir)
    copyPackageToTemp(PackagePath,PackageName,tempDir)
    optDict,i_start,i_end,lines = readProblemMO(PackageName,tempDir,problem)
    modelList = createNewModels(varName,optDict,i_start,i_end,lines)
    return modelList


def runModelList(tempDir,PackageName,modelList,initialNames={},initialValues={}):
    '''
    Ensure all needed supporting libraries are part of startup script.
    '''
    dymola = DymolaInterface()
    dymola.openModel(os.path.join(tempDir,PackageName,'package.order'), changeDirectory=False)

    runModelList_noAutoDymola(dymola,tempDir,PackageName,modelList,initialNames={},initialValues={})

    dymola.close()

def runModelList_noAutoDymola(dymola,tempDir,PackageName,modelList,initialNames={},initialValues={}):
    '''
    Ensure all needed supporting libraries already loaded.
    '''
    for problem in modelList.keys():
        model = PackageName+'.'+problem
        dymola.translateModel(model)
        result = dymola.simulateExtendedModel(model,resultFile=problem,initialNames=initialNames,initialValues=initialValues)
        #result = dymola.simulateModel(model,resultFile=problem)
        if not result:
            print("Simulation failed. Below is the translation log.")
            log = dymola.getLastErrorLog()
            print(log)
    
from buildingspy.io.outputfile import Reader
def compareModelListResults(modelList,goldValues):
    '''
    '''
    compareDict = {}
    for problem in modelList.keys():
        r = Reader(problem+'.mat','dymola')
        compareDict[problem] = {}
        sumError = 0
        for name in goldValues.keys():
            compareDict[problem][name] = {}
            compareDict[problem][name]['finalValue']=r.values(name)[1][-1]
            compareDict[problem][name]['goldDiff'] = compareDict[problem][name]['finalValue'] - goldValues[name]
            compareDict[problem][name]['goldDiffRelative'] = compareDict[problem][name]['goldDiff']/goldValues[name]
            sumError = sumError + np.abs(compareDict[problem][name]['goldDiffRelative'])
        compareDict[problem]['errorSum'] = sumError
    return compareDict


def selectBestModel(compareDict,finalNames):
    '''
    '''
    bestModel = {}
    
    for i, problem in enumerate(compareDict.keys()):
        if i == 0:
            bestModel = problem
        else:
            if compareDict[bestModel]['errorSum'] > compareDict[problem]['errorSum']:
                bestModel = problem
    return bestModel

   
def optimizeGold():
    '''
    '''
    pass
    
def _optimizeCFs(cs,*params): 
    '''
    # Function to be minimized
    '''
    
    initialValues = {val for val in cs}
    tempDir,PackageName,modelList,problem,goldValues,mapping,initialNames,dymola  = params
    modelList_single = {problem:modelList[problem]}
    # Run the model       
    runModelList_noAutoDymola(dymola,tempDir,PackageName,modelList_single,initialNames,initialValues) # need to add updated CFs somehow
    # Get results
    compareDict = compareModelListResults(modelList_single,goldValues)
    # Get error
    error = []
    for i in range(len(cs)):
        name = mapping['CFs[{}]'.format(i)]
        error.append(compareDict[problem][name]['goldDiffRelative'])
    return error
    

def _optimizeCFs_FMU(cs,*params): 
    '''
    # Function to be minimized
    '''
    
    problem,goldValues,mapping  = params
    
    fmu  = problem + '.fmu'
    outputs = goldValues.keys()
    start_values={}
    for i in range(len(cs)):
        start_values['CFs[{}]'.format(i+1)] = cs[i]
        
    # Run the model       
    result = fmpy.simulate_fmu(fmu,output=outputs,start_values=start_values)
    # Get results
    compareDict = compareModelListResults_FMU(problem,result,goldValues)
    # Get error
    error = []
    for i in range(len(cs)):
        name = mapping['CFs[{}]'.format(i+1)]
        error.append(compareDict[problem][name]['goldDiffRelative'])
        
    print(cs)
    return error


def compareModelListResults_FMU(problem,result,goldValues):
    '''
    '''
    compareDict = {}
    compareDict[problem] = {}
    sumError = 0
    for name in goldValues.keys():
        compareDict[problem][name] = {}
        compareDict[problem][name]['finalValue']=result[name][-1]
        compareDict[problem][name]['goldDiff'] = compareDict[problem][name]['finalValue'] - goldValues[name]
        compareDict[problem][name]['goldDiffRelative'] = compareDict[problem][name]['goldDiff']/goldValues[name]
        sumError = sumError + np.abs(compareDict[problem][name]['goldDiffRelative'])
    compareDict[problem]['errorSum'] = sumError
    return compareDict


if __name__ == '__main__':

    
    ### Setup the problem
    PackagePath = "C:\\Users\\greems\\Documents\\Dymola"
    PackageName = "OptimizationDemonstration"
    problem='Demo_1'
    tempDir = 'temp' #  Placed in current working directory
    
    varName = "replaceable model HeatTransfer"
    options = \
    ["TRANSFORM.Fluid.ClosureRelations.HeatTransfer.Models.DistributedPipe_1D_MultiTransferSurface.Nus_SinglePhase_2Region",
     "TRANSFORM.Fluid.ClosureRelations.HeatTransfer.Models.DistributedPipe_1D_MultiTransferSurface.Alphas"]

    ### Create a list of models to be run
    modelList = modelCreationWorkflow(PackagePath,PackageName,tempDir,problem,varName,options)

    ### Run simulations
    runModelList(tempDir,PackageName,modelList)
    
    ### Create a comparison of the results to desired values
    nV = 10
    vals = np.linspace(300,350,nV)
    goldValues = {}
    for i, val in enumerate(vals):
        goldValues["pipe.mediums[{}].T".format(i+1)] = val
 
    compareDict = compareModelListResults(modelList,goldValues)
    
    ### Find and record the best model
    bestModel = selectBestModel(compareDict,goldValues.keys())
    
    print('The best model is {}.\nThe total relative error sum for compared golden values = {:.2f} '.format(bestModel,compareDict[bestModel]['errorSum']))
        
    ### Optimize correction coefficients to improve model performance
    from scipy import optimize
        
    # Name of parameters that will be changed
    initialNames = {'CFs[{}]'.format(s+1) for s in range(nV)}
    x0 = np.ones(nV) # guess value 
    x_scale = np.ones(nV)
    
    # Required to map results to error in proper order (I think this is required \_O_/)
    mapping = {}
    for i in range(nV):
        mapping['CFs[{}]'.format(i+1)] =  "pipe.mediums[{}].T".format(i+1)
        
    use_FMU = True
    if not use_FMU:
        dymola = DymolaInterface(showwindow=False)
        dymola.openModel(os.path.join(tempDir,PackageName,'package.order'), changeDirectory=False)

        args = (tempDir,PackageName,modelList,bestModel,goldValues,mapping,initialNames,dymola)
        
        cs = optimize.least_squares( _optimizeCFs, x0,args=args,method='lm',x_scale=x_scale) 
    
        dymola.close()
        
    else:
        
        # Create FMU
        dymola = DymolaInterface(showwindow=False)
        dymola.openModel(os.path.join(tempDir,PackageName,'package.order'), changeDirectory=False)
        
        model = PackageName+'.'+bestModel
        dymola.translateModelFMU(model, False, bestModel, "2", "csSolver", False, 0);
        dymola.close()
        
        # Optimize
        import fmpy

        args = (bestModel,goldValues,mapping)
        
        cs = optimize.least_squares( _optimizeCFs_FMU, x0,args=args,method='trf',x_scale=x_scale,bounds=(0,100))