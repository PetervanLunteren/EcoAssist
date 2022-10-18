@REM ### Windows install commands for the EcoAssist application https://github.com/PetervanLunteren/EcoAssist
@REM ### Peter van Lunteren, 17 october 2022

@REM # set echo settings
echo off
@setlocal EnableDelayedExpansion

@REM # timestamp the start of installation
set START_DATE=%date%%time%

@REM # set path voor ecoassist root dir and add to PATH
set LOCATION_ECOASSIST_FILES=%ProgramFiles%\EcoAssist_files
set PATH=%PATH%;"%LOCATION_ECOASSIST_FILES%"

@REM # delete previous installation of EcoAssist if present so that it can update
if exist "%LOCATION_ECOASSIST_FILES%" (
    rd /q /s "%LOCATION_ECOASSIST_FILES%"
    echo Removed "%LOCATION_ECOASSIST_FILES%"
)

@REM # make dir
if not exist "%LOCATION_ECOASSIST_FILES%" (
    mkdir "%LOCATION_ECOASSIST_FILES%"
    attrib +h "%LOCATION_ECOASSIST_FILES%"
    echo Created empty dir "%LOCATION_ECOASSIST_FILES%"
) else (
    echo Dir "%LOCATION_ECOASSIST_FILES%" was already present.
)

@REM # install wtee to log information
cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Please send an email to contact@pvanlunteren.com for assistance. Press any key to close this window." | wtee -a "%LOG_FILE%" & PAUSE>nul & EXIT )
curl -OL https://storage.googleapis.com/google-code-archive-downloads/v2/code.google.com/wintee/wtee.exe

@REM # check if log file already exists, otherwise create empty log file
if exist "%LOCATION_ECOASSIST_FILES%\EcoAssist\logfiles\installation_log.txt" (
    set LOG_FILE=%LOCATION_ECOASSIST_FILES%\EcoAssist\logfiles\installation_log.txt
    echo LOG_FILE exists. Logging to !LOG_FILE! | wtee -a "!LOG_FILE!"
) else (
    set LOG_FILE=%LOCATION_ECOASSIST_FILES%\installation_log.txt
    echo. 2> !LOG_FILE!
    echo LOG_FILE does not exist. Logging to !LOG_FILE! | wtee -a "!LOG_FILE!"
)

@REM # log the start of the installation
echo Installation started at %START_DATE% | wtee -a "%LOG_FILE%"

@REM # check if OS is 32 or 64 bit and set variable
reg Query "HKLM\Hardware\Description\System\CentralProcessor\0" | find /i "x86" > NUL && set OS=32BIT || set OS=64BIT
if %OS%==32BIT echo This is an 32-bit operating system. | wtee -a "%LOG_FILE%"
if %OS%==64BIT echo This is an 64-bit operating system. | wtee -a "%LOG_FILE%"

@REM # log system information
systeminfo | wtee -a "%LOG_FILE%"

