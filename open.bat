@REM ### Placeholder script to open EcoAssist from inside Timelapse
@REM ### This batch script is redundant since Timelapse can also open it by executing the python command directly,
@REM ### but it is still here so that it mimics the old method. In the old method we needed this batch script to
@REM ### perform some conda operations before opening the python script. With the Jan 2025 install update 
@REM ### that is not neccesary anymore. But this script is still here so that Timelapse can run the same command as
@REM ### before and users don't have to update their timelapse version when using a new EcoAssist version. 
@REM ### Peter van Lunteren, 16 Jan 2025 (latest edit)

@REM set echo settings
echo off
@setlocal EnableDelayedExpansion

@REM run script in timelapse mode
"%homedrive%%homepath%\EcoAssist_files\envs\env-base\python.exe" "%homedrive%%homepath%\EcoAssist_files\EcoAssist\EcoAssist_GUI.py" --timelapse-path=%2
