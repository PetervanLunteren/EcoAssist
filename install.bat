@REM ### Windows install commands for the EcoAssist application https://github.com/PetervanLunteren/EcoAssist
@REM ### Peter van Lunteren, 3 May 2023 (latest edit)

@REM set echo settings
echo off
@setlocal EnableDelayedExpansion

@REM print header
echo:
echo ^|--------------------------- ECOASSIST INSTALLATION ---------------------------^|
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
        set ECOASSIST_PREFIX=%homedrive%%homepath%
        set ECOASSIST_DRIVE=%homedrive%
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
    echo Removed                                '%NO_ADMIN_INSTALL%'
)
set ADMIN_INSTALL=%ProgramFiles%\EcoAssist_files
if exist "%ADMIN_INSTALL%" (
    rd /q /s "%ADMIN_INSTALL%"
    echo Removed                                '%ADMIN_INSTALL%'
)
set CURRENT_INSTALL=%LOCATION_ECOASSIST_FILES%
if exist "%CURRENT_INSTALL%" (
    rd /q /s "%CURRENT_INSTALL%"
    echo Removed                                '%CURRENT_INSTALL%'
)

@REM make dir
if not exist "%LOCATION_ECOASSIST_FILES%" (
    mkdir "%LOCATION_ECOASSIST_FILES%" || ( echo "Cannot create %LOCATION_ECOASSIST_FILES%. Copy-paste this output and send it to petervanlunteren@hotmail.com for further support." & cmd /k & exit )
    attrib +h "%LOCATION_ECOASSIST_FILES%"
    echo Created empty dir                      '%LOCATION_ECOASSIST_FILES%'
)

@REM change directory
cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Copy-paste this output and send it to petervanlunteren@hotmail.com for further support." & cmd /k & exit )

@REM set conda cmds
:set_conda_install
echo:
set /p PATH_TO_CONDA_INSTALLATION=Enter path to conda installation ^(for example C:\ProgramData\anaconda3^): 
set PATH_TO_CONDA_INSTALLATION=%PATH_TO_CONDA_INSTALLATION:"=%
set PATH_TO_CONDA_INSTALLATION=%PATH_TO_CONDA_INSTALLATION:'=%
IF %PATH_TO_CONDA_INSTALLATION:~-1%==\ SET PATH_TO_CONDA_INSTALLATION=%PATH_TO_CONDA_INSTALLATION:~0,-1%
echo Path to conda is defined as:           '%PATH_TO_CONDA_INSTALLATION%'
if not exist "%PATH_TO_CONDA_INSTALLATION%\Scripts\activate.bat" ( echo '%PATH_TO_CONDA_INSTALLATION%\Scripts\activate.bat' does not exist. Enter a path to a valid conda installation. & goto set_conda_install )
echo 1
set PATH=%PATH_TO_CONDA_INSTALLATION%;%PATH%
echo 2
set PATH=%PATH_TO_CONDA_INSTALLATION%\Scripts;%PATH%
echo 3
set PATH=%PATH_TO_CONDA_INSTALLATION%\Library\bin;%PATH%
echo 4
echo:
echo PATH: %PATH%
echo:
echo 5
source "%PATH_TO_CONDA_INSTALLATION%\etc\profile.d\conda.sh"
echo 6
echo %PATH_TO_CONDA_INSTALLATION%> "%LOCATION_ECOASSIST_FILES%\path_to_conda_installation.txt"
echo 7
call "%PATH_TO_CONDA_INSTALLATION%\Scripts\activate.bat" "%PATH_TO_CONDA_INSTALLATION%"
echo 8
set EA_PIP_EXE=%PATH_TO_CONDA_INSTALLATION%\envs\ecoassistcondaenv\Scripts\pip3
echo 9


@REM set git cmds
:set_git_install
echo:
set /p PATH_TO_GIT_INSTALLATION=Enter path to git installation ^(for example C:\Program Files\Git^): 
set PATH_TO_GIT_INSTALLATION=%PATH_TO_GIT_INSTALLATION:"=%
set PATH_TO_GIT_INSTALLATION=%PATH_TO_GIT_INSTALLATION:'=%
IF %PATH_TO_GIT_INSTALLATION:~-1%==\ SET PATH_TO_GIT_INSTALLATION=%PATH_TO_GIT_INSTALLATION:~0,-1%
echo Path to git is defined as:             '%PATH_TO_GIT_INSTALLATION%'
if not exist "%PATH_TO_GIT_INSTALLATION%\cmd\git.exe" ( echo '%PATH_TO_GIT_INSTALLATION%\cmd\git.exe' does not exist. Enter a path to a valid git installation. & goto set_git_install )
echo %PATH_TO_GIT_INSTALLATION%> "%LOCATION_ECOASSIST_FILES%\path_to_git_installation.txt"
set EA_GIT_EXE=%PATH_TO_GIT_INSTALLATION%\cmd\git.exe