@REM # install git if not already present
git --version && set git_installed_1="Yes" || set git_installed_1="No"
git --version && git --version | wtee -a "%LOG_FILE%" || echo "git --version (1) failed." | wtee -a "%LOG_FILE%"
echo Is git installed ^(1^)^? !git_installed_1! | wtee -a "%LOG_FILE%"
if !git_installed_1!=="No" (
    echo "Git might be installed but not functioning. Searching for git.exe now.... This may take some time." | wtee -a "%LOG_FILE%"
    set LOCATION_GIT_INSTALLS_1="%LOCATION_ECOASSIST_FILES%\list_with_git_installations_1.txt"
    if exist !LOCATION_GIT_INSTALLS_1! del !LOCATION_GIT_INSTALLS_1!
    cd \ || ( echo "Could not change directory to C:\. Command could not be run. Installation was terminated. Please send an email to contact@pvanlunteren.com for assistance. Press any key to close this window." | wtee -a "%LOG_FILE%" & PAUSE>nul & EXIT )
    dir /b/s git.exe | find /I "\cmd\git.exe" >> !LOCATION_GIT_INSTALLS_1!
    cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Please send an email to contact@pvanlunteren.com for assistance. Press any key to close this window." | wtee -a "%LOG_FILE%" & PAUSE>nul & EXIT )
    for /F "tokens=*" %%A in ('type !LOCATION_GIT_INSTALLS_1!') do (
        set str=%%A
        @REM # remove the file part of path so that it is a directory
        set str=!str:git.exe=!
        echo Found path to git here: !str!
        set PATH=!PATH!;!str!
        echo "Added !str! to PATH!" | wtee -a "%LOG_FILE%"
        echo !PATH! | wtee -a "%LOG_FILE%"
        )
    @REM # check if git now works
    git --version && set git_installed_2="Yes" || set git_installed_2="No"
    git --version && git --version | wtee -a "%LOG_FILE%" || echo "git --version (2) failed." | wtee -a "%LOG_FILE%"
    echo Is git installed (^2^)^? !git_installed_2! | wtee -a "%LOG_FILE%"
    if !git_installed_2!=="No" (
        echo Installing git for windows | wtee -a "%LOG_FILE%"
        @REM # download git version for 32 or 64 bit OS
        if %OS%==32BIT (
            echo Operating system is 32bit | wtee -a "%LOG_FILE%"
            echo Downloading git for windows now | wtee -a "%LOG_FILE%"
            curl -OL https://github.com/git-for-windows/git/releases/download/v2.38.0.windows.1/Git-2.38.0-32-bit.exe
            Git-2.38.0-32-bit.exe
            if exist Git-2.38.0-32-bit.exe del Git-2.38.0-32-bit.exe
        )
        if %OS%==64BIT (
            echo Operating system is 64bit | wtee -a "%LOG_FILE%"
            echo Downloading git for windows now | wtee -a "%LOG_FILE%"
            curl -OL https://github.com/git-for-windows/git/releases/download/v2.38.0.windows.1/Git-2.38.0-64-bit.exe
            Git-2.38.0-64-bit.exe
            if exist Git-2.38.0-64-bit.exe del Git-2.38.0-64-bit.exe
        )
        set PATH=%PATH%;"%ProgramFiles%\Git\cmd"
        set PATH=%PATH%;"%ProgramFiles(84x)%\Git\cmd"
        set PATH=!PATH!;"C:\ProgramData\Git\cmd"
        set PATH=!PATH!;"%UserProfile%\Git\cmd"
        set PATH=!PATH!;"C:\Users\Git\cmd"
        set PATH=!PATH!;"C:\Users\All Users\Git\cmd"
        set PATH=!PATH!;"%SystemRoot%\Git\cmd"
        echo !PATH! | wtee -a "%LOG_FILE%"
        @REM # check if git now works
        git --version && set git_installed_3="Yes" || set git_installed_3="No"
        git --version && git --version | wtee -a "%LOG_FILE%" || echo "git --version (3) failed." | wtee -a "%LOG_FILE%"
        echo Is git installed (^3^)^? !git_installed_3! | wtee -a "%LOG_FILE%"
        if !git_installed_3!=="No" (
            echo "Git is installed but not functioning yet. Searching again for git.exe.... This may take some time." | wtee -a "%LOG_FILE%"
            set LOCATION_GIT_INSTALLS_2="%LOCATION_ECOASSIST_FILES%\list_with_git_installations_2.txt"
            if exist !LOCATION_GIT_INSTALLS_2! del !LOCATION_GIT_INSTALLS_2!
            cd \ || ( echo "Could not change directory to C:\. Command could not be run. Installation was terminated. Please send an email to contact@pvanlunteren.com for assistance. Press any key to close this window." | wtee -a "%LOG_FILE%" & PAUSE>nul & EXIT )
            dir /b/s git.exe | find /I "\cmd\git.exe" >> !LOCATION_GIT_INSTALLS_2!
            cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Please send an email to contact@pvanlunteren.com for assistance. Press any key to close this window." | wtee -a "%LOG_FILE%" & PAUSE>nul & EXIT )
            for /F "tokens=*" %%A in ('type !LOCATION_GIT_INSTALLS_2!') do (
                set str=%%A
                @REM # remove the file part of path so that it is a directory
                set str=!str:git.exe=!
                echo Found path to git here: !str!
                set PATH=!PATH!;!str!
                echo "Added !str! to PATH!" | wtee -a "%LOG_FILE%"
                echo !PATH! | wtee -a "%LOG_FILE%"
                )
            @REM # check if git now works
            git --version && set git_installed_4="Yes" || set git_installed_4="No"
            git --version && git --version | wtee -a "%LOG_FILE%" || echo "git --version (4) failed." | wtee -a "%LOG_FILE%"
            echo Is git installed (^4^)^? !git_installed_4! | wtee -a "%LOG_FILE%"
            if !git_installed_4!=="No" (
                echo "The installation of git did not succeed. Please install git manually (https://gitforwindows.org/). Try to install EcoAssist again if git is installed." | wtee -a "%LOG_FILE%"
                PAUSE>nul
                EXIT
            ) else (
                echo Git is working after being downloaded, installed and searched for. | wtee -a "%LOG_FILE%"
            )
        ) else (
            echo Git is working after installation. | wtee -a "%LOG_FILE%"
        )
    ) else (
        echo "There was an installation of git found which is working. Proceeding with rest of script." | wtee -a "%LOG_FILE%"
    )
) else (
    echo "Git is already installed and functioning. Proceeding with rest of the script." | wtee -a "%LOG_FILE%"
)

