import setuptools
from os import path

def read(fname):
    return open(path.join(path.dirname(__file__), fname)).read()
	
setuptools.setup(
    name="modelicapy",
    version="0.3.1",
    author="Scott Greenwood",
    author_email="greenwoodms@ornl.gov",
    description=("A Python library containing a variety of scripts and functions for interaction with Modelica and TRANSFORM"),
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    license="UT-Battelle Open Source License (Permissive)",
    keywords="modelica dymola openmodelica mat",
    url="https://github.com/ORNL-Modelica/ModelicaPy",
    install_requires=['future'],
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "Topic :: Utilities"
    ],
)