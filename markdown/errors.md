Below you can find some common error messages and their potential solutions. If you can't figure it out yourself, raise an error in this repository or [email me](mailto:petervanlunteren@hotmail.com) the logfiles, a detailed explenation of what's going on and a way to recreate the error. 

## How to run EcoAssist in debug mode?
It is possible to run EcoAssist in debug mode, where it'll print its output in a console window. That should point us in the right direction if there is an error. How to run it in debug mode depends on your operating system.
<details>
<summary><b>Windows</b></summary>
<br>
 
Open a fresh window of the command prompt and run the following.
```
( "%homedrive%%homepath%\EcoAssist_files\EcoAssist\open.bat" debug ) || ( "%ProgramFiles%\EcoAssist_files\EcoAssist\open.bat" debug ) || ( "%homedrive%\EcoAssist_files\EcoAssist\open.bat" debug )
```
Now try to recreate the error and check the console output for its message.
</details>
<details>
<summary><b>macOS</b></summary>
<br>
 
1. Open your `/Applications/EcoAssist.command` (or wherever you placed it) with a text editor like TextEdit or Visual Studio Code;
2. Outcomment these lines like so:
```bash
# exec 1> $LOCATION_ECOASSIST_FILES/EcoAssist/logfiles/stdout.txt
# exec 2> $LOCATION_ECOASSIST_FILES/EcoAssist/logfiles/stderr.txt
 ```
3. Close and save the file;
4. Start EcoAssist as you would do normally and recreate the error.
</details>
<details>
<summary><b>Linux</b></summary>
<br>
 
1. Open the file `/home/<username>/.EcoAssist_files/EcoAssist/open.command` with a text editor like TextEdit or Visual Studio Code;
2. Outcomment these lines like so:
```bash
# exec 1> $LOCATION_ECOASSIST_FILES/EcoAssist/logfiles/stdout.txt
# exec 2> $LOCATION_ECOASSIST_FILES/EcoAssist/logfiles/stderr.txt
 ```
3. Close and save the file;
4. Start EcoAssist as you would do normally and recreate the error.
</details>

This will show you EcoAssist's output during runtime. If there are any errors, they will most probably show up here. If you want you can copy-paste it and [email](mailto:petervanlunteren@hotmail.com) it to me, or [raise an issue](https://github.com/PetervanLunteren/EcoAssist/issues/new).

## How to create logfiles?
If there is an error during runtime, it is important to give the program the opportunity to write out its logs. First thing you'll need to do is recreate the error in EcoAssist. After that, close all EcoAssist windows by clicking the cross at the top - do not quit the program as a whole. On Mac and Linux close the terminal window last. If there is an error during the installation or opening, you don't have to worry about this - in that case the logfiles are automatically created. 
 
