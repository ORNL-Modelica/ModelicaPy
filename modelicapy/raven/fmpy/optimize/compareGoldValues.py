# -*- coding: utf-8 -*-
"""
Created on Thu Jan 13 15:15:21 2022

@author: Scott Greenwood
"""

from fmpy import simulate_fmu
import numpy as np
import pandas as pd  
import sys 
import re

# def calcError(cs,*params): 
#     '''
#     # Function to be minimized
#     '''
    
#     values,goldValues,mapping  = params
    
#     # Get results
#     compareDict = compareModelListResults_FMU(problem,result,goldValues)
#     # Get error
#     error = []
#     for i in range(len(cs)):
#         name = mapping['CFs[{}]'.format(i+1)]
#         error.append(compareDict[problem][name]['goldDiffRelative'])
        
#     print(cs)
#     return error

    
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
    # if len(sys.argv) < 2 or len(sys.argv) > 2:
    #     raise ValueError('The number of inputs must be equal to 2. {} inputs found.'.format(len(sys.argv)-1))
        
    if len(sys.argv) < 3:
        resultsFileName = "results.csv"
        goldValuesFileName = "goldValues.csv"
    else:
        resultsFileName = sys.argv[1]
        goldValuesFileName = sys.argv[2]

    if len(sys.argv) < 4:
        outputFileName = "summary.csv"
    else:
        outputFileName = sys.argv[3]
        
    if not resultsFileName.endswith(".csv"):
        resultsFileName = resultsFileName + ".csv"

    if not goldValuesFileName.endswith(".csv"):
        goldValuesFileName = goldValuesFileName + ".csv"
        
    if not outputFileName.endswith(".csv"):
        outputFileName = outputFileName + ".csv"
        
    values = pd.read_csv(resultsFileName).iloc[-1].to_dict()    
    goldValues = pd.read_csv(goldValuesFileName).iloc[0].to_dict()
    summary = compareResults(values,goldValues)
    with open(outputFileName, 'w') as f:
        f.write('errorSum\n')
        f.write(str(summary['errorSum']))