@REM # clone EcoAssist git if not present
if exist "%LOCATION_ECOASSIST_FILES%\EcoAssist\" (
    echo Dir EcoAssist already exists! Skipping this step. | wtee -a "%LOG_FILE%"
) else (
    echo Dir EcoAssist does not exists! Clone repo... | wtee -a "%LOG_FILE%"
    cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Please send an email to contact@pvanlunteren.com for assistance. Press any key to close this window." | wtee -a "%LOG_FILE%" & PAUSE>nul & EXIT )
    git clone https://github.com/PetervanLunteren/EcoAssist.git
    @REM # check the size of the folder
    dir "%LOCATION_ECOASSIST_FILES%\EcoAssist" | wtee -a "%LOG_FILE%"
)

@REM  # create a .vbs file which opens EcoAssist without the console window
echo "Creating Windows_open_EcoAssist_shortcut.vbs now..." | wtee -a "%LOG_FILE%"
echo Set WinScriptHost ^= CreateObject^("WScript.Shell"^) > "%LOCATION_ECOASSIST_FILES%\EcoAssist\Windows_open_EcoAssist_shortcut.vbs"
echo WinScriptHost.Run Chr^(34^) ^& "%LOCATION_ECOASSIST_FILES%\EcoAssist\Windows_open_EcoAssist.bat" ^& Chr^(34^)^, 0  >> "%LOCATION_ECOASSIST_FILES%\EcoAssist\Windows_open_EcoAssist_shortcut.vbs"
echo Set WinScriptHost ^= Nothing >> "%LOCATION_ECOASSIST_FILES%\EcoAssist\Windows_open_EcoAssist_shortcut.vbs"

