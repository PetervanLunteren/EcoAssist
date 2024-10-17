@REM ### Windows install commands for the EcoAssist application https://github.com/PetervanLunteren/EcoAssist
@REM ### Peter van Lunteren, set date for latest edit at DATE_OF_LAST_EDIT below.

@REM set echo settings
echo off
@setlocal EnableDelayedExpansion

@REM log the install file version
set DATE_OF_LAST_EDIT="16 Aug 2024"

@REM installing version
set CURRENT_VERSION=5.18

@REM print header
echo:
echo ^|--------------------------- ECOASSIST INSTALLATION ---------------------------^|
echo:

@REM print the install file version
echo Latest edit to this install file was on %DATE_OF_LAST_EDIT%.
echo:

@REM check admin rights
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if '%errorlevel%' NEQ '0' (
    @REM user currently has no admin rights
    echo It seems like you don't have admin rights. Do you want to proceed to install for all users and enter an admin password, or install EcoAssist only for you ^(no admin rights required^)?
    :start_input_one
    set /p INPUT_ONE=Enter [O]nly me or [P]roceed as admin: 
    If /I "!INPUT_ONE!"=="O" ( goto only_me_install )
    If /I "!INPUT_ONE!"=="o" ( goto only_me_install )
    If /I "!INPUT_ONE!"=="P" ( goto proceed_as_admin )
    If /I "!INPUT_ONE!"=="p" ( goto proceed_as_admin )
    If /I "!INPUT_ONE!"=="exit" ( echo Exiting install... & cmd /k & exit )
    echo Invalid input. Type O, P, or exit.
    goto start_input_one
) else (
    @REM user does has admin rights
    goto all_users_install
)

@REM install in userfolder
:only_me_install
    @REM check if userfolder is accessible
    if exist "%homedrive%%homepath%" (
        echo:
        echo Proceeding to install in userfolder...
        if "%homepath%"=="\" (
            set ECOASSIST_PREFIX=%homedrive%
            set ECOASSIST_DRIVE=%homedrive%
        ) else (
            set ECOASSIST_PREFIX=%homedrive%%homepath%
            set ECOASSIST_DRIVE=%homedrive%
        )
    ) else (
        echo:
        echo Your userfolder is not accessible. Would you like to install EcoAssist on a custom location?
        :start_input_two
        set /p INPUT_TWO=Enter [Y]es or [N]o: 
        If /I "!INPUT_TWO!"=="Y" ( goto custom_install )
        If /I "!INPUT_TWO!"=="y" ( goto custom_install )
        If /I "!INPUT_TWO!"=="N" ( echo Exiting install... & cmd /k & exit )
        If /I "!INPUT_TWO!"=="n" ( echo Exiting install... & cmd /k & exit )
        echo Invalid input. Type Y or N.
        goto start_input_two
    )
    goto begin_install

@REM install on custom location
:custom_install
    set /p CUSTOM_ECOASSIST_LOCATION=Set path ^(for example C:\some_folder^): 
    set CUSTOM_ECOASSIST_LOCATION=%CUSTOM_ECOASSIST_LOCATION:"=%
    set CUSTOM_ECOASSIST_LOCATION=%CUSTOM_ECOASSIST_LOCATION:'=%
    IF %CUSTOM_ECOASSIST_LOCATION:~-1%==\ SET CUSTOM_ECOASSIST_LOCATION=%CUSTOM_ECOASSIST_LOCATION:~0,-1%
    echo Custom location is defined as: %CUSTOM_ECOASSIST_LOCATION%
    set ECOASSIST_PREFIX=%CUSTOM_ECOASSIST_LOCATION%
    set ECOASSIST_DRIVE=%CUSTOM_ECOASSIST_LOCATION:~0,2%
    goto begin_install

@REM prompt the user for admin rights
:proceed_as_admin
    echo:
    echo Requesting administrative privileges...
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    set params = %*:"=""
    echo UAC.ShellExecute "cmd.exe", "/c %~s0 %params%", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    del "%temp%\getadmin.vbs"
    exit /B
    goto all_users_install

@REM if user has admin rights
:all_users_install
    echo:
    echo Proceeding with administrative privileges...
    pushd "%CD%"
    CD /D "%~dp0"
    set ECOASSIST_PREFIX=%ProgramFiles%
    set ECOASSIST_DRIVE=%ProgramFiles:~0,2%
    goto begin_install

@REM begin installation
:begin_install
    echo:
    echo Proceeding to install...

