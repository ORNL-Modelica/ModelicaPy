# -*- coding: utf-8 -*-
"""

@author: Scott Greenwood
"""

import os


def create_dsinORfinal(dicSim, dicVars, dsFileIn='dsfinal.txt', dsFileOut='dsin.txt', simulator='dymola'):
    '''
    Generate a new dsin.txt file with modified values from discSim and dicVars
    from a dsin.txt or dsfinal.txt file with a name specified by dsFileOut.

    dsFileIn = dsfile to be read (e.g., dsin.txt)
    simulator = currently only supports dymola
    dsFileOut = dsfile to be written
    dicSim = simulation settings to be changed
    dicVars = inital variable values to be changed

    Example:
        create_dsinORfinal({'StartTime': 0,'StopTime': 100},
                     {'var1.k': 10},
                     'dsfinal.txt',
                     'dsin.txt',
                     'dymola')                    
    '''

    if simulator != "dymola":
        raise ValueError('Argument "simulator" needs to be set to "dymola".')

    if not os.path.isfile(dsFileIn):
        raise IOError("File {} does not exist".format(dsFileIn))

    if dsFileIn == dsFileOut:
        answer = raw_input('''Input and ouput file names match.
    The input file will be overwritten. Continue [y/n]? ''')
        if answer.lower() in ['y', 'yes']:
            # Do nothing
            pass
        elif answer.lower() in ['n', 'no']:
            print 'Program terminated'

        else:
            raise IOError('Response not recognized. Program terminated')

    # Add '#' identifier used in dsin/dsfinal files
    for key, value in dicVars.items():
        dicVars['# %s' % key] = dicVars.pop(key)

    with open(dsFileIn) as fil:
        lines = fil.readlines()

    # Dymola generated dsin.txt files have an extra blank line
    # near the top that can be used to differentiate it from dsfinal.txt
    if len(lines[6]) == 1:
        # dsin.txt file type
        dstype = 0
    else:
        # dsfinal.txt file type
        dstype = 1

    # Experiment parameter options:
    opts_Exp = {'StartTime': (9, 8), 'StopTime': (11, 9),
                'Increment': (12, 10), 'nInterval': (13, 11),
                'Tolerance': (14, 12), 'MaxFixedStep': (16, 13),
                'Algorithm': (18, 14)}

    # Method tuning parameter options:
    opts_Tun = {'grid': (44, 18), 'nt': (54, 19),
                'dense': (55, 20), 'evgrid': (56, 21),
                'evu': (57, 22), 'evuord': (58, 23),
                'error': (59, 24), 'jac': (60, 25),
                'xd0c': (61, 26), 'f3': (62, 27),
                'f4': (63, 28), 'f5': (64, 29),
                'debug': (65, 30), 'pdebug': (66, 31),
                'fmax': (67, 32), 'ordmax': (68, 33),
                'hmax': (69, 34), 'hmin': (70, 35),
                'h0': (71, 36), 'teps': (72, 37),
                'eveps': (73, 38), 'eviter': (74, 39),
                'delaym': (75, 40), 'fexcep': (76, 41),
                'tscale': (77, 42)}

    #  Output parameter options:
    opts_Out = {'lprec': (87, 48), 'lx': (88, 49),
                'lxd': (89, 50), 'lu': (90, 51),
                'ly': (91, 52), 'lz': (92, 53),
                'lw': (93, 54), 'la': (94, 55),
                'lperf': (95, 56), 'levent': (96, 57),
                'lres': (97, 58), 'lshare': (98, 59),
                'lform': (99, 60)}

    fnew = open(dsFileOut, 'w')
    # Simulation Settings:
    # Search for each of the experiment options and replace the value
    for key, value in opts_Exp.items():
        if key in dicSim:
            lines[value[dstype]] = ' %s\n' % dicSim[key]

    # Search for each of the method tuning options and replace the value
    for key, value in opts_Tun.items():
        if key in dicSim:
            lines[value[dstype]] = ' %s\n' % dicSim[key]

    # Search for each of the output options and replace the value
    for key, value in opts_Out.items():
        if key in dicSim:
            lines[value[dstype]] = ' %s\n' % dicSim[key]
    # End Simulation Settings:

    # Initial Condition Settings:
    # Search for variable and replace the inital value
    # Variables are defined by 6 columns. Only 4 are currently read
    # Guidance is taken from section starting with:
    # "Matrix with 6 columns defining the initial value calculation"
    # c1 : type of initial value
    # c2 : value
    # c3 : Minimum value (ignored, if Minimum >= Maximum)
    # c4 : Maximum value (ignored, if Minimum >= Maximum)
    # c5 : Category of variable
    # c6 : Data type of variable and flags according to dsBaseType
    for key, value in dicVars.items():
        isFound = False
        for x in xrange(len(lines)):
            lin = lines[x]
            if key in lin:
                isFound = True
                temp = lines[x-1]
                temp = map(float, temp.split())
                c1 = int(temp[0])
                c2 = dicVars[key]
                c3 = temp[2]
                c4 = temp[3]
                lines[x-1] = ' %s %s %s %s\n' % (c1, c2, c3, c4)
        if not isFound:
            print key
            print lin
            raise ValueError('%s not found in %s.' % (key, dsFileIn))

    fnew.writelines(lines)
    fnew.close()

if __name__ == "__main__":
    dicSim = {'StartTime': 0,'StopTime': 100}
    dicVars = {'m_flow': 10}
    create_dsinORfinal(dicSim, dicVars)
 