@REM  # create and execute a .vbs file which creates a shortcut with the EcoAssist logo
echo "Creating CreateShortcut.vbs now..." | wtee -a "%LOG_FILE%"
echo Set oWS ^= WScript.CreateObject^("WScript.Shell"^) > "%LOCATION_ECOASSIST_FILES%\EcoAssist\logfiles\CreateShortcut.vbs"
echo sLinkFile ^= "%HOMEDRIVE%%HOMEPATH%\Desktop\EcoAssist.lnk" >> "%LOCATION_ECOASSIST_FILES%\EcoAssist\logfiles\CreateShortcut.vbs"
echo Set oLink ^= oWS.CreateShortcut^(sLinkFile^) >> "%LOCATION_ECOASSIST_FILES%\EcoAssist\logfiles\CreateShortcut.vbs"
echo oLink.TargetPath ^= "%LOCATION_ECOASSIST_FILES%\EcoAssist\Windows_open_EcoAssist_shortcut.vbs" >> "%LOCATION_ECOASSIST_FILES%\EcoAssist\logfiles\CreateShortcut.vbs"
echo oLink.IconLocation ^= "%LOCATION_ECOASSIST_FILES%\EcoAssist\imgs\logo_small_bg.ico" >> "%LOCATION_ECOASSIST_FILES%\EcoAssist\logfiles\CreateShortcut.vbs"
echo oLink.Save >> "%LOCATION_ECOASSIST_FILES%\EcoAssist\logfiles\CreateShortcut.vbs"
echo "Executing CreateShortcut.vbs now..." | wtee -a "%LOG_FILE%"
cscript "%LOCATION_ECOASSIST_FILES%\EcoAssist\logfiles\CreateShortcut.vbs"
echo "Created EcoAssist.lnk" | wtee -a "%LOG_FILE%"

@REM # clone cameratraps git if not present
if exist "%LOCATION_ECOASSIST_FILES%\cameratraps\" (
    echo Dir cameratraps already exists! Skipping this step. | wtee -a "%LOG_FILE%"
) else (
    echo Dir cameratraps does not exists! Clone repo... | wtee -a "%LOG_FILE%"
    cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Please send an email to contact@pvanlunteren.com for assistance. Press any key to close this window." | wtee -a "%LOG_FILE%" & PAUSE>nul & EXIT )
    git clone https://github.com/Microsoft/cameratraps
    cd "%LOCATION_ECOASSIST_FILES%\cameratraps" || ( echo "Could not change directory to cameratraps. Command could not be run. Installation was terminated. Please send an email to contact@pvanlunteren.com for assistance. Press any key to close this window." | wtee -a "%LOG_FILE%" & PAUSE>nul & EXIT )
    git checkout f8417740c1624d38988210a2dd5de58b64ae7827
    cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Please send an email to contact@pvanlunteren.com for assistance. Press any key to close this window." | wtee -a "%LOG_FILE%" & PAUSE>nul & EXIT )
    @REM # check the size of the folder
    dir "%LOCATION_ECOASSIST_FILES%\cameratraps" | wtee -a "%LOG_FILE%"
)

@REM # clone ai4eutils git if not present
if exist "%LOCATION_ECOASSIST_FILES%\ai4eutils\" (
    echo Dir ai4eutils already exists! Skipping this step. | wtee -a "%LOG_FILE%"
) else (
    echo Dir ai4eutils does not exists! Clone repo... | wtee -a "%LOG_FILE%"
    cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Please send an email to contact@pvanlunteren.com for assistance. Press any key to close this window." | wtee -a "%LOG_FILE%" & PAUSE>nul & EXIT )
    git clone https://github.com/Microsoft/ai4eutils
    cd "%LOCATION_ECOASSIST_FILES%\ai4eutils" || ( echo "Could not change directory to ai4eutils. Command could not be run. Installation was terminated. Please send an email to contact@pvanlunteren.com for assistance. Press any key to close this window." | wtee -a "%LOG_FILE%" & PAUSE>nul & EXIT )
    git checkout 1bbbb8030d5be3d6488ac898f9842d715cdca088
    cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Please send an email to contact@pvanlunteren.com for assistance. Press any key to close this window." | wtee -a "%LOG_FILE%" & PAUSE>nul & EXIT )
    @REM # check the size of the folder
    dir "%LOCATION_ECOASSIST_FILES%\ai4eutils" | wtee -a "%LOG_FILE%"
)

