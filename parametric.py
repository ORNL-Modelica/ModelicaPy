# -*- coding: utf-8 -*-
"""
Created on Tue Mar 20 09:56:18 2018

@author: vmg
"""

from dymola.dymola_interface import DymolaInterface
from dymola.dymola_exception import DymolaException

import os
import itertools as it
from shutil import move
import pickle
    
def standKeys():
    # Standard input parameters for dymola.simulateExtendedModel
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
    # Initialize the settings parameters as None
    simSettings = {}
    for key in standKeys():
            simSettings[key]=None
            
    return simSettings

def initSettingsDefaults():
    # Initialize the settings parameters with default values
    simSettings = {}
    simSettings['problem']=['']
    simSettings['startTime']=[0.0]
    simSettings['stopTime']=[1.0]
    simSettings['numberOfIntervals']=[500]
    simSettings['outputInterval']=[0.0]
    simSettings['method']=['dassl']
    simSettings['tolerance']=[0.0001]
    simSettings['fixedstepsize']=[0.0]
    simSettings['resultFile']=['dsres.mat']
    simSettings['initialNames']=None
    simSettings['initialValues']=None
    simSettings['finalNames']=None
    simSettings['autoLoad']=[True]
            
    return simSettings


def checkInput(simSettings):
    # Check for incorrect input types
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
    # Remove None and generate all experiment permutations
    simSettingsfiltered = {k:v for k,v in simSettings.items() if v is not None}
    keys, values = zip(*simSettingsfiltered.items())
    experimentsRaw = [dict(zip(keys, v)) for v in it.product(*values)]
    
    return experimentsRaw
        

def genExperiments(experimentsRaw):
    # Filter experiments to generate key/value pairs for 'initialNames' and 'initialValues'
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


def simulate(simSettings,showWindow=False,closeWindow=True):
    '''
    User Input: Solver Settings
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
    
    # Generate all experiment permutations
    experimentsRaw = genExperimentsRaw(simSettings)
    
    # Filter experiments to generate key/value pairs for 'initialNames' and 'initialValues'
    experiments = genExperiments(experimentsRaw)
        
    # Instantiate the Dymola interface and start Dymola
    dymola = None
    try:
        
        # Open Dymola
        dymola = DymolaInterface(showwindow=showWindow)
        
        # Get working directory
        cwdMod = dymola.ExecuteCommand('Modelica.Utilities.System.getWorkDirectory();')

        # Translate the model
        dymola.translateModel(experiments[0]['problem'])
        
        # Run all experiments  
        for i, value in enumerate(experiments):
    
            print(i)
            print(value)
        
            # Instantiate the Dymola interface and start Dymola
            # dymola = DymolaInterface(showwindow=showWindow)
            
            result = dymola.simulateExtendedModel(**value)
        
            if not result:
                print("Simulation failed. Below is the translation log.")
                log = dymola.getLastErrorLog()
                print(log)
                exit(1)
            else:
                if value['resultFile'] == None:
                    resultFile = 'dsres.mat'                    
                else:
                    resultFile = '{}.mat'.format(value['resultFile']) 
                resultFileNew = 'dsres{}.mat'.format(i)
                
                try:
                    move(os.path.join(cwdMod,resultFile), os.path.join(cwdMod,resultFileNew))
                    move(os.path.join(cwdMod,'dsin.txt'), os.path.join(cwdMod,'dsin{}.txt'.format(i)))
                    move(os.path.join(cwdMod,'dsfinal.txt'), os.path.join(cwdMod,'dsfinal{}.txt'.format(i)))
                    move(os.path.join(cwdMod,'dslog.txt'), os.path.join(cwdMod,'dslog{}.txt'.format(i)))
                except:
                    print('Error: Result and log files cannot be found. Looking in-> {}'.format(os.getcwd()))
    
    except DymolaException as ex:
        print(("Error: " + str(ex)))
    finally:
        if dymola is not None:
            if showWindow == True and closeWindow == False:
                pass
            else:
                dymola.close()
    
    # Save experiment dictionary as pickle in cwdMod
    with open(os.path.join(cwdMod,'experiments.pickle'), 'wb') as handle:
        pickle.dump(experiments, handle, protocol=pickle.HIGHEST_PROTOCOL)    
        
if __name__ == "__main__":
    
    # Initialize simulation settings (not required): 2 methods
    #simSettings = initSettings()  
    simSettings=initSettingsDefaults()
    
    # Specify files. Only 1 or None
    simSettings['problem']=['TRANSFORM.Fluid.Examples.RankineCycle']
    simSettings['resultFile']=None
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
    simSettings['steamTurbine.eta_mech']=[1,0.9]   
    
    # Generate parametric simulation
    simulate(simSettings,showWindow=True,closeWindow=False)
    
    
