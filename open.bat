@REM ### Windows commands to open the EcoAssist application https://github.com/PetervanLunteren/EcoAssist
@REM ### Peter van Lunteren, 14 May 2023 (latest edit)

@REM set echo settings
echo off
@setlocal EnableDelayedExpansion

@REM find location
set ECOASSIST_DRIVE=%~d0
set ECOASSIST_PREFIX=%~dp0
set ECOASSIST_PREFIX=%ECOASSIST_PREFIX:\EcoAssist_files\EcoAssist\=%
set ECOASSIST_PREFIX=%ECOASSIST_PREFIX:\ECOASS~1\ECOASS~1\=%
set ECOASSIST_PREFIX=%ECOASSIST_PREFIX:\ECOASS~2\ECOASS~1\=%
set ECOASSIST_PREFIX=%ECOASSIST_PREFIX:\ECOASS~3\ECOASS~1\=%

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

@REM fetch conda install path and set cmds
set PATH_TO_CONDA_INSTALLATION_TXT_FILE=%LOCATION_ECOASSIST_FILES%\EcoAssist\logfiles\path_to_conda_installation.txt
FOR /F "tokens=* USEBACKQ" %%F IN (`type "%PATH_TO_CONDA_INSTALLATION_TXT_FILE%"`) DO ( SET PATH_TO_CONDA_INSTALLATION=%%F)
echo Path to conda as imported from "%PATH_TO_CONDA_INSTALLATION_TXT_FILE%" is: "%PATH_TO_CONDA_INSTALLATION%"

@REM check if conda install is mambaforge and set conda command accordingly
for %%f in ("%PATH_TO_CONDA_INSTALLATION%") do set "FOLDER_NAME=%%~nxf"
if "%FOLDER_NAME%" == "mambaforge" ( set EA_CONDA_EXE=mamba ) else ( set EA_CONDA_EXE=conda )

@REM fetch git install path and set cmds
set PATH_TO_GIT_INSTALLATION_TXT_FILE=%LOCATION_ECOASSIST_FILES%\EcoAssist\logfiles\path_to_git_installation.txt
FOR /F "tokens=* USEBACKQ" %%F IN (`type "%PATH_TO_GIT_INSTALLATION_TXT_FILE%"`) DO ( SET PATH_TO_GIT_INSTALLATION=%%F)
echo Path to git as imported from "%PATH_TO_GIT_INSTALLATION_TXT_FILE%" is: "%PATH_TO_GIT_INSTALLATION%"
set PATH=%PATH_TO_GIT_INSTALLATION%\cmd;%PATH%
set GIT_PYTHON_GIT_EXECUTABLE=%PATH_TO_GIT_INSTALLATION%\cmd\git.exe

@REM change directory
cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Copy-paste this output and send it to peter@addaxdatascience.com for further support." & cmd /k & exit )

@REM set log file and delete the last one
set LOG_FILE=%LOCATION_ECOASSIST_FILES%\EcoAssist\logfiles\session_log.txt
if exist "%LOG_FILE%" del /F "%LOG_FILE%"

@REM log the start of the session
set START_DATE=%date% %time%
echo EcoAssist session started at %START_DATE% > "%LOG_FILE%"

@REM activate environment
call "%PATH_TO_CONDA_INSTALLATION%\Scripts\activate.bat" "%PATH_TO_CONDA_INSTALLATION%"
call %EA_CONDA_EXE% activate ecoassistcondaenv-base || ( echo "There was an error trying to execute the conda command. Please get in touch with the developer." & cmd /k & exit )
call %EA_CONDA_EXE% info --envs >> "%LOG_FILE%" || ( echo "There was an error trying to execute the conda command. Please get in touch with the developer." & cmd /k & exit )

@REM add gits to PYTHONPATH
set PYTHONPATH=%LOCATION_ECOASSIST_FILES%;%LOCATION_ECOASSIST_FILES%\cameratraps;%LOCATION_ECOASSIST_FILES%\ai4eutils;%LOCATION_ECOASSIST_FILES%\yolov5;%LOCATION_ECOASSIST_FILES%\EcoAssist;%LOCATION_ECOASSIST_FILES%\labelImg;%PYTHONPATH%
echo PYTHONPATH : %PYTHONPATH% >> "%LOG_FILE%"

@REM add python.exe and site packages to PATH
set PATH=%PATH_TO_CONDA_INSTALLATION%\envs\ecoassistcondaenv-base;%PATH_TO_CONDA_INSTALLATION%\envs\ecoassistcondaenv-base\lib\python3.8\site-packages;%PATH%
echo PATH : %PATH% >> "%LOG_FILE%"

@REM check python version
python -V >> "%LOG_FILE%"
where python >> "%LOG_FILE%"

@REM run script and check if executed in debug mode
echo Opening EcoAssist now... >> "%LOG_FILE%"
if "%1" == "debug" (
    python EcoAssist\EcoAssist_GUI.py
    ) else (
    python EcoAssist\EcoAssist_GUI.py 2>&1 >> "%LOG_FILE%"
    )

@REM timestamp the end of session
set END_DATE=%date% %time%
echo EcoAssist session ended at %END_DATE% >> "%LOG_FILE%"
