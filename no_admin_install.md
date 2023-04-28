# Install EcoAssist without admin rights
You've been redirected here because you are trying to install EcoAssist without admin rights and you do not have git installed on your device. Follow the steps below to make sure you install git correctly.

### Step 1: Install
Go to [gitforwindows.org](https://gitforwindows.org/) and install git using the graphical installer. Leave all options as default, but make sure that:
* the "Only show new options" is unchecked
* the destination location is inside your user folder (`C:\Users\<user_name>\...`)
* "Adjusting your PATH environment" is set to the recommended setting

I'm not sure why, but you might still get prompted to enter an admin password. Just click "No" and the installation will start anyway.

<p float="center">
  <img src="https://github.com/PetervanLunteren/EcoAssist-metadata/blob/main/imgs/install-git-1.png" width=33% height="auto" />
  <img src="https://github.com/PetervanLunteren/EcoAssist-metadata/blob/main/imgs/install-git-2.png" width=33% height="auto" />
  <img src="https://github.com/PetervanLunteren/EcoAssist-metadata/blob/main/imgs/install-git-3.png" width=33% height="auto" />
</p>

### Step 2: Check
If all went well, git should be executable from the command line. Open a new command prompt window and run `git --version`. The install was succesfull if you see something in the lines of `git version 2.40.0.windows.1`. Something went wrong if you see `'git' is not recognized as an internal or external command, operable program or batch file`. In the latter case, run the graphical installer again and make sure you enable the recommended option under "Adjusting your PATH environment".

### Step 3: Proceed
You're all set. Start [the installation](https://github.com/PetervanLunteren/EcoAssist#windows-installation) for the begining as you did before.
