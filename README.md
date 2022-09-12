<p align="center">
  <img src="https://github.com/PetervanLunteren/EcoAssist/blob/main/imgs/banner.png" width=100% height="auto" />
</p>

*UPDATE August 2022: EcoAssist 2.0 has now adopted the new MegaDetector MDv5 model which is more accurate and about 2.5 times faster than the old one.*

EcoAssist is an application designed to make life easier for wildlife ecologists who work with cameratrap data. I know how time-consuming it can be to analyse every image. Thanks to the good people at <a href="https://github.com/microsoft/CameraTraps/blob/main/megadetector.md">MegaDetector</a>, there is a  model which can recognise animals in camera trap images in a variety of terrestrial ecosystems so that you don't have to wade through all the empty images. The only problem with this model is that you need to know a bit of coding before you can use it. That is where EcoAssist comes in handy. It's a small program which makes it easy for everybody.

###
I've written this application in my free evenings and would really appreciate it if people would let me know when it's used. You can contact me at [contact@pvanlunteren.com](mailto:contact@pvanlunteren.com). Please also help me to keep improving EcoAssist and let me know about any improvements, bugs, or new features so that I can keep it up-to-date.

## Features
* Find animals, persons and vehicles in both images and video's
* Separate files into sub directories based on their detections
* Create .xml label files in Pascal VOC format for further processing
* Review and adjust annotations
* Manipulate data by visualising or cropping the detections
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
For now, it is only available for OSX users. If you would like to run EcoAssist on your Windows or Linux computer, let me know! I'll see what I can do.

EcoAssist needs the open-source software [Anaconda](https://www.anaconda.com/products/individual) to run properly. The steps below will install Anaconda if not already installed on your computer. Please note that when you install EcoAssist it is expected the [license terms of Anaconda](https://legal.anaconda.com/policies/en/?name=end-user-license-agreements#ae-5) are agreed upon. 

If you're updating EcoAssist from v1 to v2, please mannually delete the old `EcoAssist_files` folder and the `open_EcoAssist.command`.

1. Download, unzip and execute [this file](https://minhaskamal.github.io/DownGit/#/home?url=https://github.com/PetervanLunteren/EcoAssist/blob/main/install_EcoAssist.command). Mac OS can be quite reluctant when having to open command files downloaded from the internet. You can circumvent trust issues by opening it with right-click > open > open. If that still doesn't work you should open a new terminal window, copy-paste `chmod 755 ~/Downloads/install_EcoAssist.command` and hit enter. Then try again.
2. Go get yourself a beverage because this might take a few minutes to complete.

## How to start the application?
```
 📁Applications
 └── 📄EcoAssist.command
```
EcoAssist will open when you double-click the file above. You are free to move this file to a more convenient location. If you want EcoAssist in your dock, manually change `EcoAssist.command` to `EcoAssist.app`, then drag and drop it in your dock and change it back to `EcoAssist.command`. Not the prettiest solution, but it works...

## GPU Support
It is possible to run EcoAssist on your GPU for faster processing (I just never tried it before). See [this page](https://github.com/petargyurov/megadetector-gui/blob/master/GPU_SUPPORT.md) for more information. You would probably be best off by installing EcoAssist following the steps above and afterwards adjusting the `ecoassistcondaenv` conda environment accordingly.

## How to uninstall EcoAssist?
You can uninstall EcoAssist by executing [this file](https://minhaskamal.github.io/DownGit/#/home?url=https://github.com/PetervanLunteren/EcoAssist/blob/main/uninstall_EcoAssist.command). It will prompt you whether you want to uninstall Anaconda too. If you use Anaconda for something else you will probably don't want to uninstall it. You can just type 'yes' or 'no'.
