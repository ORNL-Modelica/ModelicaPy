# -*- coding: utf-8 -*-
"""
Created on Mon Jan 17 15:39:41 2022

@author: Scott Greenwood

RAVEN XML node description:
<inputs> - REQUIRED - float - RAVEN default node for defining in-memory input variables
<outputs> - REQUIRED - float - RAVEN default node for defining in-memory output variables
<settings> - custom XML node for FMU specific external model
    <filename> - REQUIRED - str - location of FMU relative to current working directory.
    <parameters> - REQUIRED - str - Variables names of the provided <inputs>. This is required to extract the variable values from the raven object. Note: Should be identical to <inputs> on the raven xml side.
    <outputs> - REQUIRED -  str - Variables names of the provided <outputs>. This is required to save the variable values to the raven object. Note: Should be identical to <outputs> on the raven xml side.
    <start_time> - OPTIONAL - float - start time for the FMU simulation. If not provided will default to time in FMU modelDescription.xml.
    <stop_time> - OPTIONAL - float - stop time for the FMU simulation. If not provided will default to time in FMU modelDescription.xml.
    <output_interval> - OPTIONAL - float - time step for simulation. If not provided will default to interval in FMU modelDescription.xml or autocalculated..
    <filenameGoldValues> - OPTIONAL - str - location of gold values relative to XML driver scripts (or perhaps where ./raven_framework was run...).
    
IMPORTANT:
    - If reserved variables names ['start_time', 'stop_time', 'output_interval'] are part of the sample space (i.e., in <parameters.), then the value provided will overwrite the pertinent section.
    For example, the sample XML input below will use the sampled output_interval values instead of the defined value of 0.5.

TODO (see in code TODO: #):
    1. ability to handle time dependent input is not currently supported. It is expected RAVEN can handle this though.
    2. Fix issues with matrices with 'parameters' and 'outputs', etc. e.g., a[1, 2] - will separate based on ',' and ' '
        
Example XML Input:
	<Models>
		<ExternalModel ModuleToLoad="../../src/simulateFMU" name="simulateFMU" subType="">
			<inputs>a, b, c, output_interval</inputs>
			<outputs>x, y, z</outputs>
			<settings>
				<filename>../fmus/myFMU.fmu</filename>
				<parameters>a, b, c, output_intervalp</parameters>
				<outputs>x, y, z</outputs>
				<start_time>0.0</start_time>
				<stop_time>50.0</stop_time>
				<output_interval>0.5</output_interval>
			</settings>
		</ExternalModel>
	</Models>
"""

import numpy as np
from fmpy import simulate_fmu
import pandas as pd
from compareGoldValues import _compareResults, _csvToDictionaryArray

reservedNames = ['start_time', 'stop_time', 'output_interval']


def without_keys(d, keys):
    '''
    Return a copy of dictionary 'd' without the specified 'keys'.
    '''
    return {x: d[x] for x in d if x not in keys}


##### RAVEN methods #####
def _readMoreXML(raven,xmlNode):
    '''
    Initialization section. Only run once.
    '''
    settings = {'filename':'',
                'start_time':None,'stop_time':None,'output_interval':None,
                'parameters':{},'outputs':[]}
    
    xmlNodeName = 'settings'
    main = xmlNode.find(xmlNodeName)
       
    for node in main:
        if node.tag == 'filename':
            settings[node.tag] = node.text
        elif node.tag == 'start_time' or node.tag == 'stop_time' or node.tag == 'output_interval':
            settings[node.tag] = float(node.text)
        elif node.tag == 'parameters':
            vals = node.text
            vals = vals.replace(' ','').strip().split(',') # TODO: 2
            for v in vals:
                settings[node.tag][v] = None
        elif node.tag == 'outputs':
            vals = node.text
            settings[node.tag] = vals.replace(' ','').strip().split(',') # TODO: 2  
        elif node.tag == "filenameGoldValues":
            settings[node.tag] = node.text
        elif node.tag == 'method':
            settings[node.tag] = node.text
        else:
            raise ValueError('Unrecognized XML node "{}" in parent "{}". xml\n'.format(node.tag, main))  
    
    if 'filenameGoldValues' in settings:
        # settings['goldValues'] = pd.read_csv(settings['filenameGoldValues']).iloc[0].to_dict()
        settings['goldValues'] = _csvToDictionaryArray(settings['filenameGoldValues'])
        if not 'method' in settings:
            settings['method'] = 'lastValue'
            
    raven.settings = settings   

    
def run(raven, Input):
    '''
    RAVEN recongnizes and runs this section for each run.
    '''

    # Load input
    parentkey = 'parameters'
    for key in raven.settings[parentkey].keys():
        raven.settings[parentkey][key] = Input[key]
    
    # Setup
    filename = raven.settings['filename']
    start_time = raven.settings['start_time']
    stop_time = raven.settings['stop_time']
    output_interval = raven.settings['output_interval']
    parameters = without_keys(raven.settings['parameters'], reservedNames)
    outputs = raven.settings['outputs']
    
    # Simulate
    results = simulate_fmu(filename,
                           start_time=start_time,stop_time=stop_time,output_interval=output_interval,
                           start_values=parameters,output=outputs)
                       # input=input)) # TODO: 1
                       
    # Save output
    parentkey = 'outputs'
    for key in raven.settings[parentkey]:
        try:
            setattr(raven, key, np.asarray(results[key]))
        except:
            pass
        try:
            Input[key] = np.asarray(results[key])
        except:
            pass

    try:
        setattr(raven, 'time', np.asarray(results['time']))
    except:
        pass
        
    # Conditional output for non-ensemble model approaches and calibration
    if 'filenameGoldValues' in raven.settings:
        values = {}
        for key in raven.settings[parentkey]:
            values[key] = np.asarray(results[key])   
        summary = _compareResults(values, raven.settings['goldValues'], raven.settings['method'])
        setattr(raven, 'errorSum', np.asarray(summary['errorSum']))    


if __name__ == '__main__':
    
    pass