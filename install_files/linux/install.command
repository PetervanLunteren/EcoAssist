#!/usr/bin/env bash

### Linux install commands 
### This install script originally was also meant for macOS, so there is a lot of redundant code in here
### The macOS install was transferred to a UI install with GitHub actions, but the linux install was too big for the GitHub runners
### So for now we just leave the install method for linux with this script as only about 1% of the EcoAssist users are Linux
### 
### Peter van Lunteren, 15 Jan 2025 (latest edit)

# check the OS and set var
if [ "$(uname)" == "Darwin" ]; then
  echo "This is an OSX computer..."
  if [[ $(sysctl -n machdep.cpu.brand_string) =~ "Apple" ]]; then
    echo "   ...with an Apple Silicon processor..."
    PLATFORM="Apple Silicon Mac"
  else
    echo "   ...with an Intel processor."
    PLATFORM="Intel Mac"
  fi
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
  echo "This is an Linux computer."
  PLATFORM="Linux"
fi

# timestamp the start of installation
START_DATE=`date`

# set location var
if [ "$PLATFORM" = "Apple Silicon Mac" ] || [ "$PLATFORM" = "Intel Mac" ]; then
  LOCATION_ECOASSIST_FILES="/Applications/.EcoAssist_files"
elif [ "$PLATFORM" = "Linux" ]; then
  LOCATION_ECOASSIST_FILES="$HOME/.EcoAssist_files"
fi

# set variables
CONDA_DIR="${LOCATION_ECOASSIST_FILES}/miniforge"
ECOASSISTCONDAENV_BASE="${CONDA_DIR}/envs/ecoassistcondaenv-base"
ECOASSISTCONDAENV_PYTORCH="${CONDA_DIR}/envs/ecoassistcondaenv-pytorch"
ECOASSISTCONDAENV_TENSORFLOW="${CONDA_DIR}/envs/ecoassistcondaenv-tensorflow"
ECOASSISTCONDAENV_PYWILDLIFE="${CONDA_DIR}/envs/ecoassistcondaenv-pywildlife"
PIP_BASE="${ECOASSISTCONDAENV_BASE}/bin/pip"
PIP_PYTORCH="${ECOASSISTCONDAENV_PYTORCH}/bin/pip"
PIP_TENSORFLOW="${ECOASSISTCONDAENV_TENSORFLOW}/bin/pip"
PIP_PYWILDLIFE="${ECOASSISTCONDAENV_PYWILDLIFE}/bin/pip"

# prevent mac to sleep during process
if [ "$PLATFORM" = "Apple Silicon Mac" ] || [ "$PLATFORM" = "Intel Mac" ]; then
  pmset noidle &
  PMSETPID=$!
fi

# check for sandbox argument and specify branch 
if [ "$1" == "sandbox" ]; then
  GITHUB_BRANCH_NAME="sandbox"
else
  GITHUB_BRANCH_NAME="main"
fi

# delete previous installation of EcoAssist if present so that it can update
rm -rf $LOCATION_ECOASSIST_FILES && echo "Removed dir '${LOCATION_ECOASSIST_FILES}'"

# make dir and change into
mkdir -p $LOCATION_ECOASSIST_FILES
cd $LOCATION_ECOASSIST_FILES || { echo "Could not change directory to ${LOCATION_ECOASSIST_FILES}. Command could not be run. Copy-paste all text in this console window and send it to peter@addaxdatascience.com for further support."; exit 1; }

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

# log the platform
echo "This installation is using platform: $PLATFORM" 2>&1 | tee -a "$LOG_FILE"

# log system information
UNAME_A=`uname -a`
if [ "$PLATFORM" = "Apple Silicon Mac" ] || [ "$PLATFORM" = "Intel Mac" ]; then
  MACHINE_INFO=`system_profiler SPSoftwareDataType SPHardwareDataType SPMemoryDataType SPStorageDataType`
