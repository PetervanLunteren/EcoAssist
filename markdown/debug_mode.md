## How to run EcoAssist in debug mode?
It is possible to run EcoAssist in debug mode, where it'll print its output in a console window. That should point us in the right direction if there is an error. How to run it in debug mode depends on your operating system.
<details>
<summary><b>Windows</b></summary>
<br>
 
Open a fresh window of the command prompt (search start for "command prompt") and copy-paste the following line and press enter.
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

This will show you EcoAssist's output during runtime. If there are any errors, they will most probably show up here. Please copy-paste the entire console output and [email](mailto:petervanlunteren@hotmail.com) it to me, or [raise an issue](https://github.com/PetervanLunteren/EcoAssist/issues/new).