@REM # clone yolov5 git if not present
if exist "%LOCATION_ECOASSIST_FILES%\yolov5\" (
    echo Dir yolov5 already exists! Skipping this step. | wtee -a "%LOG_FILE%"
) else (
    echo Dir yolov5 does not exists! Clone repo... | wtee -a "%LOG_FILE%"
    cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Please send an email to contact@pvanlunteren.com for assistance. Press any key to close this window." | wtee -a "%LOG_FILE%" & PAUSE>nul & EXIT )
    git clone https://github.com/ultralytics/yolov5/
    cd "%LOCATION_ECOASSIST_FILES%\yolov5" || ( echo "Could not change directory to yolov5. Command could not be run. Installation was terminated. Please send an email to contact@pvanlunteren.com for assistance. Press any key to close this window." | wtee -a "%LOG_FILE%" & PAUSE>nul & EXIT )
    git checkout c23a441c9df7ca9b1f275e8c8719c949269160d1
    cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Please send an email to contact@pvanlunteren.com for assistance. Press any key to close this window." | wtee -a "%LOG_FILE%" & PAUSE>nul & EXIT )
    @REM # check the size of the folder
    dir "%LOCATION_ECOASSIST_FILES%\yolov5" | wtee -a "%LOG_FILE%"
)

@REM # clone labelImg git if not present
if exist "%LOCATION_ECOASSIST_FILES%\labelImg\" (
    echo Dir labelImg already exists! Skipping this step. | wtee -a "%LOG_FILE%"
) else (
    echo Dir labelImg does not exists! Clone repo... | wtee -a "%LOG_FILE%"
    cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Please send an email to contact@pvanlunteren.com for assistance. Press any key to close this window." | wtee -a "%LOG_FILE%" & PAUSE>nul & EXIT )
    git clone https://github.com/tzutalin/labelImg.git
    cd "%LOCATION_ECOASSIST_FILES%\labelImg" || ( echo "Could not change directory to labelImg. Command could not be run. Installation was terminated. Please send an email to contact@pvanlunteren.com for assistance. Press any key to close this window." | wtee -a "%LOG_FILE%" & PAUSE>nul & EXIT )
    git checkout 276f40f5e5bbf11e84cfa7844e0a6824caf93e11
    cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Please send an email to contact@pvanlunteren.com for assistance. Press any key to close this window." | wtee -a "%LOG_FILE%" & PAUSE>nul & EXIT )
    @REM # check the size of the folder
    dir "%LOCATION_ECOASSIST_FILES%\labelImg" | wtee -a "%LOG_FILE%"
)

@REM # download the md_v5a.0.0.pt model if not present
if exist "%LOCATION_ECOASSIST_FILES%\megadetector\md_v5a.0.0.pt" (
    echo "File md_v5a.0.0.pt already exists! Skipping this step." | wtee -a "%LOG_FILE%"
) else (
    echo "File md_v5a.0.0.pt does not exists! Downloading file..." | wtee -a "%LOG_FILE%"
    if not exist "%LOCATION_ECOASSIST_FILES%\megadetector" mkdir "%LOCATION_ECOASSIST_FILES%\megadetector"
    cd "%LOCATION_ECOASSIST_FILES%\megadetector" || ( echo "Could not change directory to megadetector. Command could not be run. Installation was terminated. Please send an email to contact@pvanlunteren.com for assistance. Press any key to close this window." | wtee -a "%LOG_FILE%" & PAUSE>nul & EXIT )
    curl --keepalive -OL https://github.com/microsoft/CameraTraps/releases/download/v5.0/md_v5a.0.0.pt
    cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Please send an email to contact@pvanlunteren.com for assistance. Press any key to close this window." | wtee -a "%LOG_FILE%" & PAUSE>nul & EXIT )
    @REM # check the size of the folder
    dir "%LOCATION_ECOASSIST_FILES%\megadetector" | wtee -a "%LOG_FILE%"
)

