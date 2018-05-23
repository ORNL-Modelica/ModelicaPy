# -*- coding: utf-8 -*-
"""
Created on Mon May 21 13:01:32 2018

@author: vmg
"""

import numpy as np
from buildingspy.io.outputfile import Reader

def removeRepeatRows(data,col=0,col_del=False):
    '''
    Remove repeated rows based on the values in the column 'col' in order
    to use tools such as spline which require a monotonically increasing data
    for the independent variable.

    data => MxN matrix or 1-D array
    col => column to check for repeated row values
    col_del => =true to delete 'col' in dataNew
    '''
    
    try:
        nCol, nRow = np.shape(data)
    except:
        nCol = 1
        nRow = np.shape(data)
        
    # Turn data into matrix form
    dataM = np.zeros((nRow,nCol))
    for i in xrange(nCol):
        dataM[:,i] = data[i]

    # Find unique rows based on specified column
    a, i = np.unique(dataM[:,col],return_index=True);

    # Extract the filtered data
    dataNew =  dataM[i,:]

    # Remove sorted row based on input
    if col_del and nCol > 0:
        dataNew = np.delete(dataNew, col, 1) 

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
    
    Returns dictionary of varNames with interpolated values including the time (data['time'])
    
    tstart is start of data to be returned
    tend is end of data to be returned
    nt is number of interpolated points to be returned
    '''
    data = {}
    time = r.values(varNames[0])[0]
    t = removeRepeatRows([time])
    for i, val in enumerate(varNames):
        yRaw = r.values(val)[1]
        y = removeRepeatRows([time,yRaw],0,True)
        yint,tint = uniformData(t,y,tstart,tstop,nt)
        data[val] = yint
    data['time'] = tint  
    
    return data

if __name__ == "__main__":
    
    r = Reader('dsres.mat','dymola')
    
    # Get all variables that are not within a model (i.e., do not have a '.')
    varNames_param_base=[]
    varNames_var_base=[]
    for i, val in enumerate(r.varNames()):
        if not '.' in val:
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