#!/usr/bin/env bash

### OSx and Linux uninstall commands for the EcoAssist application https://github.com/PetervanLunteren/EcoAssist
### Peter van Lunteren, 17 Jul 2023 (latest edit)

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

# set location var
if [ "$PLATFORM" = "Apple Silicon Mac" ] || [ "$PLATFORM" = "Intel Mac" ]; then
  LOCATION_ECOASSIST_FILES="/Applications/.EcoAssist_files"
elif [ "$PLATFORM" = "Linux" ]; then
  LOCATION_ECOASSIST_FILES="$HOME/.EcoAssist_files"
fi

# check other version and prompt user to re-install
VERSION_FILE="${LOCATION_ECOASSIST_FILES}/EcoAssist/version.txt"
if [ -f $VERSION_FILE ]; then
    INSTALLED_VERSION=$(<$VERSION_FILE)
    IFS='.' read -r INSTALLED_MAJOR INSTALLED_MINOR <<< "$INSTALLED_VERSION"
    if [ "$INSTALLED_MAJOR" -lt "5" ]; then
        echo
        echo "Uninstalling EcoAssist via this script has only been implemented from v5.13 onwards, while you have v$INSTALLED_VERSION installed."
        echo
        echo "You can either uninstall EcoAssist manually by deleting the EcoAssist folder ('${LOCATION_ECOASSIST_FILES}'), or you can upgrade to the latest version and rerun the uninstall."
        echo
        exit 1
    else
        if [ "$INSTALLED_MINOR" -lt "13" ]; then
            echo
            echo "Uninstalling EcoAssist via this script has only been implemented from v5.13 onwards, while you have v$INSTALLED_VERSION installed."
            echo
            echo "You can either uninstall EcoAssist manually by deleting the EcoAssist folder ('${LOCATION_ECOASSIST_FILES}'), or you can upgrade to the latest version and rerun the uninstall."
            echo
            exit 1
        fi
    fi 
fi

# execute uninstall script
INSTALL_SCRIPT="${LOCATION_ECOASSIST_FILES}/EcoAssist/install.command"
if [ -e "$INSTALL_SCRIPT" ]; then
  bash "$INSTALL_SCRIPT" "uninstall"
else
  echo No uninstallation found. This feature is only available from v5.12 onwards.
fi
exit 1