@REM switch to install drive in case user executes this script from different drive
set SCRIPT_DRIVE=%~d0
echo Install script is located on drive:    '%SCRIPT_DRIVE%'
echo EcoAssist will be installed on drive:  '%ECOASSIST_DRIVE%'
%ECOASSIST_DRIVE%
echo Changed drive to:                      '%CD:~0,2%'

@REM timestamp the start of installation
set START_DATE=%date%%time%

@REM set EcoAssist_files
set LOCATION_ECOASSIST_FILES=%ECOASSIST_PREFIX%\EcoAssist_files
set PATH=%PATH%;%LOCATION_ECOASSIST_FILES%

@REM echo paths
echo Prefix:                                '%ECOASSIST_PREFIX%'
echo Location:                              '%LOCATION_ECOASSIST_FILES%'

@REM compare versions and prompt user
set "VERSION_FILE=%LOCATION_ECOASSIST_FILES%\EcoAssist\version.txt"
if not exist "%VERSION_FILE%" ( goto skip_version_check )
@REM read
FOR /F "tokens=* USEBACKQ" %%F IN (`type "%VERSION_FILE%"`) DO ( SET OTHER_VERSION=%%F)
echo Current version:                       'v!OTHER_VERSION!'
rem parse
for /F "tokens=1-2 delims=." %%a in ("%CURRENT_VERSION%") do (
    set "CURRENT_MAJOR=%%a"
    set "CURRENT_MINOR=%%b")
for /F "tokens=1-2 delims=." %%a in ("%OTHER_VERSION%") do (
    set "OTHER_MAJOR=%%a"
    set "OTHER_MINOR=%%b")
rem compare
if %CURRENT_MAJOR% gtr %OTHER_MAJOR% (
    echo Updating to version:                    'v!OTHER_VERSION!'
) else (
    if %CURRENT_MINOR% gtr %OTHER_MINOR% (
        echo Updating to version:                   'v!CURRENT_VERSION!'
    ) else (
        echo:
        echo You already have the latest version installed ^(v%OTHER_VERSION%^). Do you want to re-install?
        :reinstall_prompt
        set /p INPUT_REINSTALL_PROMPT=Enter [Y]es or [N]o: 
        If /I "!INPUT_REINSTALL_PROMPT!"=="Y" ( goto reinstallation )
        If /I "!INPUT_REINSTALL_PROMPT!"=="y" ( goto reinstallation )
        If /I "!INPUT_REINSTALL_PROMPT!"=="N" ( echo Exiting install... & cmd /k & exit )
        If /I "!INPUT_REINSTALL_PROMPT!"=="n" ( echo Exiting install... & cmd /k & exit )
        echo Invalid input. Type 'Y', 'y', 'N' or 'n'.
        goto reinstall_prompt
        :reinstallation
        echo Re-installing version %CURRENT_VERSION%...
    )
)
:skip_version_check

@REM delete previous EcoAssist installs
set NO_ADMIN_INSTALL=%homedrive%%homepath%\EcoAssist_files
if exist "%NO_ADMIN_INSTALL%" (
    rd /q /s "%NO_ADMIN_INSTALL%"
    if not exist "%NO_ADMIN_INSTALL%" (
        echo Succesfully removed:                   '%NO_ADMIN_INSTALL%'
    ) else (
        echo "Cannot remove the folder '%NO_ADMIN_INSTALL%'. Perhaps a permission issue? Restart your compupter try this installation again. If the error persists, try deleting the folder manually. If that still doens't work: copy-paste all text in this console window and send it to peter@addaxdatascience.com for further support."
        cmd /k & exit
    )
)
set ADMIN_INSTALL=%ProgramFiles%\EcoAssist_files
if exist "%ADMIN_INSTALL%" (
    rd /q /s "%ADMIN_INSTALL%"
    if not exist "%ADMIN_INSTALL%" (
        echo Succesfully removed:                   '%ADMIN_INSTALL%'
    ) else (
        echo "Cannot remove the folder '%ADMIN_INSTALL%'. Perhaps a permission issue? Restart your compupter try this installation again. If the error persists, try deleting the folder manually. If that still doens't work: copy-paste all text in this console window and send it to peter@addaxdatascience.com for further support."
        cmd /k & exit
    )
)
set CURRENT_INSTALL=%LOCATION_ECOASSIST_FILES%
if exist "%CURRENT_INSTALL%" (
    rd /q /s "%CURRENT_INSTALL%"
    if not exist "%CURRENT_INSTALL%" (
        echo Succesfully removed:                   '%CURRENT_INSTALL%'
    ) else (
        echo "Cannot remove the folder '%CURRENT_INSTALL%'. Perhaps a permission issue? Restart your compupter try this installation again. If the error persists, try deleting the folder manually. If that still doens't work: copy-paste all text in this console window and send it to peter@addaxdatascience.com for further support."
        cmd /k & exit
    )
)

