@REM ### Windows commands to execute classify_detections.py script in different conda environment
@REM ### Peter van Lunteren, 9 Oct 2023 (latest edit)

@REM set echo settings
echo off
@setlocal EnableDelayedExpansion

@REM set EcoAssist_files
set LOCATION_ECOASSIST_FILES=%1
set PATH=%PATH%;%LOCATION_ECOASSIST_FILES%

@REM fetch conda install path and set cmds
set PATH_TO_CONDA_INSTALLATION_TXT_FILE=%LOCATION_ECOASSIST_FILES%\EcoAssist\logfiles\path_to_conda_installation.txt
FOR /F "tokens=* USEBACKQ" %%F IN (`type "%PATH_TO_CONDA_INSTALLATION_TXT_FILE%"`) DO ( SET PATH_TO_CONDA_INSTALLATION=%%F)
call "%PATH_TO_CONDA_INSTALLATION%\Scripts\activate.bat" "%PATH_TO_CONDA_INSTALLATION%"

@REM check if conda install is mambaforge and set conda command accordingly
for %%f in ("%PATH_TO_CONDA_INSTALLATION%") do set "FOLDER_NAME=%%~nxf"
if "%FOLDER_NAME%" == "mambaforge" ( set EA_CONDA_EXE=mamba ) else ( set EA_CONDA_EXE=conda )

@REM change directory
cd "%LOCATION_ECOASSIST_FILES%" || ( cmd /k & exit )

@REM activate dedicated environment
call %EA_CONDA_EXE% deactivate
call %EA_CONDA_EXE% activate ecoassistcondaenv-yolov8

@REM add gits to PYTHONPATH
set PYTHONPATH=%LOCATION_ECOASSIST_FILES%\cameratraps\classification

@REM run script
set CLS_MODEL_FILE=%2
set CLS_JSON_FILE=%3
set CLS_THRESH=%4
set CLS_TEMP_FRAME_FOLDER=%5
python %LOCATION_ECOASSIST_FILES%\EcoAssist\classify_detections.py %CLS_MODEL_FILE% %CLS_JSON_FILE% %CLS_THRESH% %LOCATION_ECOASSIST_FILES% %CLS_TEMP_FRAME_FOLDER%

@REM activate ecoassistcondaenv again
call %EA_CONDA_EXE% deactivate
call %EA_CONDA_EXE% activate ecoassistcondaenv
