#!/usr/bin/env bash

### Unix commands to execute classify_detections.py script in different conda environment
### Peter van Lunteren, 9 Oct 2023 (latest edit)

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
  echo "This is a Linux computer."
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
ECOASSISTCONDAENV_DET="${CONDA_DIR}/envs/ecoassistcondaenv"
ECOASSISTCONDAENV_CLA="${CONDA_DIR}/envs/ecoassistcondaenv-yolov8"
PIP_DET="${ECOASSISTCONDAENV_DET}/bin/pip"
PIP_CLA="${ECOASSISTCONDAENV_CLA}/bin/pip"
HOMEBREW_DIR="${LOCATION_ECOASSIST_FILES}/homebrew"

# activate yolov8 conda env for classification
source "${CONDA_DIR}/etc/profile.d/conda.sh"
source "${CONDA_DIR}/bin/activate"
export PATH="${CONDA_DIR}/bin":$PATH
conda deactivate
conda activate "${ECOASSISTCONDAENV_CLA}"

# change directory
cd $LOCATION_ECOASSIST_FILES || { echo "Could not change directory to EcoAssist_files. Command could not be run. Did you change the name or folder structure since installing EcoAssist?"; exit 1; }

# run script
CLS_MODEL_FILE=$2
CLS_JSON_FILE=$3
CLS_THRESH=$4
CLS_TEMP_FRAME_FOLDER=$5
python "${LOCATION_ECOASSIST_FILES}/EcoAssist/classify_detections.py" "${CLS_MODEL_FILE}" "${CLS_JSON_FILE}" "${CLS_THRESH}" "${LOCATION_ECOASSIST_FILES}" "${CLS_TEMP_FRAME_FOLDER}"

# switch back to detection ecoassistcondaenv yolov5
conda deactivate
conda activate "${ECOASSISTCONDAENV_DET}"
