#!/usr/bin/env bash

### OSX commands to open labelImg from EcoAssist https://github.com/PetervanLunteren/EcoAssist
### Peter van Lunteren, 21 September 2022

# set vars
LOCATION_ECOASSIST_FILES="/Applications/.EcoAssist_files"
PATH_TO_CONDA_INSTALLATION_TXT_FILE=$LOCATION_ECOASSIST_FILES/EcoAssist/path_to_conda_installation.txt
PATH_TO_BREW_INSTALLATION_TXT_FILE=$LOCATION_ECOASSIST_FILES/EcoAssist/path_to_brew_installation.txt

# check if computer is an M1 mac and set var
echo "Chip: `sysctl -n machdep.cpu.brand_string`" 2>&1 | tee -a "$LOG_FILE"
if [[ $(sysctl -n machdep.cpu.brand_string) =~ "Apple" ]]; then
  echo "This is an M1 computer." 2>&1 | tee -a "$LOG_FILE"
  M1_MAC=true
else
  echo "This is not an M1 computer." 2>&1 | tee -a "$LOG_FILE"
  M1_MAC=false
fi

# locate conda.sh on local machine, source it and add to PATH
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
PATH_TO_BREW=`cat $PATH_TO_BREW_INSTALLATION_TXT_FILE`
echo "Path to brew as imported from $PATH_TO_BREW_INSTALLATION_TXT_FILE is: $PATH_TO_BREW"
export PATH="$PATH_TO_BREW/bin:$PATH"

# open labelImg with arguments given by EcoAssist_GUI.py
cd $LOCATION_ECOASSIST_FILES/labelImg || { echo "Could not change directory to labelImg. Command could not be run. Did you change the name or folder structure since installing labelImg?"; exit 1; }
pyrcc5 -o libs/resources.py resources.qrc
echo "python3 labelImg.py '${1}' '${2}' '${1}'"
if [ "$M1_MAC" = true ] ; then
  arch -arm64 python3 labelImg.py "${1}" "${2}" "${1}"
else
  python3 labelImg.py "${1}" "${2}" "${1}"
fi
