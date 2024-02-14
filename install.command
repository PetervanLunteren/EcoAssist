#!/usr/bin/env bash

### OSx and Linux install commands for the EcoAssist application https://github.com/PetervanLunteren/EcoAssist
### Peter van Lunteren, 12 Feb 2023 (latest edit)

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
  echo "This is an Linux computer."
  PLATFORM="Linux"
fi

# timestamp the start of installation
START_DATE=`date`

# prevent mac to sleep during process
if [ "$PLATFORM" = "Apple Silicon Mac" ] || [ "$PLATFORM" = "Intel Mac" ]; then
  pmset noidle &
  PMSETPID=$!
fi

# set location var
if [ "$PLATFORM" = "Apple Silicon Mac" ] || [ "$PLATFORM" = "Intel Mac" ]; then
  LOCATION_ECOASSIST_FILES="/Applications/.EcoAssist_files"
elif [ "$PLATFORM" = "Linux" ]; then
  LOCATION_ECOASSIST_FILES="$HOME/.EcoAssist_files"
fi

# set variables
CONDA_DIR="${LOCATION_ECOASSIST_FILES}/miniforge"
ECOASSISTCONDAENV_BASE="${CONDA_DIR}/envs/ecoassistcondaenv-base"
ECOASSISTCONDAENV_YOLOV8="${CONDA_DIR}/envs/ecoassistcondaenv-yolov8"
ECOASSISTCONDAENV_MEWC="${CONDA_DIR}/envs/ecoassistcondaenv-mewc"
PIP_BASE="${ECOASSISTCONDAENV_BASE}/bin/pip"
PIP_YOLOV8="${ECOASSISTCONDAENV_YOLOV8}/bin/pip"
PIP_MEWC="${ECOASSISTCONDAENV_MEWC}/bin/pip"
HOMEBREW_DIR="/opt/homebrew"

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
cd $LOCATION_ECOASSIST_FILES || { echo "Could not change directory to ${LOCATION_ECOASSIST_FILES}. Command could not be run. Please send an email to peter@addaxdatascience.com for assistance."; exit 1; }

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
cd $LOCATION_ECOASSIST_FILES || { echo "Could not change directory to ${LOCATION_ECOASSIST_FILES}. Command could not be run. Please send an email to peter@addaxdatascience.com for assistance."; exit 1; }
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
  git clone --progress https://github.com/agentmorris/MegaDetector.git cameratraps 2>&1 | tee -a "$LOG_FILE"
  cd $LOCATION_ECOASSIST_FILES/cameratraps || { echo "Could not change directory. Command could not be run. Please send an email to peter@addaxdatascience.com for assistance." 2>&1 | tee -a "$LOG_FILE"; exit 1; }
  git checkout f72f36f7511a8da7673d52fc3692bd10ec69eb28 2>&1 | tee -a "$LOG_FILE"
  cd $LOCATION_ECOASSIST_FILES || { echo "Could not change directory. Command could not be run. Please send an email to peter@addaxdatascience.com for assistance." 2>&1 | tee -a "$LOG_FILE"; exit 1; }
fi

# clone yolov5 git 
YOL="yolov5"
if [ -d "$YOL" ]; then
  echo "Dir ${YOL} already exists! Skipping this step." 2>&1 | tee -a "$LOG_FILE"
else
  echo "Dir ${YOL} does not exist! Clone repo..." 2>&1 | tee -a "$LOG_FILE"
  git clone --progress https://github.com/ultralytics/yolov5.git 2>&1 | tee -a "$LOG_FILE"
  # checkout will happen dynamically during runtime with switch_yolov5_git_to()
  cd $LOCATION_ECOASSIST_FILES || { echo "Could not change directory. Command could not be run. Please send an email to peter@addaxdatascience.com for assistance." 2>&1 | tee -a "$LOG_FILE"; exit 1; }
fi

# clone Human-in-the-loop git 
HIT="Human-in-the-loop"
if [ -d "$HIT" ]; then
  echo "Dir ${HIT} already exists! Skipping this step." 2>&1 | tee -a "$LOG_FILE"
else
  echo "Dir ${HIT} does not exist! Clone repo..." 2>&1 | tee -a "$LOG_FILE"
  git clone --progress --depth 1 https://github.com/PetervanLunteren/Human-in-the-loop.git 2>&1 | tee -a "$LOG_FILE"
  cd $LOCATION_ECOASSIST_FILES || { echo "Could not change directory. Command could not be run." 2>&1 | tee -a "$LOG_FILE"; exit 1; }
fi

# clone visualise_detection git 
VIS="visualise_detection"
if [ -d "$VIS" ]; then
  echo "Dir ${VIS} already exists! Skipping this step." 2>&1 | tee -a "$LOG_FILE"
else
  echo "Dir ${VIS} does not exist! Clone repo..." 2>&1 | tee -a "$LOG_FILE"
  git clone --progress --depth 1 https://github.com/PetervanLunteren/visualise_detection.git 2>&1 | tee -a "$LOG_FILE"
  cd $LOCATION_ECOASSIST_FILES || { echo "Could not change directory. Command could not be run." 2>&1 | tee -a "$LOG_FILE"; exit 1; }
