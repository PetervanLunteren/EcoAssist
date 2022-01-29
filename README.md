<p align="center">
  <img src="https://github.com/PetervanLunteren/EcoAssist/blob/main/imgs/banner.png" width=100% height="auto" />
</p>
ImSep is an application designed to make life easier for wildlife ecologists who work with cameratrap data. I know how time consuming it can be to analyse every image. Thanks to the good people at <a href="https://github.com/microsoft/CameraTraps/blob/main/megadetector.md">MegaDetector</a>, there is a pre-trained model which can recognise animals in camera trap images in a variety of terrestrial ecosystems. The only problem is that you need to know a bit of coding before you can use it. ImSep is a small program which makes it easy for everybody. With a simple user interface you can filter out the empties, visualise the detections and crop out the animals.<br/>
<br/>

Help me to keep improving ImSep and let me know about any improvements, bugs, or new features so that I can continue to keep it up-to-date. Also, I would very much like to know who uses the tool and for what reason. You can contact me at [contact@pvanlunteren.com](mailto:contact@pvanlunteren.com).

<p align="center">
  <img src="https://github.com/PetervanLunteren/EcoAssist/blob/main/imgs/parameters.png" width=60% height="auto" />
</p>

## How to download?
For now it is only available for OSX users. If you would like ImSep on your Windows of Linux computer, let me know! I'll see what I can do.

### Prerequisites
1. First of all you'll need to install [Anaconda](https://www.anaconda.com/products/individual). Need help? Follow [these steps](https://docs.anaconda.com/anaconda/install/mac-os/).
2. If Anaconda is installed you can create a directory in your root folder and download this repository. You can do that by opening a new window in the Terminal.app and entering the following commands.
```batch
mkdir ~/ImSep_files
cd ~/ImSep_files
git clone https://github.com/PetervanLunteren/ImSep.git
```

### Easy download
You can now continue to download the rest of the files. I've tried to make it easy for you by creating a bash script which will do this for you. You can simply double-click on the file `ImSep_files/ImSep/install_ImSep.command`. It downloads the MegaDetector repo and it's model file, then creates an anaconda environment in which the correct python version and all the neccesary packages are installed. If you prefer to do it your self, see the manual download below. It might take a few minutes before the installation is completed. 

### Manual download
You do not need to enter these commands if you executed `install_ImSep.command`.
```batch
cd ImSep_files
git clone https://github.com/Microsoft/cameratraps
curl --output md_v4.1.0.pb https://lilablobssc.blob.core.windows.net/models/camera_traps/megadetector/md_v4.1.0/md_v4.1.0.pb
conda create --name imsepcondaenv python=3.7 -y
conda activate imsepcondaenv
pip install -r ImSep/requirements.txt
```

## How to start the application?
The file `ImSep_files/ImSep/open_ImSep.command` will open the application when double-clicked. You are free to move this file to a more convenient location. Just keep in mind that the folderstructure and location of `ImSep_files` should not change.

## Example detections
<p float="center">
  <img src="https://github.com/PetervanLunteren/EcoAssist/blob/main/imgs/example_1.jpg" width=49.7% height="auto" />
  <img src="https://github.com/PetervanLunteren/EcoAssist/blob/main/imgs/example_2.jpg" width=49.7% height="auto" />
  <img src="https://github.com/PetervanLunteren/EcoAssist/blob/main/imgs/example_3.jpg" width=49.7% height="auto" /> 
  <img src="https://github.com/PetervanLunteren/EcoAssist/blob/main/imgs/example_4.jpg" width=49.7% height="auto" /> 
</p>

## GPU Support
It is possible to run ImSep on your GPU for faster processing. See [this page](https://github.com/petargyurov/megadetector-gui/blob/master/GPU_SUPPORT.md) for more information. Just place this repo in a directory with the `cameratraps` repo and the `md_v4.1.0.pb` file. It should work, I just never tested it...

## How to uninstall ImSep?
You only have to do two things if you are fed up with ImSep and want to get rid of it.
1. Delete the `ImSep_files` folder;
2. Either i) [uninstall Anaconda](https://docs.anaconda.com/anaconda/install/uninstall/) as a whole with the command `rm -rf ~/anaconda3` or ii) keep the Anaconda instalation and only delete the virtual environment with the command `conda env remove -n imsepcondaenv`.
