@REM ### Windows install commands for the EcoAssist application https://github.com/PetervanLunteren/EcoAssist
@REM ### Peter van Lunteren, 21 Apr 2023 (latest edit)

@REM set echo settings
echo off
@setlocal EnableDelayedExpansion

@REM ask user input
echo By default, EcoAssist will be installed in your userfolder (%homedrive%%homepath%) to avoid requiring admin rights. Do you want to install it somewhere else?
set /p INPUT=Enter [Y]es or [N]o: 
If /I "%INPUT%"=="Y" goto set_custom_location
If /I "%INPUT%"=="y" goto set_custom_location
If /I "%INPUT%"=="Ye" goto set_custom_location
If /I "%INPUT%"=="ye" goto set_custom_location
If /I "%INPUT%"=="Yes" goto set_custom_location
If /I "%INPUT%"=="yes" goto set_custom_location
goto skip_custom_location

@REM ask location and remove trailing \ and quotation marks
:set_custom_location
set /p CUSTOM_ECOASSIST_LOCATION=Set path (for example C:\some_folder): 
set CUSTOM_ECOASSIST_LOCATION=%CUSTOM_ECOASSIST_LOCATION:"=%
IF %CUSTOM_ECOASSIST_LOCATION:~-1%==\ SET CUSTOM_ECOASSIST_LOCATION=%CUSTOM_ECOASSIST_LOCATION:~0,-1%
:skip_custom_location

@REM set install location
if defined CUSTOM_ECOASSIST_LOCATION (
    echo CUSTOM_ECOASSIST_LOCATION is set: %CUSTOM_ECOASSIST_LOCATION%
    set ECOASSIST_DRIVE=%CUSTOM_ECOASSIST_LOCATION:~0,2%
    set ECOASSIST_PREFIX=%CUSTOM_ECOASSIST_LOCATION%
) else (
    echo CUSTOM_ECOASSIST_LOCATION is not set. Installing in default location: %homedrive%%homepath%
    set ECOASSIST_DRIVE=%homedrive%
    set ECOASSIST_PREFIX=%homedrive%%homepath%
)

@REM switch to install drive in case user executes this script from different drive
set SCRIPT_DRIVE=%~d0
echo Install script is located on drive: '%SCRIPT_DRIVE%'
echo EcoAssist will be installed on drive: '%ECOASSIST_DRIVE%'
%ECOASSIST_DRIVE%
echo Changed drive to: '%CD:~0,2%'

@REM timestamp the start of installation
set START_DATE=%date%%time%

@REM set variables
set LOCATION_ECOASSIST_FILES=%ECOASSIST_PREFIX%\EcoAssist_files
set PATH=%PATH%;"%LOCATION_ECOASSIST_FILES%"
set CONDA_DIRECTORY=%LOCATION_ECOASSIST_FILES%\miniconda
set ECOASSISTCONDAENV=%CONDA_DIRECTORY%\envs\ecoassistcondaenv
set PIP=%ECOASSISTCONDAENV%\Scripts\pip3
set HOMEBREW_DIR=%LOCATION_ECOASSIST_FILES%\homebrew
set GIT_DIRECTORY=%LOCATION_ECOASSIST_FILES%\git4windows
git --version && set git_installed=True || set git_installed=False

@REM set git executable
if !git_installed!==False (
    set EA_GIT_EXE=%GIT_DIRECTORY%\cmd\git.exe
) else (
    set EA_GIT_EXE=git
)

@REM delete previous installation of EcoAssist v4 or higher
if exist "%LOCATION_ECOASSIST_FILES%" (
    rd /q /s "%LOCATION_ECOASSIST_FILES%"
    echo Removed "%LOCATION_ECOASSIST_FILES%"
)

@REM make dir
if not exist "%LOCATION_ECOASSIST_FILES%" (
    mkdir "%LOCATION_ECOASSIST_FILES%" || ( echo "Cannot create %LOCATION_ECOASSIST_FILES%. Copy-paste this output or take a screenshot and send it to petervanlunteren@hotmail.com for further support." & cmd /k & exit )
    attrib +h "%LOCATION_ECOASSIST_FILES%"
    echo Created empty dir "%LOCATION_ECOASSIST_FILES%"
)

