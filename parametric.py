# -*- coding: utf-8 -*-
"""
Created on Tue Mar 20 09:56:18 2018

@author: Scott Greenwood
"""
from __future__ import division

from dymola.dymola_interface import DymolaInterface
from dymola.dymola_exception import DymolaException

import os
import itertools as it
from shutil import move
import pickle
    
def standKeys():
    '''
    Standard input parameters for dymola.simulateExtendedModel
    '''
    keys = ['problem',
            'startTime',
            'stopTime',
            'numberOfIntervals',
            'outputInterval',
            'method',
            'tolerance',
            'fixedstepsize',
            'resultFile',
            'initialNames',
            'initialValues',
            'finalNames',
            'autoLoad']
    return keys


def initSettings():
    '''
    Initialize the settings parameters as None
    '''
    simSettings = {}
    for key in standKeys():
            simSettings[key]=None
            
    return simSettings

def initSettingsDefaults():
    '''
    Initialize the settings parameters with default values
    '''
    simSettings = {}
    simSettings['problem']=['']
    simSettings['startTime']=[0.0]
    simSettings['stopTime']=[1.0]
    simSettings['numberOfIntervals']=[500]
    simSettings['outputInterval']=[0.0]
    simSettings['method']=['dassl']
    simSettings['tolerance']=[0.0001]
    simSettings['fixedstepsize']=[0.0]
    simSettings['resultFile']=['dsres']
    simSettings['initialNames']=None
    simSettings['initialValues']=None
    simSettings['finalNames']=None
    simSettings['autoLoad']=[True]
            
    return simSettings


def checkInput(simSettings):
    '''
    Check for incorrect input types
    '''
    if simSettings['initialValues'] != None or simSettings['initialNames'] != None:
        raise NameError('"initialNames" and "initialValues" must not be specified')

    # Check that 'initialNames' and 'initialValues' have not been specified
    for key, val in simSettings.items():
        if type(val) != list and val!=None:
            raise NameError("simSetting['{}'] is '{}' and must be =None or of type 'list'".format(key,type(val)))
 
    # Check that multiple inputs are not specified for constrained settings
    if 'problem' in simSettings:
        if simSettings['problem'] != None and len(simSettings['problem']) > 1:
            raise NameError("len(simSetting['problem']) is > 1 and must be =None or 1")
    if 'resultFile' in simSettings:
        if simSettings['resultFile'] != None and len(simSettings['resultFile']) > 1:
            raise NameError("len(simSetting['resultFile']) is > 1 and must be =None or 1")
    if 'autoLoad' in simSettings:
        if simSettings['autoLoad'] != None and len(simSettings['autoLoad']) > 1:
            raise NameError("len(simSetting['autoLoad']) is > 1 and must be =None or 1")


def genExperimentsRaw(simSettings):
    '''
    Remove None and generate all experiment permutations
    '''
    simSettingsfiltered = {k:v for k,v in simSettings.items() if v is not None}
    keys, values = zip(*simSettingsfiltered.items())
    experimentsRaw = [dict(zip(keys, v)) for v in it.product(*values)]
    
    return experimentsRaw
        

def genExperiments(experimentsRaw):
    '''
    Filter experiments to generate key/value pairs for 'initialNames' and 'initialValues'
    '''
    allKeys = standKeys()
    experiments = []
    for i, value in enumerate(experimentsRaw):
        initialNames = []
        initialValues = []
        for key, val in value.items(): 
            if key not in allKeys:
                initialNames.append(key)
                initialValues.append(val)
                value.pop(key)
        value['initialNames']=initialNames
        value['initialValues']=initialValues
        
        experiments.append(initSettings())
        experiments[i].update(value)
                
    return experiments

def renameFiles(simID,i,value,cwdMod,result):
    '''
    Rename the result, dslog, dsin, and dsfinal files and returns the new
    dslog file name for debugging.
    
    i => experiment index
    value => experiment dictionary simSettings
    cwdMod => current working directory of Modelica
    result => boolean success/fail (true/false) of model
    '''
    # Set the new names