fi

# download the MDv5a model 
mkdir -p "${LOCATION_ECOASSIST_FILES}/models/det/MegaDetector 5a"
cd "${LOCATION_ECOASSIST_FILES}/models/det/MegaDetector 5a" || { echo "Could not change directory to pretrained_models. Command could not be run. Please send an email to peter@addaxdatascience.com for assistance." 2>&1 | tee -a "$LOG_FILE"; exit 1; }
MDv5a="md_v5a.0.0.pt"
if [ -f "$MDv5a" ]; then
  echo "File ${MDv5a} already exists! Skipping this step." 2>&1 | tee -a "$LOG_FILE"
else
  echo "File ${MDv5a} does not exist! Downloading file..." 2>&1 | tee -a "$LOG_FILE"
  curl --keepalive -OL https://github.com/agentmorris/MegaDetector/releases/download/v5.0/md_v5a.0.0.pt 2>&1 | tee -a "$LOG_FILE"
fi
cd $LOCATION_ECOASSIST_FILES || { echo "Could not change directory to ${LOCATION_ECOASSIST_FILES}. Command could not be run. Please send an email to peter@addaxdatascience.com for assistance." 2>&1 | tee -a "$LOG_FILE"; exit 1; }

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

# create conda env
if [ "$PLATFORM" = "Linux" ]; then
  # requirements for MegaDetector 
  conda env create --name ecoassistcondaenv-base --file=$LOCATION_ECOASSIST_FILES/cameratraps/envs/environment-detector.yml
  # source "${LOCATION_ECOASSIST_FILES}/miniforge/bin/activate"
  conda activate $ECOASSISTCONDAENV_BASE
  # upgrade pip
  $PIP_BASE install --upgrade pip
  # requirements for Human-in-the-loop
  $PIP_BASE install pyqt5==5.15.2 lxml libxcb-xinerama0
  echo "We need to install libxcb-xinerama0 (https://packages.ubuntu.com/bionic/libxcb-xinerama0) and libgl1 (https://www.opengl.org/sdk/libs/). If you don't have root privileges you might be prompted for a password. Press CONTROL+D to skip authentication and not install these packages. EcoAssist will still work fine without it but you might have problems with the Human-in-the-loop software."
  { # first try without sudo
    apt install libxcb-xinerama0 
  } || { # otherwise with sudo
    sudo apt install libxcb-xinerama0 
    }
  { # first try without sudo
    apt install libgl1 
  } || { # otherwise with sudo
    sudo apt install libgl1 
    }
  cd $LOCATION_ECOASSIST_FILES/Human-in-the-loop || { echo "Could not change directory. Exiting installation." 2>&1 | tee -a "$LOG_FILE"; exit 1; }
  pyrcc5 -o libs/resources.py resources.qrc
  python3 -m pip install --pre --upgrade lxml

elif [ "$PLATFORM" = "Intel Mac" ]; then
  # requirements for MegaDetector 
  conda env create --name ecoassistcondaenv-base --file=$LOCATION_ECOASSIST_FILES/cameratraps/envs/environment-detector-mac.yml
  # source "${LOCATION_ECOASSIST_FILES}/miniforge/bin/activate"
  conda activate $ECOASSISTCONDAENV_BASE
  # upgrade pip
  $PIP_BASE install --upgrade pip
  # requirements for Human-in-the-loop
  $PIP_BASE install pyqt5==5.15.2 lxml

elif [ "$PLATFORM" = "Apple Silicon Mac" ]; then
  # requirements for MegaDetector via miniforge
  conda env create --name ecoassistcondaenv-base --file=$LOCATION_ECOASSIST_FILES/cameratraps/envs/environment-detector-m1.yml
  # source "${LOCATION_ECOASSIST_FILES}/miniforge/bin/activate"
  conda activate $ECOASSISTCONDAENV_BASE
  # upgrade pip
  $PIP_BASE install --upgrade pip
  { # install nightly pytorch via miniforge as arm64
    $PIP_BASE install torch==1.13.1 torchvision==0.14.1 torchaudio==0.13.1
  } || { # if the first try didn't work
    conda install pytorch==1.13.1 torchvision==0.14.1 torchaudio==0.13.1 -c pytorch -y
  }
  # install lxml
  $PIP_BASE install lxml

  # we need homebrew to install PyQt5 for Apple Silicon macs
  echo "In order to enable the pyQt5 package for Apple Silicon (required for the the " 2>&1 | tee -a "$LOG_FILE"
  echo "annotation and human-in-the-loop feature), we need to install it via Homebrew." 2>&1 | tee -a "$LOG_FILE"
  BREW="${HOMEBREW_DIR}/bin/brew"
  export PATH="${HOMEBREW_DIR}/bin:$PATH"

  # check if it is already installed
  if test -f $BREW; then
    echo "Homebrew already exists on the default location ($BREW). Skipping install." 2>&1 | tee -a "$LOG_FILE"
  else
    echo "Homebrew does not exist on the default location ($BREW). Proceeding to install." 2>&1 | tee -a "$LOG_FILE"
    echo "The script will check for sudo permissions and might prompt you for a password." 2>&1 | tee -a "$LOG_FILE"
    echo "If you don't know the sudo password, you can skip this by pressing Ctrl+D." 2>&1 | tee -a "$LOG_FILE"
    echo "EcoAssist will still work fine without it, but the annotation and " 2>&1 | tee -a "$LOG_FILE"
    echo "human-in-the-loop feature will not work." 2>&1 | tee -a "$LOG_FILE"
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" 2>&1 | tee -a "$LOG_FILE"
  fi

  # further requirements for Human-in-the-loop
  arch -arm64 $BREW install pyqt@5
  cd $LOCATION_ECOASSIST_FILES/Human-in-the-loop || { echo "Could not change directory. Command could not be run." 2>&1 | tee -a "$LOG_FILE"; exit 1; }
  make qt5py3
  python3 -m pip install --pre --upgrade lxml