@REM change directory
cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Please send an email to contact@pvanlunteren.com for assistance. Press any key to close this window." & cmd /k & exit )

@REM install wtee to log information
curl -OL https://storage.googleapis.com/google-code-archive-downloads/v2/code.google.com/wintee/wtee.exe

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

@REM check if OS is 32 or 64 bit and set variable
reg Query "HKLM\Hardware\Description\System\CentralProcessor\0" | find /i "x86" > NUL && set OS_BITS=32 || set OS_BITS=64
if %OS_BITS%==32 echo This is an 32-bit operating system. | wtee -a "%LOG_FILE%"
if %OS_BITS%==64 echo This is an 64-bit operating system. | wtee -a "%LOG_FILE%"

@REM log system information
systeminfo | wtee -a "%LOG_FILE%"

@REM check if user is updating from v3 or lower (different location of EcoAssist_files)
set EA_OLD_DIR=%ProgramFiles%\EcoAssist_files
if exist "%EA_OLD_DIR%" (
    echo Updating from EcoAssist v3 or lower | wtee -a "%LOG_FILE%"

    @REM locate conda which was used for the install of v3 or lower and activate
    set PATH_TO_CONDA_INSTALLATION_TXT_FILE=%EA_OLD_DIR%\EcoAssist\logfiles\path_to_conda_installation.txt
    FOR /F "tokens=* USEBACKQ" %%F IN (`type "!PATH_TO_CONDA_INSTALLATION_TXT_FILE!"`) DO ( SET PATH_TO_ANACONDA=%%F)
    echo Path to conda as imported from "!PATH_TO_CONDA_INSTALLATION_TXT_FILE!" is: "!PATH_TO_ANACONDA!" | wtee -a "%LOG_FILE%"
    call !PATH_TO_ANACONDA!\Scripts\activate.bat !PATH_TO_ANACONDA!

    @REM remove old ecoassistcondaenv
    echo conda envs before deleting old ecoassistcondaenv >> "%LOG_FILE%"
    call conda info --envs >> "%LOG_FILE%"
    call conda env remove -n ecoassistcondaenv
    echo conda envs after deleting old ecoassistcondaenv >> "%LOG_FILE%"
    call conda info --envs >> "%LOG_FILE%"
    echo Removed conda environment from v3 or lower | wtee -a "%LOG_FILE%"

    @REM remove old files
    rd /q /s "%EA_OLD_DIR%"
    echo Removed EcoAssist_files from v3 or lower "%EA_OLD_DIR%" | wtee -a "%LOG_FILE%"
) else (
    echo Dir %EA_OLD_DIR% not present. No old files to remove. | wtee -a "%LOG_FILE%"
)

@REM install git if not already installed
if !git_installed!==False (
    echo Downloading git for windows now | wtee -a "%LOG_FILE%"
    curl -L -o git_for_windows.exe https://github.com/git-for-windows/git/releases/download/v2.38.0.windows.1/Git-2.38.0-%OS_BITS%-bit.exe
    echo Installing local version of git for windows... It will not interfere with any other existing versions of git. This may take some time... | wtee -a "%LOG_FILE%"
    start /wait "" git_for_windows.exe /VERYSILENT /NORESTART /DIR="%GIT_DIRECTORY%" /SUPPRESSMSGBOXES /NOCANCEL /CURRENTUSER /NOICONS /o:PathOption=BashOnly
    if exist git_for_windows.exe del git_for_windows.exe
) else (
    echo git is already installed and functioning | wtee -a "%LOG_FILE%"
)

