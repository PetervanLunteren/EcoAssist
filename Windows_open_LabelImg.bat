@REM ### Windows commands to open the labelImg software via the EcoAssist application https://github.com/PetervanLunteren/EcoAssist
@REM ### Peter van Lunteren, 2 Apr 2023 (latest edit)

@REM # set echo settings
echo off
@setlocal EnableDelayedExpansion

@REM set variables
set LOCATION_ECOASSIST_FILES=%homedrive%%homepath%\EcoAssist_files
set PATH=%PATH%;"%LOCATION_ECOASSIST_FILES%"
set CONDA_DIRECTORY=%LOCATION_ECOASSIST_FILES%\miniconda
set ECOASSISTCONDAENV=%CONDA_DIRECTORY%\envs\ecoassistcondaenv
set PIP=%ECOASSISTCONDAENV%\Scripts\pip3
set HOMEBREW_DIR=%LOCATION_ECOASSIST_FILES%\homebrew
set GIT_DIRECTORY=%LOCATION_ECOASSIST_FILES%\git4windows
set GIT_PYTHON_GIT_EXECUTABLE=%GIT_DIRECTORY%\cmd\git.exe

@REM change directory
cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Please send an email to contact@pvanlunteren.com for assistance. Press any key to close this window." | wtee -a "%LOG_FILE%" & PAUSE>nul & EXIT )

@REM # log the start of the labelImg session
set START_DATE=%date% %time%
echo LabelImg session started at %START_DATE%

@REM # add labelImg git to PYTHONPATH
set PYTHONPATH=%PYTHONPATH%;%LOCATION_ECOASSIST_FILES%;%LOCATION_ECOASSIST_FILES%\labelImg
echo PYHTONPATH : %PYTHONPATH%

@REM # add site packages to beginning of PATH
set PATH=%PATH_TO_CONDA%\envs\ecoassistcondaenv\lib\python3.8\site-packages;%PATH%
echo PATH : %PATH%

@REM # check python version
python -V

@REM # open labelImg with arguments given by EcoAssist_GUI.py
cd "%LOCATION_ECOASSIST_FILES%\labelImg" || ( echo "Could not change directory to labelImg. Command could not be run. Installation was terminated. Please send an email to contact@pvanlunteren.com for assistance. Press any key to close this window." & PAUSE>nul & EXIT )
pyrcc5 -o libs\resources.py resources.qrc
echo python labelImg.py %1 %2 %1
python labelImg.py %1 %2 %1

@REM # timestamp the end of session
set END_DATE=%date% %time%
echo LabelImg session ended at %END_DATE%
