#!/usr/bin/env bash

### OSX install commands for the EcoAssist application https://github.com/PetervanLunteren/EcoAssist
### Peter van Lunteren, 25 August 2022

# timestamp the start of installation
START_DATE=`date`

# prevent mac to sleep during process
pmset noidle &
PMSETPID=$!

# set var for ecoassist root
LOCATION_ECOASSIST_FILES="/Applications/EcoAssist_files"

# make dir and change into
mkdir -p $LOCATION_ECOASSIST_FILES
cd $LOCATION_ECOASSIST_FILES || { echo "Could not change directory to ${LOCATION_ECOASSIST_FILES}. Command could not be run. Please install EcoAssist manually: https://github.com/PetervanLunteren/EcoAssist"; exit 1; }

# check if log file already exists, otherwise create empty log file
LOG_FILE=$LOCATION_ECOASSIST_FILES/EcoAssist/logfiles/installation_log.txt
if [ -f "$LOG_FILE" ]; then
    echo "LOG_FILE exists. Logging to ${LOCATION_ECOASSIST_FILES}/EcoAssist/logfiles/installation_log.txt" 2>&1 | tee -a "$LOG_FILE"
else
    LOG_FILE=$LOCATION_ECOASSIST_FILES/installation_log.txt
    touch "$LOG_FILE"
    echo "LOG_FILE does not exist. Logging to ${LOCATION_ECOASSIST_FILES}/installation_log.txt" 2>&1 | tee -a "$LOG_FILE"
fi

# log the start
echo "This installation started at: $START_DATE" 2>&1 | tee -a "$LOG_FILE"

# log system information
UNAME_A=`uname -a`
MACHINE_INFO=`system_profiler SPSoftwareDataType SPHardwareDataType SPMemoryDataType SPStorageDataType`
FILE_SIZES_DEPTH_0=`du -sh $LOCATION_ECOASSIST_FILES`
FILE_SIZES_DEPTH_1=`du -sh $LOCATION_ECOASSIST_FILES/*`
FILE_SIZES_DEPTH_2=`du -sh $LOCATION_ECOASSIST_FILES/*/*`
echo "uname -a:"  2>&1 | tee -a "$LOG_FILE"
echo ""  2>&1 | tee -a "$LOG_FILE"
echo "$UNAME_A"  2>&1 | tee -a "$LOG_FILE"
echo ""  2>&1 | tee -a "$LOG_FILE"
echo "System information:"  2>&1 | tee -a "$LOG_FILE"
echo ""  2>&1 | tee -a "$LOG_FILE"
echo "$MACHINE_INFO"  2>&1 | tee -a "$LOG_FILE"
echo ""  2>&1 | tee -a "$LOG_FILE"
echo "File sizes with depth 0:"  2>&1 | tee -a "$LOG_FILE"
echo ""  2>&1 | tee -a "$LOG_FILE"
echo "$FILE_SIZES_DEPTH_0"  2>&1 | tee -a "$LOG_FILE"
echo ""  2>&1 | tee -a "$LOG_FILE"
echo "File sizes with depth 1:"  2>&1 | tee -a "$LOG_FILE"
echo ""  2>&1 | tee -a "$LOG_FILE"
echo "$FILE_SIZES_DEPTH_1"  2>&1 | tee -a "$LOG_FILE"
echo ""  2>&1 | tee -a "$LOG_FILE"
echo "File sizes with depth 2:"  2>&1 | tee -a "$LOG_FILE"
echo ""  2>&1 | tee -a "$LOG_FILE"
echo "$FILE_SIZES_DEPTH_2"  2>&1 | tee -a "$LOG_FILE"
echo ""  2>&1 | tee -a "$LOG_FILE"

# clone git if not present
ECO="EcoAssist"
if [ -d "$ECO" ]; then
  echo "Dir ${ECO} already exists! Skipping this step." 2>&1 | tee -a "$LOG_FILE"
else
  echo "Dir ${ECO} does not exist! Clone repo..." 2>&1 | tee -a "$LOG_FILE"
  git clone --progress https://github.com/PetervanLunteren/EcoAssist.git 2>&1 | tee -a "$LOG_FILE"
fi

# clone git if not present
CAM="cameratraps"
if [ -d "$CAM" ]; then
  echo "Dir ${CAM} already exists! Skipping this step." 2>&1 | tee -a "$LOG_FILE"