elif [ "$PLATFORM" = "Linux" ]; then
  PATH=$PATH:/usr/sbin
  MACHINE_INFO_1=`lscpu`
  MACHINE_INFO_2=`dmidecode`
  MACHINE_INFO_3=""
  SYSTEM_INFO_DIRECTORY="/sys/devices/virtual/dmi/id/"
  if [ -d "$SYSTEM_INFO_DIRECTORY" ]; then
    echo "$SYSTEM_INFO_DIRECTORY does exist."
    cd $SYSTEM_INFO_DIRECTORY
    for f in *; do
      MACHINE_INFO_3+="
      $f = `cat $f 2>/dev/null || echo "***_Unavailable_***"`"
    done
  fi
  MACHINE_INFO="${MACHINE_INFO_1}
  ${MACHINE_INFO_2}
  ${MACHINE_INFO_3}"
fi
echo "uname -a:"  2>&1 | tee -a "$LOG_FILE"
echo "$UNAME_A"  2>&1 | tee -a "$LOG_FILE"
echo ""  2>&1 | tee -a "$LOG_FILE"
echo "System information:"  2>&1 | tee -a "$LOG_FILE"
echo "$MACHINE_INFO"  2>&1 | tee -a "$LOG_FILE"
echo ""  2>&1 | tee -a "$LOG_FILE"

# install command line tools if needed (thanks BaseZen of StackOverflow)
if [ "$PLATFORM" = "Apple Silicon Mac" ] || [ "$PLATFORM" = "Intel Mac" ]; then
  os=$(sw_vers -productVersion | awk -F. '{print $1 "." $2}')
  xcode_installed=$(xcode-select -p 1>/dev/null;echo $?)
  # removed os version check for command line tools as --history prints following now: "Command Line Tools for Xcode   14.3   01/04/2023, 09:36:08"
  # if softwareupdate --history | grep --silent "Command Line Tools"; then # this is the old condition. There were problems with this one
  if [ "$xcode_installed" = "0" ]; then # new way of checking if command line tools is installed. Hopefully this will work on newer os versions. No possibility to check.
      echo 'Command-line tools already installed.' 2>&1 | tee -a "$LOG_FILE"
  else
      echo 'Installing Command-line tools...' 2>&1 | tee -a "$LOG_FILE"
      in_progress=/tmp/.com.apple.dt.CommandLineTools.installondemand.in-progress
      touch ${in_progress}
      product=$(softwareupdate --list | awk "/\* Command Line.*${os}/ { sub(/^   \* /, \"\"); print }")
      softwareupdate --verbose --install "${product}" || echo 'Installation failed.' 1>&2 && rm ${in_progress} && exit 1
      rm ${in_progress}
      echo 'Installation succeeded.' 2>&1 | tee -a "$LOG_FILE"
  fi
fi

# clone EcoAssist git
cd $LOCATION_ECOASSIST_FILES || { echo "Could not change directory to ${LOCATION_ECOASSIST_FILES}. Command could not be run. Copy-paste all text in this console window and send it to peter@addaxdatascience.com for further support."; exit 1; }
ECO="EcoAssist"
if [ -d "$ECO" ]; then
  echo "Dir ${ECO} already exists! Skipping this step." 2>&1 | tee -a "$LOG_FILE"
else
  echo "Dir ${ECO} does not exist! Clone repo..." 2>&1 | tee -a "$LOG_FILE"
  git clone --progress --depth 1 --branch $GITHUB_BRANCH_NAME https://github.com/PetervanLunteren/EcoAssist.git 2>&1 | tee -a "$LOG_FILE"
  # move the open.cmd two dirs up and give it an icon
  if [ "$PLATFORM" = "Apple Silicon Mac" ] || [ "$PLATFORM" = "Intel Mac" ]; then
    FILE="$LOCATION_ECOASSIST_FILES/EcoAssist/open.command"
    ICON="$LOCATION_ECOASSIST_FILES/EcoAssist/imgs/logo_small_bg.icns"
    bash $LOCATION_ECOASSIST_FILES/EcoAssist/fileicon set $FILE $ICON 2>&1 | tee -a "$LOG_FILE" # set icon
    chmod 755 $FILE # change permissions
    mv -f $FILE "/Applications/EcoAssist.command" # move file and replace
  elif [ "$PLATFORM" = "Linux" ]; then
    # create shortcut file
    FILE="$LOCATION_ECOASSIST_FILES/EcoAssist/Linux_open_EcoAssist_shortcut.desktop"
    echo "[Desktop Entry]" > $FILE
    echo "Type=Application" >> $FILE
    echo "Terminal=true" >> $FILE
    echo "Name=EcoAssist" >> $FILE
    echo "Icon=logo_small_bg" >> $FILE
    echo "Exec=gnome-terminal -e \"bash -c 'bash \$HOME/.EcoAssist_files/EcoAssist/open.command;\$SHELL'\"" >> $FILE
    echo "Categories=Application;" >> $FILE
    # and give it an icon
    SOURCE="$LOCATION_ECOASSIST_FILES/EcoAssist/imgs/logo_small_bg.png"
    DEST="$HOME/.icons/logo_small_bg.png"
    mkdir -p "$HOME/.icons" # create location if not already present
    cp $SOURCE $DEST # copy icon to proper location
    FILE="$LOCATION_ECOASSIST_FILES/EcoAssist/Linux_open_EcoAssist_shortcut.desktop"
    mv -f $FILE "$HOME/Desktop/Linux_open_EcoAssist_shortcut.desktop" # move file and replace
  fi
