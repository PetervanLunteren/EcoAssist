
# Steps to install EcoAssist from ZIP file

The steps below are ment for EcoAssist users that can't execute the normal install due to unstable internet, security issues, or something else. Installing from ZIP file should be plan B, as the normal install is much quicker, performs additional checks, and automates the whole process. If you haven't tried the [normal install](https://addaxdatascience.com/ecoassist-windows/) yet, please try that first. 

**Follow the steps below to install EcoAssist from ZIP file.**
1. Download the ZIP file from [this direct download link](https://drive.google.com/uc?export=download&id=1i0v4MgfFhp5RbK6pBseyaYawP1B6hglr). It might take a while as it is 26 GB.
  <img width="500" alt="Screenshot 2024-08-13 at 15 40 13" src="https://github.com/user-attachments/assets/57347398-cd27-4b61-b271-e6bf5fc190b5">

2. Download and install 7zip via [this link](https://www.7-zip.org/a/7z2408-x64.exe).

3. 
4. Navigate to the `EcoAssist_files.zip` file. It will be in your Downloads folder.
5. Right-click > (Optionally: 'Show more options') > 7-zip > Extract files...
<img width="500" alt="Screenshot 2024-08-14 at 07 31 51" src="https://github.com/user-attachments/assets/c039f3e7-b145-4483-a6c7-a75d0a8f4704">

6. Click the `...` button to browse for your user folder. The location is important. Choose `C:\Users\<username>`.
7. Uncheck the checkbox under the 'Extract to' path.
8. Choose 'Overwrite without prompt' as 'Overwrite mode'. 
9. Click OK.
<img width="500" alt="Screenshot 2024-08-14 at 07 41 37" src="https://github.com/user-attachments/assets/e040a7b2-8da8-4b33-b347-1e27187ee3a2">


10. When that is done, check if it works by double clicking on `C:\Users\<username>\EcoAssist_files\EcoAssist\open.bat`.
11. If you want you can create a shortcut file so you don't always have to navigate to the `open.bat` file. If you still have your shortcut file left from the normal install, that will work fine. If not, you can create one by right-clicking on `open.bat` > Show more options > Create shortcut. The drag and drop that shortcut file to your desktop and rename it to 'EcoAssist'.



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
