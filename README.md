[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7223363.svg)](https://doi.org/10.5281/zenodo.7223363)


<p align="center">
  <img src="https://github.com/PetervanLunteren/EcoAssist/blob/main/imgs/banner.png" width=100% height="auto" />
</p>

EcoAssist is an application designed to make life easier for wildlife ecologists who work with camera trap data. I know how time-consuming it can be to analyse every image. Thanks to the good people at <a href="https://github.com/microsoft/CameraTraps/blob/main/megadetector.md">MegaDetector</a>, there is a  model which can recognise animals in camera trap images in a variety of terrestrial ecosystems so that you don't have to wade through all the empty images. The only problem with this model is that you need to know a bit of coding before you can use it. That is where EcoAssist comes in handy. It's a no-code interface which makes it easy for everybody.

###
I've written this application in my free evenings and would really appreciate it if people would let me know when it's used. You can contact me at [petervanlunteren@hotmail.com](mailto:petervanlunteren@hotmail.com). Please also help me to keep improving EcoAssist and let me know about any improvements, bugs, or new features so that I can keep it up-to-date.

## Features
* Use the `MDv5` model to tag animals, persons and vehicles in both images and video's
* Filter out empty images, people, vehicles or animals
* Review and edit annotations using the open-source annotation software [labelImg](https://github.com/heartexlabs/labelImg)
* Create input file for further processing in [Timelapse](https://saul.cpsc.ucalgary.ca/timelapse/)
* Export `.xml` label files in Pascal VOC format for further model training
* Manipulate data by drawing boxes or cropping detections
<br/>

## Demo
<p align="center">
  <img src="https://github.com/PetervanLunteren/EcoAssist/blob/main/imgs/demo.gif" width=60% height="auto" />
</p>

## Example detections
<p float="center">
  <img src="https://github.com/PetervanLunteren/EcoAssist/blob/main/imgs/example_1.jpg" width=45% height="auto" />
  <img src="https://github.com/PetervanLunteren/EcoAssist/blob/main/imgs/example_2.jpg" width=45% height="auto" />
  <img src="https://github.com/PetervanLunteren/EcoAssist/blob/main/imgs/example_3.jpg" width=45% height="auto" /> 
  <img src="https://github.com/PetervanLunteren/EcoAssist/blob/main/imgs/example_4.jpg" width=45% height="auto" /> 
</p>

Camera trap images taken from [Missouri camera trap database](https://lila.science/datasets/missouricameratraps). Photo of street taken from [pixabay](https://pixabay.com/photos/dog-classics-stray-pup-team-6135495/).

## Users
Here is a map of the users which have let me know that they're using EcoAssist. Are you also a user and not on this map? [Let me know](mailto:petervanlunteren@hotmail.com)!
<p align="center">
  <img src="https://github.com/PetervanLunteren/EcoAssist/blob/main/imgs/users.jpg" width=60% height="auto" />
</p>

## Download
### General information
EcoAssist needs the open-source software [Anaconda](https://www.anaconda.com/products/individual) to run properly. The steps below will install Anaconda if not already installed on your computer. When you install EcoAssist it is expected the [license terms of Anaconda](https://legal.anaconda.com/policies/en/?name=end-user-license-agreements#ae-5) are agreed upon.

*Note: EcoAssist is not yet extensively tested. If you find any problems or - hopefully - everything works perfect, [let me know](mailto:petervanlunteren@hotmail.com)!*

### Windows installation
Download [this file](https://PetervanLunteren.github.io/EcoAssist/Windows_install_EcoAssist.bat) and double-click it. If that doesn't work you can drag and drop it in a command prompt window and press enter. If you don't have admin rights, it will prompt you for an admin password because it needs access to the `C:\` drive to search for anaconda. It's possible to install EcoAssist without admin rights, but then the scripts will need some tweaking. [Email me](mailto:petervanlunteren@hotmail.com) if you want help with that. [Git](https://gitforwindows.org/) and [Anaconda](https://www.anaconda.com/products/individual) will be installed via graphical installers if it's not already installed. If you don't understand all the options prompted during these installations - the default options are just fine.

### Mac installation
1. Download and open [this file](https://PetervanLunteren.github.io/EcoAssist/MacOS_Linux_install_EcoAssist.command). Some computers can be quite reluctant when having to open command files downloaded from the internet. You can circumvent trust issues by opening it with right-click > open > open. If that still doesn't work you can change the file permissions by opening a new terminal window and copy-pasting `chmod 755 $HOME/Downloads/MacOS_Linux_install_EcoAssist.command`. Then try again.
2. Go get yourself a beverage because this might take a few minutes to complete. Especially for M1 users since some of the software packages are not yet adopted to the M1 processor. There is a workaround, but it takes some time. Please be patient and wait until you see a message saying the process is completed.

### Linux installation
1. Download [this file](https://PetervanLunteren.github.io/EcoAssist/MacOS_Linux_install_EcoAssist.command).
2. Change the permission of the file and execute it. You can do that by opening a new terminal window and copy-pasting the commands below. If you don't have root privileges, you might be prompted for a password to install `libxcb-xinerama0`. This package is required for the labelImg software on some Linux versions. If you don't know the `sudo` password, you can skip this by pressing Ctrl+D when you are prompted for the password. EcoAssist will still work fine without it, but you might have problems with the labelImg software. The rest of the installation can be done without root privileges.
```bash
chmod 755 $HOME/Downloads/MacOS_Linux_install_EcoAssist.command
bash $HOME/Downloads/MacOS_Linux_install_EcoAssist.command
```

## Update
You can update EcoAssist by following the same process described [above](https://github.com/PetervanLunteren/EcoAssist#download). The installation file will automatically update it to the latest version.

## Start the application
EcoAssist will open when double-clicked the file described below. You are free to move this file to a more convenient location. 
### Windows
```
 📁Downloads
 └── 📄EcoAssist
```
This file will be created in the same folder as your installation file (so probably `Downloads`). Because it needs access the EcoAssist folder (which is located on the `C:\` drive), you'll need admin rights to open EcoAssist. If you don't already have admin rights, you will be prompted for an admin password. If you get sick of entering a password every time you open EcoAssist, just switch to a user with admin rights and find the shortcut file from there. Or [email me](mailto:petervanlunteren@hotmail.com) for instructions to install EcoAssist without the need for admin rights. 
### Mac
```
 📁Applications
 └── 📄EcoAssist
```
If you want EcoAssist in your dock, manually change `EcoAssist.command` to `EcoAssist.app`, then drag and drop it in your dock and change it back to `EcoAssist.command`. Not the prettiest solution, but it works...

### Linux
```
 📁Desktop
 └── 📄EcoAssist
```

## GPU Support
EcoAssist will automatically run on Windows and Linux if compatible `CUDA` GPU is available with a recently installed `NVIDIA` driver. See [this page](https://github.com/petargyurov/megadetector-gui/blob/master/GPU_SUPPORT.md) prepared by Petar Gyurov for more information. The appropriate `CUDAtoolkit` and `cuDNN` software is already included in the EcoAssist installation for Windows and Linux, so no further action is required. However, this software is not included for Mac users, since `NVIDIA` GPU's are not available on Macs. Mac users with other compatible GPU will be best off by installing EcoAssist normally and afterwards installing the proper software for their GPU into the `ecoassistcondaenv` conda environment. It should then automatically run on GPU. The progress window will display whether EcoAssist is running on CPU or GPU.

<p align="center">
  <img src="https://github.com/PetervanLunteren/EcoAssist/blob/main/imgs/progress_window.png" width=40% height="auto" >
</p>

## Citation
If you use EcoAssist in your research, don't forget to cite the engine behind EcoAssist ([MegaDetector](https://github.com/microsoft/CameraTraps/blob/main/megadetector.md)) and the EcoAssist software itself.
```BibTeX
@article{beery2019efficient,
  title     = {Efficient Pipeline for Camera Trap Image Review},
  author    = {Beery, Sara and Morris, Dan and Yang, Siyu},
  journal   = {arXiv preprint arXiv:1907.06772},
  year      = {2019}
}

@software{van_Lunteren_EcoAssist_2022,
  title     = {{EcoAssist: An application for detecting animals in camera trap images using the MegaDetector model}},
  author    = {van Lunteren, Peter},
  year      = {2022},
  doi       = {10.5281/zenodo.7223363},
  url       = {https://github.com/PetervanLunteren/EcoAssist}
}
```


## How to uninstall EcoAssist?
Mac and Linux users can uninstall EcoAssist by executing [this file](https://PetervanLunteren.github.io/EcoAssist/MacOS_Linux_uninstall_EcoAssist.command).  Windows users can uninstall it with [this file](https://PetervanLunteren.github.io/EcoAssist/Windows_uninstall_EcoAssist.bat). It will prompt you whether you want to uninstall Anaconda too. You can just type `y` or `n`.