fi

# clone cameratraps git 
CAM="cameratraps"
if [ -d "$CAM" ]; then
  echo "Dir ${CAM} already exists! Skipping this step." 2>&1 | tee -a "$LOG_FILE"
else
  echo "Dir ${CAM} does not exist! Clone repo..." 2>&1 | tee -a "$LOG_FILE"
  git clone --progress https://github.com/agentmorris/MegaDetector.git cameratraps || {
    
      # if this git repo fails to clone, chances are the conda environments will give problems too
      # so better already set the conda settings to accomodate slow internet speeds
      export CONDA_REMOTE_READ_TIMEOUT_SECS=120
      export CONDA_REMOTE_CONNECTIONS=1
      export CONDA_REMOTE_MAX_RETRIES=20

      # some users experience timeout issues due to the large size of this repository
      # if it fails here, we'll try again with a larger timeout value and less checks during cloning
      echo "First attempt failed. Retrying with extended timeout..."
      GIT_HTTP_POSTBUFFER=524288000 git clone --progress \
          --config transfer.fsckObjects=false \
          --config receive.fsckObjects=false \
          --config fetch.fsckObjects=false \
          https://github.com/agentmorris/MegaDetector.git cameratraps
  }

  cd $LOCATION_ECOASSIST_FILES/cameratraps || { echo "Could not change directory. Command could not be run. Copy-paste all text in this console window and send it to peter@addaxdatascience.com for further support." 2>&1 | tee -a "$LOG_FILE"; exit 1; }
  git checkout e8a4fc19a2b9ad1892dd9ce65d437252df271576 2>&1 | tee -a "$LOG_FILE"
  cd $LOCATION_ECOASSIST_FILES || { echo "Could not change directory. Command could not be run. Copy-paste all text in this console window and send it to peter@addaxdatascience.com for further support." 2>&1 | tee -a "$LOG_FILE"; exit 1; }
fi

# clone yolov5 git 
YOL="yolov5"
if [ -d "$YOL" ]; then
  echo "Dir ${YOL} already exists! Skipping this step." 2>&1 | tee -a "$LOG_FILE"
else
  echo "Dir ${YOL} does not exist! Clone repo..." 2>&1 | tee -a "$LOG_FILE"
  git clone --progress https://github.com/ultralytics/yolov5.git 2>&1 | tee -a "$LOG_FILE"
  # checkout will happen dynamically during runtime with switch_yolov5_git_to()
  cd $LOCATION_ECOASSIST_FILES || { echo "Could not change directory. Command could not be run. Copy-paste all text in this console window and send it to peter@addaxdatascience.com for further support." 2>&1 | tee -a "$LOG_FILE"; exit 1; }
fi

# clone Human-in-the-loop git 
HIT="Human-in-the-loop"
if [ -d "$HIT" ]; then
  echo "Dir ${HIT} already exists! Skipping this step." 2>&1 | tee -a "$LOG_FILE"