@REM install and test wtee
curl -OL https://storage.googleapis.com/google-code-archive-downloads/v2/code.google.com/wintee/wtee.exe
echo hello world | wtee -a hello-world.txt || ( echo "Looks like something is blocking your downloads... This is probably due to the settings of your device. Try again with your antivirus, VPN, proxy or any other protection software disabled. Email petervanlunteren@hotmail.com if you need any further assistance." & cmd /k & exit )
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

@REM clone EcoAssist git if not present
if exist "%LOCATION_ECOASSIST_FILES%\EcoAssist\" (
    echo Dir EcoAssist already exists! Skipping this step. | wtee -a "%LOG_FILE%"
) else (
    echo Dir EcoAssist does not exists! Clone repo... | wtee -a "%LOG_FILE%"
    cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Copy-paste this output and send it to petervanlunteren@hotmail.com for further support." | wtee -a "%LOG_FILE%" & cmd /k & exit )
    "%EA_GIT_EXE%" clone https://github.com/PetervanLunteren/EcoAssist.git
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
    cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Copy-paste this output and send it to petervanlunteren@hotmail.com for further support." | wtee -a "%LOG_FILE%" & cmd /k & exit )
    "%EA_GIT_EXE%" clone https://github.com/ecologize/cameratraps
    cd "%LOCATION_ECOASSIST_FILES%\cameratraps" || ( echo "Could not change directory to cameratraps. Command could not be run. Installation was terminated. Copy-paste this output and send it to petervanlunteren@hotmail.com for further support." | wtee -a "%LOG_FILE%" & cmd /k & exit )
    "%EA_GIT_EXE%" checkout 6223b48b520abd6ad7fe868ea16ea58f75003595
    cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Copy-paste this output and send it to petervanlunteren@hotmail.com for further support." | wtee -a "%LOG_FILE%" & cmd /k & exit )
    @REM check the size of the folder
    dir "%LOCATION_ECOASSIST_FILES%\cameratraps" | wtee -a "%LOG_FILE%"
)

@REM clone ai4eutils git if not present
if exist "%LOCATION_ECOASSIST_FILES%\ai4eutils\" (
    echo Dir ai4eutils already exists! Skipping this step. | wtee -a "%LOG_FILE%"
) else (
    echo Dir ai4eutils does not exists! Clone repo... | wtee -a "%LOG_FILE%"
    cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Copy-paste this output and send it to petervanlunteren@hotmail.com for further support." | wtee -a "%LOG_FILE%" & cmd /k & exit )
    "%EA_GIT_EXE%" clone https://github.com/Microsoft/ai4eutils
    cd "%LOCATION_ECOASSIST_FILES%\ai4eutils" || ( echo "Could not change directory to ai4eutils. Command could not be run. Installation was terminated. Copy-paste this output and send it to petervanlunteren@hotmail.com for further support." | wtee -a "%LOG_FILE%" & cmd /k & exit )
    "%EA_GIT_EXE%" checkout 1bbbb8030d5be3d6488ac898f9842d715cdca088
    cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Copy-paste this output and send it to petervanlunteren@hotmail.com for further support." | wtee -a "%LOG_FILE%" & cmd /k & exit )
    @REM check the size of the folder
    dir "%LOCATION_ECOASSIST_FILES%\ai4eutils" | wtee -a "%LOG_FILE%"
)

@REM clone yolov5 git if not present
if exist "%LOCATION_ECOASSIST_FILES%\yolov5\" (
    echo Dir yolov5 already exists! Skipping this step. | wtee -a "%LOG_FILE%"
) else (
    echo Dir yolov5 does not exists! Clone repo... | wtee -a "%LOG_FILE%"
    cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Copy-paste this output and send it to petervanlunteren@hotmail.com for further support." | wtee -a "%LOG_FILE%" & cmd /k & exit )
    "%EA_GIT_EXE%" clone https://github.com/ultralytics/yolov5.git
    @REM checkout will happen dynamically during runtime with switch_yolov5_git_to()
    @REM check the size of the folder
    dir "%LOCATION_ECOASSIST_FILES%\yolov5" | wtee -a "%LOG_FILE%"
)

@REM clone labelImg git if not present
if exist "%LOCATION_ECOASSIST_FILES%\labelImg\" (
    echo Dir labelImg already exists! Skipping this step. | wtee -a "%LOG_FILE%"
) else (
    echo Dir labelImg does not exists! Clone repo... | wtee -a "%LOG_FILE%"
    cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Copy-paste this output and send it to petervanlunteren@hotmail.com for further support." | wtee -a "%LOG_FILE%" & cmd /k & exit )
    "%EA_GIT_EXE%" clone https://github.com/tzutalin/labelImg.git
    cd "%LOCATION_ECOASSIST_FILES%\labelImg" || ( echo "Could not change directory to labelImg. Command could not be run. Installation was terminated. Copy-paste this output and send it to petervanlunteren@hotmail.com for further support." | wtee -a "%LOG_FILE%" & cmd /k & exit )
    "%EA_GIT_EXE%" checkout 276f40f5e5bbf11e84cfa7844e0a6824caf93e11
    cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Copy-paste this output and send it to petervanlunteren@hotmail.com for further support." | wtee -a "%LOG_FILE%" & cmd /k & exit )
    @REM check the size of the folder
    dir "%LOCATION_ECOASSIST_FILES%\labelImg" | wtee -a "%LOG_FILE%"
)

