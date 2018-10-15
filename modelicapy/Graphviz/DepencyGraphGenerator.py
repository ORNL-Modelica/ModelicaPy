# -*- coding: utf-8 -*-
"""
Created on Mon Apr 25 15:25:18 2016

@author: Scott Greenwood

# Specify the directory for which to search for '.mo' files. A text document
# will be generated that contains the full file path of every .mo file that
# exists in that directory.
#
# The text file will then be used to search for the 'extends' keyword to
# identify the model's dependencies. A file is generated with the prefix
# 'Dep' that lists the dependcies in the specified format.
#
# The generated lists are then condensed into one file with the appropriate
# wrapper and dependency graph attributes.
#
# This final file is then sent to Graphviz to generate the dependency graph.
#
# File created for Graphviz is of format:
# digraph GraphName {
    "sourceName" -> "resultName"
    }
"""

from FindMOFiles import findFiles
from SearchMOFile import searchFile
import glob
import os

# !!! USER INPUT SECTION !!!

directories = ['C:/Users/vmg/Documents/Modelica/TRANSFORM-Library/TRANSFORM',
    'C:/Users/vmg/Documents/Modelica/TRANSFORM-Library/TRANSFORM/obsolete',
    'C:/Users/vmg/Desktop/Modelica',
    'C:/Users/vmg/Desktop/TF - Legacy/TRANSFORM_legacy']

# Specify search directory
directory = directories[0]

# Use a toplevel directory as start of source name?
useDIRName = True

# Specify toplevel directory name to start
DIRName = '/TRANSFORM/'
#DIRName = '/Modelica/'
#DIRName = '/TRANSFORM_legacy/'

# Use only component name from after last period in extends for result?
usePeriod = False

# !!! END USER INPUT SECTION !!!


# Delete the contents of ~/Dependecies
folder = 'C:/Users/vmg/Documents/Modelica/ModelicaPy/Graphviz/Dependencies'
if not os.path.exists(folder):
    os.mkdir(folder)

for the_file in os.listdir(folder):
    file_path = os.path.join(folder, the_file)
    try:
        if os.path.isfile(file_path):
            os.unlink(file_path)
        # elif os.path.isdir(file_path): shutil.rmtree(file_path)
    except Exception as e:
        print(e)

# Find all MO files
findFiles(directory)

# Find all dependencies in each file
with open('allMOFiles.txt', 'r') as allFiles:
    lines = allFiles.read().splitlines()
    for i in range(0, len(lines)):
        fullFile = lines[i].replace('\\', '/')
        searchFile(fullFile, useDIRName, DIRName, usePeriod)


# === Idea ===
# This would be a good place to put in some sort of post processing.
# For example, removing all lines in DepMaster.gv that have a component name
# to 'Function' as this is a common icon reference that has no real consequence
# === End Idea ===


# Condense information to one master file
list_of_files = glob.glob('Dependencies/*.txt')
with open('DepMaster.gv', 'w') as outputFile:
    outputFile.write('digraph DepMaster { \n')
    # print('size="6,6";', file=outputFile)
    outputFile.write('node [color=lightblue2, style=filled];\n')

    outputFile.write('')  # add a blank line for visual separation

    for fileName in list_of_files:
        with open(fileName, 'r') as f:
            lines = f.read().splitlines()
            for i in range(0, len(lines)):
                outputFile.write(lines[i]+'\n')

    outputFile.write('\n}')

# Remove all lines that reference an Icon as not very informative
newlines=[]
with open('DepMaster.gv', 'r') as tmp:
    tmplines = tmp.readlines()
    for tlin in tmplines:
        if 'Icons.' in tlin:
            pass
        else:
            newlines.append(tlin)

with open('DepMaster.gv', 'w') as outputFile:
    outputFile.writelines(newlines)
    
# Generate dependecy graph