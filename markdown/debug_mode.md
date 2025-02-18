## How to run AddaxAI in debug mode?
It is possible to run AddaxAI in debug mode, where it'll print its output in a console window. That should point us in the right direction if there is an error. How to run it in debug mode depends on your operating system.
<details>
<summary><b>Windows</b></summary>
<br>
 
Navigate to `C:\Users\<username>\AddaxAI_files` and double click the `open-debug-mode.lnk` file. This opens AddaxAI in debug mode, where it logs to a terminal window. Now try to recreate the error and check the console output for its message.

<img width="900" alt="Screenshot 2025-02-18 at 09 42 29" src="https://github.com/user-attachments/assets/6bbcc394-61e8-44d9-b592-8108d8091ac5" />

</details>
<details>
<summary><b>macOS</b></summary>
<br>

Navigate to `/Applications/AddaxAI_files` and double click the `AddaxAI debug` file. This opens AddaxAI in debug mode, where it logs to a terminal window. Now try to recreate the error and check the console output for its message.

<img width="900" alt="Screenshot 2025-02-18 at 09 43 25" src="https://github.com/user-attachments/assets/6eccaeef-116c-4e7c-923d-cc378a0e8184" />


</details>
<details>
<summary><b>Linux</b></summary>
<br>
 
1. Open the file `/home/<username>/.AddaxAI_files/AddaxAI/open.command` with a text editor like TextEdit or Visual Studio Code;
2. Outcomment the following lines by placing a hastag (`#`) in front, like so:
```bash
# exec 1> $LOCATION_ADDAXAI_FILES/AddaxAI/logfiles/stdout.txt
# exec 2> $LOCATION_ADDAXAI_FILES/AddaxAI/logfiles/stderr.txt
 ```
3. Close and save the file;
4. Start AddaxAI as you would do normally and recreate the error.
</details>

This will show you AddaxAI's output during runtime. If there are any errors, they will most probably show up here. Please copy-paste the entire console output and [email](mailto:petervanlunteren@hotmail.com) it to me, or [raise an issue](https://github.com/PetervanLunteren/AddaxAI/issues/new).

<img width="1196" alt="Screenshot 2024-08-12 at 10 47 14" src="https://github.com/user-attachments/assets/23c3d898-8de9-4369-a70d-78d736d0316d">
