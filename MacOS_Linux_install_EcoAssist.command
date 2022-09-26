#!/usr/bin/env bash

### OSx and Linux install commands for the EcoAssist application https://github.com/PetervanLunteren/EcoAssist
### Peter van Lunteren, 26 September 2022


# check the OS and set var
if [ "$(uname)" == "Darwin" ]; then
  echo "This is an OSX computer..."
  if [[ $(sysctl -n machdep.cpu.brand_string) =~ "Apple" ]]; then
    echo "   ...with an M1 processor."
    PLATFORM="M1 Mac"
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
if [ "$PLATFORM" = "M1 Mac" ] || [ "$PLATFORM" = "Intel Mac" ]; then
  pmset noidle &
  PMSETPID=$!
fi

# set location var
if [ "$PLATFORM" = "M1 Mac" ] || [ "$PLATFORM" = "Intel Mac" ]; then
  LOCATION_ECOASSIST_FILES="/Applications/.EcoAssist_files"
elif [ "$PLATFORM" = "Linux" ]; then
  LOCATION_ECOASSIST_FILES="$HOME/.EcoAssist_files"
fi

# delete previous installation of EcoAssist if present so that it can update
rm -rf $LOCATION_ECOASSIST_FILES

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
if [ "$PLATFORM" = "M1 Mac" ] || [ "$PLATFORM" = "Intel Mac" ]; then
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

# clone EcoAssist git if not present
cd $LOCATION_ECOASSIST_FILES || { echo "Could not change directory to ${LOCATION_ECOASSIST_FILES}. Command could not be run. Please install EcoAssist manually: https://github.com/PetervanLunteren/EcoAssist"; exit 1; }
ECO="EcoAssist"
if [ -d "$ECO" ]; then
  echo "Dir ${ECO} already exists! Skipping this step." 2>&1 | tee -a "$LOG_FILE"
else
  echo "Dir ${ECO} does not exist! Clone repo..." 2>&1 | tee -a "$LOG_FILE"
  git clone --progress https://github.com/PetervanLunteren/EcoAssist.git 2>&1 | tee -a "$LOG_FILE"
  # move the open.cmd two dirs up and give it an icon
  if [ "$PLATFORM" = "M1 Mac" ] || [ "$PLATFORM" = "Intel Mac" ]; then
    FILE="$LOCATION_ECOASSIST_FILES/EcoAssist/MacOS_Linux_open_EcoAssist.command"
    ICON="$LOCATION_ECOASSIST_FILES/EcoAssist/imgs/logo_small_bg.icns" 
    bash fileicon set $FILE $ICON 2>&1 | tee -a "$LOG_FILE" # set icon
    mv -f $FILE "/Applications/EcoAssist.command" # move file and replace
  elif [ "$PLATFORM" = "Linux" ]; then
    SOURCE="$LOCATION_ECOASSIST_FILES/EcoAssist/imgs/logo_small_bg.png"
    DEST="$HOME/.icons/logo_small_bg.png"
    mkdir -p "$HOME/.icons" # create location if not already present
    cp $SOURCE $DEST # copy icon to proper location
    FILE="$LOCATION_ECOASSIST_FILES/EcoAssist/Linux_open_EcoAssist_shortcut.desktop"
    mv -f $FILE "$HOME/Desktop/Linux_open_EcoAssist_shortcut.desktop" # move file and replace
  fi
  cd $LOCATION_ECOASSIST_FILES || { echo "Could not change directory. Command could not be run. Please install EcoAssist manually: https://github.com/PetervanLunteren/EcoAssist" 2>&1 | tee -a "$LOG_FILE"; exit 1; }
fi

# clone cameratraps git if not present
CAM="cameratraps"
if [ -d "$CAM" ]; then
  echo "Dir ${CAM} already exists! Skipping this step." 2>&1 | tee -a "$LOG_FILE"
