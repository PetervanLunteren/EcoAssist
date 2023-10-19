@REM ### Windows commands to open the Human-in-the-loop software via the EcoAssist application https://github.com/PetervanLunteren/EcoAssist
@REM ### Peter van Lunteren, 28 Aug 2023 (latest edit)

@REM # set echo settings
echo off
@setlocal EnableDelayedExpansion

@REM change directory
cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Please send an email to contact@pvanlunteren.com for assistance. Press any key to close this window." | wtee -a "%LOG_FILE%" & cmd /k & exit )

@REM # log the start of the Human-in-the-loop session
set START_DATE=%date% %time%
echo Human-in-the-loop session started at %START_DATE%

@REM # check python version
python -V

@REM # open Human-in-the-loop with arguments given by EcoAssist_GUI.py
cd "%LOCATION_ECOASSIST_FILES%\Human-in-the-loop" || ( echo "Could not change directory to Human-in-the-loop. Command could not be run. Installation was terminated. Please send an email to contact@pvanlunteren.com for assistance. Press any key to close this window." & cmd /k & exit )
pyrcc5 -o libs\resources.py resources.qrc
echo python labelImg.py %1 %2
python labelImg.py %1 %2

@REM # timestamp the end of session
set END_DATE=%date% %time%
echo Human-in-the-loop session ended at %END_DATE%