@REM make dir
if not exist "%LOCATION_ECOASSIST_FILES%" (
    mkdir "%LOCATION_ECOASSIST_FILES%" || ( echo "Cannot create %LOCATION_ECOASSIST_FILES%. Copy-paste all text in this console window and send it to peter@addaxdatascience.com for further support." & cmd /k & exit )
    attrib +h "%LOCATION_ECOASSIST_FILES%"
    echo Created empty dir:                     '%LOCATION_ECOASSIST_FILES%'
)

@REM change directory
cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Copy-paste all text in this console window and send it to peter@addaxdatascience.com for further support." & cmd /k & exit )

@REM set conda cmds
@REM check the default locations for a conda install
for %%x in (miniforge3, miniconda3, anaconda3) do ( 
    for %%y in ("%ProgramData%", "%HOMEDRIVE%%HOMEPATH%", "%ProgramFiles%", "%ProgramFiles(x86)%", "%LocalAppData%", "%AppData%", "C:\tools") do ( 
        set CHECK_DIR=%%y\%%x\
        set CHECK_DIR=!CHECK_DIR:"=!
        echo Checking conda dir:                    '!CHECK_DIR!'
        if exist !CHECK_DIR! (
            set PATH_TO_CONDA_INSTALLATION=!CHECK_DIR!
            echo Found conda dir:                       '!PATH_TO_CONDA_INSTALLATION!'
            goto check_conda_install
            )
        ) 
    )

@REM check if conda is added to PATH
where conda /q  && (for /f "tokens=*" %%a in ('where conda') do (for %%b in ("%%~dpa\.") do set PATH_TO_CONDA_INSTALLATION=%%~dpb)) && goto check_conda_install

@REM provide miniforge link if not found
:set_conda_install
echo:
echo:
echo REQUIREMENT: MINIFORGE
echo:
echo EcoAssist requires miniforge ^(or any other conda distribution^) to be installed on your device. It seems like this is not the case. To install Miniforge, simply download and execute the Miniforge installer via the link below. You can leave all settings as the default values. If you see a 'Windows protected your PC' warning, you may need to click 'More info' and 'Run anyway'.
echo:
echo:
echo https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Windows-x86_64.exe
echo:
echo:
cmd /k & exit

@REM clean path
:check_conda_install
set PATH_TO_CONDA_INSTALLATION=%PATH_TO_CONDA_INSTALLATION:"=%
set PATH_TO_CONDA_INSTALLATION=%PATH_TO_CONDA_INSTALLATION:'=%
IF %PATH_TO_CONDA_INSTALLATION:~-1%==\ SET PATH_TO_CONDA_INSTALLATION=%PATH_TO_CONDA_INSTALLATION:~0,-1%
echo Path to conda is defined as:           '%PATH_TO_CONDA_INSTALLATION%'
@REM check dir validity
if not exist "%PATH_TO_CONDA_INSTALLATION%\Scripts\activate.bat" ( echo '%PATH_TO_CONDA_INSTALLATION%\Scripts\activate.bat' does not exist. Enter a path to a valid conda installation. & goto set_conda_install )
echo %PATH_TO_CONDA_INSTALLATION%> "%LOCATION_ECOASSIST_FILES%\path_to_conda_installation.txt"

@REM set pip path
set EA_PIP_EXE_BASE=%PATH_TO_CONDA_INSTALLATION%\envs\ecoassistcondaenv-base\Scripts\pip3
set EA_PIP_EXE_PYTORCH=%PATH_TO_CONDA_INSTALLATION%\envs\ecoassistcondaenv-pytorch\Scripts\pip3
set EA_PIP_EXE_TENSORFLOW=%PATH_TO_CONDA_INSTALLATION%\envs\ecoassistcondaenv-tensorflow\Scripts\pip3

@REM set git cmds
@REM check the default locations for a Git install
for %%x in (Git, git) do ( 
    for %%y in ("%ProgramFiles%", "%ProgramFiles(x86)%", "%ProgramData%", "%HOMEDRIVE%%HOMEPATH%") do ( 
        set CHECK_DIR=%%y\%%x\
        set CHECK_DIR=!CHECK_DIR:"=!
        echo Checking Git dir:                      '!CHECK_DIR!'
        if exist !CHECK_DIR! (
            set PATH_TO_GIT_INSTALLATION=!CHECK_DIR!
            echo Found Git dir:                         '!PATH_TO_GIT_INSTALLATION!'
            goto check_git_install
            )
        )
    )
