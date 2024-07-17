#!/usr/bin/env bash

### OSx and Linux uninstall commands for the EcoAssist application https://github.com/PetervanLunteren/EcoAssist
### Peter van Lunteren, 17 Jul 2023 (latest edit)

# log
echo
echo Uninstalling EcoAssist...
echo

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

# delete previous installation of EcoAssist if present so that it can update
rm -rf $LOCATION_ECOASSIST_FILES && echo "Removed dir '${LOCATION_ECOASSIST_FILES}'"

# log
echo
echo Uninstalled EcoAssist. You can close this terminal window.
echo
