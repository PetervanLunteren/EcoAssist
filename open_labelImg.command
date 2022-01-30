#!/usr/bin/env bash

cd ~/EcoAssist_files || { echo "Could not change directory to EcoAssist_files. Command could not be run. Did you change the name or folder structure since installing EcoAssist?"; exit 1; }

LBL="labelImg"
if [ -d "$LBL" ]; then
  echo "Dir ${LBL} already exists! Skipping this step."
else
  echo "Dir ${LBL} does not exist! Clone repo..."
  git clone https://github.com/tzutalin/labelImg.git
  cd labelImg || { echo "Could not change directory. Command could not be run. Please install labelImg manually: https://github.com/tzutalin/labelImg"; exit 1; }
  git checkout 276f40f5e5bbf11e84cfa7844e0a6824caf93e11
  cd .. || { echo "Could not change directory. Command could not be run. Please install labelImg manually: https://github.com/tzutalin/labelImg"; exit 1; }
fi

PATH2CONDA_SH=`conda info | grep 'base environment' | cut -d ':' -f 2 | xargs | cut -d ' ' -f 1`
PATH2CONDA_SH+="/etc/profile.d/conda.sh"
echo "Path to conda.sh: $PATH2CONDA_SH"
# shellcheck source=src/conda.sh
source "$PATH2CONDA_SH"
conda activate ecoassistcondaenv
export PYTHONPATH="$PYTHONPATH:$PWD"

cd labelImg || { echo "Could not change directory to labelImg. Command could not be run. Did you change the name or folder structure since installing labelImg?"; exit 1; }
pyrcc5 -o libs/resources.py resources.qrc
echo "python labelImg.py '${1}' '${2}' '${1}'"
python labelImg.py "${1}" "${2}" "${1}"