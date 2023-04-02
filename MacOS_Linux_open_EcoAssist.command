#!/usr/bin/env bash

### OSX and Linux commands to open the EcoAssist application https://github.com/PetervanLunteren/EcoAssist
### Peter van Lunteren, 2 Apr 2023 (latest edit)

# check the OS and set var
if [ "$(uname)" == "Darwin" ]; then
  echo "This is an OSX computer..."
  if [[ $(sysctl -n machdep.cpu.brand_string) =~ "Apple" ]]; then
    echo "   ...with an Apple Silicon processor."
    PLATFORM="Apple Silicon Mac"
  else
    echo "   ...with an Intel processor."
    PLATFORM="Intel Mac"
  fi
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
  echo "This is a Linux computer."
  PLATFORM="Linux"
fi

# set location var
if [ "$PLATFORM" = "Apple Silicon Mac" ] || [ "$PLATFORM" = "Intel Mac" ]; then
  LOCATION_ECOASSIST_FILES="/Applications/.EcoAssist_files"
elif [ "$PLATFORM" = "Linux" ]; then
  LOCATION_ECOASSIST_FILES="$HOME/.EcoAssist_files"
fi

# set variables
CONDA_DIR="${LOCATION_ECOASSIST_FILES}/miniforge"
ECOASSISTCONDAENV="${CONDA_DIR}/envs/ecoassistcondaenv"
PIP="${ECOASSISTCONDAENV}/bin/pip"
HOMEBREW_DIR="${LOCATION_ECOASSIST_FILES}/homebrew"

# log output to logfiles
exec 1> $LOCATION_ECOASSIST_FILES/EcoAssist/logfiles/stdout.txt
exec 2> $LOCATION_ECOASSIST_FILES/EcoAssist/logfiles/stderr.txt

# timestamp and log the start
START_DATE=`date`
echo "Starting at: $START_DATE"
echo ""

# log system information
UNAME_A=`uname -a`
if [ "$PLATFORM" = "Apple Silicon Mac" ] || [ "$PLATFORM" = "Intel Mac" ]; then
  MACHINE_INFO=`system_profiler SPSoftwareDataType SPHardwareDataType SPMemoryDataType SPStorageDataType`
fi
FILE_SIZES_DEPTH_0=`du -sh $LOCATION_ECOASSIST_FILES`
FILE_SIZES_DEPTH_1=`du -sh $LOCATION_ECOASSIST_FILES/*`
FILE_SIZES_DEPTH_2=`du -sh $LOCATION_ECOASSIST_FILES/*/*`
echo "uname -a:"
echo ""
echo "$UNAME_A"
echo ""
if [ "$PLATFORM" = "Apple Silicon Mac" ] || [ "$PLATFORM" = "Intel Mac" ]; then
  echo "System information:"
  echo ""
  echo "$MACHINE_INFO"
  echo ""
fi
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

# activate conda env
source "${LOCATION_ECOASSIST_FILES}/miniforge/etc/profile.d/conda.sh"
source "${LOCATION_ECOASSIST_FILES}/miniforge/bin/activate"
export PATH="${CONDA_DIR}/bin":$PATH
conda activate $ECOASSISTCONDAENV

# path to python exe
PATH_TO_PYTHON="${ECOASSISTCONDAENV}/bin/"
echo "Path to python: $PATH_TO_PYTHON"
echo ""

# add to PYTHONPATH
export PYTHONPATH="$PYTHONPATH:$PATH_TO_PYTHON:$PWD/cameratraps:$PWD/ai4eutils:$PWD/yolov5:$PWD/EcoAssist"
echo "PYHTONPATH=$PYTHONPATH"
echo ""

# add to PATH
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