else
  echo "Dir ${CAM} does not exist! Clone repo..." 2>&1 | tee -a "$LOG_FILE"
  git clone --progress https://github.com/Microsoft/cameratraps 2>&1 | tee -a "$LOG_FILE"
  cd $LOCATION_ECOASSIST_FILES/cameratraps || { echo "Could not change directory. Command could not be run. Please install EcoAssist manually: https://github.com/PetervanLunteren/EcoAssist" 2>&1 | tee -a "$LOG_FILE"; exit 1; }
  git checkout 27e0f04d53a3a4b0ffa18493a80bbf1fec15c3fe 2>&1 | tee -a "$LOG_FILE"
  cd $LOCATION_ECOASSIST_FILES || { echo "Could not change directory. Command could not be run. Please install EcoAssist manually: https://github.com/PetervanLunteren/EcoAssist" 2>&1 | tee -a "$LOG_FILE"; exit 1; }
fi

# clone ai4eutils git if not present
AI4="ai4eutils"
if [ -d "$AI4" ]; then
  echo "Dir ${AI4} already exists! Skipping this step." 2>&1 | tee -a "$LOG_FILE"
else
  echo "Dir ${AI4} does not exist! Clone repo..." 2>&1 | tee -a "$LOG_FILE"
  git clone --progress https://github.com/Microsoft/ai4eutils 2>&1 | tee -a "$LOG_FILE"
  cd $LOCATION_ECOASSIST_FILES/ai4eutils || { echo "Could not change directory. Command could not be run. Please install EcoAssist manually: https://github.com/PetervanLunteren/EcoAssist" 2>&1 | tee -a "$LOG_FILE"; exit 1; }
  git checkout 9260e6b876fd40e9aecac31d38a86fe8ade52dfd 2>&1 | tee -a "$LOG_FILE"
  cd $LOCATION_ECOASSIST_FILES || { echo "Could not change directory. Command could not be run. Please install EcoAssist manually: https://github.com/PetervanLunteren/EcoAssist" 2>&1 | tee -a "$LOG_FILE"; exit 1; }
fi

# clone yolov5 git if not present
YOL="yolov5"
if [ -d "$YOL" ]; then
  echo "Dir ${YOL} already exists! Skipping this step." 2>&1 | tee -a "$LOG_FILE"
else
  echo "Dir ${YOL} does not exist! Clone repo..." 2>&1 | tee -a "$LOG_FILE"
  git clone --progress https://github.com/ultralytics/yolov5/ 2>&1 | tee -a "$LOG_FILE"
  cd $LOCATION_ECOASSIST_FILES/yolov5 || { echo "Could not change directory. Command could not be run. Please install EcoAssist manually: https://github.com/PetervanLunteren/EcoAssist" 2>&1 | tee -a "$LOG_FILE"; exit 1; }
  if [ "$PLATFORM" = "M1 Mac" ] ; then
    git checkout 868c0e9bbb45b031e7bfd73c6d3983bcce07b9c1 2>&1 | tee -a "$LOG_FILE"
  else
    git checkout c23a441c9df7ca9b1f275e8c8719c949269160d1 2>&1 | tee -a "$LOG_FILE"
  fi
  cd $LOCATION_ECOASSIST_FILES || { echo "Could not change directory. Command could not be run. Please install EcoAssist manually: https://github.com/PetervanLunteren/EcoAssist" 2>&1 | tee -a "$LOG_FILE"; exit 1; }
fi

# clone labelImg git if not present
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

# download the md_v5a.0.0.pt model if not present
mkdir -p $LOCATION_ECOASSIST_FILES/megadetector
cd $LOCATION_ECOASSIST_FILES/megadetector || { echo "Could not change directory to megadetector. Command could not be run. Please install EcoAssist manually: https://github.com/PetervanLunteren/EcoAssist" 2>&1 | tee -a "$LOG_FILE"; exit 1; }
MD="md_v5a.0.0.pt"
if [ -f "$MD" ]; then
  echo "File ${MD} already exists! Skipping this step." 2>&1 | tee -a "$LOG_FILE"
