## How to delpoy MEWC models through EcoAssist?
Below is a step-by-step tutorial on how to  deploy a custom trained Mega Efficient Wildlife Classifier (MEWC) model throurgh EcoAssist. It assumes that the MEWC training has completed succesfully, and you have the model file (`model_file.h5`) and the class list (`class_list.yaml`) at your disposal. At the end of this tutorial you will be able to make inference via a graphical user interface (GUI) and optionally make your model open-source for thousands of ecologists and nature conservationsts to use.
Learn more about the EcoAssist software: https://addaxdatascience.com/ecoassist/

### Install EcoAssist
Use the latest installation file for your operating system and follow the associated steps to install EcoAssist on your device.
EcoAssist installation: https://addaxdatascience.com/ecoassist/#install

### Navigate to the root folder
All EcoAssist files are located in one folder, called `EcoAssist_files`. Please be aware that it's hidden, so you'll probably have to adjust your settings before you can see it (find out how to: [macOS](https://www.sonarworks.com/support/sonarworks/360003040160-Troubleshooting/360003204140-FAQ/5005750481554-How-to-show-hidden-files-Mac-and-Windows-), [Windows](https://support.microsoft.com/en-us/windows/view-hidden-files-and-folders-in-windows-97fbc472-c603-9d90-91d0-1166d1d9f4b5#WindowsVersion=Windows_11), [Linux](https://askubuntu.com/questions/232649/how-to-show-or-hide-a-hidden-file)).

<details>
<summary>Location on Windows</summary>
<br>
  
```r
# All users
─── 📁Program Files
    └── 📁EcoAssist_files

# Single user
─── 📁Users
    └── 📁<username>
        └── 📁EcoAssist_files
```
</details>

<details>
<summary>Location on macOS</summary>
<br>
  
```r
─── 📁Applications
    └── 📁.EcoAssist_files
```
</details>

<details>
<summary>Location on Linux</summary>
<br>
  
```r
─── 📁home
    └── 📁<username>
        └── 📁.EcoAssist_files
```
</details>

### Prepare a new folder for your model
1. Navigate to `/EcoAssist_files/models/cls`. If you don't see the subfolder `Namibian Desert - Addax Data Science`, you might need to open and close the EcoAssist application in order to create the neccesary file structure.
2. Create a folder inside `cls` with a descriptive name for your model. For example: `Arctic fauna`.
3. Copy-paste the `variables.json` from `Namibian Desert - Addax Data Science` to your model folder.
4. Place your model file (`model_file.h5`) and classes list inside your model folder.
5. Make sure your classes list is called `class_list.yaml`. Any other filename will not work.
6. After completing this section, the folder structure should look something like this:

```raw
─── 📁 EcoAssist_files
    └── 📁 models
        └── 📁 cls
            |── 📁 Namibian Desert - Addax Data Science
            |   └── variables.json
            └── 📁 Arctic fauna
                |── variables.json
                |── class_list.yaml
                └── model_file.h5
```


### Adjust JSON values
Open your `variables.json` in any text editor (Notepad, TextEdit, VSCode, etc) and replace the exisiting values. Please note that not all fields are required at this time. If you decide to move forward and publish your model open-source, you will need to fill in the remaining fields. More about that later in this tutorial. 

Please note that only the fields below have to be adjusted at this time. The rest can be left blank. 


* `model_fname` - The filename of your model. E.g.: `"model_file.h5"`.
* `description` - Leave blank. I.e., `""`.
* `developer` - Leave blank. I.e., `""`.
* `env` - The virtual environment inside which the model should run. Fill in: `"tensorflow"`.
* `type` - The type of model inferencing. Fill in: `"mewc"`.
* `download_info` - Leave blank. I.e., `["", ""]`.
* `citation` - Leave blank. I.e., `""`.
* `license` - Leave blank. I.e., `""`.
* `total_download_size` - Leave blank. I.e., `""`.
* `info_url` - Leave blank. I.e., `""`.
* `all_classes` - Your model's species categories. Fill them in in the format `["species 1", "species 2", "species 3", ... ]` with _exactly_ the same names as in your `class_list.yaml`.  
* `selected_classes` - The categories that will show up selected inside the GUI. Should be exactly the same as what you filled in above for `all_classes`. 
* `var_cls_detec_thresh` - Leave unaltered. 
* `var_cls_detec_thresh_default` - Leave unaltered. 
* `var_cls_class_thresh` - Leave unaltered. 
* `var_cls_class_thresh_default` - Leave unaltered. 
* `var_smooth_cls_animal` - Leave unaltered. 
* `min_version` - Them minimum version of EcoAssist that is able to run this model. Fill in: `"5.2"`.
  