else
  echo "Dir ${CAM} does not exist! Clone repo..." 2>&1 | tee -a "$LOG_FILE"
  git clone --progress https://github.com/Microsoft/cameratraps 2>&1 | tee -a "$LOG_FILE"
  cd cameratraps || { echo "Could not change directory. Command could not be run. Please install EcoAssist manually: https://github.com/PetervanLunteren/EcoAssist" 2>&1 | tee -a "$LOG_FILE"; exit 1; }
  git checkout f8417740c1624d38988210a2dd5de58b64ae7827 2>&1 | tee -a "$LOG_FILE"
  cd .. || { echo "Could not change directory. Command could not be run. Please install EcoAssist manually: https://github.com/PetervanLunteren/EcoAssist" 2>&1 | tee -a "$LOG_FILE"; exit 1; }
fi

# clone git if not present
AI4="ai4eutils"
if [ -d "$AI4" ]; then
  echo "Dir ${AI4} already exists! Skipping this step." 2>&1 | tee -a "$LOG_FILE"
else
  echo "Dir ${AI4} does not exist! Clone repo..." 2>&1 | tee -a "$LOG_FILE"
  git clone --progress https://github.com/Microsoft/ai4eutils 2>&1 | tee -a "$LOG_FILE"
  cd ai4eutils || { echo "Could not change directory. Command could not be run. Please install EcoAssist manually: https://github.com/PetervanLunteren/EcoAssist" 2>&1 | tee -a "$LOG_FILE"; exit 1; }
  git checkout 1bbbb8030d5be3d6488ac898f9842d715cdca088 2>&1 | tee -a "$LOG_FILE"
  cd .. || { echo "Could not change directory. Command could not be run. Please install EcoAssist manually: https://github.com/PetervanLunteren/EcoAssist" 2>&1 | tee -a "$LOG_FILE"; exit 1; }
fi

# clone git if not present
YOL="yolov5"
if [ -d "$YOL" ]; then
  echo "Dir ${YOL} already exists! Skipping this step." 2>&1 | tee -a "$LOG_FILE"
else
  echo "Dir ${YOL} does not exist! Clone repo..." 2>&1 | tee -a "$LOG_FILE"
  git clone --progress https://github.com/ultralytics/yolov5/ 2>&1 | tee -a "$LOG_FILE"
  cd yolov5 || { echo "Could not change directory. Command could not be run. Please install EcoAssist manually: https://github.com/PetervanLunteren/EcoAssist" 2>&1 | tee -a "$LOG_FILE"; exit 1; }
  git checkout c23a441c9df7ca9b1f275e8c8719c949269160d1 2>&1 | tee -a "$LOG_FILE"
  cd .. || { echo "Could not change directory. Command could not be run. Please install EcoAssist manually: https://github.com/PetervanLunteren/EcoAssist" 2>&1 | tee -a "$LOG_FILE"; exit 1; }
fi

# clone git if not present
LBL="labelImg"
if [ -d "$LBL" ]; then
  echo "Dir ${LBL} already exists! Skipping this step." 2>&1 | tee -a "$LOG_FILE"
else
  echo "Dir ${LBL} does not exist! Clone repo..." 2>&1 | tee -a "$LOG_FILE"
  git clone --progress https://github.com/tzutalin/labelImg.git 2>&1 | tee -a "$LOG_FILE"
  cd labelImg || { echo "Could not change directory. Command could not be run. Please install labelImg manually: https://github.com/tzutalin/labelImg" 2>&1 | tee -a "$LOG_FILE"; exit 1; }
  git checkout 276f40f5e5bbf11e84cfa7844e0a6824caf93e11 2>&1 | tee -a "$LOG_FILE"
  cd .. || { echo "Could not change directory. Command could not be run. Please install labelImg manually: https://github.com/tzutalin/labelImg" 2>&1 | tee -a "$LOG_FILE"; exit 1; }
fi

# download model if not present
mkdir -p $LOCATION_ECOASSIST_FILES/megadetector
cd $LOCATION_ECOASSIST_FILES/megadetector || { echo "Could not change directory to megadetector. Command could not be run. Please install EcoAssist manually: https://github.com/PetervanLunteren/EcoAssist" 2>&1 | tee -a "$LOG_FILE"; exit 1; }
MD="md_v5a.0.0.pt"
if [ -f "$MD" ]; then
  echo "File ${MD} already exists! Skipping this step." 2>&1 | tee -a "$LOG_FILE"
else
  echo "File ${MD} does not exist! Downloading file..." 2>&1 | tee -a "$LOG_FILE"
  wget https://github.com/microsoft/CameraTraps/releases/download/v5.0/md_v5a.0.0.pt 2>&1 | tee -a "$LOG_FILE"
fi
cd .. || { echo "Could not change directory. Command could not be run. Please install EcoAssist manually: https://github.com/PetervanLunteren/EcoAssist" 2>&1 | tee -a "$LOG_FILE"; exit 1; }

