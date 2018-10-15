import os
import setuptools

# Guides for making this file:
# http://packages.python.org/an_example_pypi_project/setuptools.html
# https://marthall.github.io/blog/how-to-package-a-python-app/
# https://python-packaging.readthedocs.io/en/latest/minimal.html

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setuptools.setup(
    name="modelicapy",
    version="0.1",
    author="Scott Greenwood",
    author_email="greenwoodms@ornl.gov",
    description=("A Python library containing a variety of scripts and functions for interaction with Modelica and TRANSFORM"),
    long_description=read('README.md'),
    license="UT-Battell Open Source License (Permissive)",
    keywords="modelica dymola openmodelica mat",
    url="https://github.com/ORNL-Modelica/ModelicaPy",
    install_requires=['future'],
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 5 - Development",
        "Environment :: Console",
        "License :: Open Source :: UT-Battelle Permissive",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "Topic :: Utilities"
    ],
)