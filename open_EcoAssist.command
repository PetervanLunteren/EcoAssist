#!/usr/bin/env bash

# change directory
cd ~/EcoAssist_files || { echo "Could not change directory to EcoAssist_files. Command could not be run. Did you change the name or folder structure since installing EcoAssist?"; exit 1; }

# path to conda installation
PATH2CONDA=`conda info | grep 'base environment' | cut -d ':' -f 2 | xargs | cut -d ' ' -f 1`
echo "Path to conda: $PATH2CONDA"
echo ""

# path to conda.sh
PATH2CONDA_SH="$PATH2CONDA/etc/profile.d/conda.sh"
echo "Path to conda.sh: $PATH2CONDA_SH"
echo ""

# path to python exe
PATH2PYTHON="$PATH2CONDA/envs/ecoassistcondaenv/bin/"
echo "Path to python: $PATH2PYTHON"
echo ""

# shellcheck source=src/conda.sh
source $PATH2CONDA_SH

# activate environment
conda activate ecoassistcondaenv

# add PYTHONPATH
export PYTHONPATH="$PYTHONPATH:$PATH2PYTHON:$PWD/cameratraps:$PWD/ai4eutils"
echo "PYHTONPATH=$PYTHONPATH"
echo ""

# add python exe to PATH
export PATH="$PATH2PYTHON:/usr/bin/:$PATH"
echo "PATH=$PATH"
echo ""

# version of python exe
PYVERSION=`python -V`
echo "python version: $PYVERSION"
echo ""

# location of python exe
PYLOCATION=`which python`
echo "python location: $PYLOCATION"
echo ""

# check tensorflow version and GPU availability
python EcoAssist/tf_check.py

# run script
python EcoAssist/EcoAssist_GUI.py