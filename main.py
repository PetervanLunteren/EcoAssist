# This is a placeholder script for PyInstaller to create the main executable 
# https://addaxdatascience.com/ecoassist/
# Created by Peter van Lunteren
# Latest edit by Peter van Lunteren on 12 Jan 2024

import os
import subprocess
import sys
import platform

print("\n")

# check os
system = platform.system()

# os dependent python executables
def get_python_interprator(env_name):
    if system == 'Windows':
        return os.path.join(EcoAssist_files, "envs", f"env-{env_name}", "python.exe")
    else:
        return os.path.join(EcoAssist_files, "envs", f"env-{env_name}", "bin", "python")

# clean path
if getattr(sys, 'frozen', False):
    EcoAssist_files = os.path.dirname(sys.executable)
else:
    EcoAssist_files = os.path.dirname(os.path.abspath(__file__))
    
if EcoAssist_files.endswith("main.app/Contents/MacOS"):
    EcoAssist_files = EcoAssist_files.replace("main.app/Contents/MacOS", "")
    
if EcoAssist_files.endswith(".app/Contents/MacOS"):
    EcoAssist_files = os.path.dirname(os.path.dirname(os.path.dirname(EcoAssist_files)))

# init paths    
GUI_script = os.path.join(EcoAssist_files, "EcoAssist", "EcoAssist_GUI.py")
first_startup_file = os.path.join(EcoAssist_files, "first-startup.txt")

# log
print(f"      EcoAssist_files: {EcoAssist_files}")
print(f"       sys.executable: {sys.executable.replace(EcoAssist_files, '.')}")
print(f"           GUI_script: {GUI_script.replace(EcoAssist_files, '.')}")

# python executable
python_executable = get_python_interprator("base")
print(f"    python_executable: {python_executable.replace(EcoAssist_files, '.')}")

# cuda toolkit
cuda_toolkit_path = os.environ.get("CUDA_HOME") or os.environ.get("CUDA_PATH")
print(f"    cuda_toolkit_path: {cuda_toolkit_path}")

# run the GUI script
print("\nOpening application...") 
if system == 'Windows':
    if sys.executable.endswith("debug.exe"):
        subprocess.run([get_python_interprator("base"), GUI_script])
        input("Press [Enter] to close console window...") # keep console open after closing app
    else:
        subprocess.run([get_python_interprator("base"), GUI_script],
                       creationflags=subprocess.CREATE_NO_WINDOW)
else:
    subprocess.run([get_python_interprator("base"), GUI_script])
