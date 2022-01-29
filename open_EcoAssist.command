#!/usr/bin/env bash
cd ~/EcoAssist_files || { echo "Could not change directory to EcoAssist_files. Command could not be run. Did you change the name or folder structure since installing EcoAssist?"; exit 1; }

PATH2PIP="`which pip`"
echo "Path to pip: $PATH2PIP"
PATH2CONDA_SH=`echo $PATH2PIP | sed 's/\(anaconda.\).*/\1/g'`
PATH2CONDA_SH+="/etc/profile.d/conda.sh"

echo "Path to conda.sh: $PATH2CONDA_SH"
# shellcheck source=src/conda.sh
source $PATH2CONDA_SH
conda activate ecoassistcondaenv
export PYTHONPATH="$PYTHONPATH:$PWD/cameratraps:$PWD/ai4eutils"
python EcoAssist/EcoAssist_GUI.py