else
  echo "File ${MD} does not exist! Downloading file..." 2>&1 | tee -a "$LOG_FILE"
  if [ "$PLATFORM" = "M1 Mac" ] ; then
    curl --keepalive -L -o md_v5a.0.0.pt https://lila.science/public/md_rebuild/md_v5a.0.0_rebuild_pt-1.12_zerolr.pt 2>&1 | tee -a "$LOG_FILE" # slightly modified version for M1 macs 
  else
    curl --keepalive -OL https://github.com/microsoft/CameraTraps/releases/download/v5.0/md_v5a.0.0.pt 2>&1 | tee -a "$LOG_FILE" # normal model
  fi
fi
cd $LOCATION_ECOASSIST_FILES || { echo "Could not change directory to ${LOCATION_ECOASSIST_FILES}. Command could not be run. Please install EcoAssist manually: https://github.com/PetervanLunteren/EcoAssist" 2>&1 | tee -a "$LOG_FILE"; exit 1; }

# check if conda is already installed, if not install
PATH_TO_CONDA_INSTALLATION_TXT_FILE=$LOCATION_ECOASSIST_FILES/EcoAssist/path_to_conda_installation.txt
cd $LOCATION_ECOASSIST_FILES || { echo "Could not change directory to ${LOCATION_ECOASSIST_FILES}. Command could not be run. Please install EcoAssist manually: https://github.com/PetervanLunteren/EcoAssist" 2>&1 | tee -a "$LOG_FILE"; exit 1; }
CONDA_LIST_1=`conda list`
echo "CONDA_LIST_1 yields: $CONDA_LIST_1" 2>&1 | tee -a "$LOG_FILE"
if [ "$CONDA_LIST_1" == "" ]; then
  # the conda command is not recognised
  echo "Conda might be installed, but the conda command is not recognised. Lets try to add some common locations of anaconda to the \$PATH variable and check again..." 2>&1 | tee -a "$LOG_FILE"
  export PATH="~/anaconda3/bin:$PATH"
  export PATH="~/Anaconda3/bin:$PATH"
  export PATH="$HOME/anaconda3/bin:$PATH"
  export PATH="$HOME/Anaconda3/bin:$PATH"
  export PATH="/opt/anaconda3/bin:$PATH"
  export PATH="/Opt/anaconda3/bin:$PATH"
  export PATH="/opt/Anaconda3/bin:$PATH"
  export PATH="/Opt/Anaconda3/bin:$PATH"
  echo "PATH var is: $PATH"  2>&1 | tee -a "$LOG_FILE"
  # check if conda command works
  CONDA_LIST_2=`conda list`
  echo "CONDA_LIST_2 yields: $CONDA_LIST_2" 2>&1 | tee -a "$LOG_FILE"
  if [ "$CONDA_LIST_2" == "" ]; then
    # download and install anaconda
    echo "Looks like anaconda is not yet installed. Downloading installation file now..." 2>&1 | tee -a "$LOG_FILE"
    if [ "$PLATFORM" = "M1 Mac" ] || [ "$PLATFORM" = "Intel Mac" ]; then
      curl --keepalive -O https://repo.anaconda.com/archive/Anaconda3-2021.11-MacOSX-x86_64.sh 2>&1 | tee -a "$LOG_FILE"
      echo "Executing installation file now... The installation is not yet done. Please be patient."  2>&1 | tee -a "$LOG_FILE"
      INSTALL_SH=Anaconda3-2021.11-MacOSX-x86_64.sh
    elif [ "$PLATFORM" = "Linux" ]; then
      curl --keepalive -O https://repo.anaconda.com/archive/Anaconda3-2021.11-Linux-x86_64.sh 2>&1 | tee -a "$LOG_FILE"
      echo "Executing installation file now... The installation is not yet done. Please be patient."  2>&1 | tee -a "$LOG_FILE"
      INSTALL_SH=Anaconda3-2021.11-Linux-x86_64.sh
    fi
    echo $INSTALL_SH
    sh $INSTALL_SH -b 2>&1 | tee -a "$LOG_FILE"
    echo "Lets try to add some common locations of anaconda to the \$PATH variable."  2>&1 | tee -a "$LOG_FILE"
    export PATH="~/anaconda3/bin:$PATH"
    export PATH="~/Anaconda3/bin:$PATH"
    export PATH="$HOME/anaconda3/bin:$PATH"
    export PATH="$HOME/Anaconda3/bin:$PATH"
    export PATH="/opt/anaconda3/bin:$PATH"
    export PATH="/Opt/anaconda3/bin:$PATH"
    export PATH="/opt/Anaconda3/bin:$PATH"
    export PATH="/Opt/Anaconda3/bin:$PATH"
    echo "PATH var is: $PATH"  2>&1 | tee -a "$LOG_FILE"
    # check if this worked
    CONDA_LIST_3=`conda list`
    echo "CONDA_LIST_3 yields: $CONDA_LIST_3" 2>&1 | tee -a "$LOG_FILE"
    if [ "$CONDA_LIST_3" == "" ]; then
      echo "Looks like conda is installed but it still can't find the location of the anaconda3 folder. Lets try regex on the error message."  2>&1 | tee -a "$LOG_FILE"
      REGEX_PATH=`sh $INSTALL_SH -b 2> >(grep -o "'.*'") | tr -d "'"`
      echo "The prefix extracted from the error message is $REGEX_PATH" 2>&1 | tee -a "$LOG_FILE"
      export PATH="$REGEX_PATH/bin:$PATH"
      echo "PATH var is: $PATH"  2>&1 | tee -a "$LOG_FILE"
      # check if this worked
      CONDA_LIST_4=`conda list`
      echo "CONDA_LIST_4 yields: $CONDA_LIST_4" 2>&1 | tee -a "$LOG_FILE"
      if [ "$CONDA_LIST_4" == "" ]; then
        # could not get it to work
        if [ "$PLATFORM" = "M1 Mac" ] || [ "$PLATFORM" = "Intel Mac" ]; then
          echo "The installation of anaconda could not be completed. Please install anaconda using the graphic installer (https://repo.anaconda.com/archive/Anaconda3-2021.11-MacOSX-x86_64.pkg). After the anaconda is successfully installed, please execute the MacOS_Linux_install_EcoAssist.command again by double-clicking." 2>&1 | tee -a "$LOG_FILE"; exit 1; 
        elif [ "$PLATFORM" = "Linux" ]; then
          echo "The installation of anaconda could not be completed. Please install anaconda using the graphic installer (https://www.anaconda.com/products/distribution). After the anaconda is successfully installed, please execute the MacOS_Linux_install_EcoAssist.command again." 2>&1 | tee -a "$LOG_FILE"; exit 1; 
        fi
      fi
    else
      echo "The conda command works!" 2>&1 | tee -a "$LOG_FILE"
    fi
  else
    echo "The conda command works!" 2>&1 | tee -a "$LOG_FILE"
  fi