@REM download the md_v5a.0.0.pt model if not present
if exist "%LOCATION_ECOASSIST_FILES%\pretrained_models\md_v5a.0.0.pt" (
    echo "File md_v5a.0.0.pt already exists! Skipping this step." | wtee -a "%LOG_FILE%"
) else (
    echo "File md_v5a.0.0.pt does not exists! Downloading file..." | wtee -a "%LOG_FILE%"
    if not exist "%LOCATION_ECOASSIST_FILES%\pretrained_models" mkdir "%LOCATION_ECOASSIST_FILES%\pretrained_models"
    cd "%LOCATION_ECOASSIST_FILES%\pretrained_models" || ( echo "Could not change directory to pretrained_models. Command could not be run. Installation was terminated. Copy-paste this output and send it to petervanlunteren@hotmail.com for further support." | wtee -a "%LOG_FILE%" & cmd /k & exit )
    curl --keepalive -OL https://github.com/ecologize/CameraTraps/releases/download/v5.0/md_v5a.0.0.pt
    cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Copy-paste this output and send it to petervanlunteren@hotmail.com for further support." | wtee -a "%LOG_FILE%" & cmd /k & exit )
    @REM check the size of the folder
    dir "%LOCATION_ECOASSIST_FILES%\pretrained_models" | wtee -a "%LOG_FILE%"
)

@REM download the md_v5b.0.0.pt model if not present
if exist "%LOCATION_ECOASSIST_FILES%\pretrained_models\md_v5b.0.0.pt" (
    echo "File md_v5b.0.0.pt already exists! Skipping this step." | wtee -a "%LOG_FILE%"
) else (
    echo "File md_v5b.0.0.pt does not exists! Downloading file..." | wtee -a "%LOG_FILE%"
    if not exist "%LOCATION_ECOASSIST_FILES%\pretrained_models" mkdir "%LOCATION_ECOASSIST_FILES%\pretrained_models"
    cd "%LOCATION_ECOASSIST_FILES%\pretrained_models" || ( echo "Could not change directory to pretrained_models. Command could not be run. Installation was terminated. Copy-paste this output and send it to petervanlunteren@hotmail.com for further support." | wtee -a "%LOG_FILE%" & cmd /k & exit )
    curl --keepalive -OL https://github.com/ecologize/CameraTraps/releases/download/v5.0/md_v5b.0.0.pt
    cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Copy-paste this output and send it to petervanlunteren@hotmail.com for further support." | wtee -a "%LOG_FILE%" & cmd /k & exit )
    @REM check the size of the folder
    dir "%LOCATION_ECOASSIST_FILES%\pretrained_models" | wtee -a "%LOG_FILE%"
)

@REM create conda env and install packages for MegaDetector
echo 10
call conda env remove -n ecoassistcondaenv
echo 11
cd "%LOCATION_ECOASSIST_FILES%\cameratraps" || ( echo "Could not change directory to cameratraps. Command could not be run. Installation was terminated. Copy-paste this output and send it to petervanlunteren@hotmail.com for further support." | wtee -a "%LOG_FILE%" & cmd /k & exit )
echo 12
call conda env create --name ecoassistcondaenv --file environment-detector.yml
echo 13
cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Copy-paste this output and send it to petervanlunteren@hotmail.com for further support." | wtee -a "%LOG_FILE%" & cmd /k & exit )
echo 14
call activate ecoassistcondaenv
echo 15

@REM install additional packages for labelImg
"%EA_PIP_EXE%" install pyqt5==5.15.2 lxml

@REM install additional packages for EcoAssist
"%EA_PIP_EXE%" install bounding_box

@REM install additional packages for yolov5
"%EA_PIP_EXE%" install GitPython==3.1.30
"%EA_PIP_EXE%" install tensorboard==2.4.1
"%EA_PIP_EXE%" install thop==0.1.1.post2209072238
"%EA_PIP_EXE%" install protobuf==3.20.1
"%EA_PIP_EXE%" install setuptools==65.5.1
"%EA_PIP_EXE%" install numpy==1.23.4

@REM log env info
call conda info --envs
call conda info --envs >> "%LOG_FILE%"
call conda list >> "%LOG_FILE%"
"%EA_PIP_EXE%" freeze >> "%LOG_FILE%"

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
