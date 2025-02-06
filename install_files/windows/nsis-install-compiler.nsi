# Script to create an NSIS exe to install EcoAssist on Windows
# Peter van Lunteren, last edit on 6 Jan 2025
# Var VERSION will be defined by github actions by adding a line above like '!define VERSION "v6.34"'

# Name and output location for the installer
Outfile "EcoAssist-${VERSION}-installer.exe"

# Define variables
Var archiveUrl
Var archiveName
Var InstallStatus

# Include NSIS MUI for a modern interface
!include MUI2.nsh
!include Sections.nsh

# Set execution level
RequestExecutionLevel user

# UI Pages
Name "EcoAssist ${VERSION}"
!define MUI_PAGE_HEADER_TEXT "Step 1 of 3"
!define MUI_PAGE_HEADER_SUBTEXT "Uninstalling previous EcoAssist version..."
!define MUI_FINISHPAGE_TITLE "Installation Complete!"
!define MUI_FINISHPAGE_TEXT "EcoAssist has been successfully installed. A shortcut has been created on your desktop. The program will open when double-clicked. $\r$\n$\r$\n'$DESKTOP\EcoAssist'"
!define MUI_FINISHPAGE_LINK "Read more on the EcoAssist website"
!define MUI_FINISHPAGE_LINK_LOCATION "https://addaxdatascience.com/ecoassist/"
!define MUI_ICON "logo.ico"
!define MUI_WELCOMEPAGE_TITLE "EcoAssist ${VERSION} installer"
!define MUI_WELCOMEPAGE_TEXT "This install consists of three steps:$\r$\n$\r$\n   1 - Uninstall current EcoAssist version if present$\r$\n   2 - Download EcoAssist version ${VERSION}$\r$\n   3 - Extract and clean up files"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_LANGUAGE "English"

