# Windows installation without administrator privileges

THIS TUTORIAL IS WORK IN PROGRESS

TODO:
* check if it works without the 3rd option of anaconda. 

EcoAssist needs admin rights because it requires access to the `Anaconda3` and `Git` installations and the `EcoAssist_files` folder, which are (generally) not in your user profile folder. If we want to be able to install and open EcoAssist without admin rights, we basically have to make sure we don't have to touch anything outside your user profile folder. We can do that with some tweaking of the scripts and manual installations.

### Step 1: Mannually download anaconda
If you don't already have anaconda installed inside your user profile folder, go to www.anaconda.com and install anaconda using the graphical installer. Make sure you install it for your user only ("Just Me") and choose the destination folder directly inside your user profile folder (`C:\Users\<user_name>\anaconda3`). The rest of the default options are just fine.

<p float="center">
  <img src="https://github.com/PetervanLunteren/EcoAssist/blob/main/imgs/Install_anaconda_1.png" width=33% height="auto" />
  <img src="https://github.com/PetervanLunteren/EcoAssist/blob/main/imgs/Install_anaconda_2.png" width=33% height="auto" />
  <img src="https://github.com/PetervanLunteren/EcoAssist/blob/main/imgs/Install_anaconda_3.png" width=33% height="auto" /> 
</p>

### Step 2: Mannually download git
If you don't already have git installed inside your user profile folder, go to [gitforwindows.org](https://gitforwindows.org/) and install git using the graphical installer. Make sure you uncheck the "Only show new options" and browse for your user profile folder as destination location (`C:\Users\<user_name>\Git`). The rest of the default options are just fine. I'm not sure why, but you might get still prompted to enter an admin password. If you decline this the installation will still start anyway. 

<p float="center">
  <img src="https://github.com/PetervanLunteren/EcoAssist/blob/main/imgs/Install_git_1.png" width=45% height="auto" />
  <img src="https://github.com/PetervanLunteren/EcoAssist/blob/main/imgs/Install_git_2.png" width=45% height="auto" />
</p>

### Step 3: Adjust install script
* Download [this file](https://PetervanLunteren.github.io/EcoAssist/Windows_install_EcoAssist.bat) and open it in a text editor (notepad is fine).
* Delete the following code which asks you for an admin password

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

* Change the location of the `EcoAssist_files` folder by changing `set LOCATION_ECOASSIST_FILES=%ProgramFiles%\EcoAssist_files` into `set LOCATION_ECOASSIST_FILES=%UserProfile%\EcoAssist_files`. 

* Delete the code which installs git
  ```batch
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
  
* And replace it with

  ```batch
  echo "No admin install -> Git is manually installed." | wtee -a "%LOG_FILE%"
  set PATH=%PATH%;"%UserProfile%\Git\cmd"
  ```

* Delete the code which installs anaconda

  ```batch
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
  ```

* And replace it with

  ```batch
  echo "No admin install -> Anaconda is manually installed." | wtee -a "%LOG_FILE%"
  set PATH=%PATH%;"%UserProfile%\Anaconda3\Scripts"
  ```
* Save the file, execute it and wait for it to finish.

### Step 4: Adjust the script to open EcoAssist
* Navigate to the hidden folder `C:\Users\<user_name>\EcoAssist_files\EcoAssist` and open `Windows_open_EcoAssist.bat` in a text editor.
* Just like you did with `Windows_install_EcoAssist.bat`, delete the code which asks you for an admin password and change the location of the `EcoAssist_files` folder.

### Step 5: Adjust the script to open LabelImg
* Open `Windows_open_LabelImg.bat` in a text editor and change the location of the `EcoAssist_files` folder. Here there is no code which asks you for an admin password, so no need to delete this.

## And that's it: you've bypassed administration privileges. You're good to go!
