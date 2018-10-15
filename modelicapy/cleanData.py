# -*- coding: utf-8 -*-
"""
Created on Mon May 21 13:01:32 2018

@author: vmg
"""

import numpy as np
from builtins import range
from buildingspy.io.outputfile import Reader
	
def removeRepeats(data,iCheck=0,deleteCheck=False,axisCheck=0):
    '''
    Remove repeated rows/columns based on the values in the column 'iCheck' in order
    to use tools such as spline which require a monotonically increasing data
    for the independent variable.

    data => MxN matrix or 1-D array
    iCheck => index (row/column number) to check for repeated row values
    deleteCheck => =true to delete 'iCheck' row/column in dataNew
    axisCheck => =0 to remove repeated columns =1 for repeated rows
    '''
    # Cast as matrix to avoid issues if input is a tuple
    data = np.matrix(data)

    # Transpose data if sorting is done on column (1) instead of row (0)
    if axisCheck == 0:
        pass
    elif axisCheck == 1:
        data = np.transpose(data)
    else:
        raise ValueError('Unsupported axisCheck. Only 0 or 1 accepted')
        
    # Get matrix dimensions
    nRow, nCol = np.shape(data)

    # Turn data into matrix form
    dataM = np.zeros((nRow,nCol))

    for i in range(nRow):
        dataM[i,:] = data[i]

    # Find unique rows based on specified column
    a, i = np.unique(dataM[iCheck,:],return_index=True);

    # Extract the filtered data
    dataNew =  dataM[:,np.sort(i)]

    # Remove sorted row based on input
    if deleteCheck and nRow > 0:
        dataNew = np.delete(dataNew, iCheck, 0) 

    # Re-transpose the results so input and output data are consistent
    if axisCheck == 1:
        dataNew = np.transpose(dataNew)
        
    return dataNew

def uniformData(x,y,tstart,tstop,nt=None):
    from scipy.interpolate import interp1d
    '''
    Generate uniform data spacing:
    
    x = abscissa coordinate (e.g., time)
    y = ordinate coordinate (e.g., temperature)
    linspace(tsart,tstop,nt)
    '''
    if nt is None:
        nt=len(x)
        
    t = np.linspace(tstart,tstop,nt)
    interp = interp1d(x.squeeze(),y.squeeze(), kind='cubic')
    dataNew = interp(t)

    return dataNew, t

def cleanDataParam(r,varNames):
    '''
    Clean parameter data by removing all extra values and time information
    
    Returns dictionary of varNames with single values
    '''
    data = {}

    for i, val in enumerate(varNames):
        y = r.values(val)[-1][-1]
        data[val] = y
        
    return data

def cleanDataTime(r,varNames,tstart,tstop,nt=None):
    '''
    Clean time dependent data by removing duplicates and generating uniformly spaced data for data analysis
    varNames = list of variable names for use in Reader.values('NAME')
    
    ** Note, if a variable is included that only has a start/stop value, the variable
    will be filled for all time values with the start value
    
    Returns dictionary of varNames with interpolated values including the time (data['time'])
    
    tstart is start of data to be returned
    tend is end of data to be returned
    nt is number of interpolated points to be returned
    allowParam = True attempts to fill values with only a stop/start value with the same value for all time steps
    '''
    data = {}
    time = r.values(varNames[0])[0]
    t = removeRepeats(time)
    
    for i, val in enumerate(varNames):
        yRaw = r.values(val)[1]

        # Account for values with only a start/stop value
        if np.size(r.values(val)) == 4:
            yRaw = np.ones(len(time))*yRaw[0]

        y = removeRepeats((time,yRaw),0,True)
            
        yint,tint = uniformData(t,y,tstart,tstop,nt)
        data[val] = yint
    data['time'] = tint  
    
    return data

if __name__ == "__main__":
    
    r = Reader('dsres.mat','dymola')
    
    varNames_param_base=[]
    varNames_var_base=[]
    for i, val in enumerate(r.varNames()):
        if np.size(r.values(val)) == 4:
            varNames_param_base.append(val)
        else:      
            varNames_var_base.append(val)
                
    varNames_param = varNames_param_base
    varNames_var = varNames_var_base

    params = cleanDataParam(r,varNames_param)
    data = cleanDataTime(r,varNames_var,0,1,201)
    
    # Normalize data
    data_norm = {}
    for i, val in enumerate(data):
        data_norm[val] = data[val]/max(abs(data[val]))