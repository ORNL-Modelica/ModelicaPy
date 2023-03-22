# -*- coding: utf-8 -*-
"""

@author: Scott Greenwood
"""

import os

def write_dslogstats(dicRes, fname, mode):
    '''
    Write dictionary results to file
    '''
    with open(fname, mode) as fi:
        for key, value in dicRes.items():
            fi.write('%s,%s\n' % (key, value))


def line_search(lines, nLSearch, LS):
    '''
    Returns the resulting statistics extracted from a dslog file.
    - lines are the lines of dslog
    - nLSearch - number of lines to limit search
        (search starts from the bottom of the dslog file)
    - Ls - text to be searched in given lines
    '''

    res = {}
    for x in range(len(lines)):
        lin = lines[len(lines) - 1 - x]
        if LS['SIMSTART'] in lin:
            des = '=True if the simulation started properly'
            res['simStarted'] = (True, des)

            # Record initial time simulation started
            temp = lin.rpartition("at ")[2]
            try:
                res['t_start'] = (float(temp.rpartition(" using")[0]), des)
            except:
                temp = lin.rpartition("= ")[2]
                res['t_start'] = (float(temp.rpartition(" using")[0]), des)

            # Record solver used in simulation
            # - Solvers with multiple methods have different notation than
            # those with a single option
            # (e.g., DASSL vs RK-method: esdirk34a)
            temp = lin.rpartition("method ")[2]
            des = 'Selected solver'
            if ':' in temp:
                templin = lines[len(lines) - x]
                res['solver'] = (templin.rpartition("\n")[0], des)

            else:
                res['solver'] = (temp.rpartition("\n")[0], des)

    for x in range(nLSearch):
        lin = lines[len(lines) - 1 - x]

        if LS['SIMPASS'] in lin:
            des = '=True if simulation completed successfully)'
            # Record if simulation was successful or not
            if 'unsuccesfully' in lin:
                res['simPassed'] = (False, des)
            elif 'successfully' in lin:
                res['simPassed'] = (True, des)
            else:
                res['simPassed'] = (False, des)

            # Record time simulation ended/failed
            des = 'Time simulation ended/failed'
            temp = lin.rpartition("= ")[2]
            res['t_final'] = (float(temp.rpartition("\n")[0]), des)

        if LS['TSIM'] in lin:
            des = 'CPU-time for integration'
            temp = lin.rpartition(": ")[2]
            res['t_sim'] = (float(temp.rpartition(" seconds")[0]), des)

        if LS['TGRID'] in lin:
            des = 'CPU-time for one GRID interval'
            temp = lin.rpartition(": ")[2]
            res['t_grid'] = (float(temp.rpartition(" milli-seconds")[0]), des)

        if LS['NRESP'] in lin:
            des = 'Number of result points'
            temp = lin.rpartition(": ")[2]
            res['n_result'] = (int(temp.rpartition("\n")[0]), des)

        if LS['NGRIDP'] in lin:
            des = 'Number of GRID points'
            temp = lin.rpartition(": ")[2]
            res['n_grid'] = (int(temp.rpartition("\n")[0]), des)

        if LS['NSP'] in lin:
            des = 'Number of (successful) steps'
            temp = lin.rpartition(": ")[2]
            res['n_steps'] = (int(temp.rpartition("\n")[0]), des)

        if LS['NFEVAL'] in lin:
            des = 'Number of F-evaluations'
            temp = lin.rpartition(": ")[2]
            res['n_Fevals'] = (int(temp.rpartition("\n")[0]), des)

        if LS['NHEVAL'] in lin:
            des = 'Number of H-evaluations'
            temp = lin.rpartition(": ")[2]
            res['n_Hevals'] = (int(temp.rpartition("\n")[0]), des)

        if LS['NCEVAL'] in lin:
            des = 'Number of crossing function evaluations'
            temp = lin.rpartition(": ")[2]
            res['n_Cevals'] = (int(temp.rpartition("\n")[0]), des)

        if LS['NJEVAL'] in lin:
            des = 'Number of Jacobian-evaluations'
            temp = lin.rpartition(": ")[2]
            res['n_Jevals'] = (int(temp.rpartition("\n")[0]), des)

        if LS['NTMEVENT'] in lin:
            des = 'Number of time events'
            temp = lin.rpartition(": ")[2]
            res['n_timeEvents'] = (int(temp.rpartition("\n")[0]), des)

        if LS['NSTEVENT'] in lin:
            des = 'Number of state events'
            temp = lin.rpartition(": ")[2]
            res['n_stateEvents'] = (int(temp.rpartition("\n")[0]), des)

        if LS['NSPEVENT'] in lin:
            des = 'Number of step events'
            temp = lin.rpartition(": ")[2]
            res['n_stepEvents'] = (int(temp.rpartition("\n")[0]), des)

        if LS['MININTSP'] in lin:
            des = 'Minimimum integration stepsize'
            temp = lin.rpartition(": ")[2]
            res['min_intStepSize'] = (float(temp.rpartition("\n")[0]), des)

        if LS['MAXINTSP'] in lin:
            des = 'Maximum integration stepsize'
            temp = lin.rpartition(": ")[2]
            res['max_intStepSize'] = (float(temp.rpartition("\n")[0]), des)

        if LS['MAXINTOR'] in lin:
            des = 'Maximum integration order'
            temp = lin.rpartition(": ")[2]
            res['max_intOrder'] = (int(temp.rpartition("\n")[0]), des)

    return res


