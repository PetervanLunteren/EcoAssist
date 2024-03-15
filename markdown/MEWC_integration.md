## Make inference with MEWC models through EcoAssist GUI
Below is a step-by-step tutorial on how to  deploy a custom trained Mega Efficient Wildlife Classifier model (MEWC) throurgh EcoAssist. It assumes that the MEWC training has completed succesfully. At the end of this tutorial you will be able to make inference via EcoAssist's graphical user interface (GUI) and optionally publish your model open-source using EcoAssist's network.

Learn more about the EcoAssist software: https://addaxdatascience.com/ecoassist/

If anything is unclear, let me know: peter@addaxdatascience.com

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

### III - Prepare a new model folder
1. Navigate to `/EcoAssist_files/models/cls`. If you don't see the subfolder `Namibian Desert - Addax Data Science`, you might need to open and close the EcoAssist application in order to create the neccesary file structure.
2. Create a folder inside `cls` with a descriptive name for your model. For example: `Arctic fauna`.
3. Copy-paste the `variables.json` from `Namibian Desert - Addax Data Science` to your model folder.
4. Place your model file (`.h5`) and classes list (`.yaml`) inside your model folder. Always make sure you have a backup - just in case.
5. The model file can have a custom filename, but make sure your classes list is called `class_list.yaml`. 
6. After completing this section, the folder structure should look something like this:

```raw
─── 📁 EcoAssist_files
    └── 📁 models
        └── 📁 cls
            |── 📁 Arctic fauna
            |   |── variables.json
            |   |── class_list.yaml
            |   └── model_file.h5
            |── 📁 Namibian Desert - Addax Data Science
            |   └── variables.json
            |── 📁 ...
            └── 📁 ...
```


### IV - Adjust JSON values
1. Open your `variables.json` in any text editor (Notepad, TextEdit, VSCode, etc) and replace the exisiting values. Please note that not all fields are required at this time. If you decide to publish your model open-source, you will need to fill in the remaining fields. More about that later in this tutorial. 
    * `model_fname`  - The filename of your model. Make sure you check if you have the right extension. E.g.: `"model_file.h5"`.
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
    * `var_cls_detec_thresh`  - This is the detection threhsold. Only above this detection confidence provided by MegaDetector, the animal will be further classified. Must be in the range 0.01 - 0.99. If unsure, leave unaltered. 
    * `var_cls_detec_thresh_default`  - Match `var_cls_detec_thresh`.
    * `var_cls_class_thresh`  - This is the classification threhsold.  Below this classification confidence, the model will label the animal with “unidentified animal”. Must be in the range 0.01 - 0.99. If unsure, leave unaltered. 
    * `var_cls_class_thresh_default`  - Match `var_cls_class_thresh`.
    * `var_smooth_cls_animal`  - This is a feature that is temporarily disabled. Keep as `false`.
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
3. Save `variables.json` and open EcoAssist. Your model should now be deployable and visible in the model dropdown menu.

<img width="742" alt="Screenshot 2024-03-14 at 11 28 30" src="https://github.com/PetervanLunteren/EcoAssist/assets/85185478/b564feae-9024-4582-bc98-f2f4881f403e">

### V - Host on HuggingFace (optional)
Addax Data Science supports open-source principles, aiming to facilitate the distribution of free conservation technology. As part of this commitment, Addax provides the functionality to publish the resulting model open-source via the EcoAssist. You can use this network to share your model with other conservationists. You will retain ownership of the model, receive proper attribution, and can select an appropriate open-source license. Should you desire to do so, please proceed with the steps below.
1. Log in or sign up for the HuggingFace model hosting platform: https://huggingface.co/login
2. Once logged in, choose to add a new model: top left click "Add" > "Model".

<img width="596" alt="Screenshot 2024-03-14 at 12 42 41" src="https://github.com/PetervanLunteren/EcoAssist/assets/85185478/a59d81a2-6ef1-463c-96eb-f6f01c712d8d">

3. Choose a name for your model.
4. Select a license. Please do your own research and select whatever suits you best. If you have no idea where to start - there are two common licenses for open-source models: `mit` and `cc-by-nc-sa-4.0`. They both allow people to freely use, share, and adapt the model when proper attribution is given. `cc-by-nc-sa-4.0` differs from `mit` only in the sense that `cc-by-nc-sa-4.0` restricts commercial use.
5. Make sure the model repository is set to public and click "Create model".

<img width="638" alt="Screenshot 2024-03-14 at 12 44 43" src="https://github.com/PetervanLunteren/EcoAssist/assets/85185478/c120a691-4561-470a-89de-c7bd4c9a4295">

6. Click the tab "Files and versions".

<img width="1412" alt="Screenshot 2024-03-14 at 13 03 44" src="https://github.com/PetervanLunteren/EcoAssist/assets/85185478/1a4f3c19-226e-445c-a028-4ce642babd07">

7. Click the button "Add file" > "Upload files".

<img width="1402" alt="Screenshot 2024-03-14 at 13 12 45" src="https://github.com/PetervanLunteren/EcoAssist/assets/85185478/6307e954-0668-4d6d-9e90-e4fdd3fe47ba">

8. Drag and drop your model file (`.h5`) and classes list (`class_list.yaml`) and click "Commit to changes to `main`".

<img width="1153" alt="Screenshot 2024-03-14 at 13 16 00" src="https://github.com/PetervanLunteren/EcoAssist/assets/85185478/84585b4d-c4cf-4529-8d44-d5d96c2a86d8">

9. Once uploaded, open your `variables.json` and fill in the remaining fields.

    * `description`  - Fill in a short description about the model, on how many images it was trained, which purpose it serves, etc.
    * `developer`  - Fill in the organisation which has developed the model. 
    * `download_info`  - Provide the links and filenames of the model file and classes list in the format `[["url", "filename"], ["url", "filename"]]`. You can retrieve the download url by right-clicking the download button and selecting "Copy link address".
    * `citation`  - If you want users to cite, provide the url to your paper. Otherwise leave blank.
    * `license`  - Provide a url to your license. 
    * `total_download_size`  - Fill in the size of you model file, e.g. "107 MB".
    * `info_url`  - Provide a url to a webpage for users to find more information, or leave blank. 
  
10. After adjusting the JSON values, your `variables.json` should look something like this:
```json
{
  "model_fname": "model_file.pt",
  "description": "The model was trained on X images taken from database Y and is ment for Z.",
  "developer": "Addax Data Science",
  "env": "tensorflow",
  "type": "mewc",
  "download_info": [
    [
      "https://huggingface.co/Addax-Data-Science/arctic-fauna/resolve/main/model_file.h5?download=true",
      "model_file.h5"
    ],
    [
      "https://huggingface.co/Addax-Data-Science/arctic-fauna/resolve/main/class_list.yaml?download=true",
      "class_list.yaml"
    ]
  ],
  "citation": "https://joss.theoj.org/papers/10.21105/joss.05581",
  "license": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
  "total_download_size": "71 MB",
  "info_url": "https://addaxdatascience.com/",
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

### VI - Publish via EcoAssist (optional)
Everything is ready for the model to be published. You can either send your `variables.json` via email to peter@addaxdatascience.com, or create a pull request and add `variables.json` as an `key:value` pair in the `cls` dictionary in the latest `model_info.json` file: https://github.com/PetervanLunteren/EcoAssist/tree/main/model_info

You're done! Peter van Lunteren will review the information and take it from here.
