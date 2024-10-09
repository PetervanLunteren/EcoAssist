
# Steps to install EcoAssist from a ZIP file

Below are instructions for EcoAssist users who are unable to execute the normal install due to unstable internet, security issues, or something else. Installing from a ZIP file should be plan-B, as the normal installation is much quicker, performs additional checks, and automates the whole process. If you haven't tried the [normal install](https://addaxdatascience.com/ecoassist-windows/) yet, please try that first. 

**Follow the steps below to install EcoAssist from a ZIP file.**
1. Download the ZIP file using [this link (EcoAssist v5.17)](https://drive.google.com/uc?export=download&id=1jWgzpwWuOqy9jw_pPxRa52bRzjhHfsoz). It might take a while, as it is 23 GB.
<div align="center"><img width="500" alt="Screenshot 2024-08-13 at 15 40 13" src="https://github.com/user-attachments/assets/57347398-cd27-4b61-b271-e6bf5fc190b5"></div>

2. Download 7zip via [this link](https://www.7-zip.org/a/7z2408-x64.exe), double-click the `7z2408-x64.exe` file in your Downloads folder, leave the destination folder as it is, and press 'Install'.
<div align="center"><img width="301" alt="Screenshot 2024-08-14 at 08 14 04" src="https://github.com/user-attachments/assets/f6ad90e6-1ce3-4b1c-a2fd-d22139408c22"></div>

4. Navigate to the `EcoAssist_files.zip` file. It will be in your Downloads folder.
5. Right-click > (Optionally: 'Show more options') > 7-zip > Extract files...
<div align="center"><img width="500" alt="Screenshot 2024-08-14 at 07 31 51" src="https://github.com/user-attachments/assets/921a6f79-bf9a-4a7c-8137-df339eb9694e"></div>


6. Click the `...` button to browse your user folder. The location is important. Choose `C:\Users\<your_username>`.
7. Uncheck the checkbox under the 'Extract to' path.
8. Choose 'Overwrite without prompt' as 'Overwrite mode'. 
9. Click OK.
<div align="center">
  <img height="250" alt="Screenshot 2024-08-14 at 07 41 37" src="https://github.com/user-attachments/assets/e040a7b2-8da8-4b33-b347-1e27187ee3a2">
  <img height="250" alt="Screenshot 2024-08-14 at 07 30 42" src="https://github.com/user-attachments/assets/42b7ba8b-7ba6-4b45-bc02-e035432b9d2c">
</div>


10. When the ZIP file is extracted, check if EcoAssist works by double-clicking the `C:\Users\<your_username>\EcoAssist_files\EcoAssist\open.bat` file.
<div align="center"><img width="300" alt="Screenshot 2024-08-14 at 07 23 35" src="https://github.com/user-attachments/assets/410577b9-a722-4c1c-9217-3bd0d773aa6f"></div>


11. If you want, you can create a shortcut file so you don't always have to navigate to the `open.bat` file. If you still have your shortcut file left from the normal install, that will work fine. If not, you can create one by right-clicking on `open.bat` > (Optionally: 'Show more options') > Create shortcut. Then drag and drop that shortcut file to your desktop and rename it to 'EcoAssist'.
<div align="center"><img width="90" alt="Screenshot 2024-08-14 at 07 11 06" src="https://github.com/user-attachments/assets/d590cf69-a7fd-4b63-8d66-3278fa9443a4"></div>

_______________________________________________________________________
<details>
<summary><b>Download using Wget or cURL [for developers]</b></summary>
  
<br>

I just want to say thanks for the support, I managed to download and use Ecoassist. But for future reference, the trick with loading cookies did not work. I ended up having to go to the google api page, creating a token and then downloading the file from the api using curl to add a custom header. Fortunately, curl had the same "continue" option for download  so it still helped with my unreliable internet. 
  
<br>

The command line was something like that

<br>

```
curl -H "Authorization: Bearer <TOKEN>" https://www.googleapis.com/drive/v3/files/1i0v4MgfFhp5RbK6pBseyaYawP1B6hglr?alt=media -o Ecoassist.zip
```

Essentially I followed the instructions on this page, more precisely thunder's recommendation. 

You have to go https://developers.google.com/oauthplayground/ get a token for the Driver API v3 and use the given token in curl request (or for a native window solution using `Invoke-RestMethod` in the powershell.
</details>






_______________________________________________________________________
<details>
<summary><b>Steps to compile zip install [for developers]</b></summary>
<br>
<i>If you're an EcoAssist user, you don't have to follow these steps. This is information is for developers.</i>
<br></br>
Follow the steps below to create this all-encompassing EcoAssist zip file.

1. [Install the latest EcoAssist version](https://addaxdatascience.com/ecoassist-windows/) on a Windows machine.
2. Make sure you have copied all models to `C:\Users\smart\EcoAssist_files\models\cls` so that they will be included in the ZIP.
3. Copy the entire contents of the following folders to `C:\Users\smart\EcoAssist_files`.
   * `C:\Users\smart\miniforge3` (double check for redundant environments)
   * `C:\Program Files\Git`
4. Remove the following files
   * `C:\Users\smart\EcoAssist_files\EcoAssist\logfiles\path_to_conda_installation.txt`
   * `C:\Users\smart\EcoAssist_files\EcoAssist\logfiles\path_to_git_installation.txt`
5. Compress the folder (it takes about an hour)
```
7z a -tzip "C:\Users\smart\Desktop\EcoAssist_files.zip" "C:\Users\smart\EcoAssist_files"
```
5. Upload the zipped file to Google Drive (it takes about an hour)
```
rclone copy -P "C:\Users\smart\Desktop\EcoAssist_files.zip" "gdrive:/EcoAssist-zip-files/Windows/<VERSION-NUMBER>"
```
6. Change the Google Drive share link to a direct download link using [this website](https://sites.google.com/site/gdocs2direct/).
7. Update the instructions above with the new version and link.
</details>
