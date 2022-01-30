#!/usr/bin/env bash

pmset noidle &
PMSETPID=$!

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
  cd cameratraps || { echo "Could not change directory. Command could not be run. Please install EcoAssist manually: https://github.com/PetervanLunteren/EcoAssist"; exit 1; }
  git checkout e40755ec6f3b34e6eefa1306d5cd6ce605e0f5ab
  cd .. || { echo "Could not change directory. Command could not be run. Please install EcoAssist manually: https://github.com/PetervanLunteren/EcoAssist"; exit 1; }
fi

AI4="ai4eutils"
if [ -d "$AI4" ]; then
  echo "Dir ${AI4} already exists! Skipping this step."
else
  echo "Dir ${AI4} does not exist! Clone repo..."
  git clone https://github.com/Microsoft/ai4eutils
  cd ai4eutils || { echo "Could not change directory. Command could not be run. Please install EcoAssist manually: https://github.com/PetervanLunteren/EcoAssist"; exit 1; }
  git checkout c8692a2ed426a189ef3c1b3a5a21ae287c032a1d
  cd .. || { echo "Could not change directory. Command could not be run. Please install EcoAssist manually: https://github.com/PetervanLunteren/EcoAssist"; exit 1; }
fi

MD="md_v4.1.0.pb"
if [ -f "$MD" ]; then
  echo "File ${MD} already exists! Skipping this step."
else
  echo "File ${MD} does not exist! Downloading file..."
  curl --tlsv1.2 --keepalive --output md_v4.1.0.pb https://lilablobssc.blob.core.windows.net/models/camera_traps/megadetector/md_v4.1.0/md_v4.1.0.pb
fi

cd EcoAssist || { echo "Could not change directory. Command could not be run. Please install EcoAssist manually: https://github.com/PetervanLunteren/EcoAssist"; exit 1; }
conda env remove -n ecoassistcondaenv
conda env create -f ecoassistcondaenv.yml

kill $PMSETPID