@REM ### Windows uninstall commands for the EcoAssist application https://github.com/PetervanLunteren/EcoAssist
@REM ### Peter van Lunteren, 17 Jul (latest edit).

@REM set echo settings
echo off
@setlocal EnableDelayedExpansion

@REM log
echo.
echo Uninstalling EcoAssist...
echo.

@REM set conda cmds
@REM check the default locations for a conda install
for %%x in (miniforge3, miniconda3, anaconda3) do ( 
    for %%y in ("%ProgramData%", "%HOMEDRIVE%%HOMEPATH%", "%ProgramFiles%", "%ProgramFiles(x86)%", "%LocalAppData%", "%AppData%") do ( 
        set CHECK_DIR=%%y\%%x\
        set CHECK_DIR=!CHECK_DIR:"=!
        echo Checking conda dir:                    '!CHECK_DIR!'
        if exist !CHECK_DIR! (
            set PATH_TO_CONDA_INSTALLATION=!CHECK_DIR!
            echo Found conda dir:                       '!PATH_TO_CONDA_INSTALLATION!'
            goto check_conda_install
            )
        ) 
    )

@REM check if conda is added to PATH
where conda /q  && (for /f "tokens=*" %%a in ('where conda') do (for %%b in ("%%~dpa\.") do set PATH_TO_CONDA_INSTALLATION=%%~dpb)) && goto check_conda_install

@REM provide miniforge link if not found
:set_conda_install
echo:
echo:
echo REQUIREMENT: MINIFORGE
echo:
echo EcoAssist requires requires a conda distribution. Please add it to the PATH using your system settings.
echo:
echo:
echo https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Windows-x86_64.exe
echo:
echo:
cmd /k & exit

@REM clean path
:check_conda_install
set PATH_TO_CONDA_INSTALLATION=%PATH_TO_CONDA_INSTALLATION:"=%
set PATH_TO_CONDA_INSTALLATION=%PATH_TO_CONDA_INSTALLATION:'=%
IF %PATH_TO_CONDA_INSTALLATION:~-1%==\ SET PATH_TO_CONDA_INSTALLATION=%PATH_TO_CONDA_INSTALLATION:~0,-1%
echo Path to conda is defined as:           '%PATH_TO_CONDA_INSTALLATION%'
@REM check dir validity
if not exist "%PATH_TO_CONDA_INSTALLATION%\Scripts\activate.bat" ( echo '%PATH_TO_CONDA_INSTALLATION%\Scripts\activate.bat' does not exist. Enter a path to a valid conda installation. & goto set_conda_install )

@REM add conda dir to path
set PATH=%PATH_TO_CONDA_INSTALLATION%\Scripts;%PATH%

@REM suppress conda warnings about updates
call conda config --set notify_outdated_conda false

@REM remove index cache, lock files, unused cache packages, and tarballs
call conda clean --all -y