@REM check if Git is added to PATH
where git /q  && (for /f "tokens=*" %%a in ('where git') do (for %%b in ("%%~dpa\.") do set PATH_TO_GIT_INSTALLATION=%%~dpb)) && goto check_git_install


@REM ask user if not found
:set_git_install
echo:
echo:
echo REQUIREMENT: GIT
echo:
echo EcoAssist requires Git to be installed on your device. It seems like this is not the case. To install Git, simply download and execute the Git installer via the link below. You can leave all settings as the default values. If you see a 'Windows protected your PC' warning, you may need to click 'More info' and 'Run anyway'.
echo:
echo:
echo https://github.com/git-for-windows/git/releases/download/v2.45.0.windows.1/Git-2.45.0-64-bit.exe
echo:
echo:
cmd /k & exit

@REM clean path
:check_git_install
set PATH_TO_GIT_INSTALLATION=%PATH_TO_GIT_INSTALLATION:"=%
set PATH_TO_GIT_INSTALLATION=%PATH_TO_GIT_INSTALLATION:'=%
IF %PATH_TO_GIT_INSTALLATION:~-1%==\ SET PATH_TO_GIT_INSTALLATION=%PATH_TO_GIT_INSTALLATION:~0,-1%
echo Path to git is defined as:             '%PATH_TO_GIT_INSTALLATION%'
@REM check dir validity
if not exist "%PATH_TO_GIT_INSTALLATION%\cmd\git.exe" ( echo '%PATH_TO_GIT_INSTALLATION%\cmd\git.exe' does not exist. Enter a path to a valid git installation. & goto set_git_install )
echo %PATH_TO_GIT_INSTALLATION%> "%LOCATION_ECOASSIST_FILES%\path_to_git_installation.txt"
@REM set git path
set EA_GIT_EXE=%PATH_TO_GIT_INSTALLATION%\cmd\git.exe

@REM install and test wtee
curl -OL https://storage.googleapis.com/google-code-archive-downloads/v2/code.google.com/wintee/wtee.exe
echo hello world | wtee -a hello-world.txt || ( echo "Looks like something is blocking your downloads... This is probably due to the settings of your device. Try again with your antivirus, VPN, proxy or any other protection software disabled. Email peter@addaxdatascience.com if you need any further assistance." & cmd /k & exit )
if exist hello-world.txt del /F hello-world.txt

@REM check if log file already exists, otherwise create empty log file
if exist "%LOCATION_ECOASSIST_FILES%\EcoAssist\logfiles\installation_log.txt" (
    set LOG_FILE=%LOCATION_ECOASSIST_FILES%\EcoAssist\logfiles\installation_log.txt
    echo LOG_FILE exists. Logging to !LOG_FILE! | wtee -a "!LOG_FILE!"
) else (
    set LOG_FILE=%LOCATION_ECOASSIST_FILES%\installation_log.txt
    echo. 2> !LOG_FILE!
    echo LOG_FILE does not exist. Logging to !LOG_FILE! | wtee -a "!LOG_FILE!"
)

@REM log the start of the installation
echo Installation started at %START_DATE% | wtee -a "%LOG_FILE%"

@REM log system information
systeminfo | wtee -a "%LOG_FILE%"

@REM check for sandbox argument and specify branch
if "%1%"=="sandbox" (
  set "GITHUB_BRANCH_NAME=sandbox"
) else (
  set "GITHUB_BRANCH_NAME=main"
)

@REM clone EcoAssist git if not present
if exist "%LOCATION_ECOASSIST_FILES%\EcoAssist\" (
    echo Dir EcoAssist already exists! Skipping this step. | wtee -a "%LOG_FILE%"
) else (
    echo Dir EcoAssist does not exists! Clone repo... | wtee -a "%LOG_FILE%"
    cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Copy-paste all text in this console window and send it to peter@addaxdatascience.com for further support." | wtee -a "%LOG_FILE%" & cmd /k & exit )
    "%EA_GIT_EXE%" clone --depth 1 --branch %GITHUB_BRANCH_NAME% https://github.com/PetervanLunteren/EcoAssist.git
    @REM check the size of the folder
    dir "%LOCATION_ECOASSIST_FILES%\EcoAssist" | wtee -a "%LOG_FILE%"
)

