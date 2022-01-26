# -*- coding: utf-8 -*-
"""
Created on Wed Jan 26 10:47:14 2022

@author: Scott Greenwood
"""

import numpy as np
import pandas as pd


#%% RAVEN Method
def _readMoreXML(raven,xmlNode):
    '''
    Initialization section. Only run once.
    '''
    settings = {'parameters':[],
                'weights':[]}
    
    xmlNodeName = 'settings'
    main = xmlNode.find(xmlNodeName)
     
    for node in main:
        if node.tag == 'parameters':
            vals = node.text
            settings[node.tag] = vals.replace(' ','').strip().split(',')
        elif node.tag == 'weights':
            vals = node.text
            vals = np.array(vals.replace(' ','').strip().split(','))
            settings[node.tag] = [float(v) for v in vals]
        else:
            raise ValueError('Unrecognized XML node "{}" in parent "{}". xml\n'.format(node.tag, main))  
    
    raven.settings = settings   
    
def run(raven, Input):
    '''
    RAVEN recongnizes and runs this section for each run.
    '''    
    ans = 0.0
    for i, key in enumerate(raven.settings['parameters']):
        ans += Input[key]*raven.settings['weights'][i]
        

    setattr(raven, 'ans', ans)
    
    
#%% Default
if __name__ == '__main__':
    
    pass