It’s the first time I’ll install EcoAssist without admin rights, so I apologise if I might forget something here. The reason why EcoAssist needs admin rights, is that it needs access to files on the C:\ drive. For example, the EcoAssist_files folder with all required documents and possibly the anaconda3 folder. If you want to run it without admin rights, you need to make sure that all these files are in a place that you can access without admin rights (a folder inside your users folder).

Step 0: Send me the log files
There is the hidden EcoAssist_files folder, there is a folder containing log files. Could you send me all the files inside this folder? "C:\ProgramData\EcoAssist_files\EcoAssist\logfiles" This will give me some insight into where your installations are.

Step 1: Find Anaconda3
Search for “Anaconda3”.
- Is it located inside your users folder (that means, can you access it without admin rights)? Is so, no worries. That means it all good.
- If it is located somewhere where you do need admin rights (for example C:\ProgramData\Anaconda3) you’ll need to uninstall anaconda3. If EcoAssist is the only reason that you have Anaconda3 and you don’t use it for anything else, you can simply uninstall Anaconda and reinstall it on a location inside your users folder. If you are using it for other projects and have environments set up, you probably don’t want to uninstall it.

Step 2: Uninstall EcoAssist and possibly Anaconda3
You can do that by using this file: https://petervanlunteren.github.io/EcoAssist/Windows_uninstall_EcoAssist.bat. This uninstall needs admin rights too (sorry). Here you can enter “y” or “n” to uninstall Anaconda3.

Step 3: Adjust install and open files
I’ll send you the adjusted files later. I’ll have to go out 
