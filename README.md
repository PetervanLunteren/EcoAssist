<p align="center">
  <img src="https://github.com/PetervanLunteren/EcoAssist/blob/main/imgs/banner.png" width=100% height="auto" />
</p>
EcoAssist is an application designed to make life easier for wildlife ecologists who work with cameratrap data. I know how time consuming it can be to analyse every image. Thanks to the good people at <a href="https://github.com/microsoft/CameraTraps/blob/main/megadetector.md">MegaDetector</a>, there is a  model which can recognise animals in camera trap images in a variety of terrestrial ecosystems. The only problem with this model is that you need to know a bit of coding before you can use it. That is where EcoAssist comes in handy. It is a small program which makes it easy for everybody.

###
I've written this application in my spare time and would really appreciate it if users would let me know if they use it. You can contact me at [contact@pvanlunteren.com](mailto:contact@pvanlunteren.com). Please also help me to keep improving EcoAssist and let me know about any improvements, bugs, or new features so that I can keep it up-to-date.

## Features
* Find animals, persons and vehicles in both images and video's
* Separate files into subdirectories based on their detections
* Create .xml label files in Pascal VOC format for further processing
* Review and adjust annotations
* Manipulate data by visualising the detections
* Easily set parameters like threshold and checkpoint frequency
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

Camera trap images taken [Missouri camera trap database](https://lila.science/datasets/missouricameratraps). Photo of street taken from [pixabay](https://pixabay.com/photos/dog-classics-stray-pup-team-6135495/).

## Users
Here is a map of the users which have let me know that they're using EcoAssist. Are you also a user and not on this map? Let me know!
<p align="center">
  <img src="https://github.com/PetervanLunteren/EcoAssist/blob/main/imgs/users.jpg" width=60% height="auto" />
</p>

## How to download?
For now it is only available for OSX users. If you would like to run EcoAssist on your Windows or Linux computer, let me know! I'll see what I can do.

EcoAssist needs the open-source software [Anaconda](https://www.anaconda.com/products/individual) to run properly. The steps below will install Anaconda if not already installed on your computer. Please note that when you install EcoAssist it is expected the [license terms of Anaconda](https://legal.anaconda.com/policies/en/?name=end-user-license-agreements#ae-5) are agreed upon. 

If you're updating EcoAssist from v1 to v2, please read [the notes below](#updating-ecoassist-from-v1-to-v2) first.

1. Download [this file](https://minhaskamal.github.io/DownGit/#/home?url=https://github.com/PetervanLunteren/EcoAssist/blob/main/install_EcoAssist.command).
2. Unzip it and double click `install_EcoAssist.command`.
3. Go get youself a beverage because this might take a few minutes to complete.

## How to start the application?
EcoAssist will open when you double-click the file below.
```
 📁Applications
 └── 📁EcoAssist_files
     └── 📁EcoAssist
         └── 📄open_EcoAssist.command
```
You are free to move this file to a more convenient location. Just keep in mind that the folder structure and location of `EcoAssist_files` should not change.

## Updating EcoAssist from v1 to v2?
There are two points early adopters should take into account:
- Please make sure that the old EcoAssist files are deleted before installing version 2. So go ahead and delete the `~/EcoAssist_files` directory and the `open_EcoAssist.command` wherever you placed it. Don't worry if you forgot this prior to installing v2, it just means that you have two versions of EcoAssist installed. You can also delete it afterwards.
- Version 2 uses a different model to detect animals which is more accurate and 2.5 times faster. This new model uses the full range of confidence values much more than the old one did. So don't apply the thresholds you're accustomed to. Typical confidence thresholds for the new model are in the 0.15-0.25 range, instead of the old 0.7-0.8 range.

## GPU Support
It is possible to run EcoAssist on your GPU for faster processing (I just never tried it before). See [this page](https://github.com/petargyurov/megadetector-gui/blob/master/GPU_SUPPORT.md) for more information. You would probabaly be best off by installing EcoAssist following the steps above and afterwards adjusting the `ecoassistcondaenv` conda environment accordingly.

## How to uninstall EcoAssist?
You only have to do two things if you are fed up with EcoAssist and want to get rid of it.
1. Delete the `EcoAssist_files` folder in your applications;
2. Either i) [uninstall Anaconda](https://docs.anaconda.com/anaconda/install/uninstall/) as a whole with the command
`` rm -rf `conda info | grep 'base environment' | cut -d ':' -f 2 | xargs | cut -d ' ' -f 1` ``
or ii) keep the Anaconda installation and only delete the virtual environment with the command `conda env remove -n ecoassistcondaenv`.
