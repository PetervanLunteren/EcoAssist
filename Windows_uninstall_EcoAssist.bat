@REM ### Windows commands commands to uninstall the EcoAssist application https://github.com/PetervanLunteren/EcoAssist
@REM ### Peter van Lunteren, 17 october 2022

@REM # set echo settings
echo off
@setlocal EnableDelayedExpansion

@REM # set path voor ecoassist root dir and add to PATH
set LOCATION_ECOASSIST_FILES=%ProgramFiles%\EcoAssist_files

@REM # locate conda
set PATH_TO_CONDA_INSTALLATION_TXT_FILE=%LOCATION_ECOASSIST_FILES%\EcoAssist\logfiles\path_to_conda_installation.txt
FOR /F "tokens=* USEBACKQ" %%F IN (`type "%PATH_TO_CONDA_INSTALLATION_TXT_FILE%"`) DO ( SET PATH_TO_ANACONDA=%%F)
echo Path to conda as imported from "%PATH_TO_CONDA_INSTALLATION_TXT_FILE%" is: "%PATH_TO_ANACONDA%"

@REM # activate anaconda so that we can use it in a batch script
call "%PATH_TO_ANACONDA%\Scripts\activate.bat" "%PATH_TO_ANACONDA%"

@REM # remove EcoAssist environment
echo Removing the anaconda environment for EcoAssist...
call conda env remove -n ecoassistcondaenv
echo Anaconda environment for EcoAssist removed^^!

@REM # remove EcoAssist folder
if exist "%LOCATION_ECOASSIST_FILES%" (
    echo Removing "%LOCATION_ECOASSIST_FILES%"...
    rd /q /s "%LOCATION_ECOASSIST_FILES%"
    echo "%LOCATION_ECOASSIST_FILES%" removed^^!  
)

@REM # removing shortcut, if still on Desktop
if exist "%HOMEDRIVE%%HOMEPATH%\Desktop\EcoAssist.lnk" (
    echo Removing shortcut file "%HOMEDRIVE%%HOMEPATH%\Desktop\EcoAssist.lnk"...
    del "%HOMEDRIVE%%HOMEPATH%\Desktop\EcoAssist.lnk"
    echo Shortcut file "%HOMEDRIVE%%HOMEPATH%\Desktop\EcoAssist.lnk" removed^^!
)

@REM # remove anaconda if user wants to
:choice
set /P c=Do you wish to uninstall anaconda too? Please type 'y' or 'n'.
if /I "%c%" EQU "y" goto :uninstall_anaconda
if /I "%c%" EQU "n" goto :exit_script
goto :choice

@REM # uninstall
:uninstall_anaconda
if exist "%PATH_TO_ANACONDA%" (
    echo Uninstalling anaconda....
    if exist "%PATH_TO_ANACONDA%\Uninstall-Anaconda3.exe" (
        "%PATH_TO_ANACONDA%\Uninstall-Anaconda3.exe"
        :still_not_uninstalled
        if exist "%PATH_TO_ANACONDA%" (
            timeout 1
            goto :still_not_uninstalled
        )
    ) else (
        rd /q /s "%PATH_TO_ANACONDA%"
    )
    echo Anaconda uninstalled^^!
) else (
    echo could not find "%PATH_TO_ANACONDA%". Unable to uninstall anaconda. Did you already uninstall anaconda?
)
echo The uninstallation is all done^^! You can close this window now.
PAUSE>nul

@REM # leave installation as is
:exit_script
echo Anaconda is not uninstalled.
echo The uninstallation is all done^^! You can close this window now.
PAUSE>nul