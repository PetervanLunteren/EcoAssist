[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7223363.svg)](https://doi.org/10.5281/zenodo.7223363)

<p align="center">
  <img src="https://github.com/PetervanLunteren/EcoAssist/blob/main/imgs/logo_large.png" width=60% height="auto" />
</p>

## Introduction
EcoAssist is an application designed to make life easier for people who want to work with object detection models. Thanks to the people at <a href="https://ultralytics.com/">Ultralytics</a>, it's possible to create models which can locate objects of your interest in images. The only problem is that you need to know a bit of coding before you can use it. That is where EcoAssist comes in handy. It's a no-code interface with a one-click install, which makes it easy for everybody. Annotate, train, and deploy your models without a single line of code.

I initially created EcoAssist with the aim of assisting ecological projects (hence the name), but it will handle any kind of object. If you’re not an ecologist and not interested in animals, you’ll just have to input images of your object of interest (blood cells, traffic signs, plant diseases - whatever you want) and ignore the references to the <a href="https://github.com/microsoft/CameraTraps/blob/main/megadetector.md">MegaDetector</a> model. The rest will be exactly the same.

I've written this application in my free evenings and would really appreciate it if people would let me know when it's used, and what for. You can contact me at [petervanlunteren@hotmail.com](mailto:petervanlunteren@hotmail.com). Please also help me to keep improving EcoAssist and let me know about any improvements, bugs, or new features so that I can keep it up-to-date.

## Demo
<p align="center">
  <img src="https://github.com/PetervanLunteren/EcoAssist/blob/main/imgs/demo.gif" width=60% height="auto" />
</p>

## Main features
* Runs on Windows, Mac, and Linux (no admin rights required)
* Train your model using the [YOLOv5](https://github.com/ultralytics/yolov5) architecture  
* Deploy your model on images or videos
* Annotate your data using the [labelImg](https://github.com/heartexlabs/labelImg) software
* Post-process your data to
  * separate
  * visualise
  * crop
  * label
  * export to .csv
* Install all dependencies with a single click
* GPU acceleration for NVIDIA and Apple Silicon
* Open-source, free and will always remain free

## Extra information for ecologists
EcoAssist comes with the <a href="https://github.com/microsoft/CameraTraps/blob/main/megadetector.md">MegaDetector</a> model preloaded. This model is trained to find animals, people, and vehicles in camera trap images - and does this really well. That means that you can deploy MegaDetector to find the images or videos which contain an animal, and filter out the empties. There's also a possibility to further process the images in [Timelapse](https://saul.cpsc.ucalgary.ca/timelapse/).

Unfortunately, MegaDetector does not identify the animals, it just finds them. There is no model that can identify all species on earth. If you want a species classifier for your specific ecosystem or project, you'll have to train it yourself. In EcoAssist you can easily transfer knowledge from MegaDetector to your own species classifier to save you tremendous amounts of data and time.

To sum up:
* Use <a href="https://github.com/microsoft/CameraTraps/blob/main/megadetector.md">MegaDetector</a> to tag animals and filter out the empty images/videos
* Create input files for further processing in [Timelapse](https://saul.cpsc.ucalgary.ca/timelapse/)
* Easily create your own species classifier by transfer-learning from MegaDetector

## Teasers
<p align="center">
  <img src="https://github.com/PetervanLunteren/EcoAssist/blob/main/imgs/teaser_animal.jpg" width=45% height="auto" />
  <img src="https://github.com/PetervanLunteren/EcoAssist/blob/main/imgs/teaser_red_fox.JPG" width=45% height="auto" />
  <img src="https://github.com/PetervanLunteren/EcoAssist/blob/main/imgs/teaser_ocelot.JPG" width=45% height="auto" /> 
  <img src="https://github.com/PetervanLunteren/EcoAssist/blob/main/imgs/teaser_tinamou.JPG" width=45% height="auto" /> 
</p>

Camera trap images taken from the [Missouri camera trap database](https://lila.science/datasets/missouricameratraps) and the [WCS Camera Traps dataset](https://lila.science/datasets/wcscameratraps).

## Users
Here is a map of the users which have let me know that they're using EcoAssist. Are you also a user and not on this map? [Let me know](mailto:petervanlunteren@hotmail.com)!
<p align="center">
  <img src="https://github.com/PetervanLunteren/EcoAssist/blob/main/imgs/users.jpg" width=60% height="auto" />
</p>

## Quick links
1. [Requirements](#requirements)
2. [Download](#download)
3. [Update](#update)
4. [GPU support](#gpu-support)
5. [Cite](#cite)
6. [Uninstall](#uninstall)
7. [Code contributors](#code-contributors)

## Requirements
There are no hard system requirements for EcoAssist since it is largely hardware-agnostic, but please note that machine learning can ask quite a lot from your computer in terms of processing power. I would recommend at least 8 GB of RAM, but preferably 16 or 32 GB. Although it will run on an old laptop only designed for text editing, it’s probably not going to train any accurate models. Generally speaking, the faster the machine, the more reliable the results. GPU acceleration is a big bonus. If you don’t know whether your computer can handle EcoAssist, I would recommend to just try it out - [uninstalling](#how-to-uninstall-ecoassist) EcoAssist is as simple as deleting a folder.

## Download
EcoAssist will install quite a lot of dependencies, so don't panic if the installation takes 10-20 minutes and generates lots of textual feedback as it does so. Please note that antivirus, VPN or other protection software might interfere with the installation. If you're having trouble, please disable this protection software for the duration of the installation.

Opening EcoAssist for the first time will take a bit longer than usual due to script compiling. Have patience, all subsequent times will be better.

#### Windows installation
1. Download [this file](https://PetervanLunteren.github.io/EcoAssist/install.bat) and double-click it. If that doesn't work, you can drag and drop it in a command prompt window and press enter.
2. When the installation is finished, there will be a shortcut file in the same folder as your installation file (so probably `Downloads`). You are free to move this file to a more convenient location. EcoAssist will open when double-clicked.

#### Mac installation
1. Download and open [this file](https://PetervanLunteren.github.io/EcoAssist/install.command). Some computers can be quite reluctant when having to open command files downloaded from the internet. You can circumvent trust issues by opening it with right-click > open > open. If that still doesn't work, you can change the file permissions by opening a new terminal window and copy-pasting the following commands.
```bash
chmod 755 $HOME/Downloads/install.command
bash $HOME/Downloads/install.command
```
2. If you're an Apple Silicon user (M1/M2), go for a nice walk because this may take about 30 minutes to complete. Some of the software packages are not yet adopted to the Apple Silicon processor. There is a workaround, but it takes some time. In order to make MegaDetector work on Apple Silicon computers, the guys at [AI for Earth](https://www.microsoft.com/en-us/ai/ai-for-earth) had to re-build the model with *slightly* different results. The bounding boxes appear to be the same to around two decimal places in both location and confidence, which is good, but not *exactly* the same. Please keep in mind that this is an unvalidated version of MegaDetector, and they don't exactly know how it compares to the validated version since it is much less tested.
4. When the installation is done, you'll find a `EcoAssist.command` file in your `Applications` folder. The app will open when double-clicked. You are free to move this file to a more convenient location. If you want EcoAssist in your dock, manually change `EcoAssist.command` to `EcoAssist.app`, then drag and drop it in your dock and change it back to `EcoAssist.command`. Not the prettiest solution, but it works...

#### Linux installation
1. Download [this file](https://PetervanLunteren.github.io/EcoAssist/install.command).
2. Change the permission of the file and execute it by running the following commands in a new terminal window. If you don't have root privileges, you might be prompted for a password to install `libxcb-xinerama0`. This package is required for the labelImg software on some Linux versions. If you don't know the `sudo` password, you can skip this by pressing Ctrl+D when you are prompted for the password. EcoAssist will still work fine without it, but you might have problems with the labelImg software. The rest of the installation can be done without root privileges.
```bash
chmod 755 $HOME/Downloads/install.command
bash $HOME/Downloads/install.command
```
3. During the installation, a file called `EcoAssist` will be created on your desktop. The app will open when double-clicked. You are free to move this file to a more convenient location.

## Update
To update to the latest version, you'll have to repeat the [download](#download) procedure. It will replace all the old files and packages with the new ones. It's all automatic, you don't have to do anything.

## GPU support
EcoAssist will automatically run on GPU if available. The appropriate `CUDAtoolkit` and `cuDNN` software is already included in the EcoAssist installation for Windows and Linux. If you have `NVIDIA` GPU available but it doesn't recognise it, make sure you have a [recent driver](https://www.nvidia.com/en-us/geforce/drivers/) installed, then reboot. An `MPS` compatible version of `Pytorch` is included in the installation for Apple Silicon users. Please note that applying machine learning on Apple Silicon GPU's is still under beta version. That means that you might run into errors when trying to run on GPU. My experience is that deployment runs smoothly on GPU, but training throws errors. Training on CPU will of course still work. The progress window and console output will display whether EcoAssist is running on CPU or GPU. 

<p align="center">
  <img src="https://github.com/PetervanLunteren/EcoAssist/blob/main/imgs/progress_window.png" width=50% height="auto" >
  <img src="https://github.com/PetervanLunteren/EcoAssist/blob/main/imgs/Training_on_GPU.png" width=90% height="auto" >
</p>

## Citations
#### EcoAssist citation
If you used EcoAssist in your research, please use the following citation.
```BibTeX
@software{van_Lunteren_EcoAssist_2022,
  title     = {{EcoAssist: An application for detecting animals in camera trap images using the MegaDetector model}},
  author    = {van Lunteren, Peter},
  year      = {2022},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.7223363},
  url       = {https://github.com/PetervanLunteren/EcoAssist}
}
```

#### MegaDetector citation
If you used the MegaDetector model to analyse images or retrain your model, please use the following citation.
```BibTex
@article{beery2019efficient,
  title     = {Efficient Pipeline for Camera Trap Image Review},
  author    = {Beery, Sara and Morris, Dan and Yang, Siyu},
  journal   = {arXiv preprint arXiv:1907.06772},
  year      = {2019}
}
```

## Uninstall
All files are located in one folder, called `EcoAssist_files`. You can uninstall EcoAssist by simply deleting this folder. Please be aware that it's hidden, so you'll probably have to adjust your settings before you can see it.
```r
# windows
─── 📁Users
    └── 📁<username>
        └── 📁EcoAssist_files

# mac
─── 📁Applications
    └── 📁.EcoAssist_files

# linux
─── 📁home
    └── 📁<username>
        └── 📁.EcoAssist_files
```


## Code contributors
<a href="https://github.com/PetervanLunteren/EcoAssist/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=PetervanLunteren/EcoAssist" />
</a>

###
Please feel free to fork this repo and submit fixes, improvements or add new features.
