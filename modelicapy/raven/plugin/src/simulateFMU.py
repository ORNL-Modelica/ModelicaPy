# -*- coding: utf-8 -*-
"""
Created on Mon Jan 17 15:39:41 2022

@author: Scott Greenwood

RAVEN XML node description
<inputs> - REQUIRED - float - RAVEN default node for defining in-memory input variables
<outputs> - REQUIRED - float - RAVEN default node for defining in-memory output variables

<settingsFMU> - custom XML node for FMU specific external model
    <filename> - REQUIRED - str - location of FMU relative to current working directory
    <start_time> - OPTIONAL - float - start time for the FMU simulation. If not provided will default to time in FMU modelDescription.xml.
    <stop_time> - OPTIONAL - float - stop time for the FMU simulation. If not provided will default to time in FMU modelDescription.xml.
    <output_interval> - OPTIONAL - float - time step for simulation. If not provided will default to interval in FMU modelDescription.xml or autocalculated..
    <parameters> - REQUIRED - str - Variables names of the provided <inputs>. This is required to extract the variable values from the raven object. Note: Should be identical to <inputs> on the raven xml side.
    <outputs> - REQUIRED -  str - Variables names of the provided <outputs>. This is required to extract the variable values from the raven object. Note: Should be identical to <outputs> on the raven xml side.

TODO:
    - ability to handle time dependent input is not currently supported. It is expected RAVEN can handle this though.
"""

import numpy as np
from fmpy import simulate_fmu

reservedNames = ['start_time', 'stop_time', 'output_interval']

##### RAVEN methods #####
def _readMoreXML(raven,xmlNode):

    settings = {'filename':'',
                'start_time':None,'stop_time':None,'output_interval':None,
                'parameters':{},'outputs':[]}
    
    xmlNodeName = 'settingsFMU'
    main = xmlNode.find(xmlNodeName)
    # for key in settings.keys():
    #     node = main.find(key)
    #     if key == 'filename':
    #         settings[key] = node.text
    #     elif key == 'start_time' or key == 'stop_time' or key == 'output_interval':
    #         settings[key] = float(node.text)
    #     elif key == 'start_values':
    #         vals = node.text
    #         vals = vals.replace(' ','').strip().split(',')
    #         for v in vals:
    #             settings[key][v] = None
    #     elif key == 'outputs':
    #         vals = node.text
    #         settings[key] = vals.replace(' ','').strip().split(',')      
    #     else:
    #         raise ValueError('Unrecognized XML node in: {}\n'.format(xmlNodeName))
        
    for node in main:
        if node.tag == 'filename':
            settings[node.tag] = node.text
        elif node.tag == 'start_time' or node.tag == 'stop_time' or node.tag == 'output_interval':
            settings[node.tag] = float(node.text)
        elif node.tag == 'parameters':
            vals = node.text
            vals = vals.replace(' ','').strip().split(',')
            for v in vals:
                settings[node.tag][v] = None
        elif node.tag == 'outputs':
            vals = node.text
            settings[node.tag] = vals.replace(' ','').strip().split(',')      
        else:
            raise ValueError('Unrecognized XML node "{}" in parent "{}". xml\n'.format(node.tag, main))  
            
    raven.settings = settings   
    
    
def run(raven, Input):

    # Load input
    parentkey = 'parameters'
    toRemove = []
    for key in raven.settings[parentkey].keys():
        if key in reservedNames:
            # Handle scenario where the setup variables are sampled
            raven.settings[key] = Input[key]
            toRemove.append(key)
        else:
            # Set values from sampled variables
            raven.settings[parentkey][key] = Input[key]
    
    # Remove setup variables from parameters variable
    for key in toRemove:
        raven.settings[parentkey].pop(key)
        
    # Setup
    filename = raven.settings['filename']
    start_time = raven.settings['start_time']
    stop_time = raven.settings['stop_time']
    output_interval = raven.settings['output_interval']
    parameters = raven.settings['parameters']
    outputs = raven.settings['outputs']
    print('##############')
    print(raven.settings)
    print('##############')
    # print('start_time = {}'.format(start_time))
    # print('stop_time = {}'.format(stop_time))
    # print('output_interval = {}'.format(output_interval))
    
    # Simulate
    results = simulate_fmu(filename,
                           start_time=start_time,stop_time=stop_time,output_interval=output_interval,
                           start_values=parameters,output=outputs)
                           # input=input))
    # Save output
    parentkey = 'outputs'
    for key in raven.settings[parentkey]:
        setattr(raven, key, np.asarray(results[key]))
        
if __name__ == '__main__':
    
    pass