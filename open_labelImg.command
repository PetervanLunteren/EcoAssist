#!/usr/bin/env bash

### OSX commands to open labelImg from EcoAssist https://github.com/PetervanLunteren/EcoAssist
### Peter van Lunteren, 18 September 2022

# set vars
LOCATION_ECOASSIST_FILES="/Applications/.EcoAssist_files"
PATH_TO_CONDA_INSTALLATION_TXT_FILE=$LOCATION_ECOASSIST_FILES/EcoAssist/path_to_conda_installation.txt

# change into dir
cd $LOCATION_ECOASSIST_FILES || { echo "Could not change directory to EcoAssist_files. Command could not be run. Did you change the name or folder structure since installing EcoAssist?"; exit 1; }

# locate conda.sh on local machine and source it
PATH_TO_CONDA=`cat $PATH_TO_CONDA_INSTALLATION_TXT_FILE`
echo "Path to conda as imported from $PATH_TO_CONDA_INSTALLATION_TXT_FILE is: $PATH_TO_CONDA"
PATH2CONDA_SH="$PATH_TO_CONDA/etc/profile.d/conda.sh"
echo "Path to conda.sh: $PATH2CONDA_SH"
# shellcheck source=src/conda.sh
source "$PATH2CONDA_SH"
conda activate ecoassistcondaenv
export PYTHONPATH="$PYTHONPATH:$PWD"

# open labelImg with arguments given by EcoAssist_GUI.py
cd labelImg || { echo "Could not change directory to labelImg. Command could not be run. Did you change the name or folder structure since installing labelImg?"; exit 1; }
pyrcc5 -o libs/resources.py resources.qrc
echo "python labelImg.py '${1}' '${2}' '${1}'"
python labelImg.py "${1}" "${2}" "${1}"