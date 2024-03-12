@REM ### Windows commands to execute classify_detections.py script in different conda environment
@REM ### Peter van Lunteren, 13 Feb 2024 (latest edit)

@REM set echo settings
echo off
@setlocal EnableDelayedExpansion

@REM catch arguments
set "GPU_DISABLED=%1"
set "MODEL_ENV=%2"
set "MODEL_TYPE=%3"
set "LOCATION_ECOASSIST_FILES=%4"
set "MODEL_FPATH=%5"
set "DET_THRESH=%6"
set "CLS_THRESH=%7"
set "SMOOTH_BOOL=%8"
set "JSON_FPATH=%9"
shift
set "FRAME_DIR=%9"
if "%FRAME_DIR%" == "" ( set "FRAME_DIR=dummy-variable" )

@REM if you need to catch more arguments, you'll have to shift the index back to single digits, like so:
@REM set "H=%9"
@REM shift
@REM set "I=%9"
@REM shift
@REM set "J=%9"

@REM add EcoAssist_files to path
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

@REM set variables
set "INF_SCRIPT=%LOCATION_ECOASSIST_FILES%\EcoAssist\classification_utils\model_types\%MODEL_TYPE%\classify_detections.py"
set BASE_ENV=ecoassistcondaenv-base
set CLS_ENV=ecoassistcondaenv-%MODEL_ENV%

@REM activate dedicated environment
call %EA_CONDA_EXE% deactivate
call %EA_CONDA_EXE% activate %CLS_ENV%
call %EA_CONDA_EXE% env list 

@REM add gits to PYTHONPATH
set PYTHONPATH=%PYTHONPATH%;%LOCATION_ECOASSIST_FILES%

@REM run script
if "%GPU_DISABLED%"=="True" (
    set CUDA_VISIBLE_DEVICES="" & python %INF_SCRIPT% %LOCATION_ECOASSIST_FILES% %MODEL_FPATH% %DET_THRESH% %CLS_THRESH% %SMOOTH_BOOL% %JSON_FPATH% %FRAME_DIR%
) else (
    python %INF_SCRIPT% %LOCATION_ECOASSIST_FILES% %MODEL_FPATH% %DET_THRESH% %CLS_THRESH% %SMOOTH_BOOL% %JSON_FPATH% %FRAME_DIR%
)

@REM activate ecoassistcondaenv again
call %EA_CONDA_EXE% deactivate
call %EA_CONDA_EXE% activate %BASE_ENV%
call %EA_CONDA_EXE% env list 
