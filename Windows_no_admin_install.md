# Windows installation without administrator privileges
EcoAssist needs admin rights because it requires access to the `EcoAssist_files` folder and the `Anaconda3` installation, which are not in your user profile folder. If we want to be able to install and open EcoAssist without admin rights, we basically have to make sure we don't have to touch anything outside your user profile folder. We can do that with some tweaking of the scripts and a manual anaconda installation.

### Step 1: Anaconda
Go to www.anaconda.com and install anaconda using the graphical installer. Make sure you install it for your user only (and thus inside your user profile folder).

<p float="center">
  <img src="https://github.com/PetervanLunteren/EcoAssist/blob/main/imgs/Install_anaconda_1.png" width=33% height="auto" />
  <img src="https://github.com/PetervanLunteren/EcoAssist/blob/main/imgs/Install_anaconda_2.png" width=33% height="auto" />
  <img src="https://github.com/PetervanLunteren/EcoAssist/blob/main/imgs/Install_anaconda_3.png" width=33% height="auto" /> 
</p>

### Step 2: Install script
Download [this file](https://PetervanLunteren.github.io/EcoAssist/Windows_install_EcoAssist.bat) but don't execute it. 

### Step 3