@REM create a .vbs file which opens EcoAssist without the console window
echo "Creating Windows_open_EcoAssist_shortcut.vbs:" | wtee -a "%LOG_FILE%"
echo Set WinScriptHost ^= CreateObject^("WScript.Shell"^) > "%LOCATION_ECOASSIST_FILES%\EcoAssist\Windows_open_EcoAssist_shortcut.vbs"
echo WinScriptHost.Run Chr^(34^) ^& "%LOCATION_ECOASSIST_FILES%\EcoAssist\open.bat" ^& Chr^(34^)^, 0  >> "%LOCATION_ECOASSIST_FILES%\EcoAssist\Windows_open_EcoAssist_shortcut.vbs"
echo Set WinScriptHost ^= Nothing >> "%LOCATION_ECOASSIST_FILES%\EcoAssist\Windows_open_EcoAssist_shortcut.vbs"

@REM create a .vbs file which creates a shortcut with the EcoAssist logo
echo "Creating CreateShortcut.vbs now..." | wtee -a "%LOG_FILE%"
echo Set oWS ^= WScript.CreateObject^("WScript.Shell"^) > "%LOCATION_ECOASSIST_FILES%\EcoAssist\CreateShortcut.vbs"
echo sLinkFile ^= "%~dp0EcoAssist.lnk" >> "%LOCATION_ECOASSIST_FILES%\EcoAssist\CreateShortcut.vbs"
echo Set oLink ^= oWS.CreateShortcut^(sLinkFile^) >> "%LOCATION_ECOASSIST_FILES%\EcoAssist\CreateShortcut.vbs"
echo oLink.TargetPath ^= "%LOCATION_ECOASSIST_FILES%\EcoAssist\Windows_open_EcoAssist_shortcut.vbs" >> "%LOCATION_ECOASSIST_FILES%\EcoAssist\CreateShortcut.vbs"
echo oLink.IconLocation ^= "%LOCATION_ECOASSIST_FILES%\EcoAssist\imgs\logo_small_bg.ico" >> "%LOCATION_ECOASSIST_FILES%\EcoAssist\CreateShortcut.vbs"
echo oLink.Save >> "%LOCATION_ECOASSIST_FILES%\EcoAssist\CreateShortcut.vbs"

@REM execute this .vbs file to create a shortcut with the EcoAssist logo
%SCRIPT_DRIVE% @REM switch to script drive
echo "Executing CreateShortcut.vbs now..." | wtee -a "%LOG_FILE%"
cscript "%LOCATION_ECOASSIST_FILES%\EcoAssist\CreateShortcut.vbs"
%ECOASSIST_DRIVE% @REM back to installation drive
echo "Created EcoAssist.lnk" | wtee -a "%LOG_FILE%"

@REM clone cameratraps git if not present
if exist "%LOCATION_ECOASSIST_FILES%\cameratraps\" (
    echo Dir cameratraps already exists! Skipping this step. | wtee -a "%LOG_FILE%"
) else (
    echo Dir cameratraps does not exists! Clone repo... | wtee -a "%LOG_FILE%"
    cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Copy-paste all text in this console window and send it to peter@addaxdatascience.com for further support." | wtee -a "%LOG_FILE%" & cmd /k & exit )
    "%EA_GIT_EXE%" clone https://github.com/agentmorris/MegaDetector.git cameratraps

    @REM Some users experience timeout issues due to the large size of this repository
    @REM If it fails here, we'll try again with a larger timeout value and fewer checks during cloning
    if not !errorlevel! == 0 (

        @REM if this git repo fails to clone, chances are the conda environments will give problems too. So better already set the conda settings to better accomodate slow internet speeds.
        set CONDA_REMOTE_READ_TIMEOUT_SECS=120
        set CONDA_REMOTE_CONNECTIONS=1
        set CONDA_REMOTE_MAX_RETRIES=20

        echo First attempt failed. Retrying with extended timeout of 200... | wtee -a "%LOG_FILE%"
        set GIT_SSH_COMMAND=ssh -o ConnectTimeout=200
        "%EA_GIT_EXE%" clone --progress --config transfer.fsckObjects=false --config receive.fsckObjects=false --config fetch.fsckObjects=false https://github.com/agentmorris/MegaDetector.git cameratraps
    )
    if not !errorlevel! == 0 (
        echo Second attempt failed. Retrying with extended timeout of 1000... | wtee -a "%LOG_FILE%"
        set GIT_SSH_COMMAND=ssh -o ConnectTimeout=1000
        "%EA_GIT_EXE%" clone --progress --config transfer.fsckObjects=false --config receive.fsckObjects=false --config fetch.fsckObjects=false https://github.com/agentmorris/MegaDetector.git cameratraps
    )
    if not !errorlevel! == 0 (
        echo Second attempt failed. Retrying with extended timeout of 3000... | wtee -a "%LOG_FILE%"
        set GIT_SSH_COMMAND=ssh -o ConnectTimeout=3000
        "%EA_GIT_EXE%" clone --progress --config transfer.fsckObjects=false --config receive.fsckObjects=false --config fetch.fsckObjects=false https://github.com/agentmorris/MegaDetector.git cameratraps
    )
    if not !errorlevel! == 0 (
        echo Second attempt failed. Retrying with --depth=1 and --unshallow | wtee -a "%LOG_FILE%"
        "%EA_GIT_EXE%" clone --depth=1 --progress --config transfer.fsckObjects=false --config receive.fsckObjects=false --config fetch.fsckObjects=false https://github.com/agentmorris/MegaDetector.git cameratraps
        cd "%LOCATION_ECOASSIST_FILES%\cameratraps"
        "%EA_GIT_EXE%" fetch --unshallow
    )
    cd "%LOCATION_ECOASSIST_FILES%\cameratraps" || ( echo "Could not change directory to cameratraps. Command could not be run. Installation was terminated. Copy-paste all text in this console window and send it to peter@addaxdatascience.com for further support." | wtee -a "%LOG_FILE%" & cmd /k & exit )
    "%EA_GIT_EXE%" checkout 393441e3cea82def9f9e6c968ab787f8e89c3056
    cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Copy-paste all text in this console window and send it to peter@addaxdatascience.com for further support." | wtee -a "%LOG_FILE%" & cmd /k & exit )
    @REM check the size of the folder
    dir "%LOCATION_ECOASSIST_FILES%\cameratraps" | wtee -a "%LOG_FILE%"
)

