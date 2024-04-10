@REM ### Windows install commands for the EcoAssist application https://github.com/PetervanLunteren/EcoAssist
@REM ### Peter van Lunteren, set date for latest edit at DATE_OF_LAST_EDIT below.

@REM set echo settings
echo off
@setlocal EnableDelayedExpansion

@REM log the install file version
set DATE_OF_LAST_EDIT="10 Apr 2024"

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

@REM delete previous EcoAssist installs
set NO_ADMIN_INSTALL=%homedrive%%homepath%\EcoAssist_files
if exist "%NO_ADMIN_INSTALL%" (
    rd /q /s "%NO_ADMIN_INSTALL%"
    echo Removed:                               '%NO_ADMIN_INSTALL%'
)
set ADMIN_INSTALL=%ProgramFiles%\EcoAssist_files
if exist "%ADMIN_INSTALL%" (
    rd /q /s "%ADMIN_INSTALL%"
    echo Removed:                               '%ADMIN_INSTALL%'
)
set CURRENT_INSTALL=%LOCATION_ECOASSIST_FILES%
if exist "%CURRENT_INSTALL%" (
    rd /q /s "%CURRENT_INSTALL%"
    echo Removed:                               '%CURRENT_INSTALL%'
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
for %%x in (miniforge3, mambaforge, miniconda3, anaconda3) do ( 
    for %%y in ("%ProgramData%", "%HOMEDRIVE%%HOMEPATH%", "%ProgramFiles%", "%ProgramFiles(x86)%") do ( 
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
@REM check if conda or mamba is added to PATH
where conda /q  && (for /f "tokens=*" %%a in ('where conda') do (for %%b in ("%%~dpa\.") do set PATH_TO_CONDA_INSTALLATION=%%~dpb)) && goto check_conda_install
where mamba /q  && (for /f "tokens=*" %%a in ('where mamba') do (for %%b in ("%%~dpa\.") do set PATH_TO_CONDA_INSTALLATION=%%~dpb)) && goto check_conda_install
:set_conda_install
echo:
@REM ask user if not found
set /p PATH_TO_CONDA_INSTALLATION=Unable to automatically find the folder containing your conda files. The EcoAssist instalation needs to know this path in order to proceed. The required folder is likely called 'miniforge3', 'mambaforge', 'miniconda3', 'anaconda3' and contains the subfolders 'condabin', 'conda-meta', 'DLLs', 'envs' and more. Please provide this path ^(or drag and drop^): 
:check_conda_install
@REM clean path
set PATH_TO_CONDA_INSTALLATION=%PATH_TO_CONDA_INSTALLATION:"=%
set PATH_TO_CONDA_INSTALLATION=%PATH_TO_CONDA_INSTALLATION:'=%
IF %PATH_TO_CONDA_INSTALLATION:~-1%==\ SET PATH_TO_CONDA_INSTALLATION=%PATH_TO_CONDA_INSTALLATION:~0,-1%
echo Path to conda is defined as:           '%PATH_TO_CONDA_INSTALLATION%'
@REM check dir validity
if not exist "%PATH_TO_CONDA_INSTALLATION%\Scripts\activate.bat" ( echo '%PATH_TO_CONDA_INSTALLATION%\Scripts\activate.bat' does not exist. Enter a path to a valid conda installation. & goto set_conda_install )
echo %PATH_TO_CONDA_INSTALLATION%> "%LOCATION_ECOASSIST_FILES%\path_to_conda_installation.txt"
@REM check if mambaforge and set conda command accordingly
for %%f in ("%PATH_TO_CONDA_INSTALLATION%") do set "FOLDER_NAME=%%~nxf"
if "%FOLDER_NAME%" == "mambaforge" ( set EA_CONDA_EXE=mamba ) else ( set EA_CONDA_EXE=conda )
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
:set_git_install
echo:
@REM ask user if not found
set /p PATH_TO_GIT_INSTALLATION=Unable to automatically find the folder containing your Git files. The EcoAssist instalation needs to know this path in order to proceed. The required folder is likely called 'Git' and contains the subfolders 'bin', 'cmd', 'etc', 'tmp', 'usr' and more. Please provide this path ^(or drag and drop^): 
:check_git_install
@REM clean path
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
        echo First attempt failed. Retrying with extended timeout... | wtee -a "%LOG_FILE%"
        set GIT_SSH_COMMAND=ssh -o ConnectTimeout=200
        git clone --progress --config transfer.fsckObjects=false --config receive.fsckObjects=false --config fetch.fsckObjects=false --config transfer.fsckObjects=false --config receive.fsckObjects=false --config fetch.fsckObjects=false https://github.com/agentmorris/MegaDetector.git cameratraps
    )

    cd "%LOCATION_ECOASSIST_FILES%\cameratraps" || ( echo "Could not change directory to cameratraps. Command could not be run. Installation was terminated. Copy-paste all text in this console window and send it to peter@addaxdatascience.com for further support." | wtee -a "%LOG_FILE%" & cmd /k & exit )
    "%EA_GIT_EXE%" checkout f72f36f7511a8da7673d52fc3692bd10ec69eb28
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

@REM activate conda/mamba command
set PATH=%PATH_TO_CONDA_INSTALLATION%\Scripts;%PATH%
call "%PATH_TO_CONDA_INSTALLATION%\Scripts\activate.bat" "%PATH_TO_CONDA_INSTALLATION%"

@REM suppress conda warnings about updates
call %EA_CONDA_EXE% config --set notify_outdated_conda false

@REM remove index cache, lock files, unused cache packages, and tarballs
call %EA_CONDA_EXE% clean --all

@REM remove all old ecoassist conda evironments, if present
call %EA_CONDA_EXE% env remove -n ecoassistcondaenv || ( echo "could not conda env remove, proceeding to remove via rd..." & rd /q /s "%PATH_TO_CONDA_INSTALLATION%\envs\ecoassistcondaenv" ) || ( echo "There was an error trying to execute the conda command. Installation was terminated. Copy-paste all text in this console window and send it to peter@addaxdatascience.com for further support." & cmd /k & exit )
call %EA_CONDA_EXE% env remove -n ecoassistcondaenv-yolov8 || ( echo "could not conda env remove, proceeding to remove via rd..." & rd /q /s "%PATH_TO_CONDA_INSTALLATION%\envs\ecoassistcondaenv-yolov8" ) || ( echo "There was an error trying to execute the conda command. Installation was terminated. Copy-paste all text in this console window and send it to peter@addaxdatascience.com for further support." & cmd /k & exit )
call %EA_CONDA_EXE% env remove -n ecoassistcondaenv-mewc || ( echo "could not conda env remove, proceeding to remove via rd..." & rd /q /s "%PATH_TO_CONDA_INSTALLATION%\envs\ecoassistcondaenv-mewc" ) || ( echo "There was an error trying to execute the conda command. Installation was terminated. Copy-paste all text in this console window and send it to peter@addaxdatascience.com for further support." & cmd /k & exit )
call %EA_CONDA_EXE% env remove -n ecoassistcondaenv-base || ( echo "could not conda env remove, proceeding to remove via rd..." & rd /q /s "%PATH_TO_CONDA_INSTALLATION%\envs\ecoassistcondaenv-base" ) || ( echo "There was an error trying to execute the conda command. Installation was terminated. Copy-paste all text in this console window and send it to peter@addaxdatascience.com for further support." & cmd /k & exit )
call %EA_CONDA_EXE% env remove -n ecoassistcondaenv-pytorch || ( echo "could not conda env remove, proceeding to remove via rd..." & rd /q /s "%PATH_TO_CONDA_INSTALLATION%\envs\ecoassistcondaenv-pytorch" ) || ( echo "There was an error trying to execute the conda command. Installation was terminated. Copy-paste all text in this console window and send it to peter@addaxdatascience.com for further support." & cmd /k & exit )
call %EA_CONDA_EXE% env remove -n ecoassistcondaenv-tensorflow || ( echo "could not conda env remove, proceeding to remove via rd..." & rd /q /s "%PATH_TO_CONDA_INSTALLATION%\envs\ecoassistcondaenv-tensorflow" ) || ( echo "There was an error trying to execute the conda command. Installation was terminated. Copy-paste all text in this console window and send it to peter@addaxdatascience.com for further support." & cmd /k & exit )

@REM create conda env and install packages for MegaDetector
cd "%LOCATION_ECOASSIST_FILES%\cameratraps" || ( echo "Could not change directory to cameratraps. Command could not be run. Installation was terminated. Copy-paste all text in this console window and send it to peter@addaxdatascience.com for further support." | wtee -a "%LOG_FILE%" & cmd /k & exit )
call %EA_CONDA_EXE% env create --name ecoassistcondaenv-base --file envs\environment-detector.yml || ( echo "There was an error trying to execute the conda command. Installation was terminated. Copy-paste all text in this console window and send it to peter@addaxdatascience.com for further support." & cmd /k & exit )
cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Copy-paste all text in this console window and send it to peter@addaxdatascience.com for further support." | wtee -a "%LOG_FILE%" & cmd /k & exit )
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
@REM "%EA_PIP_EXE_BASE%" install tensorboard==2.4.1
@REM "%EA_PIP_EXE_BASE%" install thop==0.1.1.post2209072238
@REM "%EA_PIP_EXE_BASE%" install protobuf==3.20.1
@REM "%EA_PIP_EXE_BASE%" install setuptools==65.5.1
"%EA_PIP_EXE_BASE%" install numpy==1.23.4
call %EA_CONDA_EXE% deactivate

@REM create and log dedicated environment for pytorch classification
call %EA_CONDA_EXE% create -n ecoassistcondaenv-pytorch python=3.8 -y
call activate ecoassistcondaenv-pytorch
call %EA_CONDA_EXE% install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia -y
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
call %EA_CONDA_EXE% deactivate

@REM create and log dedicated environment for tensorflow classification
call %EA_CONDA_EXE% env create --file EcoAssist\classification_utils\envs\tensorflow-linux-windows.yml

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
