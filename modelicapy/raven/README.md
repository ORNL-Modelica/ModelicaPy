**Requirements**

- Tested on Ubuntu 16/Linux-x86_64 via WSL.
- FMU generated with Dymola Linux-x86_64 and binary export license.

To run this lorenzSystem example one must install RAVEN and install pyfmi

1. To install RAVEN see below
2. conda install -c conda-forge pyfmi
	- make sure you do this in the created raven environment (i.e., source activate raven_libraries)

**Steps to install RAVEN**

For more information see https://github.com/idaholab/raven/wiki

```
sudo apt-get install libtool git python-dev swig g++
wget https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh
bash Miniconda2-latest-Linux-x86_64.sh
mkdir Documents
cd Documents
git clone https://github.com/idaholab/raven.git
cd raven
git submodule init moose
git submodule update moose
./scripts/establish_conda_env.sh --install --conda-defs ~/miniconda2/etc/profile.d/conda.sh
./build_raven
./run_tests -j2
```

**Trouble installing?**

If you get the an error related to Qt, change the backend.

https://github.com/idaholab/raven/wiki/Troubleshooting#qt-related-errors-such-as-attributeerror-figure-is-not-a-qt-property-or-a-signal
 