#    if simID == '':
#        simID_1 = simID
#        simID_2 = simID
#    else:
#        simID_1 = simID+'_'
#        simID_2 = '_'+simID
        
    if value['resultFile'] == None:
        resultFile = 'dsres.mat'
        resultFileNew = '{}dsres_{}.mat'.format(simID,i)
        dsinNew = '{}dsin_{}.txt'.format(simID,i)
        dsfinalNew = '{}dsfinal_{}.txt'.format(simID,i)
        dslogNew = '{}dslog_{}.txt'.format(simID,i)
    else:
        resultFile = '{}.mat'.format(value['resultFile']) 
        resultFileNew = '{}{}_{}.mat'.format(simID,value['resultFile'],i)
        dsinNew = '{}{}_dsin_{}.txt'.format(simID,value['resultFile'],i)
        dsfinalNew = '{}{}_dsfinal_{}.txt'.format(simID,value['resultFile'],i)
        dslogNew = '{}{}_dslog_{}.txt'.format(simID,value['resultFile'],i)
    
    # Rename dsin.txt and dslog.txt
    try:
        move(os.path.join(cwdMod,'dsin.txt'), os.path.join(cwdMod,dsinNew))
    except:
        print('Error: dsin.txt cannot be found. Looking in-> {}'.format(cwdMod))         
    try:
        move(os.path.join(cwdMod,'dslog.txt'), os.path.join(cwdMod,dslogNew))
    except:
        print('Error: dslog.txt cannot be found. Looking in-> {}'.format(cwdMod))            
    try:
        move(os.path.join(cwdMod,resultFile), os.path.join(cwdMod,resultFileNew))                
    except:
        print('Error: {} cannot be found. Looking in-> {}'.format(resultFile,cwdMod))
        
    # Rename dsfinal.txt and dsres.txt        
    if result:
        try:
            move(os.path.join(cwdMod,'dsfinal.txt'), os.path.join(cwdMod,dsfinalNew))
        except:
            print('Error: dsfinal.txt cannot be found. Looking in-> {}'.format(cwdMod))
#        try:
#            move(os.path.join(cwdMod,resultFile), os.path.join(cwdMod,resultFileNew))                
#        except:
#            print('Error: {} cannot be found. Looking in-> {}'.format(resultFile,cwdMod))
            
    return dslogNew
    
def loadPickle(pickleName='experiments.pickle',picklePath=''):
    with open(os.path.join(picklePath,pickleName), 'rb') as handle:
        experiments = pickle.load(handle)
    return experiments
        