@REM # check if conda is already installed, if not install
conda -h && set conda_installed_1="Yes" || set conda_installed_1="No"
conda -h && conda -h | wtee -a "%LOG_FILE%" || echo "conda -h (1) failed." | wtee -a "%LOG_FILE%"
echo Is conda installed ^(1^)^? !conda_installed_1! | wtee -a "%LOG_FILE%"
if !conda_installed_1!=="No" (
    echo "Conda might be installed, but the conda command is not recognised. Lets try to add some common locations of anaconda to the PATH variable and check again..." | wtee -a "%LOG_FILE%"
    set PATH=!PATH!;"C:\ProgramData\Anaconda3\Scripts\"
    set PATH=!PATH!;"%UserProfile%\Anaconda3\Scripts\"
    set PATH=!PATH!;"C:\Users\Anaconda3\Scripts\"
    set PATH=!PATH!;"C:\Users\All Users\Anaconda3\Scripts\"
    set PATH=!PATH!;"%SystemRoot%\Anaconda3\Scripts\"
    set PATH=!PATH!;"%ProgramFiles%\Anaconda3\Scripts\"
    set PATH=!PATH!;"%ProgramFiles(x86)%\Anaconda3\Scripts\"
    echo !PATH! | wtee -a "%LOG_FILE%"
    @REM # check if conda now works
    conda -h && set conda_installed_2="Yes" || set conda_installed_2="No"
    conda -h && conda -h | wtee -a "%LOG_FILE%" || echo "conda -h (2) failed." | wtee -a "%LOG_FILE%"
    echo Is conda installed ^(2^)^? !conda_installed_2! | wtee -a "%LOG_FILE%"
    if !conda_installed_2!=="No" (
        echo "Lets try and search for the conda.exe file. This might take some time...." | wtee -a "%LOG_FILE%"
        set LOCATION_CONDA_INSTALLS_1="%LOCATION_ECOASSIST_FILES%\EcoAssist\logfiles\list_with_conda_installations_1.txt"
        if exist !LOCATION_CONDA_INSTALLS_1! del !LOCATION_CONDA_INSTALLS_1!
        cd \ || ( echo "Could not change directory to C:\. Command could not be run. Installation was terminated. Please send an email to contact@pvanlunteren.com for assistance. Press any key to close this window." | wtee -a "%LOG_FILE%" & PAUSE>nul & EXIT )
        dir /b/s conda.exe | find /I "\Anaconda3\Scripts\conda.exe" >> !LOCATION_CONDA_INSTALLS_1!
        cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Please send an email to contact@pvanlunteren.com for assistance. Press any key to close this window." | wtee -a "%LOG_FILE%" & PAUSE>nul & EXIT )
        for /F "tokens=*" %%A in ('type !LOCATION_CONDA_INSTALLS_1!') do (
            set str=%%A
            @REM # remove the file part of path so that it is a directory
            set str=!str:conda.exe=!
            echo Found path to Anaconda3 here: !str!
            echo "Adding !str! to PATH..." | wtee -a "%LOG_FILE%"
            set PATH=!PATH!;!str!
            echo "Added !str! to PATH!" | wtee -a "%LOG_FILE%"
            echo !PATH! | wtee -a "%LOG_FILE%"
            )
        @REM # check if conda now works
        conda -h && set conda_installed_3="Yes" || set conda_installed_3="No"
        conda -h && conda -h | wtee -a "%LOG_FILE%" || echo "conda -h (3) failed." | wtee -a "%LOG_FILE%"
        echo Is conda installed ^(3^)^? !conda_installed_3! | wtee -a "%LOG_FILE%"
        if !conda_installed_3!=="No" (
            echo "Looks like Anaconda3 is not installed on this computer. Downloading now..." | wtee -a "%LOG_FILE%"
            cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Please send an email to contact@pvanlunteren.com for assistance. Press any key to close this window." | wtee -a "%LOG_FILE%" & PAUSE>nul & EXIT )
            @REM # depending on number of bits
            if %OS%==32BIT (
                curl --keepalive -OL https://repo.anaconda.com/archive/Anaconda3-2021.11-Windows-x86.exe
                Anaconda3-2021.11-Windows-x86.exe
                if exist Anaconda3-2021.11-Windows-x86.exe del /F Anaconda3-2021.11-Windows-x86.exe
            )
            if %OS%==64BIT (
                curl --keepalive -OL https://repo.anaconda.com/archive/Anaconda3-2021.11-Windows-x86_64.exe
                Anaconda3-2021.11-Windows-x86_64.exe
                if exist Anaconda3-2021.11-Windows-x86_64.exe del /F Anaconda3-2021.11-Windows-x86_64.exe
            )
            @REM # check if conda works now
            conda -h && set conda_installed_4="Yes" || set conda_installed_4="No"
            conda -h && conda -h | wtee -a "%LOG_FILE%" || echo "conda -h (4) failed." | wtee -a "%LOG_FILE%"
            echo Is conda installed ^(4^)^? !conda_installed_4! | wtee -a "%LOG_FILE%"
            if !conda_installed_4!=="No" (
                echo "The conda command still doesn't work after downloading and installing Anaconda3. Lets try searching for it one more time." | wtee -a "%LOG_FILE%"
                set LOCATION_CONDA_INSTALLS_2="%LOCATION_ECOASSIST_FILES%\EcoAssist\logfiles\list_with_conda_installations_2.txt"
                if exist !LOCATION_CONDA_INSTALLS_2! del !LOCATION_CONDA_INSTALLS_2!
                cd \ || ( echo "Could not change directory to C:\. Command could not be run. Installation was terminated. Please send an email to contact@pvanlunteren.com for assistance. Press any key to close this window." | wtee -a "%LOG_FILE%" & PAUSE>nul & EXIT )
                dir /b/s conda.exe | find /I "\Anaconda3\Scripts\conda.exe" >> !LOCATION_CONDA_INSTALLS_2!
                cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Please send an email to contact@pvanlunteren.com for assistance. Press any key to close this window." | wtee -a "%LOG_FILE%" & PAUSE>nul & EXIT )
                for /F "tokens=*" %%A in ('type !LOCATION_CONDA_INSTALLS_2!') do (
                    set str=%%A
                    @REM # remove the file part of path so that it is a directory and can be added to PATH
                    set str=!str:conda.exe=!
                    echo Found path to Anaconda3 here: !str!
                    echo "Adding !str! to PATH..." | wtee -a "%LOG_FILE%"
                    set PATH=!PATH!;!str!
                    echo "Added !str! to PATH!" | wtee -a "%LOG_FILE%"
                    echo !PATH! | wtee -a "%LOG_FILE%"
                    )
                @REM # check if conda now works
                conda -h && set conda_installed_5="Yes" || set conda_installed_5="No"
                conda -h && conda -h | wtee -a "%LOG_FILE%" || echo "conda -h (5) failed." | wtee -a "%LOG_FILE%"
                echo Is conda installed ^(5^)^? !conda_installed_5! | wtee -a "%LOG_FILE%"
                if !conda_installed_5!=="No" (
                    echo "Could not get Anaconda3 to work on your computer. Please install it mannually (https://www.anaconda.com/products/distribution) and then try to install EcoAssist again using this script." | wtee -a "%LOG_FILE%" & PAUSE>nul & EXIT 
                ) else (
                    echo "The conda command finally works after downloading and installing Anaconda3 and searching for the conda.exe!" | wtee -a "%LOG_FILE%"
                )
            ) else (
                echo "The conda command works after downloading and installing Anaconda3." | wtee -a "%LOG_FILE%"
            )
        ) else (
            echo "The conda command works after searching for the conda.exe!" | wtee -a "%LOG_FILE%"
        )
    ) else (
        echo "The conda command works after adding the common paths!" | wtee -a "%LOG_FILE%"
    )
) else (
    echo "Anaconda was already installed!" | wtee -a "%LOG_FILE%"
)

