#!/usr/bin/env bash
cd ~/EcoAssist_files || { echo "Could not change directory to EcoAssist_files. Command could not be run. Did you change the name or folder structure since installing EcoAssist?"; exit 1; }

PATH2CONDA_SH=`conda info | grep 'base environment' | cut -d ':' -f 2 | xargs | cut -d ' ' -f 1`
PATH2CONDA_SH+="/etc/profile.d/conda.sh"
echo "Path to conda.sh: $PATH2CONDA_SH"
# shellcheck source=src/conda.sh
source $PATH2CONDA_SH
conda activate ecoassistcondaenv
export PYTHONPATH="$PYTHONPATH:$PWD/cameratraps:$PWD/ai4eutils"
python EcoAssist/EcoAssist_GUI.py