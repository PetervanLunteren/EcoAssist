<details>
<summary><b>Steps to compile zip install [for developers]</b></summary>
<br>
<i>If you're an EcoAssist user, you dont have to follow these steps. This is information is for developers.</i>
<br></br>
Follow the steps below to create this all-encompassing EcoAssist zip file.

1. [Install the latest EcoAssist version](https://addaxdatascience.com/ecoassist-windows/) on a Windows machine
2. Copy the entire contents of the following folders to `C:\Users\smart\EcoAssist_files`.
   * `C:\Users\smart\miniforge3` (double check for redundant environments)
   * `C:\Program Files\Git`
3. Remove the following files
   * `C:\Users\smart\EcoAssist_files\EcoAssist\logfiles\path_to_conda_installation.txt`
   * `C:\Users\smart\EcoAssist_files\EcoAssist\logfiles\path_to_git_installation.txt`
4. Compress the folder (takes about 1 hour)
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
