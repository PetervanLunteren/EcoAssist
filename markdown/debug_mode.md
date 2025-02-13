## How to run EcoAssist in debug mode?
It is possible to run EcoAssist in debug mode, where it'll print its output in a console window. That should point us in the right direction if there is an error. How to run it in debug mode depends on your operating system.
<details>
<summary><b>Windows</b></summary>
<br>
 
Navigate to `C:\Users\<username>\EcoAssist_files` and double click the `open-debug-mode.lnk` file. This opens EcoAssist in debug mode, where it logs to a terminal window. Now try to recreate the error and check the console output for its message.

<img width="944" alt="Screenshot 2025-02-13 at 09 03 15" src="https://github.com/user-attachments/assets/9e8a6977-8651-4808-ad32-ffd6dbe0d1bb" />


</details>
<details>
<summary><b>macOS</b></summary>
<br>

Navigate to `/Applications/EcoAssist_files` and double click the `EcoAssist <version-number> debug` file. This opens EcoAssist in debug mode, where it logs to a terminal window. Now try to recreate the error and check the console output for its message.

<img width="953" alt="Screenshot 2025-02-13 at 09 07 55" src="https://github.com/user-attachments/assets/ace4f48b-a095-4678-b4b4-a5d09a19f287" />

 
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

This will show you EcoAssist's output during runtime. If there are any errors, they will most probably show up here. Please copy-paste the entire console output and [email](mailto:petervanlunteren@hotmail.com) it to me, or [raise an issue](https://github.com/PetervanLunteren/EcoAssist/issues/new).

<img width="1196" alt="Screenshot 2024-08-12 at 10 47 14" src="https://github.com/user-attachments/assets/23c3d898-8de9-4369-a70d-78d736d0316d">
