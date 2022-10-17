@REM ### Windows commands to open the EcoAssist application https://github.com/PetervanLunteren/EcoAssist
@REM ### Peter van Lunteren, 17 october 2022

@REM # set echo settings
echo off
@setlocal EnableDelayedExpansion

@REM # set path voor ecoassist root dir and add to PATH
set LOCATION_ECOASSIST_FILES=%ProgramFiles%\EcoAssist_files
set PATH=%PATH%;%LOCATION_ECOASSIST_FILES%

@REM # set log file and delete the last one
set LOG_FILE=%LOCATION_ECOASSIST_FILES%\EcoAssist\logfiles\session_log.txt
if exist "%LOG_FILE%" del /F "%LOG_FILE%"

@REM # log the start of the session
set START_DATE=%date% %time%
echo EcoAssist session started at %START_DATE% > "%LOG_FILE%"

@REM # change directory
cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Please send an email to contact@pvanlunteren.com for assistance. Press any key to close this window." >> "%LOG_FILE%" & PAUSE>nul & EXIT )

@REM # locate conda
set PATH_TO_CONDA_INSTALLATION_TXT_FILE=%LOCATION_ECOASSIST_FILES%\EcoAssist\logfiles\path_to_conda_installation.txt
FOR /F "tokens=* USEBACKQ" %%F IN (`type "%PATH_TO_CONDA_INSTALLATION_TXT_FILE%"`) DO ( SET PATH_TO_ANACONDA=%%F)
echo Path to conda as imported from "%PATH_TO_CONDA_INSTALLATION_TXT_FILE%" is: "%PATH_TO_ANACONDA%" >> "%LOG_FILE%"

@REM # activate anaconda so that we can use it in a batch script
call "%PATH_TO_ANACONDA%\Scripts\activate.bat" "%PATH_TO_ANACONDA%"
echo Anaconda activated >> "%LOG_FILE%"

@REM # activate environment
call conda activate ecoassistcondaenv
echo conda environment activated >> "%LOG_FILE%"
call conda info --envs >> "%LOG_FILE%"

@REM # add gits to PYTHONPATH
set PYTHONPATH=%PYTHONPATH%;%LOCATION_ECOASSIST_FILES%;%LOCATION_ECOASSIST_FILES%\cameratraps;%LOCATION_ECOASSIST_FILES%\ai4eutils;%LOCATION_ECOASSIST_FILES%\yolov5;%LOCATION_ECOASSIST_FILES%\EcoAssist
echo PYHTONPATH : %PYTHONPATH% >> "%LOG_FILE%"

@REM # add python exe to beginning of PATH
set PATH=%PATH_TO_PYTHON%;%PATH%
echo PATH : %PATH% >> "%LOG_FILE%"

@REM # check python version
python -V >> "%LOG_FILE%"

@REM # run script
echo Opening EcoAssist now... >> "%LOG_FILE%"
python EcoAssist\EcoAssist_GUI.py 2>&1 >> "%LOG_FILE%"

@REM # timestamp the end of session
set END_DATE=%date% %time%
echo EcoAssist session ended at %END_DATE% >> "%LOG_FILE%"