def get_log_statistics(log_file='dslog.txt', simulator='dymola', writeToFile=False,
                       fileName='dslog_stats.txt', mode='w'):
    '''
    Open the auto-generated simulation log file (e.g., dslog.txt) and
    return a dictionary containing all the model statistics contained
    at the end of the log file.

    Optional: Save results to fileName in comma separated format if writeToFile = True

    Example:
        logfile = 'dslog.txt'
        simulator = 'dymola'
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
    LS['SIMSTART'] = 'Integration started'
    LS['SIMPASS'] = 'Integration terminated'
    LS['TSIM'] = "CPU-time for integration"
    LS['TGRID'] = "CPU-time for one GRID interval"
    LS['NRESP'] = "Number of result points"
    LS['NGRIDP'] = "Number of GRID   points"
    LS['NSP'] = "Number of (successful) steps"
    LS['NFEVAL'] = "Number of F-evaluations"
    LS['NHEVAL'] = "Number of H-evaluations"
    LS['NCEVAL'] = "Number of crossing function evaluations"
    LS['NJEVAL'] = "Number of Jacobian-evaluations"
    LS['NTMEVENT'] = "Number of (model) time events"
    LS['NSTEVENT'] = "Number of state"
    LS['NSPEVENT'] = "Number of step"
    LS['MININTSP'] = "Minimum integration stepsize"
    LS['MAXINTSP'] = "Maximum integration stepsize"
    LS['MAXINTOR'] = "Maximum integration order"

    # If SIMPASS is not found the simulation failed and function exits
    nLSearch = 30
    temp = False
    for x in range(nLSearch):
        lin = lines[len(lines) - 1 - x]
        if LS['SIMPASS'] in lin:
            temp = True

    if temp is False:
        # Simulation failed
        res = line_search(lines, nLSearch, LS)
        res['simFailed'] = True
        if writeToFile:
            write_dslogstats(res, fileName, mode)
        errorLast = lines[len(lines)-40:len(lines)]
        with open(fileName, "a") as fi:
            fi.write('\nLast 40 lines of log (less if log is < 40 lines):\n')
            for item in errorLast:
                fi.write('%s' % item)
        return res

    # Search for information from the last line up to last expected value
    res = line_search(lines, nLSearch, LS)

    if writeToFile:
        write_dslogstats(res, fileName, mode)

    if res['simPassed'] is False:
        errorLast = lines[len(lines)-40:len(lines)]
        with open(fileName, "a") as fi:
            fi.write('\nLast 40 lines of log (less if log is < 40 lines):\n')
            for item in errorLast:
                fi.write('%s' % item)

    return res


'''
Functions for accessing the mat file generated from the simulation.
'''

if __name__ == "__main__":
    
    res = get_log_statistics()