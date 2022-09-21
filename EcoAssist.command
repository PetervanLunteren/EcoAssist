#!/usr/bin/env bash

### OSX commands to open the EcoAssist application https://github.com/PetervanLunteren/EcoAssist
### Peter van Lunteren, 18 September 2022

# set vars
LOCATION_ECOASSIST_FILES="/Applications/.EcoAssist_files"
PATH_TO_CONDA_INSTALLATION_TXT_FILE=$LOCATION_ECOASSIST_FILES/EcoAssist/path_to_conda_installation.txt
PATH_TO_BREW_INSTALLATION_TXT_FILE=$LOCATION_ECOASSIST_FILES/EcoAssist/path_to_brew_installation.txt

# log output to logfiles
exec 1> $LOCATION_ECOASSIST_FILES/EcoAssist/logfiles/stdout.txt
exec 2> $LOCATION_ECOASSIST_FILES/EcoAssist/logfiles/stderr.txt

# timestamp and log the start
START_DATE=`date`
echo "Starting at: $START_DATE"
echo ""

# log system information
UNAME_A=`uname -a`
MACHINE_INFO=`system_profiler SPSoftwareDataType SPHardwareDataType SPMemoryDataType SPStorageDataType`
FILE_SIZES_DEPTH_0=`du -sh $LOCATION_ECOASSIST_FILES`
FILE_SIZES_DEPTH_1=`du -sh $LOCATION_ECOASSIST_FILES/*`
FILE_SIZES_DEPTH_2=`du -sh $LOCATION_ECOASSIST_FILES/*/*`
echo "uname -a:"
echo ""
echo "$UNAME_A"
echo ""
echo "System information:"
echo ""
echo "$MACHINE_INFO"
echo ""
echo "File sizes with depth 0:"
echo ""
echo "$FILE_SIZES_DEPTH_0"
echo ""
echo "File sizes with depth 1:"
echo ""
echo "$FILE_SIZES_DEPTH_1"
echo ""
echo "File sizes with depth 2:"
echo ""
echo "$FILE_SIZES_DEPTH_2"
echo ""

# change directory
cd $LOCATION_ECOASSIST_FILES || { echo "Could not change directory to EcoAssist_files. Command could not be run. Did you change the name or folder structure since installing EcoAssist?"; exit 1; }

# locate conda
PATH_TO_CONDA=`cat $PATH_TO_CONDA_INSTALLATION_TXT_FILE`
echo "Path to conda as imported from $PATH_TO_CONDA_INSTALLATION_TXT_FILE is: $PATH_TO_CONDA"

# path to conda.sh
PATH_TO_CONDA_SH="$PATH_TO_CONDA/etc/profile.d/conda.sh"
echo "Path to conda.sh: $PATH_TO_CONDA_SH"

# path to python exe
PATH_TO_PYTHON="$PATH_TO_CONDA/envs/ecoassistcondaenv/bin/"
echo "Path to python: $PATH_TO_PYTHON"
echo ""

# shellcheck source=src/conda.sh
source "$PATH_TO_CONDA_SH"

# activate environment
conda activate ecoassistcondaenv

# add PYTHONPATH
export PYTHONPATH="$PYTHONPATH:$PATH_TO_PYTHON:$PWD/cameratraps:$PWD/ai4eutils:$PWD/yolov5"
echo "PYHTONPATH=$PYTHONPATH"
echo ""

# add python exe to PATH
export PATH="$PATH_TO_PYTHON:/usr/bin/:$PATH"
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

# run script
python EcoAssist/EcoAssist_GUI.py

# timestamp and log the end
END_DATE=`date`
echo ""
echo "Closing at: $END_DATE"