@REM clone EcoAssist git if not present
if exist "%LOCATION_ECOASSIST_FILES%\EcoAssist\" (
    echo Dir EcoAssist already exists! Skipping this step. | wtee -a "%LOG_FILE%"
) else (
    echo Dir EcoAssist does not exists! Clone repo... | wtee -a "%LOG_FILE%"
    cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Please send an email to contact@pvanlunteren.com for assistance. Press any key to close this window." | wtee -a "%LOG_FILE%" & cmd /k & exit )
    !EA_GIT_EXE! clone https://github.com/PetervanLunteren/EcoAssist.git
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
echo Set oWS ^= WScript.CreateObject^("WScript.Shell"^) > "%LOCATION_ECOASSIST_FILES%\EcoAssist\logfiles\CreateShortcut.vbs"
echo sLinkFile ^= "%~dp0EcoAssist.lnk" >> "%LOCATION_ECOASSIST_FILES%\EcoAssist\logfiles\CreateShortcut.vbs"
echo Set oLink ^= oWS.CreateShortcut^(sLinkFile^) >> "%LOCATION_ECOASSIST_FILES%\EcoAssist\logfiles\CreateShortcut.vbs"
echo oLink.TargetPath ^= "%LOCATION_ECOASSIST_FILES%\EcoAssist\Windows_open_EcoAssist_shortcut.vbs" >> "%LOCATION_ECOASSIST_FILES%\EcoAssist\logfiles\CreateShortcut.vbs"
echo oLink.IconLocation ^= "%LOCATION_ECOASSIST_FILES%\EcoAssist\imgs\logo_small_bg.ico" >> "%LOCATION_ECOASSIST_FILES%\EcoAssist\logfiles\CreateShortcut.vbs"
echo oLink.Save >> "%LOCATION_ECOASSIST_FILES%\EcoAssist\logfiles\CreateShortcut.vbs"

@REM execute this .vbs file to create a shortcut with the EcoAssist logo
%SCRIPT_DRIVE% @REM switch to script drive
echo "Executing CreateShortcut.vbs now..." | wtee -a "%LOG_FILE%"
cscript "%LOCATION_ECOASSIST_FILES%\EcoAssist\logfiles\CreateShortcut.vbs"
%ECOASSIST_DRIVE% @REM back to installation drive
echo "Created EcoAssist.lnk" | wtee -a "%LOG_FILE%"

@REM clone cameratraps git if not present
if exist "%LOCATION_ECOASSIST_FILES%\cameratraps\" (
    echo Dir cameratraps already exists! Skipping this step. | wtee -a "%LOG_FILE%"
) else (
    echo Dir cameratraps does not exists! Clone repo... | wtee -a "%LOG_FILE%"
    cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Please send an email to contact@pvanlunteren.com for assistance. Press any key to close this window." | wtee -a "%LOG_FILE%" & cmd /k & exit )
    !EA_GIT_EXE! clone https://github.com/Microsoft/cameratraps
    cd "%LOCATION_ECOASSIST_FILES%\cameratraps" || ( echo "Could not change directory to cameratraps. Command could not be run. Installation was terminated. Please send an email to contact@pvanlunteren.com for assistance. Press any key to close this window." | wtee -a "%LOG_FILE%" & cmd /k & exit )
    !EA_GIT_EXE! checkout 6223b48b520abd6ad7fe868ea16ea58f75003595
    cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Please send an email to contact@pvanlunteren.com for assistance. Press any key to close this window." | wtee -a "%LOG_FILE%" & cmd /k & exit )
    @REM check the size of the folder
    dir "%LOCATION_ECOASSIST_FILES%\cameratraps" | wtee -a "%LOG_FILE%"
)

@REM clone ai4eutils git if not present
if exist "%LOCATION_ECOASSIST_FILES%\ai4eutils\" (
    echo Dir ai4eutils already exists! Skipping this step. | wtee -a "%LOG_FILE%"
) else (
    echo Dir ai4eutils does not exists! Clone repo... | wtee -a "%LOG_FILE%"
    cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Please send an email to contact@pvanlunteren.com for assistance. Press any key to close this window." | wtee -a "%LOG_FILE%" & cmd /k & exit )
    !EA_GIT_EXE! clone https://github.com/Microsoft/ai4eutils
    cd "%LOCATION_ECOASSIST_FILES%\ai4eutils" || ( echo "Could not change directory to ai4eutils. Command could not be run. Installation was terminated. Please send an email to contact@pvanlunteren.com for assistance. Press any key to close this window." | wtee -a "%LOG_FILE%" & cmd /k & exit )
    !EA_GIT_EXE! checkout 1bbbb8030d5be3d6488ac898f9842d715cdca088
    cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Please send an email to contact@pvanlunteren.com for assistance. Press any key to close this window." | wtee -a "%LOG_FILE%" & cmd /k & exit )
    @REM check the size of the folder
    dir "%LOCATION_ECOASSIST_FILES%\ai4eutils" | wtee -a "%LOG_FILE%"
)

