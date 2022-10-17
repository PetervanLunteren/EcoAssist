@REM ### Windows commands to open the labelImg software via the EcoAssist application https://github.com/PetervanLunteren/EcoAssist
@REM ### Peter van Lunteren, 17 october 2022

@REM # set echo settings
echo off
@setlocal EnableDelayedExpansion

@REM # set path voor ecoassist root dir and add to PATH
set LOCATION_ECOASSIST_FILES=%ProgramFiles%\EcoAssist_files
set PATH=%PATH%;%LOCATION_ECOASSIST_FILES%

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
