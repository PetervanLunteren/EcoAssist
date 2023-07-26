*-- This document is work in progress --*

Below you can find some common error messages and their potential solutions. If you can't figure it out yourself, raise an error in this repository or [email me](mailto:petervanlunteren@hotmail.com) the logfiles, a detailed explenation of what's going on and a way to recreate the error. 

## How to create logfiles?
If there is an error during runtime, it is important to give the program the opportunity to write out its logs. First thing you'll need to do is recreate the error in EcoAssist. After that, close all EcoAssist windows by clicking the cross at the top - do not quit the program as a whole. On Mac and Linux close the terminal window last. If there is an error during the installation or opening, you don't have to worry about this - in that case the logfiles are automatically created. 
 
## How to find logfiles?
* Navigate to your `EcoAssist_files` folder. It's location is OS dependent, you can find its location [here](https://github.com/PetervanLunteren/EcoAssist#uninstall). 
* Navigate to `...\EcoAssist_files\EcoAssist\logfiles\`. 
  * `installation_log.txt` will give you information about the installation.
  * `session_log.txt` writes logs during runtime on Windows.
  * `stdout.txt` and `stderr.txt` write logs during runtime on Mac and Linux.

## `Local variable 'elapsed time' referenced before assignment`
This error message can be thrown when trying to deploy a model. It basically means that the model outputs some unexpected text. First of all, try if the model deploys succesfully over the test images supplied [here](https://github.com/PetervanLunteren/EcoAssist#test-your-installation). Check if your preloaded models are correctly downloaded. Sometimes protection software prevent the download of the actual model files. There should be two files named `md_v5a.0.0.pt` and `md_v5b.0.0.pt` in `\EcoAssist_files\pretrained_models\`. You can find the location of the EcoAssist_files [here](https://github.com/PetervanLunteren/EcoAssist#uninstall). If that isn't the problem, the logfiles should point you in the right direction.

## `SSL certificate problem: unable to get local issuer certificate`
If you see this message poping up somewhere, there is something going on with your SSL certificates. Most probably that is due to some secrurity setting (VPN, firewall, proxy, etc.) which prevents it from downloading the specific package. Most of the times this can be fixed by simply disabling the VPN/firewall/proxy and reinstalling EcoAssist. If that doesn't work, try switching internet networks, from WiFi to ethernet, or vice versa. If all that doesn't work, you can disable SSL verification temporarily. If you want that, open a new console window and execute `git config --global http.sslVerify false`, then drag and drop the `install.bat` file in the same window and press enter. Please note that this solution opens you to attacks like man-in-the-middle attacks. Therefore turn on verification again after installing EcoAssist, by executing `git config --global http.sslVerify true`. If you see `'git' is not recognized as an internal or external command`, you'll have to explicitly tell you computer where it can find the git executable, by changing the commands to `path\to\git\installation\cmd\git.exe config --global http.sslVerify false`. 

## `ValueError: path is on mount '...', start on mount '...'`
This is a Windows error message and means that your training data is located on a different drive than EcoAssist. For example, it would say `ValueError: path is on mount 'C:', start on mount 'F:'`, which means that the training data is located on your `F:` drive, while EcoAssist is located on the `C:` drive. The sollution is to get everything on the same drive. So either install EcoAssist on the `F:` drive, or move the training data to the `C:` drive. 

## `An error occurred while opening the annotation software labelImg. Please send an email to petervanlunteren@hotmail.com to resolve this bug.`
This crash can occur when there are more classes in an annotation file than in the `classes.txt` file. That means that the annotation file class number of a specific annotation refers to a non-existing class in the `classes.txt`. So for example, if you have two lines in your `classes.txt` (`species A`, and `species B`), but there is an annotation file which is labeled as the third class (which would be 2 when counting from 0), for example: `2 0.929183 0.683231 0.135604 0.238979`. This will cause labelImg to crash, since it can’t find which class the “2” refers to. A good test would be to add some dummy classes to your `classes.txt`, and then try to open labelImg again. For example:
```
Species A
Species B
Dummy class 1
Dummy class 2
Dummy class 3
Dummy class 4
Dummy class 5
```
Another option to check your labelImg installation is to open a directory of non-annotated images. That should work without any problems. If not, [email me](mailto:petervanlunteren@hotmail.com) the logfiles and I will have a look. [This](https://github.com/PetervanLunteren/EcoAssist/edit/main/errors.md#how-to-create-logfiles) is how to write the error to the logfiles and [this](https://github.com/PetervanLunteren/EcoAssist/edit/main/errors.md#how-to-find-logfiles) is how to find them. 
