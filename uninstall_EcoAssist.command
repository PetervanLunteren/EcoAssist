#!/usr/bin/env bash

### OSX commands to uninstall the EcoAssist application https://github.com/PetervanLunteren/EcoAssist
### Peter van Lunteren, 30 August 2022, 11:20

# set vars
LOCATION_ECOASSIST_FILES="/Applications/.EcoAssist_files"
PATH_TO_CONDA_INSTALLATION_TXT_FILE=$LOCATION_ECOASSIST_FILES/EcoAssist/path_to_conda_installation.txt
PATH_TO_CONDA=`cat $PATH_TO_CONDA_INSTALLATION_TXT_FILE`
echo "Path to conda as imported from $PATH_TO_CONDA_INSTALLATION_TXT_FILE is: $PATH_TO_CONDA"

# remove EcoAssist files from computer
echo "Deleting $LOCATION_ECOASSIST_FILES..."
rm -rf $LOCATION_ECOASSIST_FILES
echo "Deleting EcoAssist.command..."
rm -f "/Applications/EcoAssist.command"

# ask user if anaconda must be uninstalled too
while true; do
    read -p "Do you wish to uninstall anaconda too? (y/n)" yn
    case $yn in
        [Yy]* ) echo "Removing anaconda now..."; rm -rf $PATH_TO_CONDA; break;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes or no.";;
    esac
done

# message user that it is all done
echo "The uninstallation is all done! You can close this window now."