@REM @REM # get path info, strip and write to txt file
FOR /F "tokens=*" %%g IN ('conda info ^| find /I "base environment"') do (set PATH_TO_ANACONDA=%%g)
set "PATH_TO_ANACONDA=!PATH_TO_ANACONDA:base environment : =!"
set "PATH_TO_ANACONDA=!PATH_TO_ANACONDA:  (writable)=!"
set "PATH_TO_ANACONDA=!PATH_TO_ANACONDA: =!"
echo "Found path to conda installation: %PATH_TO_ANACONDA%" | wtee -a "%LOG_FILE%"
echo %PATH_TO_ANACONDA%> "%LOCATION_ECOASSIST_FILES%\EcoAssist\logfiles\path_to_conda_installation.txt"

@REM # activate anaconda so that we can use it in a batch script
call "%PATH_TO_ANACONDA%\Scripts\activate.bat" "%PATH_TO_ANACONDA%"

@REM # create conda env and install software for MegaDetector
call conda env remove -n ecoassistcondaenv
cd "%LOCATION_ECOASSIST_FILES%\cameratraps" || ( echo "Could not change directory to cameratraps. Command could not be run. Installation was terminated. Please send an email to contact@pvanlunteren.com for assistance. Press any key to close this window." | wtee -a "%LOG_FILE%" & PAUSE>nul & EXIT )
call conda env create --name ecoassistcondaenv --file environment-detector.yml
cd "%LOCATION_ECOASSIST_FILES%" || ( echo "Could not change directory to EcoAssist_files. Command could not be run. Installation was terminated. Please send an email to contact@pvanlunteren.com for assistance. Press any key to close this window." | wtee -a "%LOG_FILE%" & PAUSE>nul & EXIT )
call activate ecoassistcondaenv

