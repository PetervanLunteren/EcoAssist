[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7223363.svg)](https://doi.org/10.5281/zenodo.7223363)


<p align="center">
  <img src="https://github.com/PetervanLunteren/EcoAssist/blob/main/imgs/logo_large.png" width=50% height="auto" />
</p>

EcoAssist is an application designed to make life easier for people who want to work with object detection models. Thanks to the good people at <a href="https://ultralytics.com/">Ultralytics</a>, it is possible to train your own custom model to detect objects in images and videos. The only problem is that you need to know a bit of coding before you can use it. That is where EcoAssist comes in handy. It's a no-code interface with a one-click install, which makes it easy for everybody. Here you can annotate, train, and deploy your models **without a single line of code**.

I initially created EcoAssist with the aim of training species classifiers to assist ecological projects (hence the name), but it will train and deploy any kind of object detection model. If you’re not an ecologist, you’ll just have to ignore the references to the <a href="https://github.com/microsoft/CameraTraps/blob/main/megadetector.md">MegaDetector</a> model and select images of your object of interest. The rest will work exactly the same.

<!---
EcoAssist is an application designed to make life easier for wildlife ecologists who work with camera trap data. Thanks to the good people at <a href="https://github.com/microsoft/CameraTraps/blob/main/megadetector.md">MegaDetector</a>, there is a  model which can recognise animals in camera trap images in a variety of terrestrial ecosystems, so that you can e.g., filter out empty images, use its results in image analysers such as <a href="https://saul.cpsc.ucalgary.ca/timelapse/">Timelapse</a>, or kick-start the training of your own species classifier. The only problem with using this model is that you need to know a bit of coding before you can use it. That is where EcoAssist comes in handy. It's a no-code interface with a one-click install, which makes it easy for everybody.

###
I've written this application in my free evenings and would really appreciate it if people would let me know when it's used. You can contact me at [petervanlunteren@hotmail.com](mailto:petervanlunteren@hotmail.com). Please also help me to keep improving EcoAssist and let me know about any improvements, bugs, or new features so that I can keep it up-to-date.
--->

## Features
* Use either `MDv5a` or `MDv5b` to tag animals, persons and vehicles in both images and video's
* Filter out empty images, people, vehicles or animals
* Review and edit annotations using the open-source annotation software [labelImg](https://github.com/heartexlabs/labelImg)
* Create input file for further processing in [Timelapse](https://saul.cpsc.ucalgary.ca/timelapse/)
* Export `.xml` label files in Pascal VOC format for further model training
* Manipulate data by drawing boxes or cropping detections
* Use custom models trained from `MDv5` using transfer learning
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

## Quick links
1. [Download](#download)
2. [Update](#update)
3. [GPU support](#gpu-support)
4. [Custom model support](#custom-model-support)
5. [Citation](#citation)
6. [How to uninstall EcoAssist](#how-to-uninstall-ecoassist)
7. [Code contributors](#code-contributors)

## Download
EcoAssist needs [Anaconda](https://www.anaconda.com/products/individual), [Git](https://git-scm.com/) and a bunch of other open-source software to run properly. The installation files linked in the steps below will check if these software packages are already present on your computer, and install them if needed. Since EcoAssist will install quite a lot of Python stuff, don't panic if the installation takes 10-20 minutes (depending on your internet connection and RAM) and generates lots of textual feedback as it does so. Somewhere during the installation, there will be a message saying that you need to update anaconda (`Please update conda by running $ conda update -n base -c defaults conda`). That is just Anaconda saying there is a new version available. You can ignore that. Futhermore, some anti-virus, VPN or other protection software enabled during the EcoAssist installation might block the download of some files. If you're having trouble, please disable this protection software during the EcoAssist installation.

### Windows installation
1. Download [this file](https://PetervanLunteren.github.io/EcoAssist/install.bat) and double-click it. If that doesn't work, you can drag and drop it in a command prompt window and press enter. If you don't have admin rights, it will prompt you for an admin password because it needs access to the `C:\` drive. Don't have an admin password? See [these instructions](https://github.com/PetervanLunteren/EcoAssist/blob/main/Windows_no_admin_install.md) to install it without admin privileges. [Git](https://gitforwindows.org/) and [Anaconda](https://www.anaconda.com/products/individual) will be installed via graphical installers if it's not already installed. If you don't understand all the options prompted during these installations - the default options are just fine.
2. When the installation is finished, there will be a shortcut file in the same folder as your installation file (so probably `Downloads`). You are free to move this file to a more convenient location. EcoAssist will open when double-clicked.

### Mac installation
1. Download and open [this file](https://PetervanLunteren.github.io/EcoAssist/install.command). Some computers can be quite reluctant when having to open command files downloaded from the internet. You can circumvent trust issues by opening it with right-click > open > open. If that still doesn't work, you can change the file permissions by opening a new terminal window and copy-pasting the following commands.
```bash
chmod 755 $HOME/Downloads/install.command
bash $HOME/Downloads/install.command
```
2. If you're a M1/M2 user, go for a nice walk outside because this may take about 30 minutes to complete. Some of the software packages are not yet adopted to the M1/M2 processor. There is a workaround, but it takes some time. In order to make it work on M1/M2 computers, the guys at MegaDetector had to re-build the models with *slightly* different results. The bounding boxes appear to be the same to around two decimal places in both location and confidence, which is good, but not *exactly* the same. Please keep in mind that this is an unvalidated version of MegaDetector, and they don't exactly know how it compares to the validated version since it is much less tested.
3. When the installation is done, you'll find a `EcoAssist.command` file in your `Applications` folder. The app will open when double-clicked. You are free to move this file to a more convenient location. If you want EcoAssist in your dock, manually change `EcoAssist.command` to `EcoAssist.app`, then drag and drop it in your dock and change it back to `EcoAssist.command`. Not the prettiest solution, but it works...

### Linux installation
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
EcoAssist will automatically run on Windows and Linux if compatible `CUDA` GPU is available with a recently installed `NVIDIA` driver. See [this page](https://github.com/petargyurov/megadetector-gui/blob/master/GPU_SUPPORT.md) prepared by [Petar Gyurov](https://github.com/petargyurov) for more information. The appropriate `CUDAtoolkit` and `cuDNN` software is already included in the EcoAssist installation for Windows and Linux, so no further action is required. However, this software is not included for Mac users, since `NVIDIA` GPU's are not available on Macs. Mac users with other compatible GPU can install the proper software for their GPU into the `ecoassistcondaenv` conda environment. It should then automatically run on GPU. The progress window will display whether EcoAssist is running on CPU or GPU.

<p align="center">
  <img src="https://github.com/PetervanLunteren/EcoAssist/blob/main/imgs/progress_window.png" width=40% height="auto" >
</p>

## Custom model support
EcoAssist can run custom `yolov5` models if they are retrained from the MegaDetector model using transfer learning. For example, if you find that MegaDetector is not great at recognising a certain species as "animal", you can retrain the model and add some labelled data of the cases you want it to improve on. You can also expand on the three default classes ("animal", "person" and "vehicle") and train the model to detect custom classes (e.g. "species A" and "species B"). Want to know how to train your own model? See [this tutorial](https://www.kaggle.com/code/evmans/train-megadetector-tutorial) created by [ehallein](https://github.com/ehallein).

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
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.7223363},
  url       = {https://github.com/PetervanLunteren/EcoAssist}
}
```

## How to uninstall EcoAssist?
Mac and Linux users can uninstall EcoAssist by executing [this file](https://PetervanLunteren.github.io/EcoAssist/MacOS_Linux_uninstall_EcoAssist.command).  Windows users can uninstall it with [this file](https://PetervanLunteren.github.io/EcoAssist/Windows_uninstall_EcoAssist.bat). It will prompt you whether you want to uninstall Anaconda too. You can just type `y` or `n`.

## Code contributors
<a href="https://github.com/PetervanLunteren/EcoAssist/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=PetervanLunteren/EcoAssist" />
</a>

###
Please feel free to fork this repo and submit fixes, improvements or add new features. Thanks:
* [ehallein](https://github.com/ehallein) for building and testing the custom model feature