# check if conda is already installed, if not install
CONDA_LIST=`conda list`
echo "'conda list' yields: $CONDA_LIST" 2>&1 | tee -a "$LOG_FILE"
if [ "$CONDA_LIST" == "" ]; then
  echo "Anaconda not yet installed. Installing now..." 2>&1 | tee -a "$LOG_FILE"
  cd $LOCATION_ECOASSIST_FILES || { echo "Could not change directory to ${LOCATION_ECOASSIST_FILES}. Command could not be run. Please install EcoAssist manually: https://github.com/PetervanLunteren/EcoAssist" 2>&1 | tee -a "$LOG_FILE"; exit 1; }
  # download install sh
  wget https://repo.anaconda.com/archive/Anaconda3-2021.11-MacOSX-x86_64.sh 2>&1 | tee -a "$LOG_FILE"
  # execute it
  echo "The installation is NOT yet done. Please be patient. The following command just loads without much verbose output..."  2>&1 | tee -a "$LOG_FILE"
  echo ""  2>&1 | tee -a "$LOG_FILE"
  sh Anaconda3-2021.11-MacOSX-x86_64.sh -b 2>&1 | tee -a "$LOG_FILE"
  echo "After this installation 'conda list' yields: `conda list`" 2>&1 | tee -a "$LOG_FILE"
  # remove it after installation
  INSTALL_SH="Anaconda3-2021.11-MacOSX-x86_64.sh"
  if [ -f "$INSTALL_SH" ]; then
    echo "File ${INSTALL_SH} is still there! Deleting now." 2>&1 | tee -a "$LOG_FILE"
    rm $INSTALL_SH
  else
    echo "File ${INSTALL_SH} does not exist! Nothing to delete..." 2>&1 | tee -a "$LOG_FILE"
  fi
  cd .. || { echo "Could not change directory. Command could not be run. Please install EcoAssist manually: https://github.com/PetervanLunteren/EcoAssist" 2>&1 | tee -a "$LOG_FILE"; exit 1; }
else
  echo "Anaconda is already installed, skipping this step." 2>&1 | tee -a "$LOG_FILE"
fi

# locate conda.sh on local machine and source it
PATH2CONDA_SH=`conda info | grep 'base environment' | cut -d ':' -f 2 | xargs | cut -d ' ' -f 1`
PATH2CONDA_SH+="/etc/profile.d/conda.sh"
echo "Path to conda.sh: $PATH2CONDA_SH" 2>&1 | tee -a "$LOG_FILE"
# shellcheck source=src/conda.sh
source "$PATH2CONDA_SH"

# get os type
function fetch_os_type() {
  echo "Checking OS type and version..." 2>&1 | tee -a "$LOG_FILE"
  OSver="unknown"  # default value
  uname_output="$(uname -a)"
  echo "$uname_output" 2>&1 | tee -a "$LOG_FILE"
  # macOS
  if echo "$uname_output" | grep -i darwin >/dev/null 2>&1; then
    # Fetch macOS version
    sw_vers_output="$(sw_vers | grep -e ProductVersion)"
    echo "$sw_vers_output" 2>&1 | tee -a "$LOG_FILE"
    OSver="$(echo "$sw_vers_output" | cut -c 17-)"
    macOSmajor="$(echo "$OSver" | cut -f 1 -d '.')"
    macOSminor="$(echo "$OSver" | cut -f 2 -d '.')"
    # Make sure OSver is supported
    if [[ "${macOSmajor}" = 10 ]] && [[ "${macOSminor}" < "${MACOSSUPPORTED}" ]]; then
      die "Sorry, this version of macOS (10.$macOSminor) is not supported. The minimum version is 10.$MACOSSUPPORTED." 2>&1 | tee -a "$LOG_FILE"
    fi
    # Fix for non-English Unicode systems on MAC
    if [[ -z "${LC_ALL:-}" ]]; then
      export LC_ALL=en_US.UTF-8
    fi

    if [[ -z "${LANG:-}" ]]; then
      export LANG=en_US.UTF-8
    fi
    OS="osx"
  # Linux
  elif echo "$uname_output" | grep -i linux >/dev/null 2>&1; then
    OS="linux"
  else
    die "Sorry, the installer only supports Linux and macOS, quitting installer" 2>&1 | tee -a "$LOG_FILE"
  fi
}
fetch_os_type

# create conda env
conda env remove -n ecoassistcondaenv
conda create -n ecoassistcondaenv python==3.7 -y
conda activate ecoassistcondaenv
pip install --upgrade pip setuptools wheel
pip install --upgrade pip
conda install -c conda-forge requests=2.26.0 -y
pip install -r $LOCATION_ECOASSIST_FILES/EcoAssist/requirements.txt