else
  echo "Dir ${HIT} does not exist! Clone repo..." 2>&1 | tee -a "$LOG_FILE"
  # for mac and linux we use the pyside6 branch which doesn't need PyQt5
  git clone --branch pyside6 --progress --depth 1 https://github.com/PetervanLunteren/Human-in-the-loop.git 2>&1 | tee -a "$LOG_FILE"
  cd $LOCATION_ECOASSIST_FILES || { echo "Could not change directory. Command could not be run. Copy-paste all text in this console window and send it to peter@addaxdatascience.com for further support." 2>&1 | tee -a "$LOG_FILE"; exit 1; }
fi

# clone visualise_detection git 
VIS="visualise_detection"
if [ -d "$VIS" ]; then
  echo "Dir ${VIS} already exists! Skipping this step." 2>&1 | tee -a "$LOG_FILE"
else
  echo "Dir ${VIS} does not exist! Clone repo..." 2>&1 | tee -a "$LOG_FILE"
  git clone --progress --depth 1 https://github.com/PetervanLunteren/visualise_detection.git 2>&1 | tee -a "$LOG_FILE"
  cd $LOCATION_ECOASSIST_FILES || { echo "Could not change directory. Command could not be run. Copy-paste all text in this console window and send it to peter@addaxdatascience.com for further support." 2>&1 | tee -a "$LOG_FILE"; exit 1; }
fi

# check if curl is installed
if command -v curl &> /dev/null
then
    echo "curl is already installed."
else
    echo "curl is not installed. Trying to installing curl..."
  { 
    sudo apt update
    sudo apt install -y curl
  } || { 
    echo "Curl could not be installed. Copy-paste all text in this console window and send it to peter@addaxdatascience.com for further support." 2>&1 | tee -a "$LOG_FILE"; exit 1;
    }
  echo "curl successfuly installed."
fi

# download the MDv5a model 
mkdir -p "${LOCATION_ECOASSIST_FILES}/models/det/MegaDetector 5a"
cd "${LOCATION_ECOASSIST_FILES}/models/det/MegaDetector 5a" || { echo "Could not change directory to pretrained_models. Command could not be run. Copy-paste all text in this console window and send it to peter@addaxdatascience.com for further support." 2>&1 | tee -a "$LOG_FILE"; exit 1; }
MDv5a="md_v5a.0.0.pt"
if [ -f "$MDv5a" ]; then
  echo "File ${MDv5a} already exists! Skipping this step." 2>&1 | tee -a "$LOG_FILE"
else
  echo "File ${MDv5a} does not exist! Downloading file..." 2>&1 | tee -a "$LOG_FILE"
  curl --keepalive -OL https://github.com/agentmorris/MegaDetector/releases/download/v5.0/md_v5a.0.0.pt 2>&1 | tee -a "$LOG_FILE"
fi
cd $LOCATION_ECOASSIST_FILES || { echo "Could not change directory to ${LOCATION_ECOASSIST_FILES}. Command could not be run. Copy-paste all text in this console window and send it to peter@addaxdatascience.com for further support." 2>&1 | tee -a "$LOG_FILE"; exit 1; }

# create a dir for the classification models, if not already present
mkdir -p "${LOCATION_ECOASSIST_FILES}/models/cls"

# create txt file to let EcoAssist know it will be the first startup since install
echo "Hello world!" >> "${LOCATION_ECOASSIST_FILES}/first-startup.txt"

# install miniforge
MFG="miniforge"
if [ -d "$MFG" ]; then
  echo "Dir ${MFG} already exists! Skipping this step." 2>&1 | tee -a "$LOG_FILE"
else
  curl --keepalive -L -o Miniforge3.sh "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
  bash Miniforge3.sh -b -p "${LOCATION_ECOASSIST_FILES}/miniforge"
  rm Miniforge3.sh
fi

# source conda executable
source "${CONDA_DIR}/etc/profile.d/conda.sh"
source "${CONDA_DIR}/bin/activate"
export PATH="${CONDA_DIR}/bin":$PATH

# suppress conda warnings about updates
conda config --set notify_outdated_conda false

# install mamba
conda install mamba -n base -c conda-forge -y

