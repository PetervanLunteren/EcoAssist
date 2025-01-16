#!/bin/bash

# MacOS Application installer script for EcoAssist
# To be used with Platipus packaging tool (https://github.com/sveinbjornt/Platypus)
# Github actions will add the version number as a first line to the script like 'VERSION="v5.109"'
# Peter van Lunteren, 12 jan 2025

URL="https://storage.googleapis.com/github-release-files-storage/${VERSION}/macos-${VERSION}.tar.xz"
APP_NAME="EcoAssist"
APPLICATIONS_DIR="/Applications"
SHORTCUT="${HOME}/Desktop/${APP_NAME}.app"
TAR_FILE="/tmp/${APP_NAME}.tar.xz"
INSTALL_DIR="/Applications/EcoAssist_files"
PBAR_POS=0

progress() {
    echo "PROGRESS:${PBAR_POS}"
    PBAR_POS=$((PBAR_POS + $1))
}

progress 2

# Read previous version
PREVIOUS_VERSION="previous installation"
PREVIOUS_VERSION_FILE="${INSTALL_DIR}/EcoAssist/version.txt"
if [[ -f "$PREVIOUS_VERSION_FILE" ]]; then
    PREVIOUS_VERSION="v$(cat "$PREVIOUS_VERSION_FILE")"
fi

progress 3

# Step 0: Remove previous installation
echo "Step 1 of 5 - Uninstalling ${PREVIOUS_VERSION}..."
if [[ -d "$INSTALL_DIR" ]]; then
    if ! rm -rf "$INSTALL_DIR"; then
        echo "ALERT:Error|Failed to remove ${PREVIOUS_VERSION} ${INSTALL_DIR}"
        exit 1
    fi
fi

progress 16

# Remove existing shortcut
if [[ -L "$SHORTCUT" ]]; then
    rm "$SHORTCUT"
fi

progress 1

# Step 1: Download the tar.xz file
if [[ -f "$TAR_FILE" ]]; then
    rm "$TAR_FILE"
fi

progress 1
echo "Step 2 of 5 - Downloading ${VERSION}..."

if ! curl -s -o "$TAR_FILE" -L "$URL"; then
    echo "ALERT:Error|Failed to download ${APP_NAME} from ${URL}"
    exit 1
fi

progress 20

# Step 2: Extract the tar.xz file to the Applications folder
if [[ ! -d "$INSTALL_DIR" ]]; then
    mkdir -p "$INSTALL_DIR"
fi

progress 2
echo "Step 3 of 5 - Extracting files..."
if ! tar -xf "$TAR_FILE" -C "$APPLICATIONS_DIR"; then
    echo "ALERT:Error|Failed to extract ${APP_NAME} to ${APPLICATIONS_DIR}"
    exit 1
fi

rm "$TAR_FILE"
progress 19

# Step 3: Remove attributes recursively
echo "Step 4 of 5 - Removing attributes..."
if ! xattr -dr com.apple.quarantine "$INSTALL_DIR"; then
    echo "Error: Failed to remove attributes"
    exit 1
fi

progress 21

# Dummy open the app to trigger the first run experience
echo "Step 5 of 5 - Compiling scripts..."
if ! "${INSTALL_DIR}/envs/env-base/bin/python" "${INSTALL_DIR}/EcoAssist/EcoAssist_GUI.py" installer; then
    echo "Error: Failed to trigger the first run experience"
    exit 1
fi

progress 12

# Step 4: Create a shortcut on the Desktop
if [[ -L "$SHORTCUT" ]]; then
    rm "$SHORTCUT"
fi

progress 2
if ln -s "${INSTALL_DIR}/${APP_NAME} ${VERSION}.app" "$SHORTCUT"; then
    echo ""
    echo "Installation successfull!"
    echo "ALERT:Installation successful!|You can now open EcoAssist via the Desktop shortcut: '${SHORTCUT}'"
    echo ""
    echo "You can now open EcoAssist via the Desktop shortcut:"
    echo ""
    echo "'${SHORTCUT}'"
    echo ""
    echo "Completed! You can quit this installer now."
else
    echo "ALERT:Error|Failed to create shortcut ${SHORTCUT}"
    exit 1
fi
