## Make inference with MEWC models through EcoAssist GUI
Below is a step-by-step tutorial on how to  deploy a custom trained Mega Efficient Wildlife Classifier model (MEWC) throurgh EcoAssist. It assumes that the MEWC training has completed succesfully. At the end of this tutorial you will be able to make inference via EcoAssist's graphical user interface (GUI) and optionally publish your model open-source using EcoAssist's network.

Learn more about the EcoAssist software: https://addaxdatascience.com/ecoassist/

### I - Install EcoAssist
Use the latest installation file for your operating system and follow the associated steps to install EcoAssist on your device.

EcoAssist installation: https://addaxdatascience.com/ecoassist/#install

### II - Navigate to the root folder
All EcoAssist files are located in one folder, called `EcoAssist_files`. Please be aware that it's hidden, so you might have to adjust your settings before you can see it (find out how to: [macOS](https://www.sonarworks.com/support/sonarworks/360003040160-Troubleshooting/360003204140-FAQ/5005750481554-How-to-show-hidden-files-Mac-and-Windows-), [Windows](https://support.microsoft.com/en-us/windows/view-hidden-files-and-folders-in-windows-97fbc472-c603-9d90-91d0-1166d1d9f4b5#WindowsVersion=Windows_11), [Linux](https://askubuntu.com/questions/232649/how-to-show-or-hide-a-hidden-file)).

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

### III - Prepare a new folder for your model
1. Navigate to `/EcoAssist_files/models/cls`. If you don't see the subfolder `Namibian Desert - Addax Data Science`, you might need to open and close the EcoAssist application in order to create the neccesary file structure.
2. Create a folder inside `cls` with a descriptive name for your model. For example: `Arctic fauna`.
3. Copy-paste the `variables.json` from `Namibian Desert - Addax Data Science` to your model folder.
4. Place your model file (`.h5`) and classes list (`.yaml`) inside your model folder.
5. The model file can have a custom filename, but make sure your classes list is called `class_list.yaml`. Any other filename will not work. 
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


### IV - Adjust JSON values
1. Open your `variables.json` in any text editor (Notepad, TextEdit, VSCode, etc) and replace the exisiting values. Please note that not all fields are required at this time. If you decide to move forward and publish your model open-source, you will need to fill in the remaining fields. More about that later in this tutorial. 
    * `model_fname`  - The filename of your model. E.g.: `"model_file.h5"`.
    * `description`  - Leave blank. I.e., `""`.
    * `developer`  - Leave blank. I.e., `""`.
    * `env`  - The virtual environment inside which the model should run. I.e., `"tensorflow"`.
    * `type`  - The type of model inferencing. I.e., `"mewc"`.
    * `download_info`  - Leave blank. I.e., `[["", ""]]`.
    * `citation`  - Leave blank. I.e., `""`.
    * `license`  - Leave blank. I.e., `""`.
    * `total_download_size`  - Leave blank. I.e., `""`.
    * `info_url`  - Leave blank. I.e., `""`.
    * `all_classes`  - Your model's species categories. Fill them in in the format `["species 1", "species 2", "species 3", ... ]` with _exactly_ the same classnames as in your `class_list.yaml`.  
    * `selected_classes`  - The categories that will show up selected inside the GUI. Fill in the same as you did for `all_classes`. 
    * `var_cls_detec_thresh`  - Leave unaltered. 
    * `var_cls_detec_thresh_default`  - Leave unaltered. 
    * `var_cls_class_thresh`  - Leave unaltered. 
    * `var_cls_class_thresh_default`  - Leave unaltered. 
    * `var_smooth_cls_animal`  - Leave unaltered. 
    * `min_version`  - The minimum version of EcoAssist that is able to run this model. I.e., `"5.2"`.

2. After adjusting the JSON values, your `variables.json` should look something like this:
```json
{
  "model_fname": "model_file.pt",
  "description": "",
  "developer": "",
  "env": "tensorflow",
  "type": "mewc",
  "download_info": [
    [
      "",
      ""
    ]
  ],
  "citation": "",
  "license": "",
  "total_download_size": "",
  "info_url": "",
  "all_classes": [
    "polar bear",
    "fox",
    "walrus",
    "seal",
    "owl",
    "reindeer"
  ],
  "selected_classes": [
    "polar bear",
    "fox",
    "walrus",
    "seal",
    "owl",
    "reindeer"
  ],
  "var_cls_detec_thresh": "0.40",
  "var_cls_detec_thresh_default": "0.40",
  "var_cls_class_thresh": "0.50",
  "var_cls_class_thresh_default": "0.50",
  "var_smooth_cls_animal": false,
  "min_version": "5.2"
}
```

### V - Test
The model should now be bale to run inference via the EcoAssist GUI. Start EcoAssist and try the model on some test images to confirm.

