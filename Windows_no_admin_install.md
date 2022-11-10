# Windows installation without administrator privileges

THIS TUTORIAL IS WORK IN PROGRESS

EcoAssist needs admin rights because it requires access to the `EcoAssist_files` folder and the `Anaconda3` installation, which are not in your user profile folder. If we want to be able to install and open EcoAssist without admin rights, we basically have to make sure we don't have to touch anything outside your user profile folder. We can do that with some tweaking of the scripts and a manual anaconda installation.

### Step 1: Mannually download anaconda
Go to www.anaconda.com and install anaconda using the graphical installer. Make sure you install it for your user only and place the folder directly inside your user profile folder. If you don't know what your user profile folder is, open a command prompt window and run `echo %UserProfile%`.

<p float="center">
  <img src="https://github.com/PetervanLunteren/EcoAssist/blob/main/imgs/Install_anaconda_1.png" width=33% height="auto" />
  <img src="https://github.com/PetervanLunteren/EcoAssist/blob/main/imgs/Install_anaconda_2.png" width=33% height="auto" />
  <img src="https://github.com/PetervanLunteren/EcoAssist/blob/main/imgs/Install_anaconda_3.png" width=33% height="auto" /> 
</p>

### Step 2: Mannually download git for windows
Go to [gitforwindows.org](https://gitforwindows.org/) and install git for windows using the graphical installer. Make sure you uncheck the "Only show new options" and browse for your user profile folder as destination location. The rest of the default options are just fine. I'm not sure why, but you might get still prompted to enter an admin password. If you decline this the installation will still start. 

<p float="center">
  <img src="https://github.com/PetervanLunteren/EcoAssist/blob/main/imgs/Install_git_1.png" width=33% height="auto" />
  <img src="https://github.com/PetervanLunteren/EcoAssist/blob/main/imgs/Install_git_2.png" width=33% height="auto" />
</p>

### Step 3: Adjust install script
* Download [this file](https://PetervanLunteren.github.io/EcoAssist/Windows_install_EcoAssist.bat) and open it in a text editor (notepad is fine).
* Delete this code

  ```batch
  @REM # set admin rights if not already in use (thanks user399109)
  @REM check for permissions
  >nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
  @REM if error flag set, we do not have admin
  if '%errorlevel%' NEQ '0' (
      echo Requesting administrative privileges...
      goto UACPrompt
  ) else ( goto gotAdmin )

  :UACPrompt
      echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
      set params = %*:"=""
      echo UAC.ShellExecute "cmd.exe", "/c %~s0 %params%", "", "runas", 1 >> "%temp%\getadmin.vbs"

      "%temp%\getadmin.vbs"
      del "%temp%\getadmin.vbs"
      exit /B

  :gotAdmin
      pushd "%CD%"
      CD /D "%~dp0"
  ```

* Change `set LOCATION_ECOASSIST_FILES=%ProgramFiles%\EcoAssist_files` into `set LOCATION_ECOASSIST_FILES=%UserProfile%\EcoAssist_files`
* Change this code
  ```batch
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
          set PATH=!PATH!;"%ProgramFiles%\Git\cmd"
          set PATH=!PATH!;"%ProgramFiles(84x)%\Git\cmd"
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
```


### Step 3
