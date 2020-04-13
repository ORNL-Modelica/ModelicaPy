# ModelicaPy
A Python package containing a variety of scripts and functions for interaction with Modelica and TRANSFORM.

## Contact

Scott Greenwood

## License

This project is licensed under the UT-Battelle Open Source [License](LICENSE.md) (Permissive)

Copyright 2017, UT-Battelle, LLC

## Installation and Use

https://pypi.org/project/modelicapy/ - *pip version may be behind GitHub* 

    pip install modelicapy

	from modelicapy import cleanData as cln
	
**For updating your pip install to the latest GitHub version:**

    pip install git+git://ADDRESS@master
	
or

    pip install --upgrade git+git://ADDRESS@master
	
## Brief Description of Files

1. GraphViz folder - Generation of dependency graphs of a Modelica library.
2. parametric.py - Generate parametric sweeps for simulations.
3. read_dslog.py - Create a summary of the dslog file (e.g., pass/fail, simulation time, etc.).
4. gen_dsin.py - Generate new dsin.txt file from dsin.txt or dsfinal.txt with modified simulation and/or variable parameters.
5. regressiontest.py - Modified regressiontest.py file from BuildingsPy for regression testing on Windows
6. cleanData.py - Returns data using a 'r=Reader' from buildingspy that has been cleaned of repeated values (i.e., due to events) and interpolates between values.
7. getValues - Functions to return single values from components. Helpful for getting initial values. Includes Modelica formatted output. For use with TRANSFORM.
8. createUnitScripts.py - autogenerate .mos files for use with buildingspy regression test.
9. raven folder - contains an example of running FMU (via pyFMI) with [RAVEN](https://github.com/idaholab/raven)
10. wordclouds folder - example playing with the Modelica conference proceedings and wordcloud

## To Contribute...
You may report any issues with using the Issues button.

Contributions in the form of Pull Requests are always welcome.
