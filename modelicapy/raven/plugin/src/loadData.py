# -*- coding: utf-8 -*-
"""
Created on Tue Jan 25 13:59:29 2022

@author: Scott Greenwood
"""

import numpy as np
import pandas as pd

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
                'outputs':[]}
    
    xmlNodeName = 'settings'
    main = xmlNode.find(xmlNodeName)
     
    import os
    print(os.getcwd())
    for node in main:
        if node.tag == 'filename':
            settings[node.tag] = node.text
            settings['values'] = _csvToDictionaryArray(settings[node.tag]) 
        elif node.tag == 'outputs':
            vals = node.text
            settings[node.tag]  = vals.replace(' ','').strip().split(',')
        else:
            raise ValueError('Unrecognized XML node "{}" in parent "{}". xml\n'.format(node.tag, main))  
    
    raven.settings = settings   
    
def run(raven, Input):
    '''
    RAVEN recongnizes and runs this section for each run.
    '''    

    # Save output
    parentkey = 'outputs'
    for key in raven.settings[parentkey]:
        try:
            setattr(raven, key, raven.settings['values'][key])
        except:
            pass
        try:
            Input[key] = raven.settings['values'][key]
        except:
            pass
    
    
#%% Default
if __name__ == '__main__':
    
    pass