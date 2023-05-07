*-- This document is work in progress --*

Below you can find some common error messages and their potential solutions. If you can't figure it out yourself, raise an error in this repository or [email me](mailto:petervanlunteren@hotmail.com) the logfiles, a detailed explenation of what's going on and a way to recreate the error. 

### How to create and find the logfiles?
* Recreate the error in EcoAssist.
* Close all EcoAssist windows by clicking the cross at the top - do not quit the program as a whole. On Mac and Linux close the terminal window last.
* Navigate to `EcoAssist_files\EcoAssist\logfiles\`. You can find the location of `EcoAssist_files` [here](https://github.com/PetervanLunteren/EcoAssist#uninstall). 
  * `installation_log.txt` will give you information about the installation.
  * `session_log.txt` writes logs during runtime on Windows.
  * `stdout.txt` and `stderr.txt` write logs during runtime on Mac and Linux. 

### `Local variable 'elapsed time' referenced before assignment`
This error message can be thrown when trying to deploy a model. It basically means that the model outputs some unexpected text. First of all, try if the model deploys succesfully over the test images supplied [here](https://github.com/PetervanLunteren/EcoAssist#test-your-installation). Check if your preloaded models are correctly downloaded. Sometimes protection software prevent the download of the actual model files. There should be two files named `md_v5a.0.0.pt` and `md_v5b.0.0.pt` in `\EcoAssist_files\pretrained_models\`. You can find the location of the EcoAssist_files [here](https://github.com/PetervanLunteren/EcoAssist#uninstall). If that isn't the problem, the logfiles should point you in the right direction.