@REM # install additional packages for labelImg
%PATH_TO_ANACONDA%\envs\ecoassistcondaenv\python.exe -m pip install pyqt5==5.15.2 lxml

@REM # install additional packages for EcoAssist
%PATH_TO_ANACONDA%\envs\ecoassistcondaenv\python.exe -m pip install bounding_box

@REM # log env info
call conda info --envs >> "%LOG_FILE%"
call conda list >> "%LOG_FILE%"
%PATH_TO_ANACONDA%\envs\ecoassistcondaenv\python.exe -m pip freeze >> "%LOG_FILE%"

@REM # deactivate conda env
call conda deactivate

@REM # log folder structure
dir "%LOCATION_ECOASSIST_FILES%" | wtee -a "%LOG_FILE%"

@REM # timestamp the end of installation
set END_DATE=%date%%time%
echo Installation ended at %END_DATE% | wtee -a "%LOG_FILE%"

@REM # move txt files to log_folder if they are in  EcoAssist_files
if exist "%LOCATION_ECOASSIST_FILES%\list_with_git_installations_1.txt" ( move /Y "%LOCATION_ECOASSIST_FILES%\list_with_git_installations_1.txt" "%LOCATION_ECOASSIST_FILES%\EcoAssist\logfiles" )
if exist "%LOCATION_ECOASSIST_FILES%\list_with_git_installations_2.txt" ( move /Y "%LOCATION_ECOASSIST_FILES%\list_with_git_installations_2.txt" "%LOCATION_ECOASSIST_FILES%\EcoAssist\logfiles" )
if exist "%LOCATION_ECOASSIST_FILES%\installation_log.txt" ( move /Y "%LOCATION_ECOASSIST_FILES%\installation_log.txt" "%LOCATION_ECOASSIST_FILES%\EcoAssist\logfiles" )

@REM # end process
echo The installation is done^! Press any key to close this window.

@REM # close window with any key
PAUSE>nul
