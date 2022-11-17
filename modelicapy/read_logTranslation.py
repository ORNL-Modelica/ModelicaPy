# -*- coding: utf-8 -*-
"""

@author: Scott Greenwood

Summarize the translation log created by using the savelog() command in Dymola.
"""

import os

def write_dslogstats(dicRes, fname, mode):
    '''
    Write dictionary results to file
    '''
    with open(fname, mode) as fi:
        for key, value in dicRes.items():
            fi.write('%s,%s\n' % (key, value))

def stringArrayToList(string):
    temp = string.replace('{','').replace('}','').strip().split(',')
    if temp[0] != '':
        ls = [int(val) for val in temp]
    else:
        ls = [0]
    return ls
                
def line_search(lines, LS):
    '''
    Returns the resulting statistics extracted from a dslog file.
    - lines are the lines of dslog
    - nLSearch - number of lines to limit search
        (search starts from the bottom of the dslog file)
    - Ls - text to be searched in given lines
    '''

    res = {}
    res['STATISTICS'] = {}
    res['ORIGINAL'] = {}
    res['TRANSLATED'] = {}
    res['INITIAL'] = {}
    
    iSTATISTICS = -1
    iORIGINAL = -1
    iTRANSLATED = -1
    iINITIAL = -1
    iVARSNONLIN = -1
    
    for i, lin in enumerate(lines):
        if lin == 'Statistics\n':
            iSTATISTICS = i
        if lin == 'Original Model\n':
            iORIGINAL = i
        if lin == 'Translated Model\n':
            iTRANSLATED = i
        if lin =="  Initialization problem\n":
            iINITIAL = i
        if lin =="   Variables appearing in the nonlinear systems of equations\n":
            iVARSNONLIN = i

    for lin in lines[iSTATISTICS:iORIGINAL]:
        currentSection = 'STATISTICS'
            
    for lin in lines[iORIGINAL:iTRANSLATED]:
        currentSection = 'ORIGINAL'
        if LS[currentSection]['NCOMPONENTS'] in lin:
            temp = lin.rpartition(": ")[2]
            res[currentSection]['NCOMPONENTS'] = int(temp.rpartition("\n")[0])

        if LS[currentSection]['VARS'] in lin:
            temp = lin.rpartition(": ")[2]
            res[currentSection]['VARS'] = int(temp.rpartition("\n")[0])

        if LS[currentSection]['CONST'] in lin:
            temp = lin.rpartition(": ")[2]
            res[currentSection]['CONST'] = int(temp.rpartition(" (")[0])

        if LS[currentSection]['PARAMS'] in lin:
            temp = lin.rpartition(": ")[2]
            res[currentSection]['PARAMS'] = int(temp.rpartition(" (")[0])

        if LS[currentSection]['UNKNOWN'] in lin:
            temp = lin.rpartition(": ")[2]
            res[currentSection]['UNKNOWN'] = int(temp.rpartition(" (")[0])

        if LS[currentSection]['DIFFVAR'] in lin:
            temp = lin.rpartition(": ")[2]
            res[currentSection]['DIFFVAR'] = int(temp.rpartition(" scalars")[0])

        if LS[currentSection]['EQNS'] in lin:
            temp = lin.rpartition(": ")[2]
            res[currentSection]['EQNS'] = int(temp.rpartition("\n")[0])

        if LS[currentSection]['NONTRIV'] in lin:
            temp = lin.rpartition(": ")[2]
            res[currentSection]['NONTRIV'] = int(temp.rpartition("\n")[0])

    for lin in lines[iTRANSLATED:iINITIAL]:
        currentSection = 'TRANSLATED'
      
        if LS[currentSection]['CONST'] in lin:
            temp = lin.rpartition(": ")[2]
            res[currentSection]['CONST'] = int(temp.rpartition(" scalars")[0])
        if LS[currentSection]['FPARAMS'] in lin:
            temp = lin.rpartition(": ")[2]
            res[currentSection]['FPARAMS'] = int(temp.rpartition(" scalars")[0])
        if LS[currentSection]['PARAMS'] in lin:
            temp = lin.rpartition(": ")[2]
            res[currentSection]['PARAMS'] = int(temp.rpartition(" scalars")[0])
        if LS[currentSection]['OUTPUT'] in lin:
            temp = lin.rpartition(": ")[2]
            res[currentSection]['OUTPUT'] = int(temp.rpartition(" scalars")[0])
        if LS[currentSection]['CSTATE'] in lin:
            temp = lin.rpartition(": ")[2]
            res[currentSection]['CSTATE'] = int(temp.rpartition(" scalars")[0])
        if LS[currentSection]['TVARS'] in lin:
            temp = lin.rpartition(": ")[2]
            res[currentSection]['TVARS'] = int(temp.rpartition(" scalars")[0])
        if LS[currentSection]['ALIAS'] in lin:
            temp = lin.rpartition(": ")[2]
            res[currentSection]['ALIAS'] = int(temp.rpartition(" scalars")[0])
        if LS[currentSection]['NSYS'] in lin:
            temp = lin.rpartition(": ")[2]
            res[currentSection]['NSYS'] = int(temp.rpartition("\n")[0])
        if LS[currentSection]['LIN'] in lin:
            temp = lin.rpartition(": ")[2]
            res[currentSection]['LIN'] = stringArrayToList(temp.rpartition("\n")[0])
        if LS[currentSection]['LINMAN'] in lin:
            temp = lin.rpartition(": ")[2]
            res[currentSection]['LINMAN'] = stringArrayToList(temp.rpartition("\n")[0])
        if LS[currentSection]['NONLIN'] in lin:
            temp = lin.rpartition(": ")[2]
            res[currentSection]['NONLIN'] = stringArrayToList(temp.rpartition("\n")[0])
        if LS[currentSection]['NONLINMAN'] in lin:
            temp = lin.rpartition(": ")[2]
            res[currentSection]['NONLINMAN'] = stringArrayToList(temp.rpartition("\n")[0])
        if LS[currentSection]['NJAC'] in lin:
            temp = lin.rpartition(": ")[2]
            res[currentSection]['NJAC'] = stringArrayToList(temp.rpartition("\n")[0])
            
    for lin in lines[iINITIAL:iVARSNONLIN]:
        currentSection = 'INITIAL'
        if LS[currentSection]['LIN'] in lin:
            temp = lin.rpartition(": ")[2]
            res[currentSection]['LIN'] = stringArrayToList(temp.rpartition("\n")[0])
        if LS[currentSection]['LINMAN'] in lin:
            temp = lin.rpartition(": ")[2]
            res[currentSection]['LINMAN'] = stringArrayToList(temp.rpartition("\n")[0])
        if LS[currentSection]['NONLIN'] in lin:
            temp = lin.rpartition(": ")[2]
            res[currentSection]['NONLIN'] = stringArrayToList(temp.rpartition("\n")[0])
        if LS[currentSection]['NONLINMAN'] in lin:
            temp = lin.rpartition(": ")[2]
            res[currentSection]['NONLINMAN'] = stringArrayToList(temp.rpartition("\n")[0])
        if LS[currentSection]['NJAC'] in lin:
            temp = lin.rpartition(": ")[2]
            res[currentSection]['NJAC'] = stringArrayToList(temp.rpartition("\n")[0])
            
    return res