else
  echo "The conda command works!" 2>&1 | tee -a "$LOG_FILE"
fi

# remove if the installation file is still there
cd $LOCATION_ECOASSIST_FILES || { echo "Could not change directory to ${LOCATION_ECOASSIST_FILES}. Command could not be run. Please install EcoAssist manually: https://github.com/PetervanLunteren/EcoAssist" 2>&1 | tee -a "$LOG_FILE"; exit 1; }
if [ -f "$INSTALL_SH" ]; then
  echo "File ${INSTALL_SH} is still there! Deleting now." 2>&1 | tee -a "$LOG_FILE"
  rm $INSTALL_SH
else
  echo "File ${INSTALL_SH} does not exist! Nothing to delete..." 2>&1 | tee -a "$LOG_FILE"
fi

# write path to conda to txt file
echo `conda info | grep 'base environment' | cut -d ':' -f 2 | xargs | cut -d ' ' -f 1` > $PATH_TO_CONDA_INSTALLATION_TXT_FILE

# locate conda.sh on local machine and source it
PATH_TO_CONDA=`cat $PATH_TO_CONDA_INSTALLATION_TXT_FILE`
echo "Path to conda as imported from $PATH_TO_CONDA_INSTALLATION_TXT_FILE is: $PATH_TO_CONDA" 2>&1 | tee -a "$LOG_FILE"
PATH2CONDA_SH="$PATH_TO_CONDA/etc/profile.d/conda.sh"
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