# additional packages required for MegaDetector v5
pip install Pillow==9.1.0 
pip install pandas==1.1.5
pip install seaborn==0.11.2
pip install PyYAML==5.3.1
conda install -c conda-forge pytorch==1.10.1 -y
conda install -c conda-forge torchvision==0.11.2 -y

# log env info
conda info --envs >> "$LOG_FILE"
conda list >> "$LOG_FILE"
pip freeze >> "$LOG_FILE"

# check if CPU supports AVX instruction set and install precompiled TensorFlow if it isn't
case $OS in
linux*)
  if ! lscpu | grep -q " avx "; then
    echo "AVX is not supported by this CPU! Installing a version of TensorFlow compiled for older CPUs..." 2>&1 | tee -a "$LOG_FILE"
    pip uninstall tensorflow -y
    pip install https://github.com/spinalcordtoolbox/docker-tensorflow-builder/releases/download/v1.15.5-py3.7/tensorflow-1.15.5-cp37-cp37m-linux_x86_64.whl
  else
    echo "AVX is supported on this Linux machine. Keeping default TensorFlow..." 2>&1 | tee -a "$LOG_FILE"
  fi
  ;;
osx)
  if sysctl machdep.cpu.brand_string | grep -q "Apple M1"; then
    echo "AVX is not supported on M1 Macs! Installing a version of TensorFlow compiled for M1 Macs..." 2>&1 | tee -a "$LOG_FILE"
    pip uninstall tensorflow -y
    pip install https://github.com/spinalcordtoolbox/docker-tensorflow-builder/releases/download/v1.15.5-py3.7/tensorflow-1.15.0-py3-none-any.whl
    pip freeze
  else
    echo "AVX is supported on this macOS machine. Keeping default TensorFlow..." 2>&1 | tee -a "$LOG_FILE"
  fi
  ;;
esac

# log env info again, after the possible new TensorFlow installation
conda info --envs >> "$LOG_FILE"
conda list >> "$LOG_FILE"
pip freeze >> "$LOG_FILE"

# deactivate conda env
conda deactivate

# log system information again after installation
UNAME_A=`uname -a`
MACHINE_INFO=`system_profiler SPSoftwareDataType SPHardwareDataType SPMemoryDataType SPStorageDataType`
FILE_SIZES_DEPTH_0=`du -sh $LOCATION_ECOASSIST_FILES`
FILE_SIZES_DEPTH_1=`du -sh $LOCATION_ECOASSIST_FILES/*`
echo "uname -a:"  2>&1 | tee -a "$LOG_FILE"
echo ""  2>&1 | tee -a "$LOG_FILE"
echo "$UNAME_A"  2>&1 | tee -a "$LOG_FILE"
echo ""  2>&1 | tee -a "$LOG_FILE"
echo "System information:"  2>&1 | tee -a "$LOG_FILE"
echo ""  2>&1 | tee -a "$LOG_FILE"
echo "$MACHINE_INFO"  2>&1 | tee -a "$LOG_FILE"
echo ""  2>&1 | tee -a "$LOG_FILE"
echo "File sizes with depth 0:"  2>&1 | tee -a "$LOG_FILE"
echo ""  2>&1 | tee -a "$LOG_FILE"
echo "$FILE_SIZES_DEPTH_0"  2>&1 | tee -a "$LOG_FILE"
echo ""  2>&1 | tee -a "$LOG_FILE"
echo "File sizes with depth 1:"  2>&1 | tee -a "$LOG_FILE"
echo ""  2>&1 | tee -a "$LOG_FILE"
echo "$FILE_SIZES_DEPTH_1"  2>&1 | tee -a "$LOG_FILE"
echo ""  2>&1 | tee -a "$LOG_FILE"

# timestamp the end of installation
END_DATE=`date`
echo "This installation ended at: $END_DATE" 2>&1 | tee -a "$LOG_FILE"
echo "" 2>&1 | tee -a "$LOG_FILE"
echo "" 2>&1 | tee -a "$LOG_FILE"
echo "" 2>&1 | tee -a "$LOG_FILE"
echo "" 2>&1 | tee -a "$LOG_FILE"

# move LOG_FILE is needed
WRONG_LOG_FILE_LOCATION=$LOCATION_ECOASSIST_FILES/installation_log.txt
if [ "$LOG_FILE" == "$WRONG_LOG_FILE_LOCATION" ]; then
  mv $LOG_FILE $LOCATION_ECOASSIST_FILES/EcoAssist/logfiles
fi

# message for the user
echo ""
echo "THE INSTALLATION IS DONE! You can close this window now and proceed to open EcoAssist by double clicking the ${LOCATION_ECOASSIST_FILES}/EcoAssist/open_EcoAssist.command file."
echo ""

# the computer may go to sleep again
kill $PMSETPID