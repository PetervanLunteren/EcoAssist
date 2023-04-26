# Install EcoAssist without admin rights
It's possible to install EcoAssist without admin rights. Actually, the only thing in the normal install requiring admin rights is git for windows. When you install git prior to installing EcoAssist, everything should work without problems.

### Step 1: Download
First you'll need to install (a specfic version of) git. Click on the links below to start the download for your OS bit version (i.e., 32 or 64 bits). Don't know what OS bit version you are running? Check it [here](https://toolster.net/os_bit_checker).

* [Git for windows - 32-bit](https://github.com/git-for-windows/git/releases/download/v2.35.1.windows.2/Git-2.35.1.2-32-bit.exe)
* [Git for windows - 64 bit](https://github.com/git-for-windows/git/releases/download/v2.35.1.windows.2/Git-2.35.1.2-64-bit.exe)

### Step 2: Install
Execute the graphical installer and leave all options as default, but make sure that:
* the "Only show new options" is unchecked
* the destination location is inside your user folder (`C:\Users\<user_name>\...`)
* "Adjusting your PATH environment" is set to the recommended setting

I'm not sure why, but you might still get prompted to enter an admin password. Just click "No" and the installation will start anyway.

<p float="center">
  <img src="https://github.com/PetervanLunteren/EcoAssist-metadata/blob/main/imgs/install-git-1.png" width=33% height="auto" />
  <img src="https://github.com/PetervanLunteren/EcoAssist-metadata/blob/main/imgs/install-git-2.png" width=33% height="auto" />
  <img src="https://github.com/PetervanLunteren/EcoAssist-metadata/blob/main/imgs/install-git-3.png" width=33% height="auto" />
</p>

### Step 3: Check
If all went well, git should be executable from the command line. Open a new command prompt window and run `git --version`. The install was succesfull if you see `git version 2.35.1.windows.2`. Something went wrong if you see `'git' is not recognized as an internal or external command, operable program or batch file`. In the latter case, run the graphical installer again and make sure you enable the recommended option under "Adjusting your PATH environment".

### Step 4: Proceed
You're all set. Proceed with [the installation](https://github.com/PetervanLunteren/EcoAssist#windows-installation).
