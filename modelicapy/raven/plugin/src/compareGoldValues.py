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
    <method> - OPTIONAL - str - Supported method for comparing values. Defaults to the last values 'lastValue' provided in the input.
IMPORTANT:

TODO (see in code TODO: #):

        
Example XML Input:
	<Models>
		<ExternalModel ModuleToLoad="../../src/compareGoldValues" name="compareGoldValues" subType="">
			<inputs>gOutputsFMU</inputs>
			<outputs>errorSum</outputs>
			<settings>
				<filename>goldValues/calibrateFMU.csv</filename>
				<parameters>a, b, c, output_intervalp</parameters>
          <method>dtw</method>
			</settings>
		</ExternalModel>
	</Models>
"""

import numpy as np
import pandas as pd

#%% Method Section - BEGIN

methods = ['lastValue','dtw']

def _lastValue(values, goldValues, sharedKeys):
    '''
    TODO: 1
    '''
    summary = {}
    summary['error'] = {}
    summary['errorRelative'] = {}
    errorSum = 0.0
    for key in sharedKeys:
        summary['error'][key] = values[key][-1] - goldValues[key][-1]
        summary['errorRelative'][key] = summary['error'][key]/goldValues[key][-1]
        errorSum += np.abs(summary['errorRelative'][key])   
    summary['errorSum'] = errorSum
    return summary


from dtaidistance import dtw
def _dtw(values, goldValues, sharedKeys):
    summary = {}
    errorSum = 0.0
    for key in sharedKeys:
        # summary[key] = dtw.distance(values[key], goldValues[key])
        summary[key] = dtw.distance_fast(values[key], goldValues[key], use_pruning=True)
        errorSum += summary[key] 
    summary['errorSum'] = errorSum
    
    return summary
    
    
def _compareResults(values, goldValues, method):
    '''
    '''
    sharedKeys = []
    skippedKeys = []
    for key in values.keys():
        if key in goldValues and not key=='time':
            sharedKeys.append(key)
        else:
            skippedKeys.append(key)

    if method == 'lastValue':
        summary = _lastValue(values, goldValues, sharedKeys)
    elif method == 'dtw':
        summary = _dtw(values, goldValues, sharedKeys)
    else:
        raise ValueError('Unrecognized method: {}\n Recognized method values include: {}\n'.format(method, methods)) 
      
    if skippedKeys:
        print('The following variables were skipped as they were NOT found in the goldValues file:\n {}\n'.format(skippedKeys))
    
    return summary

#%% Other functions
def _csvToDictionaryArray(filename, dtype='double'):
    df = pd.read_csv(filename)
    if not dtype == '':
        result = {key:df[key].values.astype(dtype) for key in df.columns}
    return result


#%% RAVEN Method
def _readMoreXML(raven,xmlNode):
    '''
    Initialization section. Only run once.
    '''
    settings = {'filename':'',
                'method':'lastValue',
                'parameters':{}}
    
    xmlNodeName = 'settings'
    main = xmlNode.find(xmlNodeName)
       
    for node in main:
        if node.tag == 'filename':
            settings[node.tag] = node.text
            settings['goldValues'] = _csvToDictionaryArray(settings[node.tag])
        elif node.tag == 'method':
            settings[node.tag] = node.text
            if not node.text in methods:
                raise ValueError('Unrecognized method: {}\n Supported methods include: {}\n'.format(node.text, methods))    
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
    summary = _compareResults(raven.settings['parameters'],raven.settings['goldValues'], raven.settings['method'])

    # Save output
    setattr(raven, 'errorSum', np.asarray(summary['errorSum']))

#%% Default
if __name__ == '__main__':
    
    pass