fi

# requirements for EcoAssist
$PIP_BASE install RangeSlider
$PIP_BASE install gpsphoto
$PIP_BASE install exifread
$PIP_BASE install piexif
$PIP_BASE install openpyxl
$PIP_BASE install customtkinter
$PIP_BASE install CTkTable

# requirements for yolov5
$PIP_BASE install "gitpython>=3.1.30"
$PIP_BASE install "tensorboard>=2.4.1"
$PIP_BASE install "thop>=0.1.1"
$PIP_BASE install "protobuf<=3.20.1"
$PIP_BASE install "setuptools>=65.5.1"

# log env info
conda info --envs >> "$LOG_FILE"
conda list >> "$LOG_FILE"
$PIP_BASE freeze >> "$LOG_FILE"
conda deactivate

# create dedicated yolov8 classification environment # DEBUG
if [ "$PLATFORM" = "Intel Mac" ]; then
  conda env remove -p $ECOASSISTCONDAENV_YOLOV8
  conda create -p $ECOASSISTCONDAENV_YOLOV8 python=3.8 -y
  conda activate $ECOASSISTCONDAENV_YOLOV8
  # $PIP_YOLOV8 install torch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2
  conda install pytorch::pytorch torchvision torchaudio -c pytorch
  # conda install -c pytorch  -c conda-forge pytorch torchvision pytorch=11.8 ultralytics
  conda install -c conda-forge ultralytics
  conda install -c conda-forge numpy
  conda install -c conda-forge humanfriendly
  conda install -c conda-forge jsonpickle
  # conda install -c conda-forge opencv
  # $PIP_YOLOV8 install "ultralytics==8.0.191"
  # $PIP_YOLOV8 install "numpy==1.24.1"
  # $PIP_YOLOV8 install "humanfriendly==10.0"
  # $PIP_YOLOV8 install "jsonpickle==3.0.2"
  conda info --envs >> "$LOG_FILE"
  conda list >> "$LOG_FILE"
  $PIP_YOLOV8 freeze >> "$LOG_FILE" 
  conda deactivate
else
  # apple silicon and linux
  conda env remove -p $ECOASSISTCONDAENV_YOLOV8
  conda create -p $ECOASSISTCONDAENV_YOLOV8 python=3.8 -y
  conda activate $ECOASSISTCONDAENV_YOLOV8
  $PIP_YOLOV8 install torch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2
  $PIP_YOLOV8 install "ultralytics==8.0.191"
  $PIP_YOLOV8 install "numpy==1.24.1"
  $PIP_YOLOV8 install "humanfriendly==10.0"
  $PIP_YOLOV8 install "jsonpickle==3.0.2"
  conda info --envs >> "$LOG_FILE"
  conda list >> "$LOG_FILE"
  $PIP_YOLOV8 freeze >> "$LOG_FILE" 
  conda deactivate
fi

# create dedicated mewc classification environment # DEBUG
elif [ "$PLATFORM" = "Apple Silicon Mac" ]; then
  conda env create --file="${LOCATION_ECOASSIST_FILES}/EcoAssist/classification_utils/envs/mewc-macos.yml"
  conda activate $ECOASSISTCONDAENV_MEWC
  conda info --envs >> "$LOG_FILE"
  conda list >> "$LOG_FILE"
  $PIP_MEWC freeze >> "$LOG_FILE" 
  conda deactivate
else
  # intel macs and linux
  conda env create --file="${LOCATION_ECOASSIST_FILES}/EcoAssist/classification_utils/envs/mewc-windows.yml"
  conda activate $ECOASSISTCONDAENV_MEWC
  conda info --envs >> "$LOG_FILE"
  conda list >> "$LOG_FILE"
  $PIP_MEWC freeze >> "$LOG_FILE" 
  conda deactivate
fi

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