def get_log_statistics(log_file='dslog.txt', simulator='dymola', writeToFile=False,
                       fileName='dslog_stats.txt', mode='w'):
    '''
    Open the generated translation log file (e.g., from savelog() command) and
    return a dictionary containing all the model statistics.

    Optional: Save results to fileName in comma separated format if writeToFile = True
    '''

    if simulator != "dymola":
        raise ValueError('Argument "simulator" needs to be set to "dymola".')

    if not os.path.isfile(log_file):
        raise IOError("File {} does not exist".format(log_file))

    with open(log_file) as fil:
        lines = fil.readlines()

    # Instantiate a dictionary that is used for the return value
    res = {}

    # Define all lines to be searched for information
    LS = {}
    LS['ORIGINAL'] = {}
    LS['ORIGINAL']['NCOMPONENTS'] = 'Number of components'
    LS['ORIGINAL']['VARS'] = 'Variables'
    LS['ORIGINAL']['CONST'] = "Constants"
    LS['ORIGINAL']['PARAMS'] = "Parameters"
    LS['ORIGINAL']['UNKNOWN'] = "Unknowns"
    LS['ORIGINAL']['DIFFVAR'] = "Differentiated variables"
    LS['ORIGINAL']['EQNS'] = "Equations"
    LS['ORIGINAL']['NONTRIV'] = "Nontrivial"

    LS['TRANSLATED'] = {}
    LS['TRANSLATED']['CONST'] = 'Constants'
    LS['TRANSLATED']['FPARAMS'] = 'Free parameters'
    LS['TRANSLATED']['PARAMS'] = 'Parameter depending'
    LS['TRANSLATED']['OUTPUT'] = 'Outputs'
    LS['TRANSLATED']['CSTATE'] = 'Continuous time states'
    LS['TRANSLATED']['TVARS'] = 'Time-varying variables'
    LS['TRANSLATED']['ALIAS'] = 'Alias variables'
    LS['TRANSLATED']['NSYS'] = 'Number of mixed real/discrete systems of equations'
    LS['TRANSLATED']['LIN'] = 'Sizes of linear systems of equations'
    LS['TRANSLATED']['LINMAN'] = 'Sizes after manipulation of the linear systems'
    LS['TRANSLATED']['NONLIN'] = 'Sizes of nonlinear systems of equations'
    LS['TRANSLATED']['NONLINMAN'] = 'Sizes after manipulation of the nonlinear systems'
    LS['TRANSLATED']['NJAC'] = 'Number of numerical Jacobians'
    
    LS['INITIAL'] = {}
    LS['INITIAL']['LIN'] = 'Sizes of linear systems of equations'
    LS['INITIAL']['LINMAN'] = 'Sizes after manipulation of the linear systems'
    LS['INITIAL']['NONLIN'] = 'Sizes of nonlinear systems of equations'
    LS['INITIAL']['NONLINMAN'] = 'Sizes after manipulation of the nonlinear systems'
    LS['INITIAL']['NJAC'] = 'Number of numerical Jacobians'

