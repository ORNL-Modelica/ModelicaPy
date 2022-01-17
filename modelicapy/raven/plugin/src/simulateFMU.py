# -*- coding: utf-8 -*-
"""
Created on Mon Jan 17 15:39:41 2022

@author: Scott Greenwood
"""

import numpy as np
from fmpy import simulate_fmu
# import numpy as np
# import pandas as pd  
# import sys 
# import re

##### RAVEN methods #####
def _readMoreXML(raven,xmlNode):

    settings = {'filename':'',
                'start_time':None,'stop_time':None,'output_interval':None,
                'start_values':{},'output':[]}
    
    xmlNodeName = 'settingsFMU'
    main = xmlNode.find(xmlNodeName)
    for key in settings.keys():
        node = main.find(key)
        if key == 'filename':
            settings[key] = node.text
        elif key == 'start_time' or key == 'stop_time' or key == 'output_interval':
                settings[key] = float(node.text)
        elif key == 'start_values':
            vals = node.text
            vals = vals.replace(' ','').strip().split(',')
            for v in vals:
                settings[key][v] = None
        elif key == 'output':
            vals = node.text
            print(node.text)
            settings[key] = vals.replace(' ','').strip().split(',')      
        else:
            raise ValueError('Unrecognized XML node in: {}\n'.format(xmlNodeName))
        
    raven.settings = settings   
    
    
def run(raven, Input):
    print(raven.settings)
    
    parentkey = 'start_values'
    for key in raven.settings[parentkey].keys():
        raven.settings[parentkey][key] = Input[key]
        
    # Simulate
    filename = raven.settings['filename']
    start_time = raven.settings['start_time']
    stop_time = raven.settings['stop_time']
    output_interval = raven.settings['output_interval']
    start_values = raven.settings['start_values']
    output = raven.settings['output']
    
    results = simulate_fmu(filename,
                           start_time=start_time,stop_time=stop_time,output_interval=output_interval,
                           start_values=start_values,output=output)
                           # input=input))
    parentkey = 'output'
    for key in raven.settings[parentkey]:
        setattr(raven, key, np.asarray(results[key]))
        
if __name__ == '__main__':
    
    pass