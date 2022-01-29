#!/usr/bin/env bash

cd ~/ImSep_files || { echo "Could not change directory to ImSep_files. Command could not be run. Did you change the name or folder structure since installing ImSep?"; exit 1; }

LBL="labelImg"
if [ -d "$LBL" ]; then
  echo "Dir ${LBL} already exists! Skipping this step."
else
  echo "Dir ${LBL} does not exist! Clone repo..."
  git clone https://github.com/tzutalin/labelImg.git
fi

 PATH2PIP="`which pip`"
 echo "Path to pip: $PATH2PIP"
 PATH2CONDA_SH="${PATH2PIP%/*/*/*/*}/etc/profile.d/conda.sh"
 echo "Path to conda.sh: $PATH2CONDA_SH"
 # shellcheck source=src/conda.sh
 source "$PATH2CONDA_SH"
 conda activate imsepcondaenv
 export PYTHONPATH="$PYTHONPATH:$PWD"

cd labelImg || { echo "Could not change directory to labelImg. Command could not be run. Did you change the name or folder structure since installing labelImg?"; exit 1; }
pyrcc5 -o libs/resources.py resources.qrc
echo "python labelImg.py '${1}' '${2}' '${1}'"
python labelImg.py "${1}" "${2}" "${1}"