## How to find logfiles?
* Navigate to your `EcoAssist_files` folder. It's location is OS dependent, you can find its location [here](https://github.com/PetervanLunteren/EcoAssist/edit/main/errors.md#where-to-find-the-ecoassist-installation-files). 
* Navigate to `...\EcoAssist_files\EcoAssist\logfiles\`. 
  * `installation_log.txt` will give you information about the installation.
  * `session_log.txt` writes logs during runtime on Windows.
  * `stdout.txt` and `stderr.txt` write logs during runtime on Mac and Linux.

## Where to find the EcoAssist installation files?
All files are located in one folder, called `EcoAssist_files`. Please be aware that it's hidden, so you'll probably have to adjust your settings before you can see it (find out how to: [macOS](https://www.sonarworks.com/support/sonarworks/360003040160-Troubleshooting/360003204140-FAQ/5005750481554-How-to-show-hidden-files-Mac-and-Windows-), [Windows](https://support.microsoft.com/en-us/windows/view-hidden-files-and-folders-in-windows-97fbc472-c603-9d90-91d0-1166d1d9f4b5#WindowsVersion=Windows_11), [Linux](https://askubuntu.com/questions/232649/how-to-show-or-hide-a-hidden-file)).

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

## `Local variable 'elapsed time' referenced before assignment`
This error message can be thrown when trying to deploy a model. It basically means that the model outputs some unexpected text. First of all, try if the model deploys succesfully over the test images supplied [here](https://github.com/PetervanLunteren/EcoAssist#test-your-installation). Check if your preloaded models are correctly downloaded. Sometimes protection software prevent the download of the actual model files. There should be two files named `md_v5a.0.0.pt` and `md_v5b.0.0.pt` in `\EcoAssist_files\pretrained_models\`. You can find the location of the EcoAssist_files [here](https://github.com/PetervanLunteren/EcoAssist#uninstall). If that isn't the problem, the logfiles should point you in the right direction.

## `SSL certificate problem: unable to get local issuer certificate`
If you see this message poping up somewhere, there is something going on with your SSL certificates. Most probably that is due to some secrurity setting (VPN, firewall, proxy, etc.) which prevents it from downloading the specific package. Most of the times this can be fixed by simply disabling the VPN/firewall/proxy and reinstalling EcoAssist. If that doesn't work, try switching internet networks, from WiFi to ethernet, or vice versa. If all that doesn't work, you can disable SSL verification temporarily. If you want that, open a new console window and execute `git config --global http.sslVerify false`, then drag and drop the `install.bat` file in the same window and press enter. Please note that this solution opens you to attacks like man-in-the-middle attacks. Therefore turn on verification again after installing EcoAssist, by executing `git config --global http.sslVerify true`. If you see `'git' is not recognized as an internal or external command`, you'll have to explicitly tell you computer where it can find the git executable, by changing the commands to `path\to\git\installation\cmd\git.exe config --global http.sslVerify false`. 

## `ValueError: path is on mount '...', start on mount '...'`
This is a Windows error message and means that your training data is located on a different drive than EcoAssist. For example, it would say `ValueError: path is on mount 'C:', start on mount 'F:'`, which means that the training data is located on your `F:` drive, while EcoAssist is located on the `C:` drive. The sollution is to get everything on the same drive. So either install EcoAssist on the `F:` drive, or move the training data to the `C:` drive. 

## `error: RPC failed; curl 92 HTTP/2 stream 5 was not closed cleanly: CANCEL (err 8)` while installing
This error usually occurs when the internet signal speed is too slow or unstable. Are you by chance on a weak wifi network? If possible, try the installation again on a fibre internet connection, or perhaps on a different, stronger, wifi network. If you're using a VPN, try disconnecting from it. There are also some other ways we can try to solve it, but I think this would be the easiest one.

Let me know if this doesn't work!

## `PackagesNotFoundError: The following packages are not available from current channels`
I'm not sure what causes conda to not find certain packages on your device, but my guess is that some kind of protection software (firewall, VPN, antivirus, proxy settings, etc.) might be blocking Conda from accessing the required channels. Company computers often have protection software like this enabled. Could this be the case? If possible, try the EcoAssist installation again with the protection software (temporarily) disabled. Another possible solution is to run the conda installation with administrator privileges (if possible). Right-click on the installation script and select "Run as administrator."

You can check if the computer has access to the Conda channels by attempting to access the channels. Here's how:

**Using a Web Browser:**
Open a web browser and try to access the Conda channels directly. Can you open the following websites? You should see a list of hyperlinks (see screenshot).
* [https://conda.anaconda.org/conda-forge/win-64](https://conda.anaconda.org/conda-forge/win-64)
* [https://conda.anaconda.org/pytorch/win-64](https://conda.anaconda.org/pytorch/win-64)

**Using the command line:**
Open a new command prompt window and copy-paste the following commands and press enter. It will download a text file from the Conda channels to check if something is blocking the connection. This can be done using the following commands:
```
curl -O https://conda.anaconda.org/conda-forge/win-64/patch_instructions.json
```
```
curl -O https://conda.anaconda.org/pytorch/win-64/repodata_from_packages.json
```

The text files (`.json`) are downloaded to your root folder (if the download succeeded), and can be deleted afterward. We don't need them, It's just to check the connection. 

Let me know how this goes!

## `Exception: '>=' not supported between instances of 'RuntimeError' and 'int'`
Solution comming up...

## Example email for faulty installation

Seems like there was an issue during the installation. Nine times out of ten, these issues are due to security settings blocking certain downloads. This may be attributed to security software such as VPNs, proxy servers, firewall, or antivirus applications, which are known to be particularly strict on company computers. Could you please check if any of these security settings are enabled on your computer?

In order to debug, could you please:
1. Reboot your computer.
2. If possible, temporarily disable the protection software.
3. Repeat the EcoAssist installation using the latest installation file: https://addaxdatascience.com/ecoassist/#install.
4. Copy-paste the entire console output and save it to a text file. You might need to send it to me, if it turns out EcoAssist won’t function properly.
5. Double-click the shortcut file to open EcoAssist. Have some patience. The first time opening might take about a minute due to script compiling.
6. If that doesn’t work, try opening it in debug mode: https://github.com/PetervanLunteren/EcoAssist/blob/main/markdown/errors.md#how-to-run-ecoassist-in-debug-mode
7. Now you should see some output in the console. Again, copy-paste the entire console output, add it to your log file, and send it to me.

I’ll take a look and help you to get EcoAssist running!

## `ImportError: DLL load failed while importing _ctypes: The specified module could not be found.`
### Option 1
It looks like your miniforge installation was corrupted in one way or another. Perhaps due to an unstable internet connection, but who knows. A reinstall with stable internet should do the trick, but please note that all virtual environments created through miniforge will be lost. That is, if you installed miniforge just for EcoAssist, there is nothing to worry about. I'm just saying that if you're using miniforge for other applications too, you should double check before uninstalling it. 

### Option 2
It looks like you have two conda distributions on your machine, namely "C:\ProgramData\anaconda3" and "C:\ProgramData\miniforge3". These two might be interfering with each other. Try uninstalling one of them and retry the EcoAssist installation. I'm guessing that you installed miniforge3 especially for EcoAssist, right? Then it is safe to uninstall it again. Follow the steps below.
1. Double click the file "C:\ProgramData\miniforge3\Uninstall-Miniforge3.exe";
2. Follow the steps provided to uninstall;Leave Anaconda3 as it is and do not reinstall Miniforge3;
3. Repeat the EcoAssist installation with the latest install file: https://addaxdatascience.com/ecoassist/#install
4. It will probably find your anaconda3 installation automatically, but perhaps you'll have to provide the path when prompted: "C:\ProgramData\anaconda3".

Hope this works! Let me know how it goes.

## `PermissionError: [Errno 13] Permission denied: 'C:\\Users\\<>username\\AppData\\Local\\conda\\conda\\Cache\\notices\\notices.cache'`

This looks like conda can't access a certain file, which might be due to the fact that it is being used by another program. Could you restart your computer and try again? Make sure you are executing the latest install file: https://addaxdatascience.com/ecoassist/#install
