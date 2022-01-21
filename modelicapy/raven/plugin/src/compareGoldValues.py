# -*- coding: utf-8 -*-
"""
Created on Mon Jan 21 14:15:11 2022

@author: Scott Greenwood

RAVEN XML node description:
<inputs> - REQUIRED - float - RAVEN default node for defining in-memory input variables
<outputs> - REQUIRED - float - RAVEN default node for defining in-memory output variables
<settings> - custom XML node for FMU specific external model
    <filename> - REQUIRED - str - location of gold values relative to XML driver scripts (or perhaps where ./raven_framework was run...).
    <parameters> - REQUIRED - str - Variables names of the provided <inputs>. This is required to extract the variable values from the raven object. Note: Should be identical to <inputs> on the raven xml side.

IMPORTANT:

TODO (see in code TODO: #):
    1. Increase flexibility by auto recognizing if array versus singular, etc.
    2. Fix issues with matrices with 'parameters' and 'outputs', etc. e.g., a[1, 2] - will separate based on ',' and ' '
        
Example XML Input:
	<Models>
		<ExternalModel ModuleToLoad="../../src/compareGoldValues" name="compareGoldValues" subType="">
			<inputs>gOutputsFMU</inputs>
			<outputs>errorSum</outputs>
			<settings>
				<filename>goldValues/calibrateFMU.csv</filename>
				<parameters>a, b, c, output_intervalp</parameters>
			</settings>
		</ExternalModel>
	</Models>
"""

import numpy as np
import pandas as pd


def compareResults(values,goldValues):
    '''
    TODO: 1
    '''
    sharedKeys = []
    skippedKeys = []
    for key in values.keys():
        if key in goldValues:
            sharedKeys.append(key)
        else:
            skippedKeys.append(key)
    
    summary = {}
    summary['error'] = {}
    summary['errorRelative'] = {}
    errorSum = 0
    for key in sharedKeys:
        summary['error'][key] = values[key] - goldValues[key]
        summary['errorRelative'][key] = summary['error'][key]/goldValues[key]
        errorSum += np.abs(summary['errorRelative'][key])   
    summary['errorSum'] = errorSum
    
    print('The following variables were skipped as they were NOT found in the goldValues file:\n {}\n'.format(skippedKeys))
    return summary


##### RAVEN methods #####
def _readMoreXML(raven,xmlNode):
    '''
    Initialization section. Only run once.
    '''
    settings = {'filename':'',
                'parameters':{}}
    
    xmlNodeName = 'settings'
    main = xmlNode.find(xmlNodeName)
       
    for node in main:
        if node.tag == 'filename':
            settings[node.tag] = node.text
            settings['goldValues'] = pd.read_csv(settings[node.tag]).iloc[0].to_dict()
        elif node.tag == 'parameters':
            vals = node.text
            vals = vals.replace(' ','').strip().split(',') # TODO: 2
            for v in vals:
                settings[node.tag][v] = None
        else:
            raise ValueError('Unrecognized XML node "{}" in parent "{}". xml\n'.format(node.tag, main))  
    
    raven.settings = settings   

    
def run(raven, Input):
    '''
    RAVEN recongnizes and runs this section for each run.
    '''    
    # Load input
    parentkey = 'parameters'
    for key in raven.settings[parentkey].keys():
        raven.settings[parentkey][key] = Input[key]
    
    # Calculate error
    values = pd.DataFrame(raven.settings['parameters']).iloc[-1].to_dict()    
    summary = compareResults(values,raven.settings['goldValues'])

    # Save output
    setattr(raven, 'errorSum', np.asarray(summary['errorSum']))


if __name__ == '__main__':
    
    pass