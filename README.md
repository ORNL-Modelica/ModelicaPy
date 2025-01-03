# ModelicaPy
A Python package containing a variety of scripts and functions for interaction with Modelica and TRANSFORM.

## Contact

Scott Greenwood

## Installation and Use

https://pypi.org/project/modelicapy/ - *pip version may be behind GitHub* 

    pip install modelicapy

	from modelicapy import cleanData as cln
	
**For updating your pip install to the latest GitHub version:**

    pip install git+https://github.com/ORNL-Modelica/ModelicaPy.git@master
    
  
	
or

    pip install --upgrade git+https://github.com/ORNL-Modelica/ModelicaPy.git@master
	
## Brief Description of Files

1. GraphViz folder - Generation of dependency graphs of a Modelica library.
2. parametric.py - Generate parametric sweeps for simulations.
3. read_dslog.py - Create a summary of the dslog file (e.g., pass/fail, simulation time, etc.).
4. gen_dsin.py - Generate new dsin.txt file from dsin.txt or dsfinal.txt with modified simulation and/or variable parameters.
5. regressiontest.py - Modified regressiontest.py file from BuildingsPy for regression testing on Windows (use with buildingspy tag 1.7 and Anaconda2)
6. cleanData.py - Returns data using a 'r=Reader' from buildingspy that has been cleaned of repeated values (i.e., due to events) and interpolates between values.
7. getValues - Functions to return single values from components. Helpful for getting initial values. Includes Modelica formatted output. For use with TRANSFORM.
8. createUnitScripts.py - autogenerate .mos files for use with buildingspy regression test.
9. raven folder - contains an example of running FMU (via pyFMI) with [RAVEN](https://github.com/idaholab/raven)
10. wordclouds folder - example playing with the Modelica conference proceedings and wordcloud
11. optimize folder - a demonstration. auto-simulate multiple heat transfer models, select the best one based on gold values, and then optimize CFs to match the gold values
12. FMPy folder - a couple simple templates for using fmpy
13. coolTSplots - a reference (may not simulate) for putting Modelica simulation results onto a TS diagram
14. createUnitTestScript_runAll.py - Quickly generate a .mos for simulating all tests in a library. Tested on Dymola and OMEdt but is extensible to other IDEs.

## To Contribute...
You may report any issues with using the Issues button.

Contributions in the form of Pull Requests are always welcome.
