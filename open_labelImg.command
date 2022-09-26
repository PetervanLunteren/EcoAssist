#!/usr/bin/env bash

### OSX and Linux commands to open labelImg from EcoAssist https://github.com/PetervanLunteren/EcoAssist
### Peter van Lunteren, 26 September 2022

# check the OS and set var
if [ "$(uname)" == "Darwin" ]; then
  echo "This is an OSX computer..."
  if [[ $(sysctl -n machdep.cpu.brand_string) =~ "Apple" ]]; then
    echo "   ...with an M1 processor."
    PLATFORM="M1 Mac"
  else
    echo "   ...with an Intel processor."
    PLATFORM="Intel Mac"
  fi
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
  echo "This is an Linux computer."
  PLATFORM="Linux"
fi

# set location var
if [ "$PLATFORM" = "M1 Mac" ] || [ "$PLATFORM" = "Intel Mac" ]; then
  LOCATION_ECOASSIST_FILES="/Applications/.EcoAssist_files"
elif [ "$PLATFORM" = "Linux" ]; then
  LOCATION_ECOASSIST_FILES="$HOME/.EcoAssist_files"
fi

# locate conda.sh on local machine, source it and add to PATH
PATH_TO_CONDA_INSTALLATION_TXT_FILE=$LOCATION_ECOASSIST_FILES/EcoAssist/path_to_conda_installation.txt
PATH_TO_CONDA=`cat $PATH_TO_CONDA_INSTALLATION_TXT_FILE`
echo "Path to conda as imported from $PATH_TO_CONDA_INSTALLATION_TXT_FILE is: $PATH_TO_CONDA"
PATH2CONDA_SH="$PATH_TO_CONDA/etc/profile.d/conda.sh"
echo "Path to conda.sh: $PATH2CONDA_SH"
# shellcheck source=src/conda.sh
source "$PATH2CONDA_SH"

# activate conda env and add paths
conda activate ecoassistcondaenv
export PYTHONPATH="$PYTHONPATH:$LOCATION_ECOASSIST_FILES"
export PATH="$PATH_TO_CONDA/envs/ecoassistcondaenv/lib/python3.8/site-packages:$PATH"

# locate brew installed packages and add to PATH
PATH_TO_BREW_INSTALLATION_TXT_FILE=$LOCATION_ECOASSIST_FILES/EcoAssist/path_to_brew_installation.txt
if [ "$PLATFORM" = "M1 Mac" ] ; then
  PATH_TO_BREW=`cat $PATH_TO_BREW_INSTALLATION_TXT_FILE`
  echo "Path to brew as imported from $PATH_TO_BREW_INSTALLATION_TXT_FILE is: $PATH_TO_BREW"
  export PATH="$PATH_TO_BREW/bin:$PATH"
fi

# open labelImg with arguments given by EcoAssist_GUI.py
cd $LOCATION_ECOASSIST_FILES/labelImg || { echo "Could not change directory to labelImg. Command could not be run. Did you change the name or folder structure since installing labelImg?"; exit 1; }
pyrcc5 -o libs/resources.py resources.qrc
echo "python3 labelImg.py '${1}' '${2}' '${1}'"
if [ "$PLATFORM" = "M1 Mac" ] ; then
  arch -arm64 python3 labelImg.py "${1}" "${2}" "${1}"
else
  python3 labelImg.py "${1}" "${2}" "${1}"
fi