@REM clone yolov5 git if not present
if exist "%LOCATION_ECOASSIST_FILES%\yolov5\" (
    echo Dir yolov5 already exists! Skipping this step. | wtee -a "%LOG_FILE%"
) else (
    echo Dir yolov5 does not exists! Clone repo... | wtee -a "%LOG_FILE%"
    cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Copy-paste all text in this console window and send it to peter@addaxdatascience.com for further support." | wtee -a "%LOG_FILE%" & cmd /k & exit )
    "%EA_GIT_EXE%" clone https://github.com/ultralytics/yolov5.git
    @REM checkout will happen dynamically during runtime with switch_yolov5_git_to()
    @REM check the size of the folder
    dir "%LOCATION_ECOASSIST_FILES%\yolov5" | wtee -a "%LOG_FILE%"
)

@REM clone Human-in-the-loop git if not present
if exist "%LOCATION_ECOASSIST_FILES%\Human-in-the-loop\" (
    echo Dir Human-in-the-loop already exists! Skipping this step. | wtee -a "%LOG_FILE%"
) else (
    echo Dir Human-in-the-loop does not exists! Clone repo... | wtee -a "%LOG_FILE%"
    cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Copy-paste all text in this console window and send it to peter@addaxdatascience.com for further support." | wtee -a "%LOG_FILE%" & cmd /k & exit )
    "%EA_GIT_EXE%" clone --depth 1 https://github.com/PetervanLunteren/Human-in-the-loop.git
    @REM check the size of the folder
    dir "%LOCATION_ECOASSIST_FILES%\Human-in-the-loop" | wtee -a "%LOG_FILE%"
)

@REM clone visualise_detection git if not present
if exist "%LOCATION_ECOASSIST_FILES%\visualise_detection\" (
    echo Dir visualise_detection already exists! Skipping this step. | wtee -a "%LOG_FILE%"
) else (
    echo Dir visualise_detection does not exists! Clone repo... | wtee -a "%LOG_FILE%"
    cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Copy-paste all text in this console window and send it to peter@addaxdatascience.com for further support." | wtee -a "%LOG_FILE%" & cmd /k & exit )
    "%EA_GIT_EXE%" clone --depth 1 https://github.com/PetervanLunteren/visualise_detection.git
    @REM check the size of the folder
    dir "%LOCATION_ECOASSIST_FILES%\visualise_detection" | wtee -a "%LOG_FILE%"
)

