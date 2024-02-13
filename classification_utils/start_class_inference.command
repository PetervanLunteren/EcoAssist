#!/usr/bin/env bash

### Unix commands to execute the classification inference in a specific conda env
### Peter van Lunteren, 22 Jan 2024 (latest edit)

# check the OS and set var
if [ "$(uname)" == "Darwin" ]; then
  if [[ $(sysctl -n machdep.cpu.brand_string) =~ "Apple" ]]; then
    PLATFORM="Apple Silicon Mac"
  else
    PLATFORM="Intel Mac"
  fi
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
  PLATFORM="Linux"
fi

# catch arguments
GPU_DISABLED=${1}
MODEL_TYPE=${2}
LOCATION_ECOASSIST_FILES=${3}
MODEL_FPATH=${4}
DET_THRESH=${5}
CLS_THRESH=${6}
SMOOTH_BOOL=${7}
JSON_FPATH=${8}
FRAME_DIR=${9}

# set variables
INF_SCRIPT="${LOCATION_ECOASSIST_FILES}/EcoAssist/classification_utils/model_types/${MODEL_TYPE}/classify_detections.py"
CONDA_DIR="${LOCATION_ECOASSIST_FILES}/miniforge"
BASE_ENV="${CONDA_DIR}/envs/ecoassistcondaenv-base"
CLS_ENV="${CONDA_DIR}/envs/ecoassistcondaenv-${MODEL_TYPE}"

# add ecoassist folder to path
export PATH="$LOCATION_ECOASSIST_FILES:$PATH"

# activate conda env for classification
source "${CONDA_DIR}/etc/profile.d/conda.sh"
source "${CONDA_DIR}/bin/activate" base
export PATH="${CONDA_DIR}/bin":$PATH
conda deactivate
conda activate "${CLS_ENV}"

# change directory
cd $LOCATION_ECOASSIST_FILES || { echo "Could not change directory to EcoAssist_files. Command could not be run. Did you change the name or folder structure since installing EcoAssist?"; exit 1; }

# run script
if [ "$GPU_DISABLED" == "True" ] && [ "$PLATFORM" == "Linux" ]; then
    CUDA_VISIBLE_DEVICES='' python "${INF_SCRIPT}" "${LOCATION_ECOASSIST_FILES}" "${MODEL_FPATH}" "${DET_THRESH}" "${CLS_THRESH}" "${SMOOTH_BOOL}" "${JSON_FPATH}" "${FRAME_DIR}"
else
    python "${INF_SCRIPT}" "${LOCATION_ECOASSIST_FILES}" "${MODEL_FPATH}" "${DET_THRESH}" "${CLS_THRESH}" "${SMOOTH_BOOL}" "${JSON_FPATH}" "${FRAME_DIR}"
fi

# switch back to base ecoassistcondaenv
conda deactivate
conda activate "${BASE_ENV}"