# TODO: Modify this check based on what a failed translation log looks like
    #  If SIMPASS is not found the simulation failed and function exits
    # temp = False
    # for x in range(20):
    #     lin = lines[len(lines) - 1 - x]
    #     if LS['SIMPASS'] in lin:
    #         temp = True

    # if temp is False:
    #     # Simulation failed
    #     res = line_search(lines, 20, LS)
    #     res['simFailed'] = True
    #     if writeToFile:
    #         write_dslogstats(res, fileName, mode)
    #     errorLast = lines[len(lines)-40:len(lines)]
    #     with open(fileName, "a") as fi:
    #         fi.write('\nLast 40 lines of log (less if log is < 40 lines):\n')
    #         for item in errorLast:
    #             fi.write('%s' % item)
    #     return res

    # Search for information
    res = line_search(lines, LS)

    if writeToFile:
        write_dslogstats(res, fileName, mode)

    # if res['simPassed'] is False:
    #     errorLast = lines[len(lines)-40:len(lines)]
    #     with open(fileName, "a") as fi:
    #         fi.write('\nLast 40 lines of log (less if log is < 40 lines):\n')
    #         for item in errorLast:
    #             fi.write('%s' % item)

    return res


'''
Functions for accessing the mat file generated from the simulation.
'''

if __name__ == "__main__":
    
    res = get_log_statistics()
