# -*- coding: utf-8 -*-
"""
Created on Tue Jan 18 12:45:57 2022

@author: Scott Greenwood
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Jan 17 15:39:41 2022

@author: Scott Greenwood

RAVEN XML node description:
<inputs> - REQUIRED - float - RAVEN default node for defining in-memory input variables
<outputs> - REQUIRED - float - RAVEN default node for defining in-memory output variables
<settingsFMU> - custom XML node for FMU specific external model
    <filename> - REQUIRED - str - location of gold values relative to root directory (e.g., location of python file?)
    <parameters> - REQUIRED - str - Variables names of the provided <inputs>. This is required to extract the variable values from the raven object. Note: Should be identical to <inputs> on the raven xml side.
    <outputs> - REQUIRED -  str - Variables names of the provided <outputs>. This is required to save the variable values to the raven object. Note: Should be identical to <outputs> on the raven xml side.


IMPORTANT:

TODO:
   
Example XML Input:
	<Models>
		<ExternalModel ModuleToLoad="../../src/simulateFMU" name="simulateFMU" subType="">
			<inputs>a, b, c</inputs>
			<outputs>errorSumz</outputs>
			<settingsFMU>
				<filename>../goldValues/myGoldValues.csv</filename>
				<parameters>a, b, c</parameters>
          <outputs>errorSum</outputs>
			</settingsFMU>
		</ExternalModel>
	</Models>
"""

import numpy as np
import pandas as pd

def compareResults(values,goldValues):
    '''
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
        elif node.tag == 'parameters':
            vals = node.text
            vals = vals.replace(' ','').strip().split(',')
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
    
    # Setup
    filename = raven.settings['filename']
    parameters = raven.settings['parameters']
    outputs = raven.settings['outputs']
    
    # Compare values
    values = parameters#pd.DataFrame(results).iloc[-1].to_dict()    
    goldValues = pd.read_csv(raven.settings['filename']).iloc[0].to_dict()
    summary = compareResults(values,goldValues)
    
    # Save output
    parentkey = 'outputs'
    for key in raven.settings[parentkey]:
        setattr(raven, key, np.asarray(summary[key]))
        
if __name__ == '__main__':
    
    pass