@REM download the md_v5a.0.0.pt model if not present
if exist "%LOCATION_ECOASSIST_FILES%\models\det\MegaDetector 5a\md_v5a.0.0.pt" (
    echo "File md_v5a.0.0.pt already exists! Skipping this step." | wtee -a "%LOG_FILE%"
) else (
    echo "File md_v5a.0.0.pt does not exists! Downloading file..." | wtee -a "%LOG_FILE%"
    if not exist "%LOCATION_ECOASSIST_FILES%\models\det\MegaDetector 5a" mkdir "%LOCATION_ECOASSIST_FILES%\models\det\MegaDetector 5a"
    cd "%LOCATION_ECOASSIST_FILES%\models\det\MegaDetector 5a" || ( echo "Could not change directory to \models\det\MegaDetector 5a. Command could not be run. Installation was terminated. Copy-paste all text in this console window and send it to peter@addaxdatascience.com for further support." | wtee -a "%LOG_FILE%" & cmd /k & exit )
    curl --keepalive -OL https://github.com/ecologize/CameraTraps/releases/download/v5.0/md_v5a.0.0.pt
    cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Copy-paste all text in this console window and send it to peter@addaxdatascience.com for further support." | wtee -a "%LOG_FILE%" & cmd /k & exit )
    @REM check the size of the folder
    dir "%LOCATION_ECOASSIST_FILES%\models\det\MegaDetector 5a" | wtee -a "%LOG_FILE%"
)

@REM create folder for classification models
if not exist "%LOCATION_ECOASSIST_FILES%\models\cls" mkdir "%LOCATION_ECOASSIST_FILES%\models\cls"

@REM create txt file to let EcoAssist know it will be the first startup since install
echo Hello world! >> "%LOCATION_ECOASSIST_FILES%\first-startup.txt"

@REM add conda dir to path
set PATH=%PATH_TO_CONDA_INSTALLATION%\Scripts;%PATH%

@REM suppress conda warnings about updates
call conda config --set notify_outdated_conda false

@REM remove index cache, lock files, unused cache packages, and tarballs
call conda clean --all -y

@REM install mamba
call conda install mamba -n base -c conda-forge -y

@REM remove all old ecoassist conda evironments on the conda way, if possible
set environments=ecoassistcondaenv ecoassistcondaenv-yolov8 ecoassistcondaenv-mewc ecoassistcondaenv-base ecoassistcondaenv-pytorch ecoassistcondaenv-tensorflow
for %%E in (%environments%) do (
    echo "Attempting to remove environment %%E..."
    if exist "%PATH_TO_CONDA_INSTALLATION%\envs\%%E" (
        echo "Environment directory %%E exists. Proceeding with removal."
        call mamba env remove -n %%E -y || (
            echo "Could not mamba env remove %%E, proceeding to remove via rd..."
            rd /q /s "%PATH_TO_CONDA_INSTALLATION%\envs\%%E"
        ) || (
            echo "There was an error trying to execute the conda command for %%E. Installation was terminated. Copy-paste all text in this console window and send it to peter@addaxdatascience.com for further support."
            cmd /k & exit
        )
    ) else (
        echo "Environment directory %%E does not exist. Skipping removal."
    )
)

@REM loop over common locations for old ecoassist conda environments and remove them the hard way (rd)
for %%x in (miniforge3, mambaforge, miniconda3, anaconda3) do ( 
    for %%y in ("%ProgramData%", "%HOMEDRIVE%%HOMEPATH%", "%ProgramFiles%", "%ProgramFiles(x86)%") do ( 
        set CHECK_DIR=%%y\%%x\
        set CHECK_DIR=!CHECK_DIR:"=!
        echo Checking conda dir:                  '!CHECK_DIR!'
        if exist !CHECK_DIR! (
            for %%z in ("", "-yolov8", "-mewc", "-base", "-pytorch", "-tensorflow") do ( 
                set ENV_DIR_PATH=!CHECK_DIR!envs\ecoassistcondaenv%%z\
                set ENV_DIR_PATH=!ENV_DIR_PATH:"=!
                echo Checking env dir:                         '!ENV_DIR_PATH!'
                if exist !ENV_DIR_PATH! (
                    echo Found existing old conda env:                 '!ENV_DIR_PATH!'
                    echo Removing existing old conda env:                 '!ENV_DIR_PATH!'
                    rd /q /s "!ENV_DIR_PATH!"
                    )
                ) 
            )
        ) 
    )