@REM clone yolov5 git if not present
if exist "%LOCATION_ECOASSIST_FILES%\yolov5\" (
    echo Dir yolov5 already exists! Skipping this step. | wtee -a "%LOG_FILE%"
) else (
    echo Dir yolov5 does not exists! Clone repo... | wtee -a "%LOG_FILE%"
    cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Please send an email to contact@pvanlunteren.com for assistance. Press any key to close this window." | wtee -a "%LOG_FILE%" & cmd /k & exit )
    !EA_GIT_EXE! clone https://github.com/ultralytics/yolov5.git
    @REM checkout will happen dynamically during runtime with switch_yolov5_git_to()
    @REM check the size of the folder
    dir "%LOCATION_ECOASSIST_FILES%\yolov5" | wtee -a "%LOG_FILE%"
)

@REM clone labelImg git if not present
if exist "%LOCATION_ECOASSIST_FILES%\labelImg\" (
    echo Dir labelImg already exists! Skipping this step. | wtee -a "%LOG_FILE%"
) else (
    echo Dir labelImg does not exists! Clone repo... | wtee -a "%LOG_FILE%"
    cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Please send an email to contact@pvanlunteren.com for assistance. Press any key to close this window." | wtee -a "%LOG_FILE%" & cmd /k & exit )
    !EA_GIT_EXE! clone https://github.com/tzutalin/labelImg.git
    cd "%LOCATION_ECOASSIST_FILES%\labelImg" || ( echo "Could not change directory to labelImg. Command could not be run. Installation was terminated. Please send an email to contact@pvanlunteren.com for assistance. Press any key to close this window." | wtee -a "%LOG_FILE%" & cmd /k & exit )
    !EA_GIT_EXE! checkout 276f40f5e5bbf11e84cfa7844e0a6824caf93e11
    cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Please send an email to contact@pvanlunteren.com for assistance. Press any key to close this window." | wtee -a "%LOG_FILE%" & cmd /k & exit )
    @REM check the size of the folder
    dir "%LOCATION_ECOASSIST_FILES%\labelImg" | wtee -a "%LOG_FILE%"
)

@REM download the md_v5a.0.0.pt model if not present
if exist "%LOCATION_ECOASSIST_FILES%\pretrained_models\md_v5a.0.0.pt" (
    echo "File md_v5a.0.0.pt already exists! Skipping this step." | wtee -a "%LOG_FILE%"
) else (
    echo "File md_v5a.0.0.pt does not exists! Downloading file..." | wtee -a "%LOG_FILE%"
    if not exist "%LOCATION_ECOASSIST_FILES%\pretrained_models" mkdir "%LOCATION_ECOASSIST_FILES%\pretrained_models"
    cd "%LOCATION_ECOASSIST_FILES%\pretrained_models" || ( echo "Could not change directory to pretrained_models. Command could not be run. Installation was terminated. Please send an email to contact@pvanlunteren.com for assistance. Press any key to close this window." | wtee -a "%LOG_FILE%" & cmd /k & exit )
    curl --keepalive -OL https://github.com/microsoft/CameraTraps/releases/download/v5.0/md_v5a.0.0.pt
    cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Please send an email to contact@pvanlunteren.com for assistance. Press any key to close this window." | wtee -a "%LOG_FILE%" & cmd /k & exit )
    @REM check the size of the folder
    dir "%LOCATION_ECOASSIST_FILES%\pretrained_models" | wtee -a "%LOG_FILE%"
)

