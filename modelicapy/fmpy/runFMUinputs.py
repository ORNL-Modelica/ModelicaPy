# -*- coding: utf-8 -*-

""" This example demonstrates how to use the FMU.get*() and FMU.set*() functions
 to set custom input and control the simulation """

from fmpy import read_model_description, extract
from fmpy.fmi2 import FMU2Slave
import shutil
import pandas as pd
import matplotlib.pyplot as plt

def Merge(dict1, dict2): 
    res = {**dict1, **dict2}
    return res 

# define the model name and simulation parameters
fmu_filename = 'FMUNAME.fmu'
start_time = 0.0
stop_time = 8640
nSteps = 864
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

fmu = FMU2Slave(guid=model_description.guid,
                unzipDirectory=unzipdir,
                modelIdentifier=model_description.coSimulation.modelIdentifier,
                instanceName='instance1')

# initialize
fmu.instantiate()
fmu.setupExperiment(startTime=start_time)
fmu.enterInitializationMode()
fmu.exitInitializationMode()

# %% - Example of how to get some other potential parameters
nC = fmu.getInteger([vrs['VARNAMEOFCHOICE']])[0]

# %% - Simulation loop

time = start_time

rows = []  # list to record the results

# simulation loop
while time < stop_time:

    # NOTE: the FMU.get*() and FMU.set*() functions take lists of
    # value references as arguments and return lists of values
        
    for v in inputs:
        fmu.setReal([v.valueReference], [0.0 if time < stop_time/2 else 1.0 ])
        fmu.setRealInputDerivatives([v.valueReference],[1],[0.0 if time < stop_time/2 else 0.0])
    # perform one step
    fmu.doStep(currentCommunicationPoint=time, communicationStepSize=step_size)

    # get the values for 'inputs' and 'outputs'
    val_inputs = {}
    for v in inputs:
        val_inputs[v.name] = fmu.getReal([v.valueReference])[0]

    val_outputs = {}
    for v in outputs:
        val_outputs[v.name] = fmu.getReal([v.valueReference])[0]
    
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
plt.plot(result['time'],result['VARNAMTOPLOT'])
