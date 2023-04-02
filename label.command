#!/usr/bin/env bash

### OSX and Linux commands to open labelImg from EcoAssist https://github.com/PetervanLunteren/EcoAssist
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
  echo "This is an Linux computer."
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

# add paths
export PYTHONPATH="$PYTHONPATH:$LOCATION_ECOASSIST_FILES"
export PATH="$CONDA_DIR/envs/ecoassistcondaenv/lib/python3.8/site-packages:$PATH"
if [ "$PLATFORM" = "Apple Silicon Mac" ] ; then
  export PATH="$HOMEBREW_DIR/bin:$PATH"
fi

# open labelImg with arguments given by EcoAssist_GUI.py
cd $LOCATION_ECOASSIST_FILES/labelImg || { echo "Could not change directory to labelImg. Command could not be run. Did you change the name or folder structure since installing labelImg?"; exit 1; }
pyrcc5 -o libs/resources.py resources.qrc
echo "python3 labelImg.py '${1}' '${2}' '${1}'"
if [ "$PLATFORM" = "Apple Silicon Mac" ] ; then
  arch -arm64 python3 labelImg.py "${1}" "${2}" "${1}"
else
  python3 labelImg.py "${1}" "${2}" "${1}"
fi
