# -*- coding: utf-8 -*-

""" This example demonstrates how to use the FMU.get*() and FMU.set*() functions
 to set custom input and control the simulation """

from fmpy import read_model_description, extract
from fmpy.fmi3 import FMU3Slave
import shutil
import pandas as pd
import matplotlib.pyplot as plt

def Merge(dict1, dict2): 
    res = {**dict1, **dict2}
    return res 

# define the model name and simulation parameters
fmu_filename = '../fmus/simulator_3.fmu'
start_time = 0.0
stop_time = 10
nSteps = 10
step_size  = stop_time/nSteps

# read the model description
model_description = read_model_description(fmu_filename)

# collect the value references
vrs = {}
for variable in model_description.modelVariables:
    vrs[variable.name] = variable.valueReference

## get the value references for the variables we want to get/set
inputs = [v for v in model_description.modelVariables if v.causality == 'input']
outputs = [v for v in model_description.modelVariables if v.causality == 'output']

# extract the FMU
unzipdir = extract(fmu_filename)

fmu = FMU3Slave(guid=model_description.guid,
                unzipDirectory=unzipdir,
                modelIdentifier=model_description.coSimulation.modelIdentifier,
                instanceName='instance1')

vars_extra = ['gain.y']
outputs_extra = [v for v in model_description.modelVariables if v.name in vars_extra]
outputs += outputs_extra

# initialize
fmu.instantiate()
fmu.enterInitializationMode()
fmu.exitInitializationMode()

# %% - Simulation loop

time = start_time

rows = []  # list to record the results

# simulation loop
while time < stop_time:

    # NOTE: the FMU.get*() and FMU.set*() functions take lists of
    # value references as arguments and return lists of values
        
    for v in inputs:
        fmu.setFloat64([v.valueReference], [0.0 if time < stop_time/2 else 1.0 ])
        
        # No longer supported... now some "Intermediate Update Mode"... more restrictive on parameters :(
        # Not clear how to access...
        # fmu.setRealInputDerivatives([v.valueReference],[1],[0.0 if time < stop_time/2 else 0.0])
        
    # perform one step
    fmu.doStep(currentCommunicationPoint=time, communicationStepSize=step_size)

    # get the values for 'inputs' and 'outputs'
    val_inputs = {}
    for v in inputs:
        val_inputs[v.name] = fmu.getFloat64([v.valueReference])[0]

    val_outputs = {}
    for v in outputs:
        val_outputs[v.name] = fmu.getFloat64([v.valueReference])[0]
    
    val_time = {}
    val_time['time'] = time
    # append the results
    rowsDict = Merge(Merge(val_time,val_inputs),val_outputs)
    rows.append(rowsDict)

#    print(time)
    # advance the time
    time += step_size

fmu.terminate()
fmu.freeInstance()

# clean up
shutil.rmtree(unzipdir, ignore_errors=True)

# %% - Plot Results
# convert the results to a structured NumPy array
result = pd.DataFrame(rows)

# plot the results
fig, ax = plt.subplots()
ax.plot(result['time'],result[inputs[0].name],'x', label='input')
ax.plot(result['time'],result[vars_extra[0]], 'o', label='output')
ax.legend()
