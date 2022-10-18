<p align="center">
  <img src="https://github.com/PetervanLunteren/EcoAssist/blob/main/imgs/banner.png" width=100% height="auto" />
</p>

EcoAssist is an application designed to make life easier for wildlife ecologists who work with cameratrap data. I know how time-consuming it can be to analyse every image. Thanks to the good people at <a href="https://github.com/microsoft/CameraTraps/blob/main/megadetector.md">MegaDetector</a>, there is a  model which can recognise animals in camera trap images in a variety of terrestrial ecosystems so that you don't have to wade through all the empty images. The only problem with this model is that you need to know a bit of coding before you can use it. That is where EcoAssist comes in handy. It's a small program which makes it easy for everybody.

###
I've written this application in my free evenings and would really appreciate it if people would let me know when it's used. You can contact me at [petervanlunteren@hotmail.com](mailto:petervanlunteren@hotmail.com). Please also help me to keep improving EcoAssist and let me know about any improvements, bugs, or new features so that I can keep it up-to-date.

## Features
* Use the `MDv5` model to tag animals, persons and vehicles in both images and video's
* Filter out empty images, people, vehicles or animals
* Review and edit annotations using the open-source annotation software [labelImg](https://github.com/heartexlabs/labelImg)
* Export `.xml` label files in Pascal VOC format for further model training
* Manipulate data by drawing boxes or cropping detections
<br/>

## Demo
<p align="center">
  <img src="https://github.com/PetervanLunteren/EcoAssist/blob/main/imgs/demo.gif" width=60% height="auto" />
</p>

## Example detections
<p float="center">
  <img src="https://github.com/PetervanLunteren/EcoAssist/blob/main/imgs/example_1.jpg" width=49.7% height="auto" />
  <img src="https://github.com/PetervanLunteren/EcoAssist/blob/main/imgs/example_2.jpg" width=49.7% height="auto" />
  <img src="https://github.com/PetervanLunteren/EcoAssist/blob/main/imgs/example_3.jpg" width=49.7% height="auto" /> 
  <img src="https://github.com/PetervanLunteren/EcoAssist/blob/main/imgs/example_4.jpg" width=49.7% height="auto" /> 
</p>

Camera trap images taken from [Missouri camera trap database](https://lila.science/datasets/missouricameratraps). Photo of street taken from [pixabay](https://pixabay.com/photos/dog-classics-stray-pup-team-6135495/).

## Users
Here is a map of the users which have let me know that they're using EcoAssist. Are you also a user and not on this map? [let me know](mailto:petervanlunteren@hotmail.com)!
<p align="center">
  <img src="https://github.com/PetervanLunteren/EcoAssist/blob/main/imgs/users.jpg" width=60% height="auto" />
</p>

## How to download/update?
### General information
EcoAssist needs the open-source software [Anaconda](https://www.anaconda.com/products/individual) to run properly. The steps below will install Anaconda if not already installed on your computer. Please note that when you install EcoAssist it is expected the [license terms of Anaconda](https://legal.anaconda.com/policies/en/?name=end-user-license-agreements#ae-5) are agreed upon.

### Windows installation
Download and double-click [this file](https://PetervanLunteren.github.io/EcoAssist/Windows_install_EcoAssist.bat). [Git](https://gitforwindows.org/) and [Anaconda](https://www.anaconda.com/products/individual) will be installed via graphical installers if it's not already installed. If you don't know what you are doing - the default options are just fine. 

*Note: EcoAssist is not yet extensively tested on Windows computers. If you find any problems or everything works perfectly, [let me know](mailto:petervanlunteren@hotmail.com)!*

### Mac installation
1. Download and open [this file](https://PetervanLunteren.github.io/EcoAssist/MacOS_Linux_install_EcoAssist.command). Some computers can be quite reluctant when having to open command files downloaded from the internet. You can circumvent trust issues by opening it with right-click > open > open. If that still doesn't work you can change the file permissions by opening a new terminal window and copy-pasting `chmod 755 $HOME/Downloads/MacOS_Linux_install_EcoAssist.command`. Then try again.
2. Go get yourself a beverage because this might take a few minutes to complete. Especially for M1 users since some of the software packages are not yet adopted to the M1 processor. There is a workaround, but it takes some time. Please be patient and wait until you see a message saying the process is completed.

*Note: EcoAssist is not yet extensively tested on M1 macs. If you find any problems or everything works perfectly, please [let me know](mailto:petervanlunteren@hotmail.com)!*

### Linux installation
1. Download [this file](https://PetervanLunteren.github.io/EcoAssist/MacOS_Linux_install_EcoAssist.command).
2. Change the permission of the file and execute it. You can do that by opening a new terminal window and copy-pasiting the commands below. If you don't have root privileges you might be prompted for a password to install `libxcb-xinerama0`. This package is required for the labelImg software to use properly on some Linux versions. If you don't know the `sudo` password you can skip this by pressing Ctrl+D when you are prompted for the password. EcoAssist will still work fine without it but you might have problems with the labelImg software. The rest of the installation can be done without root privileges.
```bash
chmod 755 $HOME/Downloads/MacOS_Linux_install_EcoAssist.command
bash $HOME/Downloads/MacOS_Linux_install_EcoAssist.command
```
*Note: EcoAssist is not yet extensively tested on Linux computers. If you find any problems or everything works perfectly, please [let me know](mailto:petervanlunteren@hotmail.com)!*

## How to start the application?
### Windows and Linux
```
 📁Desktop
 └── 📄EcoAssist
```
EcoAssist will open when you double-click the file above. You are free to move this file to a more convenient location.

### Mac
```
 📁Applications
 └── 📄EcoAssist.command
```
EcoAssist will open when you double-click the file above. You are free to move this file to a more convenient location. If you want EcoAssist in your dock, manually change `EcoAssist.command` to `EcoAssist.app`, then drag and drop it in your dock and change it back to `EcoAssist.command`. Not the prettiest solution, but it works...

## GPU Support
EcoAssist will automatically run on your GPU if you have the proper hardware and `NVIDIA` drivers. See [this page](https://github.com/petargyurov/megadetector-gui/blob/master/GPU_SUPPORT.md) for more information. Whether it is running on CPU or GPU will be displayed in the progress window. The approproate `CUDA` software is included in the EcoAssist installation for Windows and Linux, but unfortunately not for Mac users. Mac users with compatible GPU and drivers will be best off by installing EcoAssist normally and afterwards installing the proper software into the `ecoassistcondaenv` conda environment.

*Note: EcoAssist hasn't been tested on a GPU accelerated computer. I know it should work, but I just never had the opportunity to test it. Please [let me know](mailto:petervanlunteren@hotmail.com) if you tried it.*

<p align="center">
  <img src="https://github.com/PetervanLunteren/EcoAssist/blob/main/imgs/progress_window.png" width=30% height="auto" >
</p>

## Citation
If you use EcoAssist in you research, don't forget to cite the engine behind EcoAssist.
```BibTeX
@article{beery2019efficient,
  title={Efficient Pipeline for Camera Trap Image Review},
  author={Beery, Sara and Morris, Dan and Yang, Siyu},
  journal={arXiv preprint arXiv:1907.06772},
  year={2019}
}
```

## How to uninstall EcoAssist?
Mac and Linux users can uninstall EcoAssist by executing [this file](https://PetervanLunteren.github.io/EcoAssist/MacOS_Linux_uninstall_EcoAssist.command).  Windows users can uninstall it with [this file](https://PetervanLunteren.github.io/EcoAssist/Windows_uninstall_EcoAssist.bat). It will prompt you whether you want to uninstall Anaconda too. You can just type `y` or `n`.
