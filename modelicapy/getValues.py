# -*- coding: utf-8 -*-
"""
Created on Wed Sep 26 14:26:05 2018

@author: vmg

This returns a specific index value from the time dependent data (variables)
for a give component and prints the specified file name if desired.

The idea is to provide a repeatable way to extract initial conditions for
copying back into the Modelca model.
"""

import numpy as np
from buildingspy.io.outputfile import Reader


def combineKeyValues(results,additional):
    '''
Use to update an existing results dictionary with more results from components
which already exist in the results without overwriting existing data
    '''
    for key in results.keys():
        if key in additional.keys():
            results[key].update(additional[key])
            
    return results

    
def getCombineValues(r,compDict):
    '''
    *** Do not recommend using, likely to change/be deleted/improved
Provided a components list this function calls the appropriate functions and
combines all the results into a single dictionary.

!!! Currently only able to use default settings from the functions


    r = Reader('matfile','dymola')
    compDict = {
            'GenericPipe':{'core.coolantSubchannel','hotLeg','coldLeg','STHX.tube','STHX.shell'},
            'SimpleVolume':{'inletPlenum'}
            }
    '''   
    results = {}
    for key, value in compDict.iteritems():
        results.update(globals()[key](r,value))
            
    return results        
            
def writeValues(components,results,fileName='returnValues.txt'):
    '''
Create a file with minimal/zero formatting
    '''
    with open(fileName,'w') as fil:
        for c in components:
            fil.write('{}\n'.format(c))
            for key, value in results[c].items():
                
                # Condense values, arrays, etc. into single line
                line = ','.join(str(value).split()).replace('[','{').replace(']','}')
                
                # Remove extraneous ','
                line = line.replace(',}','}')
                line = line.replace('{,','{')
                
                # Write the file
                fil.write('{} = {}\n'.format(key,line))
       
        
def writeValues_MOFormatted(components,results,fileName='returnValues.txt',
        unitMap={'p':'SI.Pressure','T':'SI.Temperature','h':'SI.SpecificEnthalpy','d':'SI.Density','level':'SI.Length'},
        fullName=False,
        classMo = 'parameter',
        annotation='Dialog(tab="Initialization")',
        useRedefine=False,
        ignorePrefix=''):
    '''
Create a file with formatting for Modelica files

useRedefine = True => puts output in format for redefining values of underlying model
    '''
    import re
    
    with open(fileName,'w') as fil:
        for c in components:
            if not useRedefine:
                fil.write('//{}\n'.format(c))
                
            for key, value in results[c].items():
                
                # Condense values, arrays, etc. into single line
                line = ','.join(str(value).split()).replace('[','{').replace(']','}')
                
                #Remove extraneous ','
                line = line.replace(',}','}')
                line = line.replace('{,','{')
                
                # Create new key with formating
                if not fullName:
                    c = c.split('.')[0]
                newKey = key + '_start_{}'.format(c).replace('.','_')
                newKey = newKey.replace('_'+ignorePrefix,'')
                
                # Assign units if foundin the mapped unit dictionary
                unit = ''
                if key in unitMap:
                    unit = unitMap[key]
                else:
                    unit = 'Real'
                
                # Check for dimensions and provide approriate suffix
                suffix = ''
                ch_ = '{'
                str_ = line
                m = re.match(r'[%s]+' % ch_, str_)
                nDims = m.end() if m else 0
                if nDims < 1:
                    pass
                else:
                    suffix = '[' + ','.join((':') for i in range(nDims)) + ']'
                    
                if not useRedefine:
                    # Write the file
                    fil.write('{}{} {}{} = {}{};\n'.format('' if not classMo else classMo+' ',unit,newKey,suffix,line, '' if not annotation else ' annotation({})'.format(annotation)))
                else:
                    fil.write('{} = {},\n'.format(newKey,line))
             
