# ModelicaPy
A Python library containing a variety of scripts and functions for interaction with Modelica.

## Authors

* **Scott Greenwood**

See also the list of [contributors](https://github.com/ORNL-Modelica/ModelicaPy/contributors) who participated in this project.

## License

This project is licensed under the UT-Battelle Open Source [License](LICENSE.md) (Permissive) - see the [LICENSE.md](LICENSE.md) file for details

Copyright 2017, UT-Battelle, LLC

## Brief Description of Files

1. GraphViz - Generation of dependency graphs of a Modelica library.
2. parametric.py - Generate parametric sweeps for simulations.
3. read_dslog.py - Create a summary of the dslog file (e.g., pass/fail, simulation time, etc.).
4. gen_dsin.py - Generate new dsin.txt file from dsin.txt or dsfinal.txt with modified simulation and/or variable parameters.
5. regressiontest.py - Modified regressiontest.py file from BuildingsPy for regression testing on Windows
6. cleanData.py - Returns data using a 'r=Reader' from buildingspy that has been cleaned of repeated values (i.e., due to events) and interpolates between values.
7. getValues - Functions to return single values from components. Helpful for getting initial values. Includes Modelica formatted output. For use with TRANSFORM.
8. createUnitScripts.py - autogenerate .mos files for use with buildingspy regression test.

## To Contribute...
You may report any issues with using the [Issues](https://github.com/ORNL-Modelica/ModelicaPy/issues) button.

Contributions in the form of [Pull Requests](https://github.com/ORNL-Modelica/ModelicaPy/pulls) are always welcome.
