# -*- coding: utf-8 -*-
"""
Created on Tue Jan 11 09:03:37 2022

@author: Scott Greenwood
"""

from fmpy import simulate_fmu
import numpy as np
import pandas as pd  
import sys 
import re
   
    
def simulateFMU(inputFileName,input=None,set_input_derivatives=False):
    '''
    Read an input file of a specific format, update setting values, simulate the FMU, and output results.

    *Note* - Current flexibility, i.e., for time depedent inputs is not handled but could be by modifying/expanding
    this file or perhaps creating a RAVEN interface specifically for pyfmi or, preferably, the FMI standard.

    inputFileName = 'referenceInput.txt' (default)
    outputFileName = 'results.csv' (default)

    Format of inputFileName:
    Requires -
    1) the location and name of the FMU     <--- Only one, must be the first line
    2) variables to be set by RAVEN         <--- May include any number
    3) and variables to be output to RAVEN     <--- May include any number

    Example:
    fmuName = 'PATHTOFMU/myFMU.fmu' <--- Must be the first line!!!
    sigma = $RAVEN-sigma$
    rho = $RAVEN-rho$
    lorenzSystem.x
    lorenzSystem.y
    '''
    
    # Read the input file
    with open(inputFileName,'r') as f:
        lines = f.readlines() 
    
    # Extract file name of FMU
    if "fmuName" in lines[0]:
        fmuName = ''.join(re.findall("'([^']*')", lines[0])).replace("'","")
    else:
        raise ValueError('fmuName must be specified in first line of input file. Found instead:\n',lines[0])

    # Initialize inputs/outputs
    start_time = None
    stop_time = None
    output_interval = None
    
    start_values = {}
    output = []
    for i, line in enumerate(lines):
        if i == 0:
            # Skip first line which contains fmuName
            pass
        elif '=' in line:
            # Set the new model parameters
            key, value = line.replace(' ','').strip().split('=')
            if key == 'start_time':
                start_time = float(value)
            elif key == 'stop_time':
                stop_time = float(value)
            elif key == 'output_interval':
                output_interval = float(value)
            else:
                start_values[key] = float(value)
        else:
            # Generate key for variable to be saved
            key = line.replace(' ','').strip()
            if not 'errorSum' in key:
                output.append(key)
            
    # If empty set to None to return default output variables
    if len(output) == 0: output = None
    
    # Simulate
    results = simulate_fmu(fmuName,
                           start_time=start_time,stop_time=stop_time,output_interval=output_interval,
                           input=input,set_input_derivatives=set_input_derivatives,
                           start_values=start_values,output=output)

    # Save results to csv (column - variable, row - values)
    df = pd.DataFrame(results)#.to_csv(outputFileName, index=False)
    return df

def compareResults(values,goldValues):
    '''
    '''
    sharedKeys = []
    skippedKeys = []
    for key in values.keys():
        if key in goldValues:
            sharedKeys.append(key)
        else:
            skippedKeys.append(key)
    
    summary = {}
    summary['error'] = {}
    summary['errorRelative'] = {}
    errorSum = 0
    for key in sharedKeys:
        summary['error'][key] = values[key] - goldValues[key]
        summary['errorRelative'][key] = summary['error'][key]/goldValues[key]
        errorSum += np.abs(summary['errorRelative'][key])   
    summary['errorSum'] = errorSum
    
    print('The following variables were skipped as they were NOT found in the goldValues file:\n {}\n'.format(skippedKeys))
    return summary


if __name__ == '__main__':

    # Check for number of arguments provided by raven and define appropriate file name
    if len(sys.argv) == 1:
        inputFileName = "referenceInput_pyTest.txt"
    else:
        inputFileName = sys.argv[1]
        
    if len(sys.argv) < 3:
        outputFileName = "results.csv"
    else:
        outputFileName = sys.argv[2]
        
    if len(sys.argv) < 4:
        goldValuesFileName = "goldValues.csv"
    else:
        goldValuesFileName = sys.argv[3]
            
    if not outputFileName.endswith(".csv"):
        outputFileName = outputFileName + ".csv"
    
    if not goldValuesFileName.endswith(".csv"):
        goldValuesFileName = goldValuesFileName + ".csv"
             
    set_input_derivatives = False # suggested to leave as False for now - does not perform as expected -https://github.com/CATIA-Systems/FMPy/issues/214
       
    # Simple inputs to play with
    dtype = [('time', np.double), ('u', np.double)]
    signals = np.array([(0.0, 0.0), (10.0, 1.0)], dtype=dtype)
    
    # Alternative more complicated input shapes
    # t = np.linspace(0.0,25,25)
    # x = np.sin(0.5*t)
    # signals = np.array([(t[i],x[i]) for i in range(len(t))],dtype=dtype)

    # Run the FMU and create the output file
    df = simulateFMU(inputFileName)#,input=signals,set_input_derivatives=set_input_derivatives)
        
    # Block to check final values against gold values
    values = df.iloc[-1].to_dict()   
    goldValues = pd.read_csv(goldValuesFileName).iloc[0].to_dict()
    # goldValues = {'pipe.mediums[1].T':	300,
    #                 'pipe.mediums[2].T':	305.5555556,
    #                 'pipe.mediums[3].T':	311.1111111,
    #                 'pipe.mediums[4].T':	316.6666667,
    #                 'pipe.mediums[5].T':	322.2222222,
    #                 'pipe.mediums[6].T':	327.7777778,
    #                 'pipe.mediums[7].T':	333.3333333,
    #                 'pipe.mediums[8].T':	338.8888889,
    #                 'pipe.mediums[9].T':	344.4444444,
    #                 'pipe.mediums[10].T':	350}

    summary = compareResults(values,goldValues)
    with open(outputFileName, 'w') as f:
        f.write('errorSum\n')
        f.write(str(summary['errorSum']))