# Section for installation steps
Section "Install"

    ; Prevent the system from sleeping
    System::Call 'kernel32::SetThreadExecutionState(i 0x80000000|0x00000001)'
    
    # Set fixed installation directory without prompting the user
    StrCpy $INSTDIR "$PROFILE\EcoAssist_files"

    # Hide progress bar
    Push "true"
    Call ShowProgressBar

    # Step 1: Remove old files and directory if they exist
    DetailPrint "Removing previous files... "
    SetOutPath $INSTDIR

    SetDetailsPrint textonly
    RMDir /r $INSTDIR\visualise_detection
    RMDir /r $INSTDIR\Human-in-the-loop
    RMDir /r $INSTDIR\envs\env-pytorch\Lib
    RMDir /r $INSTDIR\envs\env-pytorch\Library
    RMDir /r $INSTDIR\envs\env-pytorch
    RMDir /r $INSTDIR\EcoAssist
    RMDir /r $INSTDIR\models
    RMDir /r $INSTDIR\envs\env-tensorflow\Lib
    RMDir /r $INSTDIR\envs\env-tensorflow\Library
    RMDir /r $INSTDIR\envs\env-tensorflow
    RMDir /r $INSTDIR\cameratraps
    RMDir /r $INSTDIR\yolov5_versions
    RMDir /r $INSTDIR\envs\env-base\Lib\site-packages\torch
    RMDir /r $INSTDIR\envs\env-base\Lib\site-packages\PyQt5
    RMDir /r $INSTDIR\envs\env-base\Lib\site-packages\plotly
    RMDir /r $INSTDIR\envs\env-base\Lib
    RMDir /r $INSTDIR\envs\env-base\Library
    RMDir /r $INSTDIR\envs\env-base

    ; Proceed to Success if no errors
    IfErrors 0 RemoveSuccess 

    ; Handle failure
    MessageBox MB_ICONEXCLAMATION "Failed to remove the installation directory. Often a reboot solves this issue. Please try again after a reboot. "
    StrCpy $InstallStatus 0 ; Installation failure
    Abort
    Goto RemoveDone

    RemoveSuccess:
    StrCpy $InstallStatus 1 ; Installation success

    RemoveDone:
    RMDir /r $INSTDIR

    SetDetailsPrint both

    # remove dir all together
    RMDir $INSTDIR

    # add dir 
    CreateDirectory "$INSTDIR"

    # Hide progress bar
    Push "false"
    Call ShowProgressBar

    # adjust header
    !insertmacro MUI_HEADER_TEXT "Step 2 of 3" "Downloading EcoAssist version ${VERSION}..."

    # Download the 7z archive
    DetailPrint "Downloading files..."
    StrCpy $archiveUrl "https://storage.googleapis.com/github-release-files-storage/${VERSION}/windows-${VERSION}.7z" 
    StrCpy $archiveName "$INSTDIR\windows-${VERSION}.7z"
    NSISdl::download $archiveUrl $archiveName
    # inetc::get $archiveUrl $archiveName
    Pop $0

    # Check if download was successful
    IntCmp $0 0 downloadSuccess downloadFail
    downloadSuccess:
        DetailPrint "Downloaded archive successfully."
        Goto downloadDone
    downloadFail:
        DetailPrint "Failed to download archive. Exiting."
        MessageBox MB_ICONEXCLAMATION "An error occurred during installation! Could not download archive."
        Abort
    downloadDone:

    # Show progress bar
    Push "true"
    Call ShowProgressBar

    # adjust header
    !insertmacro MUI_HEADER_TEXT "Step 3 of 3" "Extracting files..."

    # Extract the 7z archrive
    Nsis7z::ExtractWithDetails "$INSTDIR\windows-${VERSION}.7z" "Extracting files... %s"

    # clean up temporary files
    Delete "$INSTDIR\windows-${VERSION}.7z"

    # PyQT5 needs to be installed on the local device
    DetailPrint "Installing PyQT5..."
    nsExec::Exec '"$INSTDIR\envs\env-base\python.exe" -m pip install PyQt5'
    nsExec::Exec '"$INSTDIR\envs\env-base\python.exe" -m pip install pyqt5-tools'   

    # compile pyrcc5 on local device
    DetailPrint "Compiling PyQT5..."
    nsExec::Exec '"$INSTDIR\envs\env-base\Scripts\pyrcc5.exe" -o "$INSTDIR\Human-in-the-loop\libs\resources.py" "$INSTDIR\Human-in-the-loop\resources.qrc"'
    
    # Installation completed successfully
    DetailPrint "Installation completed successfully."

    ; Create a shortcut on the desktop
    CreateShortcut "$INSTDIR\open-debug-mode.lnk" "$INSTDIR\EcoAssist\open.bat" "" "$INSTDIR\EcoAssist\install_files\windows\logo.ico" 0 SW_SHOWNORMAL

    ; create a shortcut for the desktop that executes the open.bat file without any terminal window
    ; Create Windows_open_EcoAssist_shortcut.vbs
    FileOpen $0 "$INSTDIR\EcoAssist\Windows_open_EcoAssist_shortcut.vbs" w
    FileWrite $0 "Set WinScriptHost = CreateObject($\"WScript.Shell$\")$\r$\n"
    FileWrite $0 "WinScriptHost.Run Chr(34) & $\"$INSTDIR\EcoAssist\open.bat$\" & Chr(34), 0$\r$\n"
    FileWrite $0 "Set WinScriptHost = Nothing$\r$\n"
    FileClose $0

    ; Create CreateShortcut.vbs
    FileOpen $0 "$INSTDIR\EcoAssist\CreateShortcut.vbs" w
    FileWrite $0 "Set oWS = WScript.CreateObject($\"WScript.Shell$\")$\r$\n"
    FileWrite $0 "sLinkFile = $\"$DESKTOP\EcoAssist.lnk$\"$\r$\n"
    FileWrite $0 "Set oLink = oWS.CreateShortcut(sLinkFile)$\r$\n"
    FileWrite $0 "oLink.TargetPath = $\"$INSTDIR\EcoAssist\Windows_open_EcoAssist_shortcut.vbs$\"$\r$\n"
    FileWrite $0 "oLink.IconLocation = $\"$INSTDIR\EcoAssist\install_files\windows\logo.ico$\"$\r$\n"
    FileWrite $0 "oLink.Save$\r$\n"
    FileClose $0

    ; Execute CreateShortcut.vbs
    nsExec::Exec 'cscript //nologo "$INSTDIR\EcoAssist\CreateShortcut.vbs"'

    # open EcoAssist in installer mode to load all dependencies and compile script so that the users doesnt have to wait long the next time
    nsExec::Exec '"$INSTDIR\\envs\\env-base\\python.exe" "$INSTDIR\\EcoAssist\\EcoAssist_GUI.py" "installer"'

    ; Notify user
    DetailPrint "Shortcut created on the desktop."

    ; Allow the system to sleep again after installation
    System::Call 'kernel32::SetThreadExecutionState(i 0x80000000)'
    
SectionEnd

# function to hide / show pbar
Function ShowProgressBar
    Exch $0
    FindWindow $1 "#32770" "" $HWNDPARENT
    GetDlgItem $2 $1 1004
    IntCmp $2 0 skip

    StrCmp $0 "true" show hide

    show:
        ShowWindow $2 1
        Return

    hide:
        ShowWindow $2 0
        Return

    skip:
        MessageBox MB_OK "Progress bar control not found."
FunctionEnd

# this happens whenever the user presses cancel
Function .onInstFailed
    MessageBox MB_ICONEXCLAMATION "The installation was canceled. Some files may not have been fully installed."
    abort
FunctionEnd
