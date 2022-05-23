# -*- coding: utf-8 -*-
"""
Created on Tue Feb  8 09:43:40 2022

@author: Scott Greenwood
"""

from fmpy import *
import shutil


serialization_time = None
serialized_state = None  # a simple byte string that can be saved to a file


def save_state(time, recorder):
    """ callback to serialize the FMU state and stop the simulation """
    
    if time >= 0.6:  # condition to serialize the FMU state
        fmu = recorder.fmu
        state = fmu.getFMUstate()
        global serialization_time, serialized_state
        serialization_time = time
        serialized_state = fmu.serializeFMUstate(state)
        return False  # stop the simulation

    return True  # continue the simulation


filename = '../tests/fmus/lotkaVolterra.fmu'

# simulate the FMU...
result = simulate_fmu(filename, stop_time=3.0, step_finished=save_state)

# # ... and resume the simulation with the serialized state
unzipdir = extract(filename)
model_description = read_model_description(unzipdir)

fmu_instance = instantiate_fmu(unzipdir=unzipdir, model_description=model_description)

state = fmu_instance.deSerializeFMUstate(serialized_state)
fmu_instance.setFMUstate(state)

result = simulate_fmu(filename=unzipdir, model_description=model_description,
                      fmu_instance=fmu_instance, start_time=serialization_time)

plot_result(result)

# clean up
shutil.rmtree(unzipdir, ignore_errors=True)