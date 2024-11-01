# -*- coding: utf-8 -*-
"""
Created on Fri Nov  1 11:06:54 2024

@author: fig
"""

from buildingspy.io.outputfile import Reader
import re

def summarize(r, variables):
    values = {}
    
    for var in variables:
        key = var.split('.')[0:-2]
        key = '.'.join(key)
        time, val = r.values(var)
        
        if key not in values.keys():
            values[key] = {}
            
        values[key][var.split('.')[-2]+'_start'] = val[0]
        values[key][var.split('.')[-2]+'_end'] = val[-1]
        values[key][var.split('.')[-2]+'_diff'] = val[0] - val[-1]
        print(f"{key} = {values[key][var.split('.')[-2]+'_diff']}")
    return values

result = r'C:\Users\fig\Documents\Dymola\FullSystem_kinetics.mat'
r = Reader(result,'dymola')
# all_var_names = r.varNames()
#%%

# Define a regular expression pattern for 'pipe.mediums[*].T'

pattern = re.compile(r".*pipe\.Ts_start")
var_start = r.varNames(pattern)

#%%
pattern = re.compile(r".*pipe\.mediums\[\d+\]\.T$")
var_dynamic = r.varNames(pattern)
values_pipe = summarize(r, var_dynamic)

#%%
pattern = re.compile(r".*medium.T$")
var_dynamic = r.varNames(pattern)
values_vol = summarize(r, var_dynamic)