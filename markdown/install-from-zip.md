<details>
<summary><b>Steps to produce zip file - For developer only</b></summary>
<br>
<i>If you're an EcoAssist user, you dont have to follow these steps. This is information is for the developer.</i>
<br></br>
Follow the steps below to create this all-encompassing EcoAssist zip file.

1. [Install the latest EcoAssist version](https://addaxdatascience.com/ecoassist-windows/) on a Windows machine
2. Copy the entire contents of the following folders to `C:\Users\smart\Desktop\EcoAssist_files`.
   * `C:\Users\smart\miniforge3` (double check for redundant environments)
   * `C:\Program Files\Git`
 

</details>


# copy the entire miniforge3 and Git folders to EcoAssist_files

# remove the folowwing files
EcoAssist\logfiles\path_to_conda_installation.txt
EcoAssist\logfiles\path_to_git_installation.txt

# zip folder (takes about 1 hour)
7z a -tzip "C:\Users\smart\Desktop\EcoAssist_files.zip" "C:\Users\smart\Desktop\EcoAssist_files"

# upload the EcoAssist_files folder to Google Drive (takes about 1 hour)
rclone copy -P "C:\Users\smart\Desktop\EcoAssist_files.zip" "gdrive:/EcoAssist-zip-files/Windows/v5.14"

# update download link in this file above
