@REM ### Windows commands to open the EcoAssist application https://github.com/PetervanLunteren/EcoAssist
@REM ### Peter van Lunteren, 2 May 2023 (latest edit)

@REM set echo settings
echo off
@setlocal EnableDelayedExpansion

@REM find location
set ECOASSIST_DRIVE=%~d0
set ECOASSIST_PREFIX=%~dp0
set ECOASSIST_PREFIX=%ECOASSIST_PREFIX:\EcoAssist_files\EcoAssist\=%

@REM check if installed in program files
if "%ECOASSIST_PREFIX%"=="%ProgramFiles%" (
    goto check_permissions
) else (
    goto skip_permissions
)

@REM check for admin rights and prompt for password if needed
:check_permissions
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if '%errorlevel%' NEQ '0' (
    echo Requesting administrative privileges...
    goto UACPrompt
) else ( goto gotAdmin )
:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    set params = %*:"=""
    echo UAC.ShellExecute "cmd.exe", "/c %~s0 %params%", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    del "%temp%\getadmin.vbs"
    exit /B
:gotAdmin
    pushd "%CD%"
    CD /D "%~dp0"

@REM begin opening EcoAssist
:skip_permissions

@REM set EcoAssist_files
set LOCATION_ECOASSIST_FILES=%ECOASSIST_PREFIX%\EcoAssist_files
set PATH=%PATH%;%LOCATION_ECOASSIST_FILES%

@REM set automatical git install as default
set GIT_DIRECTORY=%LOCATION_ECOASSIST_FILES%\git4windows

@REM and change if git is already working
git --version || goto skip_git_exe
for /f %%i in ('where git') do set GIT_DIRECTORY=%%i
set GIT_DIRECTORY=%GIT_DIRECTORY:\cmd\git.exe=%
:skip_git_exe

@REM change directory
cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Copy-paste this output and send it to petervanlunteren@hotmail.com for further support." & cmd /k & exit )

@REM set log file and delete the last one
set LOG_FILE=%LOCATION_ECOASSIST_FILES%\EcoAssist\logfiles\session_log.txt
if exist "%LOG_FILE%" del /F "%LOG_FILE%"

@REM log the start of the session
set START_DATE=%date% %time%
echo EcoAssist session started at %START_DATE% > "%LOG_FILE%"

@REM add path to git to PATH
set PATH=%GIT_DIRECTORY%\cmd;%PATH%
set GIT_PYTHON_GIT_EXECUTABLE=%GIT_DIRECTORY%\cmd\git.exe

@REM check if user used a manual anaconda install
set PATH_TO_CONDA_INSTALLATION_TXT_FILE=%LOCATION_ECOASSIST_FILES%\EcoAssist\logfiles\path_to_conda_installation.txt
if exist "%PATH_TO_CONDA_INSTALLATION_TXT_FILE%" (
    echo user used a manual anaconda install >> "%LOG_FILE%"
    FOR /F "tokens=* USEBACKQ" %%F IN (`type "%PATH_TO_CONDA_INSTALLATION_TXT_FILE%"`) DO ( SET CONDA_DIRECTORY=%%F)
    echo Path to conda as imported from "%PATH_TO_CONDA_INSTALLATION_TXT_FILE%" is: "!CONDA_DIRECTORY!" >> "%LOG_FILE%"
    set PATH=!CONDA_DIRECTORY!\Scripts;%PATH%
    call "!CONDA_DIRECTORY!\Scripts\activate.bat" "!CONDA_DIRECTORY!"
)

@REM activate conda if not active yet
call conda --version && set conda_installed=True || set conda_installed=False
if %conda_installed%==False (
    echo conda not yet working >> "%LOG_FILE%"
    echo trying automatic miniconda install >> "%LOG_FILE%"
    set PATH=%LOCATION_ECOASSIST_FILES%\miniconda\Scripts;%PATH%
    call "%LOCATION_ECOASSIST_FILES%\miniconda\Scripts\activate.bat" "%LOCATION_ECOASSIST_FILES%\miniconda"
) else (
    echo conda is functioning >> "%LOG_FILE%"
)

@REM activate environment
call conda activate ecoassistcondaenv
echo conda environment activated >> "%LOG_FILE%"
call conda info --envs >> "%LOG_FILE%"

@REM add gits to PYTHONPATH
set PYTHONPATH=%LOCATION_ECOASSIST_FILES%;%LOCATION_ECOASSIST_FILES%\cameratraps;%LOCATION_ECOASSIST_FILES%\ai4eutils;%LOCATION_ECOASSIST_FILES%\yolov5;%LOCATION_ECOASSIST_FILES%\EcoAssist;%LOCATION_ECOASSIST_FILES%\labelImg;%PYTHONPATH%
echo PYTHONPATH : %PYTHONPATH% >> "%LOG_FILE%"

@REM check python version
python -V >> "%LOG_FILE%"
where python >> "%LOG_FILE%"

@REM run script
echo Opening EcoAssist now... >> "%LOG_FILE%"
python EcoAssist\EcoAssist_GUI.py 2>&1 >> "%LOG_FILE%"

@REM timestamp the end of session
set END_DATE=%date% %time%
echo EcoAssist session ended at %END_DATE% >> "%LOG_FILE%"