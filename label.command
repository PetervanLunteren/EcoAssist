#!/usr/bin/env bash

### OSX and Linux commands to open Human-in-the-loop from EcoAssist https://github.com/PetervanLunteren/EcoAssist
### Peter van Lunteren, 1 May 2024 (latest edit)

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
ECOASSISTCONDAENV_BASE="${CONDA_DIR}/envs/ecoassistcondaenv-base"
ECOASSISTCONDAENV_PYTORCH="${CONDA_DIR}/envs/ecoassistcondaenv-pytorch"
ECOASSISTCONDAENV_TENSORFLOW="${CONDA_DIR}/envs/ecoassistcondaenv-tensorflow"
PIP_BASE="${ECOASSISTCONDAENV_BASE}/bin/pip"
PIP_PYTORCH="${ECOASSISTCONDAENV_PYTORCH}/bin/pip"
PIP_TENSORFLOW="${ECOASSISTCONDAENV_TENSORFLOW}/bin/pip"

# add paths
export PYTHONPATH="$PYTHONPATH:$LOCATION_ECOASSIST_FILES"
export PATH="${ECOASSISTCONDAENV_BASE}/lib/python3.8/site-packages:$PATH"
if [ "$PLATFORM" = "Apple Silicon Mac" ] ; then
  export PATH="$HOMEBREW_DIR/bin:$PATH"
fi

# activate env
conda activate $ECOASSISTCONDAENV_BASE

# open Human-in-the-loop with arguments given by EcoAssist_GUI.py
cd $LOCATION_ECOASSIST_FILES/Human-in-the-loop || { echo "Could not change directory to Human-in-the-loop. Command could not be run."; exit 1; }
# pyrcc5 -o libs/resources.py resources.qrc # not nessecary anymore since we use the pyside6 variant of labelimg? 
echo "python3 labelImg.py '${1}' '${2}'"
if [ "$PLATFORM" = "Apple Silicon Mac" ] ; then
  arch -arm64 python3 labelImg.py "${1}" "${2}"
else
  python3 labelImg.py "${1}" "${2}"
fi

# activate env for main script
conda activate $ECOASSISTCONDAENV_BASE