def GenericPipe(r,components = ['pipe'],keyword='mediums',variables = ['p','T','h','d'],iGet=-1,fileName='returnValues.txt',writeToFile = False):
    resultsFull = {}
    results = {}   
    
    for c in components:
        resultsFull[c] = dict.fromkeys(variables)
        results[c] = dict.fromkeys(variables)
        
        # Check for component
        if r.varNames('{}{}\[1].{}'.format(c,keyword if not keyword else '.'+keyword,variables[0])):
            
            # Get number of elements
            nI = int(r.values('{}.geometry.nV'.format(c))[1][0])
            
            # Get length of simulation results
            nt = len(r.values('{}{}[1].{}'.format(c,keyword if not keyword else '.'+keyword,variables[0]))[0])
            
            # Store results in a matrix
            for v in variables:
                temp = np.ndarray((nI,nt))
                for i in range(nI):
                    temp[i,:] = r.values('{}{}[{}].{}'.format(c,keyword if not keyword else '.'+keyword,i+1,v))[1]
                resultsFull[c][v] = temp
                results[c][v] = temp[:,iGet]
                
        else:
            print('No results found for {}'.format(c))
    
    if writeToFile:
        writeValues(components,results,fileName)
    
    return results


def SimpleVolume(r,components = ['pipe'],keyword='medium',variables = ['p','T','h','d'],iGet=-1,fileName='returnValues.txt',writeToFile = False):
    resultsFull = {}
    results = {}
    
    for c in components:
        resultsFull[c] = dict.fromkeys(variables)
        results[c] = dict.fromkeys(variables)
                      
        # Check for component    
        if r.varNames('{}{}.{}'.format(c,keyword if not keyword else '.'+keyword,variables[0])):
            
            # Store results in a matrix
            for v in variables:
                temp = r.values('{}{}.{}'.format(c,keyword if not keyword else '.'+keyword,v))[1]
                resultsFull[c][v] = temp
                results[c][v] = temp[iGet]
                
        else:
            print('No results found for {}'.format(c))
    
    if writeToFile:
            writeValues(components,results,fileName)
    
    return results


def Cylinder_FD(r,components = ['cylinder'],keyword='solutionMethod', variables = ['Ts'],iGet=-1,fileName='returnValues.txt',writeToFile = True):
    resultsFull = {}
    results = {}
    
    for c in components:
        resultsFull[c] = dict.fromkeys(variables)
        results[c] = dict.fromkeys(variables)
        
        # Check for component
        if r.varNames('{}{}.{}\[1, 1]'.format(c,keyword if not keyword else '.'+keyword,variables[0])):
            
            # Get number of elements per dimension
            nI = int(r.values('{}.nR'.format(c))[1][0])
            nJ = int(r.values('{}.nZ'.format(c))[1][0])
            
            # Get length of simulation results
            nt = len(r.values('{}{}.{}[1, 1]'.format(c,keyword if not keyword else '.'+keyword,variables[0]))[0])
            
            # Store results in a matrix
            for v in variables:
                temp = np.ndarray((nI,nJ,nt))
                for i in range(nI):
                    for j in range(nJ):
                        temp[i,j,:] = r.values('{}{}.{}[{}, {}]'.format(c,keyword if not keyword else '.'+keyword,v,i+1,j+1))[1]
                resultsFull[c][v] = temp
                results[c][v] = temp[:,:,iGet]
                
        else:
            print('No results found for {}'.format(c))
    
    if writeToFile:
        writeValues(components,results,fileName)
    
    return results


def Conduction_2D(r,components = ['conduction'],keyword='materials', variables = ['T'],iGet=-1,fileName='returnValues.txt',writeToFile = True):
    resultsFull = {}
    results = {}
    
    for c in components:
        resultsFull[c] = dict.fromkeys(variables)
        results[c] = dict.fromkeys(variables)
        
        # Check for component
        if r.varNames('{}{}\[1, 1].{}'.format(c,keyword if not keyword else '.'+keyword,variables[0])):
            
            # Get number of elements per dimension
            nI = int(r.values('{}.nVs[1]'.format(c))[1][0])
            nJ = int(r.values('{}.nVs[2]'.format(c))[1][0])
            
            # Get length of simulation results
            nt = len(r.values('{}{}[1, 1].{}'.format(c,keyword if not keyword else '.'+keyword,variables[0]))[0])
            
            # Store results in a matrix
            for v in variables:
                temp = np.ndarray((nI,nJ,nt))
                for i in range(nI):
                    for j in range(nJ):
                        temp[i,j,:] = r.values('{}{}[{}, {}].{}'.format(c,keyword if not keyword else '.'+keyword,i+1,j+1,v))[1]
                resultsFull[c][v] = temp
                results[c][v] = temp[:,:,iGet]
                
        else:
            print('No results found for {}'.format(c))
    
    if writeToFile:
        writeValues(components,results,fileName)
    
    return results