# create conda env
if [ "$PLATFORM" = "Linux" ]; then
  # requirements for MegaDetector 
  mamba env create --name ecoassistcondaenv-base --file=$LOCATION_ECOASSIST_FILES/cameratraps/envs/environment-detector.yml -y
  conda activate $ECOASSISTCONDAENV_BASE
  # upgrade pip
  $PIP_BASE install --upgrade pip

  # requirements for Human-in-the-loop
  echo "We need to install libxcb-cursor-dev (https://packages.debian.org/sid/libxcb-cursor-dev) and libxcb-cursor0 (https://packages.debian.org/sid/libxcb-cursor0). If you don't have root privileges you might be prompted for a password. Press CONTROL+D to skip authentication and not install these packages. EcoAssist will still work fine without it but you might have problems with the Human-in-the-loop software."
  { # first try without sudo
    add-apt-repository universe
    apt-get update
    apt-get install libxcb-cursor-dev
    apt-get install libxcb-cursor0
  } || { # otherwise with sudo
    sudo add-apt-repository universe
    sudo apt-get update
    sudo apt-get install libxcb-cursor-dev
    sudo apt-get install libxcb-cursor0
    }

elif [ "$PLATFORM" = "Intel Mac" ]; then
  # requirements for MegaDetector 
  mamba env create --name ecoassistcondaenv-base --file=$LOCATION_ECOASSIST_FILES/cameratraps/envs/environment-detector-mac.yml -y
  conda activate $ECOASSISTCONDAENV_BASE
  # upgrade pip
  $PIP_BASE install --upgrade pip

elif [ "$PLATFORM" = "Apple Silicon Mac" ]; then
  # requirements for MegaDetector via miniforge
  mamba env create --name ecoassistcondaenv-base --file=$LOCATION_ECOASSIST_FILES/cameratraps/envs/environment-detector-m1.yml -y
  conda activate $ECOASSISTCONDAENV_BASE
  # upgrade pip
  $PIP_BASE install --upgrade pip
  { # install nightly pytorch via miniforge as arm64
    $PIP_BASE install torch==1.13.1 torchvision==0.14.1 torchaudio==0.13.1
  } || { # if the first try didn't work
    mamba install pytorch==1.13.1 torchvision==0.14.1 torchaudio==0.13.1 -c pytorch -y
  }
  # for some reason conda-installed opencv decided it doesn't work on silicon macs anymore
  mamba uninstall opencv -y
  pip install opencv-python
fi

# requirements for EcoAssist
$PIP_BASE install RangeSlider
$PIP_BASE install gpsphoto
$PIP_BASE install exifread
$PIP_BASE install piexif
$PIP_BASE install openpyxl
$PIP_BASE install customtkinter
$PIP_BASE install CTkTable
$PIP_BASE install folium
$PIP_BASE install plotly

# requirements for yolov5
$PIP_BASE install "gitpython>=3.1.30"
$PIP_BASE install "tensorboard>=2.4.1"
$PIP_BASE install "thop>=0.1.1"
$PIP_BASE install "protobuf<=3.20.1"
$PIP_BASE install "setuptools>=65.5.1"

# requirements for human-in-the-loop
cd $LOCATION_ECOASSIST_FILES/Human-in-the-loop || { echo "Could not change directory. Command could not be run. Copy-paste all text in this console window and send it to peter@addaxdatascience.com for further support." 2>&1 | tee -a "$LOG_FILE"; exit 1; }
$PIP_BASE install PySide6
if [ "$PLATFORM" = "Apple Silicon Mac" ]; then
  mamba install lxml -y
  make pyside6
elif [ "$PLATFORM" = "Intel Mac" ]; then
  $PIP_BASE install "lxml==4.9.0"
  make pyside6
elif [ "$PLATFORM" = "Linux" ]; then
  $PIP_BASE install "lxml==4.6.3"
  pyside6-rcc -o libs/resources.py resources.qrc
fi
cd $LOCATION_ECOASSIST_FILES || { echo "Could not change directory. Command could not be run. Copy-paste all text in this console window and send it to peter@addaxdatascience.com for further support." 2>&1 | tee -a "$LOG_FILE"; exit 1; }

# log env info
mamba info --envs >> "$LOG_FILE"
mamba list >> "$LOG_FILE"
$PIP_BASE freeze >> "$LOG_FILE"
conda deactivate

# create dedicated tensorflow classification environment 
if [ "$PLATFORM" = "Apple Silicon Mac" ]; then
  mamba env create --file="${LOCATION_ECOASSIST_FILES}/EcoAssist/classification_utils/envs/tensorflow-macos-silicon.yml" -y
