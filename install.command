#!/usr/bin/env bash

### OSx and Linux install commands for the EcoAssist application https://github.com/PetervanLunteren/EcoAssist
### Peter van Lunteren, 2 Apr 2023 (latest edit)

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
ECOASSISTCONDAENV="${CONDA_DIR}/envs/ecoassistcondaenv"
PIP="${ECOASSISTCONDAENV}/bin/pip"
HOMEBREW_DIR="${LOCATION_ECOASSIST_FILES}/homebrew"

# delete previous installation of EcoAssist if present so that it can update
rm -rf $LOCATION_ECOASSIST_FILES

# make dir and change into
mkdir -p $LOCATION_ECOASSIST_FILES
cd $LOCATION_ECOASSIST_FILES || { echo "Could not change directory to ${LOCATION_ECOASSIST_FILES}. Command could not be run. Please send an email to petervanlunteren@hotmail.com for assistance."; exit 1; }

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
  if softwareupdate --history | grep --silent "Command Line Tools.*${os}"; then
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
cd $LOCATION_ECOASSIST_FILES || { echo "Could not change directory to ${LOCATION_ECOASSIST_FILES}. Command could not be run. Please send an email to petervanlunteren@hotmail.com for assistance."; exit 1; }
ECO="EcoAssist"
if [ -d "$ECO" ]; then
  echo "Dir ${ECO} already exists! Skipping this step." 2>&1 | tee -a "$LOG_FILE"
else
  echo "Dir ${ECO} does not exist! Clone repo..." 2>&1 | tee -a "$LOG_FILE"
  git clone --progress https://github.com/PetervanLunteren/EcoAssist.git 2>&1 | tee -a "$LOG_FILE"
  # move the open.cmd two dirs up and give it an icon
  if [ "$PLATFORM" = "Apple Silicon Mac" ] || [ "$PLATFORM" = "Intel Mac" ]; then
    FILE="$LOCATION_ECOASSIST_FILES/EcoAssist/open.command"
    ICON="$LOCATION_ECOASSIST_FILES/EcoAssist/imgs/logo_small_bg.icns"
    bash $LOCATION_ECOASSIST_FILES/EcoAssist/fileicon set $FILE $ICON 2>&1 | tee -a "$LOG_FILE" # set icon
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
  git clone --progress https://github.com/Microsoft/cameratraps 2>&1 | tee -a "$LOG_FILE"
  cd $LOCATION_ECOASSIST_FILES/cameratraps || { echo "Could not change directory. Command could not be run. Please send an email to petervanlunteren@hotmail.com for assistance." 2>&1 | tee -a "$LOG_FILE"; exit 1; }
  git checkout 6223b48b520abd6ad7fe868ea16ea58f75003595 2>&1 | tee -a "$LOG_FILE"
  cd $LOCATION_ECOASSIST_FILES || { echo "Could not change directory. Command could not be run. Please send an email to petervanlunteren@hotmail.com for assistance." 2>&1 | tee -a "$LOG_FILE"; exit 1; }
fi

# clone ai4eutils git 
AI4="ai4eutils"
if [ -d "$AI4" ]; then
  echo "Dir ${AI4} already exists! Skipping this step." 2>&1 | tee -a "$LOG_FILE"
else
  echo "Dir ${AI4} does not exist! Clone repo..." 2>&1 | tee -a "$LOG_FILE"
  git clone --progress https://github.com/Microsoft/ai4eutils 2>&1 | tee -a "$LOG_FILE"
  cd $LOCATION_ECOASSIST_FILES/ai4eutils || { echo "Could not change directory. Command could not be run. Please send an email to petervanlunteren@hotmail.com for assistance." 2>&1 | tee -a "$LOG_FILE"; exit 1; }
  git checkout 9260e6b876fd40e9aecac31d38a86fe8ade52dfd 2>&1 | tee -a "$LOG_FILE"
  cd $LOCATION_ECOASSIST_FILES || { echo "Could not change directory. Command could not be run. Please send an email to petervanlunteren@hotmail.com for assistance." 2>&1 | tee -a "$LOG_FILE"; exit 1; }
fi