def ExpansionTank_1Port(r,components = ['tank'],keyword='',variables = ['p','h'],iGet=-1,fileName='returnValues.txt',writeToFile = False):
    resultsFull = {}
    results = {}

    for c in components:
        resultsFull[c] = dict.fromkeys(variables)
        results[c] = dict.fromkeys(variables)
                      
        # Check for component    
        if r.varNames('{}{}.{}'.format(c,keyword if not keyword else '.'+keyword,variables[0])):
            
            # Store results in a matrix
            for v in variables:
                temp = r.values('{}{}.{}'.format(c,keyword if not keyword else '.'+keyword,v))[1]
                resultsFull[c][v] = temp
                results[c][v] = temp[iGet]
                
        else:
            print('No results found for {}'.format(c))
    
    if writeToFile:
            writeValues(components,results,fileName)
    
    return results


def TeeJunctionVolume(r,components = ['tee'],keyword='medium',variables = ['p','T','h','d'],iGet=-1,fileName='returnValues.txt',writeToFile = False):
    resultsFull = {}
    results = {}
    
    for c in components:
        resultsFull[c] = dict.fromkeys(variables)
        results[c] = dict.fromkeys(variables)
                      
        # Check for component    
        if r.varNames('{}{}.{}'.format(c,keyword if not keyword else '.'+keyword,variables[0])):
            
            # Store results in a matrix
            for v in variables:
                temp = r.values('{}{}.{}'.format(c,keyword if not keyword else '.'+keyword,v))[1]
                resultsFull[c][v] = temp
                results[c][v] = temp[iGet]
                
        else:
            print('No results found for {}'.format(c))
    
    if writeToFile:
            writeValues(components,results,fileName)
    
    return results


if __name__ == "__main__":
#    r = Reader('GenericModule3.mat','dymola')
    r = Reader('SouthEast3.mat','dymola')
    
    prefix = 'PHS'
    
    components_GenericPipe = ['core.coolantSubchannel','hotLeg','coldLeg','STHX.tube','STHX.shell']
    components_SimpleVolume = ['inletPlenum','outletPlenum']
    components_Cylinder_FD = ['core.fuelModel.region_1','core.fuelModel.region_2','core.fuelModel.region_3']
    components_Conduction_2D = ['STHX.tubeWall']
    components_ExpansionTank_1Port = ['pressurizer']
    components_TeeJunctionVolume = ['pressurizer_tee']
   
    for i in xrange(len(components_GenericPipe)):
        components_GenericPipe[i] = prefix + '.' + components_GenericPipe[i]
    for i in xrange(len(components_SimpleVolume)):
        components_SimpleVolume[i] = prefix + '.' + components_SimpleVolume[i]
    for i in xrange(len(components_Cylinder_FD)):
        components_Cylinder_FD[i] = prefix + '.' + components_Cylinder_FD[i]
    for i in xrange(len(components_Conduction_2D)):
        components_Conduction_2D[i] = prefix + '.' + components_Conduction_2D[i]
    for i in xrange(len(components_ExpansionTank_1Port)):
        components_ExpansionTank_1Port[i] = prefix + '.' + components_ExpansionTank_1Port[i]
    for i in xrange(len(components_TeeJunctionVolume)):
        components_TeeJunctionVolume[i] = prefix + '.' + components_TeeJunctionVolume[i]
        
    results = {}
    results.update(GenericPipe(r,components_GenericPipe))
    results.update( SimpleVolume(r,components_SimpleVolume))
    results.update( Cylinder_FD(r,components_Cylinder_FD))
    results.update( Conduction_2D(r,components_Conduction_2D))
    results.update( ExpansionTank_1Port(r,components_ExpansionTank_1Port))
    results = combineKeyValues(results,ExpansionTank_1Port(r,components_ExpansionTank_1Port,keyword='',variables=['level']))
    results.update( TeeJunctionVolume(r,components_TeeJunctionVolume))

    components = components_GenericPipe + components_SimpleVolume + components_Cylinder_FD+components_Conduction_2D + components_ExpansionTank_1Port + components_TeeJunctionVolume
         
    writeValues(components,results)
    writeValues_MOFormatted(components,results,fullName=True,classMo='final parameter',annotation='',useRedefine=True,ignorePrefix=prefix)
