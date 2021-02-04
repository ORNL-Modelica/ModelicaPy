# -*- coding: utf-8 -*-

# %%
import fmpy
import matplotlib.pyplot as plt
import numpy as np

## User Input
fmu_filename = 'FMUNAME.fmu'
outputs=['VARIABLENAME(s)']

##
fmpy.dump(fmu_filename)

model_description = fmpy.read_model_description(fmu_filename)

vrs = []
for variable in model_description.modelVariables:
        vrs.append(variable.name)
        

result = fmpy.simulate_fmu(fmu_filename,output=outputs)#,stop_time=100,output_interval=1)

# %%
#from fmpy.util import plot_result  # import the plot function
#plot_result(result,names=outputs)
plt.plot(result['time'],result[outputs[0]])