def simulate(simSettings,showWindow=False,closeWindow=True,simID='',seed=0,singleTranslate=True):
    '''
    
    simSettings => dictionary of setting parameters (see below for details)
    showWindow  => =True to launch Dymola GUI
    closeWindow => =False to prevent auto-closing of the Dymola GUI when done
    simID       => simulation ID to differentiate output files (e.g., simID_dsres0.mat vs. dsres0.mat)
    seed        => starting seed value for output file naming (e.g., seed+0, ..., seed+len(experiments))
    singleTranslate => =True to only translate the model once
    
    - !!! If variables needed to be changed require retranslation then add them to problem name.
    i.e., simSettings['problem']=['Example.Test(var1=1,var2=5)'] or try to set 'annotation(Evaluate=false)' in the model
    
    simSettings details:
    - All settings, besides `=None`, must be enclosed in brackets []
    
    - !!! 'initialNames' and 'initialValues' are set different than others.
    Specify each variable indepenently. The script will generate the tests
    and collapse all 'non-standard' keys.
    
    - 'problem', 'resultFile', and 'autoLoad' only support 1 or None entries
    
    - Only specify 'numberOfIntervals' or 'outputInterval', not both
    
    - 'fixedstepsize' is only for fixed step size solvers 
    
    - showWindow=True and closeWindow=False only a specified number of simulations
    are retained in memory according, not all simulations.
    
    - The experiments generated are a list of dictionaries which are saved
    as experiments.pickle in the working directory of the Modelica simulation (cwdMOD).
    To open the pickle in python:
        
    with open(os.path.join('PATHTOPICKLE,'experiments.pickle'), 'rb') as handle:
        experiments = pickle.load(handle)
    
    - !!! Settings not specified assume Dymola default settings.
    Any simulation settings (tolerance, solver, etc.) located in the model
    are ignored.
        
    Default Settings:
    'problem' = ''             => Modelica file (.mo) to be run (e.g., ['TRANSFORM.Fluid.Examples.RankineCycl'] )
    'startTime' = 0            => Start time of simulation
    'stopTime' = 1             => Stop time of simulation
    'numberOfIntervals' = 500  => Number of intervals to be saved to result file
    'outputInterval' = 0       => Time (seconds) between intervals to be saved to result file
    'method' = 'dassl'         => Solver
    'tolerance' = 0.0001       => Solver tolerance
    'fixedstepsize' = 0        => Step size for solver (certain solvers only, e.g., Euler)
    'resultFile' = 'dsres.mat' => Name of the result file
    'initialNames' = ''        => Names of variables in model
    'initialValues' = ''       => Value of variables in model (len(initialNames) = len(initialValues))
    'finalNames' = ''          => Variable for Dymola to print to screen when simulation is finished
    'autoLoad' = true          => Automatically load (true) the result file into the Dymola plot window
    
    Possible Methods:
    'methods' = Lsodar, dassl, Euler, Rkfix2, Rkfix3, Rkfix4,
                Esdirk23a, Esdirk34a, Esdirk45a, Dopri45, Dopri853,
                Sdirk34hw, Cerk23, Cerk34, Cerk34, Cvode
    
     For the current supported solvers and their use see Dymola
     '''
    
    # Check User Input
    checkInput(simSettings)
    try:
        if int(seed) >= 0:
            seed = int(seed)
        else:
            raise NameError("seedNum must be a positive integer")
    except:
        raise NameError("seedNum must be a positive integer")
    
    # Modify simID for naminc conventions
    if simID != '':
        simID = simID+'_'
            
    # Generate all experiment permutations
    experimentsRaw = genExperimentsRaw(simSettings)
    
    # Filter experiments to generate key/value pairs for 'initialNames' and 'initialValues'
    experiments = genExperiments(experimentsRaw)
        
    # Instantiate the Dymola interface and start Dymola
    dymola = None
    result_tran = False
    try:
        
        # Open Dymola
        dymola = DymolaInterface(showwindow=showWindow)
        
        # Get working directory
        cwdMod = dymola.ExecuteCommand('Modelica.Utilities.System.getWorkDirectory();')

        # Translate the model
        if singleTranslate:
            result_tran = dymola.translateModel(experiments[0]['problem'])
            if not result_tran:
                raise Exception("Translation failed. Aborting parametric simulation. Investigate model in IDE for details.")
            
        # Run all experiments
        saveResult=[]
        j = seed
        print('Total experiments = {} for simID = "{}"'.format(len(experiments),simID))
        print('Experiment numbering started at seed = {}'.format(seed))
        for i, value in enumerate(experiments):
            j = seed + i
            print('Experiment {} (= {}/{})'.format(j,i+1,len(experiments)))
            print(value)
                   
           # ModelTranslate = "Dymola.Path.To.Your.Model(Dymola.Path.to.Variable=1000)"
            if not singleTranslate:
                result_tran = False
                result_tran = dymola.translateModel(value['problem'])
                if not result_tran:
                    print("Translation failed. Aborting parametric simulation. Investigate model in IDE for details.")
                    break
                
            # Simulate the model
            result = dymola.simulateExtendedModel(**value)[0]
            
            # Save the result (success/fail)
            saveResult.append(result)
            
            # Rename the log files and return new log file for debugging ref.
            dslogNew = renameFiles(simID,j,value,cwdMod,result)     
                
            # Print last line of error
            if not result:
                print("Simulation failed. Below is the translation log. For more details see: {}".format(dslogNew))
                log = dymola.getLastErrorLog()
                print('### Log Start ###\n' + log + '### Log End ###')
                      
    except DymolaException as ex:
        print(("Error: " + str(ex)))
    except Exception as inst:
        print('{}'.format(inst.message))
    finally:
        if dymola is not None:
            if showWindow == True and closeWindow == False:
                pass
            else:
                dymola.close()

    if result_tran:    
        # Save experiment dictionary as pickle in cwdMod
        with open(os.path.join(cwdMod,'{}experiments_{}to{}.pickle'.format(simID,seed,j)), 'wb') as handle:
            pickle.dump(experiments, handle, protocol=pickle.HIGHEST_PROTOCOL)    
    
        # Save summary off success/fail (true/false) of simulations
        with open(os.path.join(cwdMod,'{}summary_{}to{}.txt'.format(simID,seed,j)),'w') as fil:
            fil.write('Summary of success/fail (true/false) of experiments\n')
            for i, val in enumerate(saveResult):
                fil.write('\t'.join(['Experiment','{}'.format(i),'{}'.format(val)]) + '\n')

if __name__ == "__main__":
    
    # Initialize simulation settings (not required): 2 methods
    #simSettings = initSettings()  
    simSettings=initSettingsDefaults()
    
    # Specify files. Only 1 or None
    simSettings['problem']=['TRANSFORM.Fluid.Examples.RankineCycle']
    simSettings['resultFile']=['dummy']
    simSettings['autoLoad']=[False]
    
    # Specify simulation settings
    # (if unchanged from init/default then does not need to be specified)
    simSettings['startTime']=None
    simSettings['stopTime']=[100]
    simSettings['numberOfIntervals']=[100]
    simSettings['outputInterval']=None
    simSettings['method']=None
    simSettings['tolerance']=None
    simSettings['fixedstepsize']=None
    simSettings['finalNames']=None

    # Specify parameters (instead of 'initialNames' and 'initialValues')
    simSettings['m_flow']=[100,110]
    simSettings['steamTurbine.eta_mech']=[1,9/10]   
    
    # Generate parametric simulation
    simulate(simSettings,showWindow=False,closeWindow=False,simID='Test',seed=4,singleTranslate=False)
    
    
