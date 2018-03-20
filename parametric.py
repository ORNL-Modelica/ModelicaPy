# -*- coding: utf-8 -*-
"""
Created on Tue Mar 20 09:56:18 2018

@author: vmg
"""

from dymola.dymola_interface import DymolaInterface
from dymola.dymola_exception import DymolaException

import os
import itertools as it

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
    # Initialize the settings parameters
    simSettings = {}
    for key in standKeys():
            simSettings[key]=None
            
    return simSettings


def checkInput(simSettings):
    # Check for incorrect input types
    if simSettings['initialValues'] != None or simSettings['initialNames'] != None:
        raise NameError('"initialNames" and "initialValues" must not be specified')

    # Check that 'initialNames' and 'initialValues' have not been specified
    for key, val in simSettings.items():
        if type(val) != list and val!=None:
            raise NameError("simSetting['{}'] is '{}' and must be =None or of type 'list'".format(key,type(val)))
 
    
    #for key, val in simSettings.items():
#    print key
#    print val
#    if val != None:
#        print len(val)
#    if key == 'initialValues':
#        if len(val) != len(simSettings['initialNames']):
#            raise NameError('Length of dictionary items "initialNames" and "initialValues" must be equal')

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

   
def test(problem=None, startTime=None, stopTime=None,
                             numberOfIntervals=None, outputInterval=None,
                             method=None, tolerance=None, fixedstepsize=None,
                             resultFile=None, initialNames=None, initialValues=None,
                             finalNames=None, autoLoad=None):
    print('hi')
    
    print problem
    print startTime
    print stopTime
    print numberOfIntervals
    print outputInterval
    print method
    print tolerance
    print fixedstepsize
    print resultFile
    print initialNames
    print initialValues
    print finalNames
    print autoLoad


def simulate(simSettings):
    '''
    User Input: Solver Settings
    All settings, besides `=None`, must be enclosed in brackets []
    !!! 'initialNames' and 'initialValues' are set different than others
    Specify each variable indepenently. The script will generate the tests
    and collapse all 'non-standard' keys.
    '''
    
    # Check User Input
    checkInput(simSettings)
    
    # Generate all experiment permutations
    experimentsRaw = genExperimentsRaw(simSettings)
    
    # Filter experiments to generate key/value pairs for 'initialNames' and 'initialValues'
    experiments = genExperiments(experimentsRaw)
    
    # Run all experiments  
    for i, value in enumerate(experiments):
        #test(**experiments[i])    
        print i
        print value
    
        dymola = None
        try:
            # Instantiate the Dymola interface and start Dymola
            dymola = DymolaInterface()

            #dymola.translateModel(problem)
            # Call a function in Dymola and check its return value
            #result = dymola.simulateModel("TRANSFORM.Fluid.Examples.RankineCycle")
            
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

                os.rename(resultFile, resultFileNew)
                os.rename('dsin.txt', 'dsin{}.txt'.format(i))
                os.rename('dsfinal.txt', 'dsfinal{}.txt'.format(i))
                os.rename('dslog.txt', 'dslog{}.txt'.format(i))
               
        except DymolaException as ex:
            print(("Error: " + str(ex)))
        finally:
            if dymola is not None:
                dymola.close()
                dymola = None
        
if __name__ == "__main__":
    simSettings = initSettings()  
    simSettings['problem']=['TRANSFORM.Fluid.Examples.RankineCycle']
    simSettings['startTime']=None
    simSettings['stopTime']=[1]
    simSettings['numberOfIntervals']=[100]
    simSettings['outputInterval']=None
    simSettings['method']=None
    simSettings['tolerance']=None
    simSettings['fixedstepsize']=None
    simSettings['resultFile']=None
    simSettings['finalNames']=None
    simSettings['autoLoad']=None
    
    simSettings['m_flow']=[100,110]
    simSettings['steamTurbine.eta_mech']=[1,0.95,0.9]   
    
    simulate(simSettings)
    
    