# clone yolov5 git 
YOL="yolov5"
if [ -d "$YOL" ]; then
  echo "Dir ${YOL} already exists! Skipping this step." 2>&1 | tee -a "$LOG_FILE"
else
  echo "Dir ${YOL} does not exist! Clone repo..." 2>&1 | tee -a "$LOG_FILE"
  git clone --progress https://github.com/ultralytics/yolov5.git 2>&1 | tee -a "$LOG_FILE"
  # checkout will happen dynamically during runtime with switch_yolov5_git_to()
  cd $LOCATION_ECOASSIST_FILES || { echo "Could not change directory. Command could not be run. Please send an email to petervanlunteren@hotmail.com for assistance." 2>&1 | tee -a "$LOG_FILE"; exit 1; }
fi

# clone labelImg git 
LBL="labelImg"
if [ -d "$LBL" ]; then
  echo "Dir ${LBL} already exists! Skipping this step." 2>&1 | tee -a "$LOG_FILE"
else
  echo "Dir ${LBL} does not exist! Clone repo..." 2>&1 | tee -a "$LOG_FILE"
  git clone --progress https://github.com/tzutalin/labelImg.git 2>&1 | tee -a "$LOG_FILE"
  cd $LOCATION_ECOASSIST_FILES/labelImg || { echo "Could not change directory. Command could not be run. Please install labelImg manually: https://github.com/tzutalin/labelImg" 2>&1 | tee -a "$LOG_FILE"; exit 1; }
  git checkout 276f40f5e5bbf11e84cfa7844e0a6824caf93e11 2>&1 | tee -a "$LOG_FILE"
  cd $LOCATION_ECOASSIST_FILES || { echo "Could not change directory. Command could not be run. Please install labelImg manually: https://github.com/tzutalin/labelImg" 2>&1 | tee -a "$LOG_FILE"; exit 1; }
fi

# download the MDv5a model 
mkdir -p $LOCATION_ECOASSIST_FILES/pretrained_models
cd $LOCATION_ECOASSIST_FILES/pretrained_models || { echo "Could not change directory to pretrained_models. Command could not be run. Please send an email to petervanlunteren@hotmail.com for assistance." 2>&1 | tee -a "$LOG_FILE"; exit 1; }
MDv5a="md_v5a.0.0.pt"
if [ -f "$MDv5a" ]; then
  echo "File ${MDv5a} already exists! Skipping this step." 2>&1 | tee -a "$LOG_FILE"
else
  echo "File ${MDv5a} does not exist! Downloading file..." 2>&1 | tee -a "$LOG_FILE"
  if [ "$PLATFORM" = "Apple Silicon Mac" ] ; then
    curl --keepalive -L -o md_v5a.0.0.pt https://lila.science/public/md_rebuild/md_v5a.0.0_rebuild_pt-1.12_zerolr.pt 2>&1 | tee -a "$LOG_FILE" # slightly modified version for Apple Silicon macs 
  else
    curl --keepalive -OL https://github.com/microsoft/CameraTraps/releases/download/v5.0/md_v5a.0.0.pt 2>&1 | tee -a "$LOG_FILE" # normal model
  fi
fi

# download the MDv5b model 
MDv5b="md_v5b.0.0.pt"
if [ -f "$MDv5b" ]; then
  echo "File ${MDv5b} already exists! Skipping this step." 2>&1 | tee -a "$LOG_FILE"
else
  echo "File ${MDv5b} does not exist! Downloading file..." 2>&1 | tee -a "$LOG_FILE"
  if [ "$PLATFORM" = "Apple Silicon Mac" ] ; then
    curl --keepalive -L -o md_v5b.0.0.pt https://lila.science/public/md_rebuild/md_v5b.0.0_rebuild_pt-1.12_zerolr.pt 2>&1 | tee -a "$LOG_FILE" # slightly modified version for Apple Silicon macs 
  else
    curl --keepalive -OL https://github.com/microsoft/CameraTraps/releases/download/v5.0/md_v5b.0.0.pt 2>&1 | tee -a "$LOG_FILE" # normal model
  fi
