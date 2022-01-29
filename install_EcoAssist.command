#!/usr/bin/env bash

mkdir -p ~/EcoAssist_files
cd ~/EcoAssist_files || { echo "Could not change directory to EcoAssist_files. Command could not be run. Please install EcoAssist manually: https://github.com/PetervanLunteren/EcoAssist"; exit 1; }

ECO="EcoAssist"
if [ -d "$ECO" ]; then
  echo "Dir ${ECO} already exists! Skipping this step."
else
  echo "Dir ${ECO} does not exist! Clone repo..."
  git clone https://github.com/PetervanLunteren/EcoAssist.git
fi

CAM="cameratraps"
if [ -d "$CAM" ]; then
  echo "Dir ${CAM} already exists! Skipping this step."
else
  echo "Dir ${CAM} does not exist! Clone repo..."
  git clone https://github.com/Microsoft/cameratraps
fi

AI4="ai4eutils"
if [ -d "$AI4" ]; then
  echo "Dir ${AI4} already exists! Skipping this step."
else
  echo "Dir ${AI4} does not exist! Clone repo..."
  git clone https://github.com/Microsoft/ai4eutils
fi

MD="md_v4.1.0.pb"
if [ -f "$MD" ]; then
  echo "File ${MD} already exists! Skipping this step."
else
  echo "File ${MD} does not exist! Downloading file..."
  curl --tlsv1.2 --output md_v4.1.0.pb https://lilablobssc.blob.core.windows.net/models/camera_traps/megadetector/md_v4.1.0/md_v4.1.0.pb
fi

PATH2PIP="`which pip`"
echo "Path to pip: $PATH2PIP"
PATH2CONDA_SH=`echo $PATH2PIP | sed 's/\(anaconda.\).*/\1/g'`
PATH2CONDA_SH+="/etc/profile.d/conda.sh"

echo "Path to conda.sh: $PATH2CONDA_SH"
# shellcheck source=src/conda.sh
source "$PATH2CONDA_SH"

conda env remove -n ecoassistcondaenv
conda create --name ecoassistcondaenv python=3.7 -y
conda activate ecoassistcondaenv
pip install -r EcoAssist/requirements.txt
conda deactivate