@REM download the md_v5b.0.0.pt model if not present
if exist "%LOCATION_ECOASSIST_FILES%\pretrained_models\md_v5b.0.0.pt" (
    echo "File md_v5b.0.0.pt already exists! Skipping this step." | wtee -a "%LOG_FILE%"
) else (
    echo "File md_v5b.0.0.pt does not exists! Downloading file..." | wtee -a "%LOG_FILE%"
    if not exist "%LOCATION_ECOASSIST_FILES%\pretrained_models" mkdir "%LOCATION_ECOASSIST_FILES%\pretrained_models"
    cd "%LOCATION_ECOASSIST_FILES%\pretrained_models" || ( echo "Could not change directory to pretrained_models. Command could not be run. Installation was terminated. Please send an email to contact@pvanlunteren.com for assistance. Press any key to close this window." | wtee -a "%LOG_FILE%" & cmd /k & exit )
    curl --keepalive -OL https://github.com/microsoft/CameraTraps/releases/download/v5.0/md_v5b.0.0.pt
    cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Please send an email to contact@pvanlunteren.com for assistance. Press any key to close this window." | wtee -a "%LOG_FILE%" & cmd /k & exit )
    @REM check the size of the folder
    dir "%LOCATION_ECOASSIST_FILES%\pretrained_models" | wtee -a "%LOG_FILE%"
)

@REM install miniconda
echo Downloading miniconda... | wtee -a "%LOG_FILE%"
if %OS_BITS%==32 (curl --keepalive -L -o miniconda.exe https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86.exe)
if %OS_BITS%==64 (curl --keepalive -L -o miniconda.exe https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe)
echo Installing local version of miniconda... It will not interfere with any other existing versions of conda. This may take some time... | wtee -a "%LOG_FILE%"
start /wait "" miniconda.exe /InstallationType=JustMe /AddToPath=0 /RegisterPython=0 /S /D=%CONDA_DIRECTORY%
if exist miniconda.exe del /F miniconda.exe
set PATH="%CONDA_DIRECTORY%";"%CONDA_DIRECTORY%\Scripts";%PATH%
call "%CONDA_DIRECTORY%\Scripts\activate.bat" "%CONDA_DIRECTORY%"

@REM create conda env and install packages required for MegaDetector
call conda env create --name ecoassistcondaenv --file "%LOCATION_ECOASSIST_FILES%\cameratraps\environment-detector.yml"
call activate %ECOASSISTCONDAENV%

@REM install additional packages for labelImg
"%PIP%" install pyqt5==5.15.2 lxml

@REM install additional packages for EcoAssist
"%PIP%" install bounding_box

@REM install additional packages for yolov5
"%PIP%" install GitPython==3.1.30
"%PIP%" install tensorboard==2.4.1
"%PIP%" install thop==0.1.1.post2209072238
"%PIP%" install protobuf==3.20.1
"%PIP%" install setuptools==65.5.1
"%PIP%" install numpy==1.23.4

@REM log env info
call conda info --envs >> "%LOG_FILE%"
call conda list >> "%LOG_FILE%"
"%PIP%" freeze >> "%LOG_FILE%"

@REM log folder structure
dir "%LOCATION_ECOASSIST_FILES%" | wtee -a "%LOG_FILE%"

@REM timestamp the end of installation
set END_DATE=%date%%time%
echo Installation ended at %END_DATE% | wtee -a "%LOG_FILE%"

@REM move txt files to log_folder if they are in EcoAssist_files
if exist "%LOCATION_ECOASSIST_FILES%\installation_log.txt" ( move /Y "%LOCATION_ECOASSIST_FILES%\installation_log.txt" "%LOCATION_ECOASSIST_FILES%\EcoAssist\logfiles" )

@REM end process
echo THE INSTALLATION IS DONE^^! You can close this window now and proceed to open EcoAssist by double clicking the EcoAssist.lnk file in the same folder as this installation file ^(so probably Downloads^).

@REM keep console open after finishing
cmd /k & exit