fi
cd $LOCATION_ECOASSIST_FILES || { echo "Could not change directory to ${LOCATION_ECOASSIST_FILES}. Command could not be run. Please send an email to petervanlunteren@hotmail.com for assistance." 2>&1 | tee -a "$LOG_FILE"; exit 1; }

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

# remove previous EcoAssist conda env if present
conda env remove -p $ECOASSISTCONDAENV

# create conda env
if [ "$PLATFORM" = "Linux" ]; then
  # requirements for MegaDetector 
  conda env create --name ecoassistcondaenv --file=$LOCATION_ECOASSIST_FILES/cameratraps/environment-detector.yml
  # source "${LOCATION_ECOASSIST_FILES}/miniforge/bin/activate"
  conda activate $ECOASSISTCONDAENV
  # requirements for labelImg
  $PIP install pyqt5==5.15.2 lxml libxcb-xinerama0
  echo "For the use of labelImg we need to install the libxcb-xinerama0 package (https://packages.ubuntu.com/bionic/libxcb-xinerama0). If you don't have root privileges you might be prompted for a password. Press CONTROL+D to skip authentication and not install libxcb-xinerama0. EcoAssist will still work fine without it but you might have problems with the labelImg software."
  { # first try without sudo
    apt install libxcb-xinerama0 
  } || { # otherwise with sudo
    sudo apt install libxcb-xinerama0 
    }
  cd $LOCATION_ECOASSIST_FILES/labelImg || { echo "Could not change directory. Exiting installation." 2>&1 | tee -a "$LOG_FILE"; exit 1; }
  pyrcc5 -o libs/resources.py resources.qrc
  python3 -m pip install --pre --upgrade lxml

elif [ "$PLATFORM" = "Intel Mac" ]; then
  # requirements for MegaDetector 
  conda env create --name ecoassistcondaenv --file=$LOCATION_ECOASSIST_FILES/cameratraps/environment-detector-mac.yml
  # source "${LOCATION_ECOASSIST_FILES}/miniforge/bin/activate"
  conda activate $ECOASSISTCONDAENV
  # requirements for labelImg
  $PIP install pyqt5==5.15.2 lxml

elif [ "$PLATFORM" = "Apple Silicon Mac" ]; then
  # requirements for MegaDetector via miniforge
  conda env create --name ecoassistcondaenv --file $LOCATION_ECOASSIST_FILES/cameratraps/environment-detector-m1.yml
  # source "${LOCATION_ECOASSIST_FILES}/miniforge/bin/activate"
  conda activate $ECOASSISTCONDAENV
  { # install nightly pytorch via miniforge as arm64
    $PIP install --pre torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/nightly/cpu
  } || { # if the first try didn't work
    conda install -c conda-forge pytorch torchvision -y
  }
  # install lxml
  $PIP install lxml

  # we need homebrew to install PyQt5 for Apple Silicon macs
  cd $LOCATION_ECOASSIST_FILES || { echo "Could not change directory to ${LOCATION_ECOASSIST_FILES}. Command could not be run. Please send an email to petervanlunteren@hotmail.com for assistance." 2>&1 | tee -a "$LOG_FILE"; exit 1; }
  mkdir homebrew && curl -L https://github.com/Homebrew/brew/tarball/master | tar xz --strip 1 -C homebrew 2>&1 | tee -a "$LOG_FILE"
  export PATH="${HOMEBREW_DIR}/bin:$PATH"
  
  # further requirements for labelImg
  arch -arm64 brew install pyqt@5
  cd $LOCATION_ECOASSIST_FILES/labelImg || { echo "Could not change directory. Command could not be run. Please install labelImg manually: https://github.com/tzutalin/labelImg" 2>&1 | tee -a "$LOG_FILE"; exit 1; }
  make qt5py3
  python3 -m pip install --pre --upgrade lxml
fi

# requirements for EcoAssist
$PIP install bounding_box

# requirements for yolov5
$PIP install "gitpython>=3.1.30"
$PIP install "tensorboard>=2.4.1"
$PIP install "thop>=0.1.1"
$PIP install "protobuf<=3.20.1"
$PIP install "setuptools>=65.5.1"

# log env info
conda info --envs >> "$LOG_FILE"
conda list >> "$LOG_FILE"
$PIP freeze >> "$LOG_FILE"

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