@REM create mamba env and install packages for MegaDetector
cd "%LOCATION_ECOASSIST_FILES%\cameratraps" || ( echo "Could not change directory to cameratraps. Command could not be run. Installation was terminated. Copy-paste all text in this console window and send it to peter@addaxdatascience.com for further support." | wtee -a "%LOG_FILE%" & cmd /k & exit )
call mamba env create --name ecoassistcondaenv-base --file envs\environment-detector.yml || ( echo "There was an error trying to execute the conda command. Installation was terminated. Copy-paste all text in this console window and send it to peter@addaxdatascience.com for further support." & cmd /k & exit )
cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Copy-paste all text in this console window and send it to peter@addaxdatascience.com for further support." | wtee -a "%LOG_FILE%" & cmd /k & exit )
call "%PATH_TO_CONDA_INSTALLATION%\Scripts\activate.bat" "%PATH_TO_CONDA_INSTALLATION%"
call activate ecoassistcondaenv-base
"%EA_PIP_EXE_BASE%" install pyqt5==5.15.2 lxml
"%EA_PIP_EXE_BASE%" install RangeSlider
"%EA_PIP_EXE_BASE%" install gpsphoto
"%EA_PIP_EXE_BASE%" install exifread
"%EA_PIP_EXE_BASE%" install piexif
"%EA_PIP_EXE_BASE%" install openpyxl
"%EA_PIP_EXE_BASE%" install pyarrow
"%EA_PIP_EXE_BASE%" install customtkinter
"%EA_PIP_EXE_BASE%" install CTkTable
"%EA_PIP_EXE_BASE%" install GitPython==3.1.30
"%EA_PIP_EXE_BASE%" install folium
"%EA_PIP_EXE_BASE%" install plotly
"%EA_PIP_EXE_BASE%" install numpy==1.23.4
"%EA_PIP_EXE_BASE%" install pytorchwildlife==1.0.2.15
"%EA_PIP_EXE_BASE%" uninstall torch torchvision torchaudio -y
"%EA_PIP_EXE_BASE%" install torch==2.3.1+cu118 torchaudio==2.3.1+cu118 torchvision==0.18.1+cu118 --index-url https://download.pytorch.org/whl/cu118
call "%PATH_TO_CONDA_INSTALLATION%\Scripts\activate.bat" "%PATH_TO_CONDA_INSTALLATION%"
call conda deactivate

@REM create and log dedicated environment for pytorch classification
call mamba create -n ecoassistcondaenv-pytorch python=3.8 -y
call "%PATH_TO_CONDA_INSTALLATION%\Scripts\activate.bat" "%PATH_TO_CONDA_INSTALLATION%"
call activate ecoassistcondaenv-pytorch
call mamba install pytorch==2.3.0 torchvision==0.18.0 torchaudio==2.3.0 pytorch-cuda=11.8 -c pytorch -c nvidia -y
"%EA_PIP_EXE_PYTORCH%" install ultralytics==8.0.230
"%EA_PIP_EXE_PYTORCH%" install timm
"%EA_PIP_EXE_PYTORCH%" install pandas
"%EA_PIP_EXE_PYTORCH%" install numpy
"%EA_PIP_EXE_PYTORCH%" install opencv-python
"%EA_PIP_EXE_PYTORCH%" install pillow
"%EA_PIP_EXE_PYTORCH%" install dill
"%EA_PIP_EXE_PYTORCH%" install hachoir
"%EA_PIP_EXE_PYTORCH%" install versions
"%EA_PIP_EXE_PYTORCH%" install jsonpickle
call "%PATH_TO_CONDA_INSTALLATION%\Scripts\activate.bat" "%PATH_TO_CONDA_INSTALLATION%"
call conda deactivate

@REM create and log dedicated environment for tensorflow classification
call mamba env create --file EcoAssist\classification_utils\envs\tensorflow-linux-windows.yml

@REM log folder structure
dir "%LOCATION_ECOASSIST_FILES%" | wtee -a "%LOG_FILE%"

@REM timestamp the end of installation
set END_DATE=%date%%time%
echo Installation ended at %END_DATE% | wtee -a "%LOG_FILE%"

@REM move txt files to log_folder if they are in EcoAssist_files
if exist "%LOCATION_ECOASSIST_FILES%\installation_log.txt" ( move /Y "%LOCATION_ECOASSIST_FILES%\installation_log.txt" "%LOCATION_ECOASSIST_FILES%\EcoAssist\logfiles" )
if exist "%LOCATION_ECOASSIST_FILES%\path_to_conda_installation.txt" ( move /Y "%LOCATION_ECOASSIST_FILES%\path_to_conda_installation.txt" "%LOCATION_ECOASSIST_FILES%\EcoAssist\logfiles" )
if exist "%LOCATION_ECOASSIST_FILES%\path_to_git_installation.txt" ( move /Y "%LOCATION_ECOASSIST_FILES%\path_to_git_installation.txt" "%LOCATION_ECOASSIST_FILES%\EcoAssist\logfiles" )

@REM end process
echo THE INSTALLATION IS DONE^^! You can close this window now and proceed to open EcoAssist by double clicking the EcoAssist.lnk file in the same folder as this installation file ^(so probably Downloads^).

@REM keep console open after finishing
cmd /k & exit
