
# Steps to install EcoAssist from ZIP file

The below steps are ment for EcoAssist users that can't execute the normal install due to unstable internet or security issues. The normal install is preferred since it performs additional checks and automates the process. If you haven't tried the [normal install](https://addaxdatascience.com/ecoassist-windows/) yet, please try that first. 

Follow the following steps to install EcoAssist from ZIP file. 
1. Download the ZIP file from [this direct download link](https://drive.google.com/uc?export=download&id=1i0v4MgfFhp5RbK6pBseyaYawP1B6hglr).
<img width="822" alt="Screenshot 2024-08-13 at 15 40 13" src="https://github.com/user-attachments/assets/57347398-cd27-4b61-b271-e6bf5fc190b5">


2. 



_______________________________________________________________________
<details>
<summary><b>Steps to compile zip install [for developers]</b></summary>
<br>
<i>If you're an EcoAssist user, you dont have to follow these steps. This is information is for developers.</i>
<br></br>
Follow the steps below to create this all-encompassing EcoAssist zip file.

1. [Install the latest EcoAssist version](https://addaxdatascience.com/ecoassist-windows/) on a Windows machine.
2. Make sure you have copy-pasted all models to `C:\Users\smart\EcoAssist_files\models\cls` so that they will be included in the ZIP.
3. Copy the entire contents of the following folders to `C:\Users\smart\EcoAssist_files`.
   * `C:\Users\smart\miniforge3` (double check for redundant environments)
   * `C:\Program Files\Git`
4. Remove the following files
   * `C:\Users\smart\EcoAssist_files\EcoAssist\logfiles\path_to_conda_installation.txt`
   * `C:\Users\smart\EcoAssist_files\EcoAssist\logfiles\path_to_git_installation.txt`
5. Compress the folder (takes about 1 hour)
```
7z a -tzip "C:\Users\smart\Desktop\EcoAssist_files.zip" "C:\Users\smart\EcoAssist_files"
```
5. Upload the zipped file to Google Drive (takes about 1 hour)
```
rclone copy -P "C:\Users\smart\Desktop\EcoAssist_files.zip" "gdrive:/EcoAssist-zip-files/Windows/<VERSION-NUMBER>"
```
6. Change the google drive share link to a direct download link using [this website](https://sites.google.com/site/gdocs2direct/).
7. Update the instructions above with the new version and link.
</details>