@REM remove all old ecoassist conda evironments on the conda way, if present
call mamba env remove -n ecoassistcondaenv -y || ( echo "could not mamba env remove, proceeding to remove via rd..." & rd /q /s "%PATH_TO_CONDA_INSTALLATION%\envs\ecoassistcondaenv" ) || ( echo "There was an error trying to execute the conda command. Installation was terminated. Copy-paste all text in this console window and send it to peter@addaxdatascience.com for further support." & cmd /k & exit )
call mamba env remove -n ecoassistcondaenv-yolov8 -y || ( echo "could not mamba env remove, proceeding to remove via rd..." & rd /q /s "%PATH_TO_CONDA_INSTALLATION%\envs\ecoassistcondaenv-yolov8" ) || ( echo "There was an error trying to execute the conda command. Installation was terminated. Copy-paste all text in this console window and send it to peter@addaxdatascience.com for further support." & cmd /k & exit )
call mamba env remove -n ecoassistcondaenv-mewc -y || ( echo "could not mamba env remove, proceeding to remove via rd..." & rd /q /s "%PATH_TO_CONDA_INSTALLATION%\envs\ecoassistcondaenv-mewc" ) || ( echo "There was an error trying to execute the conda command. Installation was terminated. Copy-paste all text in this console window and send it to peter@addaxdatascience.com for further support." & cmd /k & exit )
call mamba env remove -n ecoassistcondaenv-base -y || ( echo "could not mamba env remove, proceeding to remove via rd..." & rd /q /s "%PATH_TO_CONDA_INSTALLATION%\envs\ecoassistcondaenv-base" ) || ( echo "There was an error trying to execute the conda command. Installation was terminated. Copy-paste all text in this console window and send it to peter@addaxdatascience.com for further support." & cmd /k & exit )
call mamba env remove -n ecoassistcondaenv-pytorch -y || ( echo "could not mamba env remove, proceeding to remove via rd..." & rd /q /s "%PATH_TO_CONDA_INSTALLATION%\envs\ecoassistcondaenv-pytorch" ) || ( echo "There was an error trying to execute the conda command. Installation was terminated. Copy-paste all text in this console window and send it to peter@addaxdatascience.com for further support." & cmd /k & exit )
call mamba env remove -n ecoassistcondaenv-tensorflow -y || ( echo "could not mamba env remove, proceeding to remove via rd..." & rd /q /s "%PATH_TO_CONDA_INSTALLATION%\envs\ecoassistcondaenv-tensorflow" ) || ( echo "There was an error trying to execute the conda command. Installation was terminated. Copy-paste all text in this console window and send it to peter@addaxdatascience.com for further support." & cmd /k & exit )

@REM loop over common locations for old ecoassist conda environments and remove them the hard way (rd)
for %%x in (miniforge3, mambaforge, miniconda3, anaconda3) do ( 
    for %%y in ("%ProgramData%", "%HOMEDRIVE%%HOMEPATH%", "%ProgramFiles%", "%ProgramFiles(x86)%") do ( 
        set CHECK_DIR=%%y\%%x\
        set CHECK_DIR=!CHECK_DIR:"=!
        echo Checking conda dir:                  '!CHECK_DIR!'
        if exist !CHECK_DIR! (
            for %%z in ("", "-yolov8", "-mewc", "-base", "-pytorch", "-tensorflow") do ( 
                set ENV_DIR_PATH=!CHECK_DIR!envs\ecoassistcondaenv%%z\
                set ENV_DIR_PATH=!ENV_DIR_PATH:"=!
                echo Checking env dir:                         '!ENV_DIR_PATH!'
                if exist !ENV_DIR_PATH! (
                    echo Found existing old conda env:                 '!ENV_DIR_PATH!'
                    echo Removing existing old conda env:                 '!ENV_DIR_PATH!'
                    rd /q /s "!ENV_DIR_PATH!"
                    )
                ) 
            )
        ) 
    )

@REM remove ecoassist files
set NO_ADMIN_INSTALL=%homedrive%%homepath%\EcoAssist_files
set ADMIN_INSTALL=%ProgramFiles%\EcoAssist_files

if exist "%NO_ADMIN_INSTALL%" (
    rd /q /s "%NO_ADMIN_INSTALL%"
    if not exist "%NO_ADMIN_INSTALL%" (
        echo Successfully removed:                '%NO_ADMIN_INSTALL%'
    ) else (
        echo "Cannot remove the folder '%NO_ADMIN_INSTALL%'. Perhaps a permission issue? Restart your computer and try this installation again. If the error persists, try deleting the folder manually. If that still doesn't work: copy-paste all text in this console window and send it to peter@addaxdatascience.com for further support."
        cmd /k & exit
    )
) else (
    if exist "%ADMIN_INSTALL%" (
        rd /q /s "%ADMIN_INSTALL%"
        if not exist "%ADMIN_INSTALL%" (
            echo Successfully removed:                '%ADMIN_INSTALL%'
        ) else (
            echo "Cannot remove the folder '%ADMIN_INSTALL%'. Perhaps a permission issue? Restart your computer and try this installation again. If the error persists, try deleting the folder manually. If that still doesn't work: copy-paste all text in this console window and send it to peter@addaxdatascience.com for further support."
            cmd /k & exit
        )
    )
)

@REM log
echo THE UNINSTALL IS DONE^^! You can close this window.

@REM keep console open after finishing
cmd /k & exit