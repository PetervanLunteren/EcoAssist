#!/usr/bin/env bash

### OSX and Linux commands to uninstall the EcoAssist application https://github.com/PetervanLunteren/EcoAssist
### Peter van Lunteren, 30 August 2022, 11:20

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

# set location var
if [ "$PLATFORM" = "M1 Mac" ] || [ "$PLATFORM" = "Intel Mac" ]; then
  LOCATION_ECOASSIST_FILES="/Applications/.EcoAssist_files"
elif [ "$PLATFORM" = "Linux" ]; then
  LOCATION_ECOASSIST_FILES="$HOME/.EcoAssist_files"
fi

# set other vars
PATH_TO_CONDA_INSTALLATION_TXT_FILE=$LOCATION_ECOASSIST_FILES/EcoAssist/path_to_conda_installation.txt
PATH_TO_CONDA=`cat $PATH_TO_CONDA_INSTALLATION_TXT_FILE`
echo "Path to conda as imported from $PATH_TO_CONDA_INSTALLATION_TXT_FILE is: $PATH_TO_CONDA"

# remove EcoAssist files from computer
echo "Deleting $LOCATION_ECOASSIST_FILES..."
rm -rf $LOCATION_ECOASSIST_FILES
echo "Deleting EcoAssist.command..."
if [ "$PLATFORM" = "M1 Mac" ] || [ "$PLATFORM" = "Intel Mac" ]; then
  rm -f "/Applications/EcoAssist.command"
elif [ "$PLATFORM" = "Linux" ]; then
  rm -f "$HOME/Desktop/LINUX_EcoAssist_shortcut.desktop"
fi

# ask user if anaconda must be uninstalled too
while true; do
    read -p "Do you wish to uninstall anaconda too? Please type 'y' or 'n'." yn
    case $yn in
        [Yy]* ) echo "Removing anaconda now..."; rm -rf $PATH_TO_CONDA; break;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes or no.";;
    esac
done

# message user that it is all done
echo "The uninstallation is all done! You can close this window now."