elif [ "$PLATFORM" = "Intel Mac" ]; then
  mamba env create --file="${LOCATION_ECOASSIST_FILES}/EcoAssist/classification_utils/envs/tensorflow-macos-intel.yml" -y
elif [ "$PLATFORM" = "Linux" ]; then
  mamba env create --file="${LOCATION_ECOASSIST_FILES}/EcoAssist/classification_utils/envs/tensorflow-linux-windows.yml" -y
fi

# create dedicated pytorch classification environment
if [ "$PLATFORM" = "Intel Mac" ]; then
  mamba env remove -p $ECOASSISTCONDAENV_PYTORCH
  mamba create -p $ECOASSISTCONDAENV_PYTORCH python=3.8 -y
  conda activate $ECOASSISTCONDAENV_PYTORCH
  mamba install pytorch::pytorch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 -c pytorch -y
  $PIP_YOLOV8 install "ultralytics==8.0.191"
  mamba install -c conda-forge numpy==1.24.1 -y
  mamba install -c conda-forge humanfriendly==10.0 -y
  mamba install -c conda-forge jsonpickle==3.0.2 -y
  mamba install -c conda-forge timm
  mamba info --envs >> "$LOG_FILE"
  mamba list >> "$LOG_FILE"
  $PIP_PYTORCH freeze >> "$LOG_FILE" 
  conda deactivate
else
  # apple silicon and linux
  mamba env remove -p $ECOASSISTCONDAENV_PYTORCH
  mamba create -p $ECOASSISTCONDAENV_PYTORCH python=3.8 -y
  conda activate $ECOASSISTCONDAENV_PYTORCH
  $PIP_PYTORCH install torch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2
  $PIP_PYTORCH install "ultralytics==8.0.191"
  $PIP_PYTORCH install "numpy==1.24.1"
  $PIP_PYTORCH install "humanfriendly==10.0"
  $PIP_PYTORCH install "jsonpickle==3.0.2"
  $PIP_PYTORCH install timm
  mamba info --envs >> "$LOG_FILE"
  mamba list >> "$LOG_FILE"
  $PIP_PYTORCH freeze >> "$LOG_FILE" 
  conda deactivate
fi

# create dedicated classification environment for the pytorchwildlife models
mamba env remove -p $ECOASSISTCONDAENV_PYWILDLIFE
mamba create -p $ECOASSISTCONDAENV_PYWILDLIFE python=3.8 -y
conda activate $ECOASSISTCONDAENV_PYWILDLIFE
$PIP_PYWILDLIFE install pytorchwildlife
$PIP_PYWILDLIFE install "setuptools<70"
$PIP_PYWILDLIFE install jsonpickle
conda deactivate

# delete compressed versions of the packages
conda clean --all --yes --force-pkgs-dirs

# log system files with sizes after installation
FILE_SIZES_DEPTH_0=`du -sh $LOCATION_ECOASSIST_FILES`
FILE_SIZES_DEPTH_1=`du -sh $LOCATION_ECOASSIST_FILES/*`
FILE_SIZES_DEPTH_2=`du -sh $LOCATION_ECOASSIST_FILES/*/*`
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

# timestamp the end of installation
END_DATE=`date`
echo "This installation ended at: $END_DATE" 2>&1 | tee -a "$LOG_FILE"

# move LOG_FILE is needed
WRONG_LOG_FILE_LOCATION=$LOCATION_ECOASSIST_FILES/installation_log.txt
if [ "$LOG_FILE" == "$WRONG_LOG_FILE_LOCATION" ]; then
  mv $LOG_FILE $LOCATION_ECOASSIST_FILES/EcoAssist/logfiles
fi

# message for the user
echo ""
echo "THE INSTALLATION IS DONE! You can close this window now and proceed to open EcoAssist by double clicking the EcoAssist.command file in your applications folder (Mac) or on your desktop (Linux)."
echo ""

# the computer may go to sleep again
if [ "$PLATFORM" = "Apple Silicon Mac" ] || [ "$PLATFORM" = "Intel Mac" ]; then
  kill $PMSETPID
fi
