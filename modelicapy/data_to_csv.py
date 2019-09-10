import numpy as np
import matplotlib.pyplot as plt

# From ModelicaPy, copy this file into your current working directory
from cleanData import cleanDataParam, cleanDataTime

# If not already performed, run `pip install buildingspy`
from buildingspy.io.outputfile import Reader

# Used for saving the data to csv
import pandas as pd


# Load the result file
r = Reader('res.mat','dymola')

# To see available parameter/variable names: 
r.varNames('lorenz*')

# Specify the parameters and variables that you want cleaned and included in the output file
keys_parameter = ['beta','rho','sigma']
keys_variable = ['lorenzSystem.x','lorenzSystem.y','lorenzSystem.z']

# Remove repeated information for parameters
dict_parameter = cleanDataParam(r, keys_parameter)

# Remove repeated information for variables. Note 'time' variable is automatically included.
tstart = 0 # First time to be included
tstop = 100 # Last time to be included
nt = 500 # Number of points between start and stop
dict_variable = cleanDataTime(r, keys_variable, tstart, tstop, nt)

# Example of cleaned and extracted data
plt.plot(dict_variable['time'],dict_variable['lorenzSystem.x'])

# Save data to csv via pandas package
df_parameter = pd.DataFrame(dict_parameter, index=[0]) 
df_parameter.head()
df_parameter.to_csv('savedParameters.csv')

# Save data to csv via pandas package
df_variable = pd.DataFrame(dict_variable) 
df_variable.set_index('time',inplace=True)
df_variable.head()
df_variable.to_csv('savedVariables.csv')

