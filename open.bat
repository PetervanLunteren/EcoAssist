@REM This script opens the AddaxAI program and allows for shortcut creation and execution from within Timelapse.
@REM Timelapse can also open it by executing the python command directly, but it is still here so that it mimics 
@REM the old method. In the old method we needed this batch script to perform some conda operations before opening
@REM the python script. With the Jan 2025 install update that is not neccesary anymore. But this script is still 
@REM here so that Timelapse can run the same command as before and users don't have to update their Timelapse 
@REM version when using a new AddaxAI version. 
@REM Peter van Lunteren, 25 Jan 2025 (latest edit)

@REM set echo settings
echo off
@setlocal EnableDelayedExpansion

@REM set paths
set ADDAXAI_GUI="%ProgramFiles%\EcoAssist_files\EcoAssist\EcoAssist_GUI.py"
set PYTHON_EXE="%ProgramFiles%\EcoAssist_files\envs\env-base\python.exe"

@REM run script in either timelapse or normal mode
if "%1" == "timelapse" (
    %PYTHON_EXE% %ADDAXAI_GUI% --timelapse-path=%2
) else (
    %PYTHON_EXE% %ADDAXAI_GUI%
)