# remove previous EcoAssist conda env if present
conda env remove -n ecoassistcondaenv

# create conda env
if [ "$PLATFORM" = "Linux" ]; then
  # requirements for MegaDetector 
  conda env create --name ecoassistcondaenv --file=$LOCATION_ECOASSIST_FILES/cameratraps/environment-detector.yml
  conda activate ecoassistcondaenv
  # requirements for labelImg
  pip install pyqt5==5.15.2 lxml libxcb-xinerama0
  cd $LOCATION_ECOASSIST_FILES/labelImg || { echo "Could not change directory. Command could not be run. Please install labelImg manually: https://github.com/tzutalin/labelImg" 2>&1 | tee -a "$LOG_FILE"; exit 1; }
  pyrcc5 -o libs/resources.py resources.qrc
  python3 -m pip install --pre --upgrade lxml
elif [ "$PLATFORM" = "Intel Mac" ]; then
  # requirements for MegaDetector 
  conda env create --name ecoassistcondaenv --file=$LOCATION_ECOASSIST_FILES/cameratraps/environment-detector-mac.yml
  conda activate ecoassistcondaenv
  # requirements for labelImg
  pip install pyqt5==5.15.2 lxml
elif [ "$PLATFORM" = "M1 Mac" ] ; then
  # requirements for MegaDetector
  CONDA_SUBDIR=osx-arm64 conda env create --name ecoassistcondaenv --file $LOCATION_ECOASSIST_FILES/cameratraps/environment-detector-m1.yml
  conda activate ecoassistcondaenv
  pip3 install -U --pre torch torchvision --extra-index-url https://download.pytorch.org/whl/nightly/cpu

  # requirements for labelImg
  pip3 install lxml

  # we need homebrew to install PyQt5 for M1 macs...
  # check if homebrew is already installed, if not install
  PATH_TO_BREW_INSTALLATION_TXT_FILE=$LOCATION_ECOASSIST_FILES/EcoAssist/path_to_brew_installation.txt
  cd $LOCATION_ECOASSIST_FILES || { echo "Could not change directory to ${LOCATION_ECOASSIST_FILES}. Command could not be run. Please install EcoAssist manually: https://github.com/PetervanLunteren/EcoAssist" 2>&1 | tee -a "$LOG_FILE"; exit 1; }
  BREW_V_1=`brew -v`
  echo "BREW_V_1 yields: $BREW_V_1" 2>&1 | tee -a "$LOG_FILE"
  if [ "$BREW_V_1" == "" ]; then
    # the brew command is not recognised
    echo "Homebrew might be installed, but the brew command is not recognised. Lets try to add some common locations of homebrew to the \$PATH variable and check again..." 2>&1 | tee -a "$LOG_FILE"
    export PATH="$LOCATION_ECOASSIST_FILES/homebrew/bin:$PATH"
    export PATH="/usr:$PATH"
    export PATH="/usr/homebrew:$PATH"
    export PATH="/usr/bin:$PATH"
    export PATH="/usr/homebrew/bin:$PATH"
    export PATH="/usr/local:$PATH"
    export PATH="/usr/local/homebrew:$PATH"
    export PATH="/usr/local/bin:$PATH"
    export PATH="/usr/local/homebrew/bin:$PATH"
    export PATH="/usr/local/opt:$PATH"
    export PATH="/usr/local/opt/homebrew:$PATH"
    export PATH="/usr/local/opt/bin:$PATH"
    export PATH="/usr/local/opt/homebrew/bin:$PATH"
    export PATH="/opt:$PATH"
    export PATH="/opt/homebrew:$PATH"
    export PATH="/opt/bin:$PATH"
    export PATH="/opt/homebrew/bin:$PATH"
    echo "PATH var is: $PATH"  2>&1 | tee -a "$LOG_FILE"
    # check if brew command works
    BREW_V_2=`brew -v`
    echo "BREW_V_2 yields: $BREW_V_2" 2>&1 | tee -a "$LOG_FILE"
    if [ "$BREW_V_2" == "" ]; then
      # download and install homebrew
      echo "Looks like homebrew is not yet installed. Downloading installation file now..." 2>&1 | tee -a "$LOG_FILE"
      mkdir homebrew && curl -L https://github.com/Homebrew/brew/tarball/master | tar xz --strip 1 -C homebrew 2>&1 | tee -a "$LOG_FILE"
      export PATH="$LOCATION_ECOASSIST_FILES/homebrew/bin:$PATH"
      # check if this worked
      BREW_V_3=`brew -v`
      echo "BREW_V_3 yields: $BREW_V_3" 2>&1 | tee -a "$LOG_FILE"
      if [ "$BREW_V_3" == "" ]; then
        # could not get it to work
        echo "The installation of homebrew could not be completed. Please install homebrew manually (https://brew.sh/). After homebrew is successfully installed, please execute the MacOS_Linux_install_EcoAssist.command again by double-clicking." 2>&1 | tee -a "$LOG_FILE"; exit 1; 
      else
        echo "The brew command works!" 2>&1 | tee -a "$LOG_FILE"
      fi
    else
      echo "The brew command works!" 2>&1 | tee -a "$LOG_FILE"
    fi
  else
    echo "The brew command works!" 2>&1 | tee -a "$LOG_FILE"
  fi

  # write path to homebrew to txt file
  echo `brew --prefix` > $PATH_TO_BREW_INSTALLATION_TXT_FILE
  
  # further requirements for labelImg
  arch -arm64 brew install pyqt@5
  cd $LOCATION_ECOASSIST_FILES/labelImg || { echo "Could not change directory. Command could not be run. Please install labelImg manually: https://github.com/tzutalin/labelImg" 2>&1 | tee -a "$LOG_FILE"; exit 1; }
  make qt5py3
  python3 -m pip install --pre --upgrade lxml
fi

# requirements for EcoAssist
pip install bounding_box

# log env info
conda info --envs >> "$LOG_FILE"
conda list >> "$LOG_FILE"
pip freeze >> "$LOG_FILE"

# deactivate conda env
conda deactivate

# log system files with sizes after installation
FILE_SIZES_DEPTH_0=`du -sh $LOCATION_ECOASSIST_FILES`
FILE_SIZES_DEPTH_1=`du -sh $LOCATION_ECOASSIST_FILES/*`
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

# move LOG_FILE is needed
WRONG_LOG_FILE_LOCATION=$LOCATION_ECOASSIST_FILES/installation_log.txt
if [ "$LOG_FILE" == "$WRONG_LOG_FILE_LOCATION" ]; then
  mv $LOG_FILE $LOCATION_ECOASSIST_FILES/EcoAssist/logfiles
fi

# message for the user
echo ""
echo "THE INSTALLATION IS DONE! You can close this window now and proceed to open EcoAssist by double clicking the EcoAssist.command file in your applications folder."
echo ""

# the computer may go to sleep again
if [ "$PLATFORM" = "M1 Mac" ] || [ "$PLATFORM" = "Intel Mac" ]; then
  kill $PMSETPID
fi
