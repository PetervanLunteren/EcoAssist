# GUI wrapper around MegaDetector with some additional features.
# Written by Peter van Lunteren, 30 Jan 2022 (latest edit)

# import packages like a christmas tree
import os
import re
import sys
import cv2
import git
import json
import math
import time
import signal
import shutil
import platform
import datetime
import traceback
import subprocess
import webbrowser
import numpy as np
import tkinter as tk
from pathlib import Path
from random import randint
from functools import partial
from tkHyperlinkManager import *
from subprocess import Popen, PIPE
import xml.etree.cElementTree as ET
from PIL import ImageTk, Image, ImageFilter
from bounding_box import bounding_box as bb
from tkinter import filedialog, ttk, messagebox as mb

# set global variables
version = "3.0"
EcoAssist_files = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# insert pythonpath
sys.path.insert(0, os.path.join(EcoAssist_files))
sys.path.insert(0, os.path.join(EcoAssist_files, "ai4eutils"))
sys.path.insert(0, os.path.join(EcoAssist_files, "yolov5"))
sys.path.insert(0, os.path.join(EcoAssist_files, "cameratraps"))
print(sys.path)

##########################################
############# MAIN FUNCTIONS #############
##########################################

# create json output files 
def md_process(path_to_image_folder, selected_options, data_type):
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")
    
    # adjust variables for images or videos
    if data_type == "img":
        progress_stats = progress_img_stats
        progress_frame = progress_img_frame
        progress_progbar = progress_img_progbar
    else:
        progress_stats = progress_vid_stats
        progress_frame = progress_vid_frame
        progress_progbar = progress_vid_progbar
    
    # display loading window
    progress_stats['text'] = create_md_progress_lbl(command="load", data_type = data_type)

    # prepare variables
    chosen_folder = str(Path(path_to_image_folder))
    run_detector_batch_py = os.path.join(EcoAssist_files, "cameratraps", "detection", "run_detector_batch.py")
    image_recognition_file = os.path.join(chosen_folder, "image_recognition_file.json")
    process_video_py = os.path.join(EcoAssist_files, "cameratraps", "detection", "process_video.py")
    video_recognition_file = "--output_json_file=" + os.path.join(chosen_folder, "video_recognition_file.json")
    GPU_param = "Unknown"

    # select model based on user input via dropdown menu
    custom_model_bool = False
    if var_model.get() == "MDv5a": 
        # set model file
        model_file = os.path.join(EcoAssist_files, "megadetector", "md_v5a.0.0.pt")
        
        # set yolov5 git to accommodate old models
        switch_yolov5_git_to("old models")
        
    elif var_model.get() == "MDv5b":
        # set model file
        model_file = os.path.join(EcoAssist_files, "megadetector", "md_v5b.0.0.pt")
        
        # set yolov5 git to accommodate old models
        switch_yolov5_git_to("old models")
    else:
        # set model file
        model_file = custom_model_choice
        custom_model_bool = True

        # set yolov5 git to accommodate new models
        switch_yolov5_git_to("new models")
        
        # extract classes
        label_map = extract_label_map_from_model(model_file)
            
    # create commands for Windows
    if os.name == 'nt':
        if selected_options == []:
            img_command = [sys.executable, run_detector_batch_py, model_file, chosen_folder, image_recognition_file]
            vid_command = [sys.executable, process_video_py, video_recognition_file, model_file, chosen_folder]
        else:
            img_command = [sys.executable, run_detector_batch_py, model_file, *selected_options, chosen_folder, image_recognition_file]
            vid_command = [sys.executable, process_video_py, *selected_options, video_recognition_file, model_file, chosen_folder]

     # create command for MacOS and Linux
    else:
        if selected_options == []:
            img_command = [f"'{sys.executable}' '{run_detector_batch_py}' '{model_file}' '{chosen_folder}' '{image_recognition_file}'"]
            vid_command = [f"'{sys.executable}' '{process_video_py}' '{video_recognition_file}' '{model_file}' '{chosen_folder}'"]
        else:
            selected_options = "' '".join(selected_options)
            img_command = [f"'{sys.executable}' '{run_detector_batch_py}' '{model_file}' '{selected_options}' '{chosen_folder}' '{image_recognition_file}'"]
            vid_command = [f"'{sys.executable}' '{process_video_py}' '{selected_options}' '{video_recognition_file}' '{model_file}' '{chosen_folder}'"]

    # pick one command
    if data_type == "img":
        command = img_command
    else:
        command = vid_command
    
    # log
    print(f"command:\n\n{command}\n\n")

    # prepare process and cancel method per OS
    if os.name == 'nt':
        # run windows command
        p = Popen(command,
                  stdout=subprocess.PIPE,
                  stderr=subprocess.STDOUT,
                  bufsize=1,
                  shell=True,
                  universal_newlines=True)

        # cancel button
        btn_cancel = Button(progress_frame, text="Cancel", command=lambda: Popen(f"TASKKILL /F /PID {p.pid} /T"))
        btn_cancel.grid(row=9, column=0, columnspan=2)

    else:
        # run unix command
        p = Popen(command,
                  stdout=subprocess.PIPE,
                  stderr=subprocess.STDOUT,
                  bufsize=1,
                  shell=True,
                  universal_newlines=True,
                  preexec_fn=os.setsid)
        
        # add cancel button
        btn_cancel = Button(progress_frame, text="Cancel", command=lambda: os.killpg(os.getpgid(p.pid), signal.SIGTERM))
        btn_cancel.grid(row=9, column=0, columnspan=2)

    
    # read output and direct to tkinter
    for line in p.stdout:
        print(line, end='')
        
        # catch megadetecor errors
        if line.startswith("No image files found"):
            mb.showerror("No images found", f"There are no images found in '{chosen_folder}'. \n\n"
                            "Are you sure you specified the correct folder? Or should you have "
                            "selected the option 'Include subdirectories'?")
            return
        if line.startswith("No videos found"):
            mb.showerror("No videos found", line + "\nAre you sure you specified the correct "
                            "folder? Or should you have selected the option 'Include subdirectories'?")
            return
        if line.startswith("No frames extracted"):
            mb.showerror("Could not extract frames", line + "\nConverting the videos to .mp4 might"
                            " fix the issue.")
            return
        if "Exception:" in line:
            mb.showerror("Error", "MegaDetector error:\n\n" + line)
        if "Warning:" in line and not '%' in line[0:4]:
            mb.showerror("Warning", "MegaDetector warning:\n\n" + line)
        
        # get process stats and send them to tkinter
        if line.startswith("GPU available: False"):
            GPU_param = "CPU"
        elif line.startswith("GPU available: True"):
            GPU_param = "GPU"
        elif '%' in line[0:4]:
            
            # read stats
            times = re.search("(\[.*?\])", line)[1]
            progress_bar = re.search("^[^\/]*[^[^ ]*", line.replace(times, ""))[0]
            percentage = re.search("\d*%", progress_bar)[0][:-1]
            current_im = re.search("\d*\/", progress_bar)[0][:-1]
            total_im = re.search("\/\d*", progress_bar)[0][1:]
            elapsed_time = re.search("(?<=\[)(.*)(?=<)", times)[1]
            time_left = re.search("(?<=<)(.*)(?=,)", times)[1]
            processing_speed = re.search("(?<=,)(.*)(?=])", times)[1].strip()
            
            # order stats
            stats = create_md_progress_lbl(elapsed_time = elapsed_time,
                                            time_left = time_left,
                                            current_im = current_im,
                                            total_im = total_im,
                                            processing_speed = processing_speed,
                                            percentage = percentage,
                                            GPU_param = GPU_param,
                                            data_type = data_type,
                                            command = "running")
            
            # print stats
            progress_progbar['value'] = percentage
            progress_stats['text'] = stats
        root.update()
    
    # repeat when process is done
    progress_stats['text'] = create_md_progress_lbl(elapsed_time = elapsed_time,
                                                    time_left = time_left,
                                                    current_im = current_im,
                                                    total_im = total_im,
                                                    processing_speed = processing_speed,
                                                    percentage = percentage,
                                                    GPU_param = GPU_param,
                                                    data_type = data_type,
                                                    command = "done")
    root.update()
        
    # remove button after process is done
    btn_cancel.grid_remove()
    
    # remove frames.json file
    frames_video_recognition_file = os.path.join(chosen_folder, "video_recognition_file.frames.json")
    if os.path.isfile(frames_video_recognition_file):
        os.remove(frames_video_recognition_file)
    
    # create ecoassist metadata
    ecoassist_metadata = {"ecoassist_metadata" : {"version" : version,
                                                  "frame_completion_info" : {"sep_frame_completed" : False,
                                                                             "vis_frame_completed" : False,
                                                                             "crp_frame_completed" : False,
                                                                             "xml_frame_completed" : False},
                                                  "custom_model" : custom_model_bool,
                                                  "custom_model_info" : {}}}
    if custom_model_bool:
        ecoassist_metadata["ecoassist_metadata"]["custom_model_info"] = {"model_name" : os.path.basename(os.path.normpath(model_file)),
                                                                         "label_map" : label_map}
    
    # write metadata to json
    image_recognition_file = os.path.join(chosen_folder, "image_recognition_file.json")
    video_recognition_file = os.path.join(chosen_folder, "video_recognition_file.json")
    if data_type == "img" and os.path.isfile(image_recognition_file):
        append_to_json(image_recognition_file, ecoassist_metadata)
        if var_abs_paths.get():
            # make paths absolute if user specified
            make_json_absolute(image_recognition_file)
    if data_type == "vid" and os.path.isfile(video_recognition_file):
        append_to_json(video_recognition_file, ecoassist_metadata)
        if var_abs_paths.get():
            make_json_absolute(video_recognition_file)# create json output files 

# start megadetector process
def start_md():
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")
    
    # fetch global variables
    global progress_img_frame
    global progress_vid_frame
    
    # check if user selected to process either images or videos
    if not var_process_img.get() and not var_process_vid.get():
        mb.showerror("Nothing selected to be processed", message="You selected neither images nor videos to be processed.")
        return
    
    # check if chosen folder is valid
    if var_choose_folder.get() in ["", "/", "\\", ".", "~", ":"] or not os.path.isdir(var_choose_folder.get()):
        mb.showerror("Error", message="Please specify a directory with data to be processed.")
        return
    
    # check if checkpoint entry is valid
    if var_use_checkpnts.get() and not var_checkpoint_freq.get().isdecimal():
        if mb.askyesno("Invalid value",
                        "You either entered an invalid value for the checkpoint frequency, or none at all. You can only "
                        "enter numberic characters.\n\nDo you want to proceed with the default value 100?"):
            var_checkpoint_freq.set("100")
            ent_checkpoint_freq.config(fg='black')
        else:
            return
    
    # check if the nth frame entry is valid
    if var_not_all_frames.get() and not var_nth_frame.get().isdecimal():
        if mb.askyesno("Invalid value",
                        "You either entered an invalid value for 'Analyse every Nth frame', or none at all. You can only "
                        "enter numberic characters.\n\nDo you want to proceed with the default value 10?\n\n"
                        "That means you process only 1 out of 10 frames, making the process time 10 times faster."):
            var_nth_frame.set("10")
            ent_nth_frame.config(fg='black')
        else:
            return
        
    # create command for the image process to be passed on to run_detector_batch.py
    additional_img_options = ["--output_relative_filenames"]
    if not var_exclude_subs.get():
        additional_img_options.append("--recursive")
    if var_excl_detecs.get():
        additional_img_options.append("--threshold=" + str(var_md_thresh.get()))
    if var_use_checkpnts.get():
        additional_img_options.append("--checkpoint_frequency=" + var_checkpoint_freq.get())
    if var_cont_checkpnt.get():
        additional_img_options.append("--resume_from_checkpoint=" + loc_chkpnt_file)

    # create command for the video process to be passed on to process_video.py
    additional_vid_options = []
    if not var_exclude_subs.get():
        additional_vid_options.append("--recursive")
    if var_excl_detecs.get():
        additional_vid_options.append("--rendering_confidence_threshold=" + str(var_md_thresh.get()))
        additional_vid_options.append("--json_confidence_threshold=" + str(var_md_thresh.get()))
    if var_not_all_frames.get():
        additional_vid_options.append("--frame_sample=" + var_nth_frame.get())
    
    # open new window with progress bar and stats
    md_progress_window = Toplevel(root)
    md_progress_window.title("MegaDetector progress")
    md_progress_window.geometry()

    # logo
    logo = tk.Label(md_progress_window, image=grey_bg_logo)
    logo.grid(column=0, row=0, columnspan=2, sticky='ew', pady=(5, 0))

    # add image progress
    if var_process_img.get():
        progress_img_frame = LabelFrame(md_progress_window, text=" Process images ", pady=2, padx=5, relief='solid', highlightthickness=5, font=100, fg='darkblue')
        progress_img_frame.configure(font=(text_font, 15, "bold"))
        progress_img_frame.grid(column=0, row=1, columnspan=2, sticky='ew')
        progress_img_frame.columnconfigure(0, weight=3, minsize=115)
        progress_img_frame.columnconfigure(1, weight=1, minsize=115)
        global progress_img_progbar
        progress_img_progbar = ttk.Progressbar(master=progress_img_frame, orient='horizontal', mode='determinate', length=280)
        progress_img_progbar.grid(column=0, row=0, columnspan=2, padx=5, pady=(3,0))
        global progress_img_stats
        progress_img_stats = ttk.Label(master=progress_img_frame, text=create_postprocess_lbl())
        progress_img_stats.grid(column=0, row=1, padx=5, pady=(0,3), columnspan=2)

    # add video progress
    if var_process_vid.get():
        progress_vid_frame = LabelFrame(md_progress_window, text=" Process videos ", pady=2, padx=5, relief='solid', highlightthickness=5, font=100, fg='darkblue')
        progress_vid_frame.configure(font=(text_font, 15, "bold"))
        progress_vid_frame.grid(column=0, row=2, columnspan=2, sticky='ew')
        progress_vid_frame.columnconfigure(0, weight=3, minsize=115)
        progress_vid_frame.columnconfigure(1, weight=1, minsize=115)
        global progress_vid_progbar
        progress_vid_progbar = ttk.Progressbar(master=progress_vid_frame, orient='horizontal', mode='determinate', length=280)
        progress_vid_progbar.grid(column=0, row=0, columnspan=2, padx=10, pady=2)
        global progress_vid_stats
        progress_vid_stats = ttk.Label(master=progress_vid_frame, text=create_postprocess_lbl())
        progress_vid_stats.grid(column=0, row=1, columnspan=2)
    
    try:
        # process images ...
        if var_process_img.get():
            md_process(var_choose_folder.get(), additional_img_options, data_type = "img")
        # ... and/or videos
        if var_process_vid.get():
            md_process(var_choose_folder.get(), additional_vid_options, data_type = "vid")
        
        # reset window
        update_frame_states()
        
        # close progress window
        md_progress_window.destroy()

    except Exception as error:
        # log error
        print("ERROR:\n" + str(error) + "\n\nDETAILS:\n" + str(traceback.format_exc()) + "\n\n")
        
        # show error
        mb.showerror(title="Error",
                     message="An error has occurred (EcoAssist v" + version + "): '" + str(error) + "'.",
                     detail=traceback.format_exc())
        
        # reset root with new states
        reset_frame_states()
        
        # close window
        md_progress_window.destroy()

# move the files to their associated directories and adjust the json file paths
def sep_process(path_to_image_folder, var_file_placement, threshold, data_type, var_sep_conf):
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")
    
    # prepare variables
    global cancel_var
    if data_type == "img":
        recognition_file = os.path.join(path_to_image_folder, "image_recognition_file.json")
        progress_sep_frame = img_progress_sep_frame
        progress_sep_progbar = img_progress_sep_progbar
        progress_sep_stats = img_progress_sep_stats
    else:
        recognition_file = os.path.join(path_to_image_folder, "video_recognition_file.json")
        progress_sep_frame = vid_progress_sep_frame
        progress_sep_progbar = vid_progress_sep_progbar
        progress_sep_stats = vid_progress_sep_stats
    start_time = time.time()
    nloop = 1
    
    # make sure json has absolute paths
    json_paths_converted = False
    if check_json_paths(recognition_file) == "relative":
        make_json_absolute(recognition_file)
        json_paths_converted = True
    
    # add cancel button
    cancel_var = False
    btn_cancel = Button(progress_sep_frame, text="Cancel", command=cancel)
    btn_cancel.grid(row=9, column=0, columnspan=2)
    
    # fetch label map
    label_map = fetch_label_map_from_json(recognition_file)
        
    # open json file
    with open(recognition_file) as image_recognition_file_content:
        data = json.load(image_recognition_file_content)
    n_images = len(data['images'])
    
    # loop though json
    for image in data['images']:
        if cancel_var:
            break
        
        # get info
        file = image['file']
        detections_list = image['detections']
        n_detections = len(detections_list)
        max_detection_conf = image['max_detection_conf']
        progress_sep_progbar['value'] += 100 / n_images
        if n_detections == 0:
            image['file'] = move_files(file, "empty", var_file_placement, max_detection_conf, var_sep_conf)
        else:
            
            # check detections
            unique_labels = []
            for detection in image['detections']:
                conf = detection["conf"]
                category = detection["category"]
                if conf >= threshold:
                    label = label_map[category]
                    unique_labels.append(label)
                    unique_labels = list(set(unique_labels))
            
            # move images
            if len(unique_labels) > 1:
                image['file'] = move_files(file, "multiple_categories", var_file_placement, max_detection_conf, var_sep_conf)
            elif len(unique_labels) == 0:
                image['file'] = move_files(file, "empty", var_file_placement, max_detection_conf, var_sep_conf)
            else:
                image['file'] = move_files(file, label, var_file_placement, max_detection_conf, var_sep_conf)
                
        # calculate stats
        elapsed_time_sep = str(datetime.timedelta(seconds=round(time.time() - start_time)))
        time_left_sep = str(datetime.timedelta(seconds=round(((time.time() - start_time) * n_images / nloop) - (time.time() - start_time))))
        progress_sep_stats['text'] = create_postprocess_lbl(elapsed_time_sep, time_left_sep, command="running")
        nloop += 1
        root.update()
    
    # remove cancel button
    btn_cancel.grid_remove()
    
    # write adjusted paths to json file
    with open(recognition_file, "w") as json_file:
        json.dump(data, json_file, indent=1)
    
    # change json paths back, if converted earlier
    if json_paths_converted:
        make_json_relative(recognition_file)
    
    # update completed status in json
    update_frame_completion_info(recognition_file, "sep_frame_completed", True)
    
    # let the user know it's done
    progress_sep_stats['text'] = create_postprocess_lbl(elapsed_time_sep, time_left_sep, command="done")
    root.update()

# start folder separation
def start_sep():
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")
        
    # set global variables
    global img_progress_sep_frame
    global vid_progress_sep_frame
    
    # check which json files are present
    img_json = False
    if os.path.isfile(os.path.join(var_choose_folder.get(), "image_recognition_file.json")):
        img_json = True
    vid_json = False
    if os.path.isfile(os.path.join(var_choose_folder.get(), "video_recognition_file.json")):
        vid_json = True
    if not img_json and not vid_json:
        mb.showerror("Error", "No MegaDetector output file present. Make sure you run step "
                     "2 before separating the files.")
        return
    
    # open new window with progress bar and stats
    sep_progress_window = Toplevel(root)
    sep_progress_window.title("File separation progress")
    sep_progress_window.geometry()

    # logo
    logo = tk.Label(sep_progress_window, image=grey_bg_logo)
    logo.grid(column=0, row=0, columnspan=2, sticky='ew', pady=(5, 0))

    # add image progress
    if img_json:
        img_progress_sep_frame = LabelFrame(sep_progress_window, text=" Separating images ", pady=2, padx=5, relief='solid', highlightthickness=5, font=100, fg='darkblue')
        img_progress_sep_frame.configure(font=(text_font, 15, "bold"))
        img_progress_sep_frame.grid(column=0, row=1, columnspan=2, sticky='ew')
        img_progress_sep_frame.columnconfigure(0, weight=3, minsize=115)
        img_progress_sep_frame.columnconfigure(1, weight=1, minsize=115)
        global img_progress_sep_progbar
        img_progress_sep_progbar = ttk.Progressbar(master=img_progress_sep_frame, orient='horizontal', mode='determinate', length=280)
        img_progress_sep_progbar.grid(column=0, row=0, columnspan=2, padx=5, pady=(3,0))
        global img_progress_sep_stats
        img_progress_sep_stats = ttk.Label(master=img_progress_sep_frame, text=create_postprocess_lbl())
        img_progress_sep_stats.grid(column=0, row=1, padx=5, pady=(0,3), columnspan=2)

    # add video progress
    if vid_json:
        vid_progress_sep_frame = LabelFrame(sep_progress_window, text=" Separating videos ", pady=2, padx=5, relief='solid', highlightthickness=5, font=100, fg='darkblue')
        vid_progress_sep_frame.configure(font=(text_font, 15, "bold"))
        vid_progress_sep_frame.grid(column=0, row=2, columnspan=2, sticky='ew')
        vid_progress_sep_frame.columnconfigure(0, weight=3, minsize=115)
        vid_progress_sep_frame.columnconfigure(1, weight=1, minsize=115)
        global vid_progress_sep_progbar
        vid_progress_sep_progbar = ttk.Progressbar(master=vid_progress_sep_frame, orient='horizontal', mode='determinate', length=280)
        vid_progress_sep_progbar.grid(column=0, row=0, columnspan=2, padx=5, pady=(3,0))
        global vid_progress_sep_stats
        vid_progress_sep_stats = ttk.Label(master=vid_progress_sep_frame, text=create_postprocess_lbl())
        vid_progress_sep_stats.grid(column=0, row=1, padx=5, pady=(0,3), columnspan=2)
    
    try:
        # separate images ...
        if img_json:
            sep_process(var_choose_folder.get(), var_file_placement.get(), var_sep_thresh.get(), "img", var_sep_conf.get())
        # ... and videos
        if vid_json:
            sep_process(var_choose_folder.get(), var_file_placement.get(), var_sep_thresh.get(), "vid", var_sep_conf.get())
        
        # reset window
        update_frame_states()
        
        # close progress window
        sep_progress_window.destroy()
    
    except Exception as error:
        # log error
        print("ERROR:\n" + str(error) + "\n\nDETAILS:\n" + str(traceback.format_exc()) + "\n\n")
        
        # show error
        mb.showerror(title="Error",
                     message="An error has occurred (EcoAssist v" + version + "): '" + str(error) + "'.",
                     detail=traceback.format_exc())
        
        # reset window
        update_frame_states()
        
        # close window
        sep_progress_window.destroy()

# draw bounding boxes
def vis_process(path_to_image_folder, threshold):
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")
    
    # warn user if needed
    if check_json_presence_and_warn_user("visualize", "visualizing", "visualization"):
        return

    # prepare variables
    global cancel_var
    start_time = time.time()
    nloop = 1
    recognition_file = os.path.join(path_to_image_folder, "image_recognition_file.json")

    # make sure json has absolute paths
    json_paths_converted = False
    if check_json_paths(recognition_file) == "relative":
        make_json_absolute(recognition_file)
        json_paths_converted = True
    
    # add cancel button
    cancel_var = False
    btn_cancel = Button(progress_vis_frame, text="Cancel", command=cancel)
    btn_cancel.grid(row=9, column=0, columnspan=2)
    
    # fetch label map
    label_map = fetch_label_map_from_json(recognition_file)
    
    # create list with colours
    colors = ["fuchsia", "blue", "orange", "yellow", "green", "red"]
    length_diff = len(colors) - len(label_map)
    if length_diff > 0:
        # first 6 classes get default colors
        colors = colors[:length_diff]
    if length_diff < 0:
        # all classes after that get random color
        for i in range(abs(length_diff)):
            colors.append('#%06X' % randint(0, 0xFFFFFF))
    
    # open json file
    with open(recognition_file) as json_file:
        data = json.load(json_file)
    n_images = len(data['images'])
    
    # loop though json
    for image in data['images']:
        if cancel_var:
            break
        n_detections = len(image['detections'])
        progress_vis_progbar['value'] += 100 / n_images
        if not n_detections == 0:
            file = image['file']
            
            # open image
            im = cv2.imread(file)
            
            # loop though detections
            for detection in image['detections']:
                
                # get info 
                category = detection['category']
                conf = detection['conf']
                height, width = im.shape[:2]
                left = int(round(detection['bbox'][0] * width))
                top = int(round(detection['bbox'][1] * height))
                right = int(round(detection['bbox'][2] * width)) + left
                bottom = int(round(detection['bbox'][3] * height)) + top
                
                # draw box
                visualizations = 0
                if conf >= threshold:
                    label = f"{str(label_map[category])} {conf}"
                    color = colors[int(category)-1]
                    bb.add(im, left, top, right, bottom, label, color)
                    visualizations += 1
            
            # save image
            if visualizations > 0:
                path, file = os.path.split(os.path.splitext(file)[0] + '_visualized' + '.jpg')
                Path(os.path.join(path, 'visualized_images')).mkdir(parents=True, exist_ok=True)
                cv2.imwrite(os.path.join(path, 'visualized_images', file), im)
        
        # calculate stats
        elapsed_time_bbox = str(datetime.timedelta(seconds=round(time.time() - start_time)))
        time_left_bbox = str(datetime.timedelta(seconds=round(((time.time() - start_time) * n_images / nloop) - (time.time() - start_time))))
        progress_vis_stats['text'] = create_postprocess_lbl(elapsed_time_bbox, time_left_bbox, command="running")
        nloop += 1
        root.update()
    
    # remove cancel button
    btn_cancel.grid_remove()

    # change json paths back, if converted earlier
    if json_paths_converted:
        make_json_relative(recognition_file)
    
    # update completed status in json
    update_frame_completion_info(recognition_file, "vis_frame_completed", True)
    
    # let the user know it's done
    progress_vis_stats['text'] = create_postprocess_lbl(elapsed_time_bbox, time_left_bbox, command="done")
    root.update()

# start drawing bounding boxes
def start_vis():
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")

    # set global variable
    global progress_vis_frame

    # open new window with progress bar and stats
    vis_progress_window = Toplevel(root)
    vis_progress_window.title("File visualization progress")
    vis_progress_window.geometry()
    
    # logo
    logo = tk.Label(vis_progress_window, image=grey_bg_logo)
    logo.grid(column=0, row=0, columnspan=2, sticky='ew', pady=(5, 0))
    
    # show visualisation progress
    progress_vis_frame = LabelFrame(vis_progress_window, text=" Visualizing images ", pady=2, padx=5, relief='solid', highlightthickness=5, font=100, fg='darkblue')
    progress_vis_frame.configure(font=(text_font, 15, "bold"))
    progress_vis_frame.grid(column=0, row=1, columnspan=2, sticky='ew')
    progress_vis_frame.columnconfigure(0, weight=3, minsize=115)
    progress_vis_frame.columnconfigure(1, weight=1, minsize=115)
    global progress_vis_progbar
    progress_vis_progbar = ttk.Progressbar(master=progress_vis_frame, orient='horizontal', mode='determinate', length=280)
    progress_vis_progbar.grid(column=0, row=0, columnspan=2, padx=5, pady=(3,0))
    global progress_vis_stats
    progress_vis_stats = ttk.Label(master=progress_vis_frame, text=create_postprocess_lbl())
    progress_vis_stats.grid(column=0, row=1, padx=5, pady=(0,3), columnspan=2)

    try:
        # start actual visualisation process
        vis_process(var_choose_folder.get(), var_vis_thresh.get())
        
        # reset window
        update_frame_states()
        
        # close progress window
        vis_progress_window.destroy()

    except Exception as error:
        # log error
        print("ERROR:\n" + str(error) + "\n\nDETAILS:\n" + str(traceback.format_exc()) + "\n\n")
        
        # show error
        mb.showerror(title="Error",
                     message="An error has occurred (EcoAssist v" + version + "): '" + str(error) + "'.",
                     detail=traceback.format_exc())
        
        # reset window
        update_frame_states()
        
        # close window
        vis_progress_window.destroy()

# crop detections
def crp_process(path_to_image_folder, threshold):
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")

    # warn user if needed
    if check_json_presence_and_warn_user("crop", "cropping", "cropping"):
        return

    # prepare variables
    global cancel_var
    start_time = time.time()
    nloop = 1
    recognition_file = os.path.join(path_to_image_folder, "image_recognition_file.json")

    # make sure json has absolute paths
    json_paths_converted = False
    if check_json_paths(recognition_file) == "relative":
        make_json_absolute(recognition_file)
        json_paths_converted = True

    # add cancel button
    cancel_var = False
    btn_cancel = Button(progress_crp_frame, text="Cancel", command=cancel)
    btn_cancel.grid(row=9, column=0, columnspan=2)

    # fetch label map
    label_map = fetch_label_map_from_json(recognition_file)

    # open json file
    with open(recognition_file) as json_file:
        data = json.load(json_file)
    n_images = len(data['images'])
    
    # loop though json
    for image in data['images']:
        if cancel_var:
            break
        n_detections = len(image['detections'])
        progress_crp_progbar['value'] += 100 / n_images
        counter = 1
        if not n_detections == 0:
            
            # loop though detections
            for detection in image['detections']:
                
                # get info 
                file = image['file']
                category = detection['category']
                conf = detection['conf']
                im = Image.open(file)
                width, height = im.size
                left = int(round(detection['bbox'][0] * width))
                top = int(round(detection['bbox'][1] * height))
                right = int(round(detection['bbox'][2] * width)) + left
                bottom = int(round(detection['bbox'][3] * height)) + top
                
                # crop image
                cropped_im = im.crop((left, top, right, bottom))
                if conf >= threshold:
                    label = label_map[category]
                    path, file_ext = os.path.split(os.path.splitext(file)[0] + '_crop' + str(counter) + '_' + label + '.jpg')
                    counter += 1
                
                # save image
                if counter > 1:
                    Path(os.path.join(path, 'cropped_images')).mkdir(parents=True, exist_ok=True)
                    cropped_im.save(os.path.join(path, 'cropped_images', file_ext))

        # calculate stats
        elapsed_time_crop = str(datetime.timedelta(seconds=round(time.time() - start_time)))
        time_left_crop = str(datetime.timedelta(seconds=round(((time.time() - start_time) * n_images / nloop) - (time.time() - start_time))))
        progress_crp_stats['text'] = create_postprocess_lbl(elapsed_time_crop, time_left_crop, command="running")
        nloop += 1
        root.update()

    # remove cancel button
    btn_cancel.grid_remove()

    # change json paths back, if converted earlier
    if json_paths_converted:
        make_json_relative(recognition_file)
    
    # update completed status in json
    update_frame_completion_info(recognition_file, "crp_frame_completed", True)

    # let the user know it's done
    progress_crp_stats['text'] = create_postprocess_lbl(elapsed_time_crop, time_left_crop, command="done")
    root.update()

# start cropping
def start_crp():
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")
    
    # set global variable
    global progress_crp_frame
    
    # open new window with progress bar and stats
    crp_progress_window = Toplevel(root)
    crp_progress_window.title("File cropping progress")
    crp_progress_window.geometry()
    
    # logo
    logo = tk.Label(crp_progress_window, image=grey_bg_logo)
    logo.grid(column=0, row=0, columnspan=2, sticky='ew', pady=(5, 0))
    
    # show cropping progress
    progress_crp_frame = LabelFrame(crp_progress_window, text=" Cropping images ", pady=2, padx=5, relief='solid', highlightthickness=5, font=100, fg='darkblue')
    progress_crp_frame.configure(font=(text_font, 15, "bold"))
    progress_crp_frame.grid(column=0, row=1, columnspan=2, sticky='ew')
    progress_crp_frame.columnconfigure(0, weight=3, minsize=115)
    progress_crp_frame.columnconfigure(1, weight=1, minsize=115)
    global progress_crp_progbar
    progress_crp_progbar = ttk.Progressbar(master=progress_crp_frame, orient='horizontal', mode='determinate', length=280)
    progress_crp_progbar.grid(column=0, row=0, columnspan=2, padx=5, pady=(3,0))
    global progress_crp_stats
    progress_crp_stats = ttk.Label(master=progress_crp_frame, text=create_postprocess_lbl())
    progress_crp_stats.grid(column=0, row=1, padx=5, pady=(0,3), columnspan=2)

    try:
        # start actual cropping process
        crp_process(var_choose_folder.get(), var_crp_thresh.get())
        
        # reset window
        update_frame_states()
        
        # close progress window
        crp_progress_window.destroy()

    except Exception as error:
        # log error
        print("ERROR:\n" + str(error) + "\n\nDETAILS:\n" + str(traceback.format_exc()) + "\n\n")
        
        # show error
        mb.showerror(title="Error",
                     message="An error has occurred (EcoAssist v" + version + "): '" + str(error) + "'.",
                     detail=traceback.format_exc())
        
        # reset window
        update_frame_states()
        
        # close window
        crp_progress_window.destroy()

# create xml files
def xml_process(path_to_image_folder, threshold):
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")

    # warn user if needed
    if check_json_presence_and_warn_user("annotate", "annotating", "annotation"):
        return
    
    # prepare variables
    global cancel_var
    start_time = time.time()
    nloop = 1
    recognition_file = os.path.join(path_to_image_folder, "image_recognition_file.json")

    # make sure json has absolute paths
    json_paths_converted = False
    if check_json_paths(recognition_file) == "relative":
        make_json_absolute(recognition_file)
        json_paths_converted = True
    
    # add cancel button
    cancel_var = False
    btn_cancel = Button(progress_xml_frame, text="Cancel", command=cancel)
    btn_cancel.grid(row=9, column=0, columnspan=2)
    
    # fetch label map
    label_map = fetch_label_map_from_json(recognition_file)
    
    # open json file
    with open(recognition_file) as json_file:
        data = json.load(json_file)
    n_images = len(data['images'])
    
    # loop though json
    for image in data['images']:
        if cancel_var:
            break
        progress_xml_progbar['value'] += 100 / n_images
        file = str(image['file'])
        n_detections = len(image['detections'])
        annotation_list = []
        if not n_detections == 0:
            
            # loop though detections
            for detection in image['detections']:
                
                # open image
                im = Image.open(file)
                
                # get info
                annotations = 0
                width, height = im.size
                left = int(round(detection['bbox'][0] * width))
                top = int(round(detection['bbox'][1] * height))
                right = int(round(detection['bbox'][2] * width)) + left
                bottom = int(round(detection['bbox'][3] * height)) + top
                conf = detection['conf']
                category = detection['category']
                label = label_map[category]

                # create string with annotation info
                list_of_coords = [left, bottom, left, left, right, top, left, label]
                string = ','.join(map(str, list_of_coords))
                if conf > threshold:
                    annotation_list.append(string)
                    annotations += 1
            
            # create annotation file
            if annotations > 0:
                create_labimg_xml(file, annotation_list)
        
        # calculate stats
        elapsed_time_xml = str(datetime.timedelta(seconds=round(time.time() - start_time)))
        time_left_xml = str(datetime.timedelta(seconds=round(((time.time() - start_time) * n_images / nloop) - (time.time() - start_time))))
        progress_xml_stats['text'] = create_postprocess_lbl(elapsed_time_xml, time_left_xml, command="running")
        nloop += 1
        root.update()

    # remove cancel button
    btn_cancel.grid_remove()

    # change json paths back, if converted earlier
    if json_paths_converted:
        make_json_relative(recognition_file)
    
    # update completed status in json
    update_frame_completion_info(recognition_file, "xml_frame_completed", True)
    
    # let the user know it's done
    progress_xml_stats['text'] = create_postprocess_lbl(elapsed_time_xml, time_left_xml, command="done")
    root.update()

# start creating annotation files
def start_xml():
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")
    
    # set global variable
    global progress_xml_frame
    
    # open new window with progress bar and stats
    xml_progress_window = Toplevel(root)
    xml_progress_window.title("Annotation progress")
    xml_progress_window.geometry()
    
    # logo
    logo = tk.Label(xml_progress_window, image=grey_bg_logo)
    logo.grid(column=0, row=0, columnspan=2, sticky='ew', pady=(5, 0))
    
    # show cropping progress
    progress_xml_frame = LabelFrame(xml_progress_window, text=" Creating annotation files ", pady=2, padx=5, relief='solid', highlightthickness=5, font=100, fg='darkblue')
    progress_xml_frame.configure(font=(text_font, 15, "bold"))
    progress_xml_frame.grid(column=0, row=1, columnspan=2, sticky='ew')
    progress_xml_frame.columnconfigure(0, weight=3, minsize=115)
    progress_xml_frame.columnconfigure(1, weight=1, minsize=115)
    global progress_xml_progbar
    progress_xml_progbar = ttk.Progressbar(master=progress_xml_frame, orient='horizontal', mode='determinate', length=280)
    progress_xml_progbar.grid(column=0, row=0, columnspan=2, padx=5, pady=(3,0))
    global progress_xml_stats
    progress_xml_stats = ttk.Label(master=progress_xml_frame, text=create_postprocess_lbl())
    progress_xml_stats.grid(column=0, row=1, padx=5, pady=(0,3), columnspan=2)

    try:
        # start actual cropping process
        xml_process(var_choose_folder.get(), var_xml_thresh.get())
        
        # reset window
        update_frame_states()
        
        # close progress window
        xml_progress_window.destroy()

    except Exception as error:
        # log error
        print("ERROR:\n" + str(error) + "\n\nDETAILS:\n" + str(traceback.format_exc()) + "\n\n")
        
        # show error
        mb.showerror(title="Error",
                     message="An error has occurred (EcoAssist v" + version + "): '" + str(error) + "'.",
                     detail=traceback.format_exc())
        
        # reset window
        update_frame_states()
        
        # close window
        xml_progress_window.destroy()

############################################
############# HELPER FUNCTIONS #############
############################################

# switch beteen versions of yolov5 git to accommodate either old or new models
def switch_yolov5_git_to(model_type):
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")
    
    # checkout repo
    repo = git.Repo(os.path.join(EcoAssist_files, "yolov5"))
    if model_type == "old models":
        if platform.processor() == "arm" and os.name != "nt": # M1 and M2
            repo.git.checkout("4db6757ef9d43f49a780ff29deb06b28e96fbe84")
        else:
            repo.git.checkout("c23a441c9df7ca9b1f275e8c8719c949269160d1")
    elif model_type == "new models":
        repo.git.checkout("064365d8683fd002e9ad789c1e91fa3d021b44f0")

# extract label map from custom model
def extract_label_map_from_model(model_file):
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})")

    # import module from cameratraps dir
    from cameratraps.detection.pytorch_detector import PTDetector
            
    # load model
    detector = PTDetector(model_file)
    
    # log
    print(f"detector: {detector}")
    
    # fetch classes
    try:
        CUSTOM_DETECTOR_LABEL_MAP = {}
        for id in detector.model.names:
            CUSTOM_DETECTOR_LABEL_MAP[id+1] = detector.model.names[id]
    except Exception as error:
        # log error
        print("ERROR:\n" + str(error) + "\n\nDETAILS:\n" + str(traceback.format_exc()) + "\n\n")
        
        # show error
        mb.showerror(title="Error",
                     message="An error has occurred when trying to extract classes (EcoAssist v" + version + "): '" + str(error) + "'"
                             ".\n\nWill try to proceed and produce the output json file, but post-processing"
                             " features of EcoAssist will not work.",
                     detail=traceback.format_exc())
    
    # log
    print(f"Label map: {CUSTOM_DETECTOR_LABEL_MAP})\n")

    # return label map
    return CUSTOM_DETECTOR_LABEL_MAP

# fetch label map from json
def fetch_label_map_from_json(path_to_json):
    with open(path_to_json, "r") as json_file:
        data = json.load(json_file)
    custom_model = data['info']['ecoassist_metadata']['custom_model']
    if custom_model:
        label_map = data['info']['ecoassist_metadata']['custom_model_info']['label_map']
    else:
        label_map = data['detection_categories']
    return label_map

# check if json paths are relative or absolute
def check_json_paths(path_to_json):
    with open(path_to_json, "r") as json_file:
        data = json.load(json_file)
    path = data['images'][0]['file']
    if path.startswith(os.path.normpath(var_choose_folder.get())):
        return "absolute"
    else:
        return "relative"

# make json paths relative
def make_json_relative(path_to_json):
    if check_json_paths(path_to_json) == "absolute":
        with open(path_to_json, "r") as json_file:
            data = json.load(json_file)
        for image in data['images']:
            absolute_path = image['file']
            relative_path = absolute_path.replace(os.path.normpath(var_choose_folder.get()), "")[1:]
            image['file'] = relative_path
        with open(path_to_json, "w") as json_file:
            json.dump(data, json_file, indent=1)
            
# make json paths absolute
def make_json_absolute(path_to_json):
    if check_json_paths(path_to_json) == "relative":
        with open(path_to_json, "r") as json_file:
            data = json.load(json_file)
        for image in data['images']:
            relative_path = image['file']
            absolute_path = os.path.normpath(os.path.join(var_choose_folder.get(), relative_path))
            image['file'] = absolute_path
        with open(path_to_json, "w") as json_file:
            json.dump(data, json_file, indent=1)

# add information to json file
def append_to_json(path_to_json, object_to_be_appended):
    with open(path_to_json, "r") as json_file:
        data = json.load(json_file)
    data['info'].update(object_to_be_appended)
    with open(path_to_json, "w") as json_file:
        json.dump(data, json_file, indent=1)

# update information in json file
def update_frame_completion_info(path_to_json, parameter_to_be_updated, value):
    with open(path_to_json, "r") as json_file:
        data = json.load(json_file)
    data['info']['ecoassist_metadata']['frame_completion_info'][parameter_to_be_updated] = value
    with open(path_to_json, "w") as json_file:
        json.dump(data, json_file, indent=1)

# check json presence and show warnings
def check_json_presence_and_warn_user(infinitive, continuous, noun):
    img_json = False
    if os.path.isfile(os.path.join(var_choose_folder.get(), "image_recognition_file.json")):
        img_json = True
    vid_json = False
    if os.path.isfile(os.path.join(var_choose_folder.get(), "video_recognition_file.json")):
        vid_json = True
    if not img_json:
        if vid_json:
            mb.showerror("Error", f"{noun.capitalize()} is not supported for videos.")
            return True
        if not vid_json:
            mb.showerror("Error", f"No MegaDetector output file present. Make sure you run step "
                        f"2 before {continuous} the files. {noun.capitalize()} is only supported "
                        f"for images.")
            return True
    if img_json:
        if vid_json:
            mb.showinfo("Warning", f"{noun.capitalize()} is not supported for videos. Will "
                        f"continue to only {infinitive} the images...")

# dir names for when separating on confidence
conf_dirs = {0.0 : "conf_0.0",
             0.1 : "conf_0.0-0.1",
             0.2 : "conf_0.1-0.2",
             0.3 : "conf_0.2-0.3",
             0.4 : "conf_0.3-0.4",
             0.5 : "conf_0.4-0.5",
             0.6 : "conf_0.5-0.6",
             0.7 : "conf_0.6-0.7",
             0.8 : "conf_0.7-0.8",
             0.9 : "conf_0.8-0.9",
             1.0 : "conf_0.9-1.0"}

# create dirs and move image files into
def move_files(file, detection_type, var_file_placement, max_detection_conf, var_sep_conf):
    # prepare variables
    global conf_dirs
    file_no_ext, file_ext = os.path.splitext(os.path.basename(os.path.normpath(file)))
    src_dir = os.path.dirname(file)
    if var_sep_conf and detection_type != "empty":
        # squeeze in an extra dir
        ceiled_confidence = math.ceil(max_detection_conf * 10) / 10.0
        confidence_dir = conf_dirs[ceiled_confidence]
        dst_dir = os.path.join(src_dir, "separated_files", detection_type, confidence_dir)
    else:
        dst_dir = os.path.join(src_dir, "separated_files", detection_type)
    src = os.path.join(src_dir, file_no_ext + file_ext)
    dst = os.path.join(dst_dir, file_no_ext + file_ext)
    src_xml = os.path.join(src_dir, file_no_ext + ".xml")
    dst_xml = os.path.join(dst_dir, file_no_ext + ".xml")
    
    # create subfolder
    Path(dst_dir).mkdir(parents=True, exist_ok=True)
    
    # place image or video in subfolder
    if var_file_placement == 1: # move
        shutil.move(src, dst)
    elif var_file_placement == 2: # copy
        shutil.copy2(src, dst)
        
    # move xml file if present
    if os.path.isfile(src_xml):
        shutil.move(src_xml, dst_xml)
        
    # return destination path so the json data can be adjusted
    return(dst)

# indent xml files so it is human readable (thanks to ade from stack overflow)
def indent(elem, level=0):
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

# create xml label files in Pascal VOC format (thanks to uzzal podder from stack overflow)
def create_labimg_xml(image_path, annotation_list):
    image_path = Path(image_path)
    img = np.array(Image.open(image_path).convert('RGB'))
    annotation = ET.Element('annotation')
    ET.SubElement(annotation, 'folder').text = str(image_path.parent.name)
    ET.SubElement(annotation, 'filename').text = str(image_path.name)
    ET.SubElement(annotation, 'path').text = str(image_path)
    source = ET.SubElement(annotation, 'source')
    ET.SubElement(source, 'database').text = 'Unknown'
    size = ET.SubElement(annotation, 'size')
    ET.SubElement(size, 'width').text = str(img.shape[1])
    ET.SubElement(size, 'height').text = str(img.shape[0])
    ET.SubElement(size, 'depth').text = str(img.shape[2])
    ET.SubElement(annotation, 'segmented').text = '0'
    for annot in annotation_list:
        tmp_annot = annot.split(',')
        cords, label = tmp_annot[0:-2], tmp_annot[-1]
        xmin, ymin, xmax, ymax = cords[0], cords[1], cords[4], cords[5]
        object = ET.SubElement(annotation, 'object')
        ET.SubElement(object, 'name').text = label
        ET.SubElement(object, 'pose').text = 'Unspecified'
        ET.SubElement(object, 'truncated').text = '0'
        ET.SubElement(object, 'difficult').text = '0'
        bndbox = ET.SubElement(object, 'bndbox')
        ET.SubElement(bndbox, 'xmin').text = str(xmin)
        ET.SubElement(bndbox, 'ymin').text = str(ymin)
        ET.SubElement(bndbox, 'xmax').text = str(xmax)
        ET.SubElement(bndbox, 'ymax').text = str(ymax)
    indent(annotation)
    tree = ET.ElementTree(annotation)
    xml_file_name = image_path.parent / (image_path.name.split('.')[0] + '.xml')
    tree.write(xml_file_name)

# check if checkpoint file is present and assign global variable
def check_checkpnt():
    global loc_chkpnt_file
    for filename in os.listdir(var_choose_folder.get()):
            if re.search('^checkpoint_\d+\.json$', filename):
                loc_chkpnt_file = os.path.join(var_choose_folder.get(), filename)
                return True
    mb.showinfo("No checkpoint file found", "There is no checkpoint file found. Cannot continue "
                "from checkpoint file...")
    return False

# order statistics from megadetector output and return string
def create_md_progress_lbl(elapsed_time="",
                           time_left="",
                           current_im="",
                           total_im="",
                           processing_speed="",
                           percentage="",
                           GPU_param="",
                           data_type="",
                           command=""):
    # difference between processing images and videos
    if data_type == "img":
        unit = "image"
    else:
        unit = "frame"
    
    # properly translate processing speed 
    if "it/s" in processing_speed:
        speed_prefix = f"{unit.capitalize()} per sec:"
        speed_suffix = processing_speed.replace("it/s", "")
    elif "s/it" in processing_speed:
        speed_prefix = f"Sec per {unit}: "
        speed_suffix = processing_speed.replace("s/it", "")
    else:
        speed_prefix = ""
        speed_suffix = ""
        
    # return load text
    if command == "load":
        return f"Algorithm is starting up..."
    
    # return processing stats (OS dependant)
    if command == "running":
        if os.name == "nt":
            if data_type == "img":
                return f"Percentage done:\t\t{percentage}%\n" \
                    f"Processing {unit}:\t{current_im} of {total_im}\n" \
                    f"Elapsed time:\t\t{elapsed_time}\n" \
                    f"Remaining time:\t\t{time_left}\n" \
                    f"{speed_prefix}\t\t{speed_suffix}\n" \
                    f"Running on:\t\t{GPU_param}"
            else:
                return f"Percentage done:\t\t{percentage}%\n" \
                    f"Processing {unit}:\t\t{current_im} of {total_im}\n" \
                    f"Elapsed time:\t\t{elapsed_time}\n" \
                    f"Remaining time:\t\t{time_left}\n" \
                    f"{speed_prefix}\t\t{speed_suffix}\n" \
                    f"Running on:\t\t{GPU_param}"
        elif sys.platform == "linux" or sys.platform == "linux2":
            return f"Percentage done:\t{percentage}%\n" \
                f"Processing {unit}:\t{current_im} of {total_im}\n" \
                f"Elapsed time:\t\t{elapsed_time}\n" \
                f"Remaining time:\t\t{time_left}\n" \
                f"{speed_prefix}\t\t{speed_suffix}\n" \
                f"Running on:\t\t{GPU_param}"
        elif sys.platform == "darwin":
            return f"Percentage done:\t{percentage}%\n" \
                f"Processing {unit}:\t{current_im} of {total_im}\n" \
                f"Elapsed time:\t{elapsed_time}\n" \
                f"Remaining time:\t{time_left}\n" \
                f"{speed_prefix}\t{speed_suffix}\n" \
                f"Running on:\t{GPU_param}"
    
    # return stats when process is done
    if command == "done":
        return f"Elapsed time:\t{elapsed_time}\n" \
            f"{speed_prefix}\t{speed_suffix}"     

# get post-processing statistics and return string
def create_postprocess_lbl(elapsed_time="", time_left="", command=""):
    # waiting
    if command == "":
        return f"In queue"
    
    # running
    if command == "running":
        return f"Elapsed time:\t\t{elapsed_time}\n" \
               f"Remaining time:\t\t{time_left}"
               
    # done
    if command == "done":
        return f"Done!\n"

# browse directory
def browse_dir_button():
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")

    # choose directory
    chosen_dir = filedialog.askdirectory()
    var_choose_folder.set(chosen_dir)
    
    # display it and shorten if needed
    dsp_chosen_dir = chosen_dir
    cut_off_length = 100
    if len(dsp_chosen_dir) > cut_off_length:
        dsp_chosen_dir = "..." + dsp_chosen_dir[0 - cut_off_length + 3:]
    dsp_chosen_dir = "  " + dsp_chosen_dir
    var_choose_folder_short.set(dsp_chosen_dir)
    if var_choose_folder.get() != '':
        dsp_choose_folder.grid(column=1, row=0, sticky='w')
        
    # reset frame states
    reset_frame_states()

# load a custom yolov5 model and set global variable
def model_options(self):
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")
    
    global custom_model_choice
    if var_model.get() == "Custom":
        
        # choose file
        custom_model_choice = filedialog.askopenfilename(filetypes=[("Yolov5 model","*.pt")])
        
        # display it and shorten if needed
        dsp_filename = custom_model_choice
        cut_off_length = 30
        if len(dsp_filename) > cut_off_length:
            dsp_filename = "..." + dsp_filename[0 - cut_off_length + 3:]
        var_model_short.set(os.path.basename(dsp_filename))
        
        # set to default if faulty choice
        if custom_model_choice != '':
            dsp_model.grid(column=0, row=0, sticky='e')
        else:
            var_model.set("MDv5a")
    else:
        var_model_short.set("")
        
# open graphic annotation program labelImg 
def open_labelImg():
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")
    
    # prepare variables
    chosen_dir = var_choose_folder.get()
    path_to_labelImg = os.path.join(EcoAssist_files, "labelImg")
    path_to_classes_txt = os.path.join(path_to_labelImg, "data", "predefined_classes.txt")

    # check if the files are separated ...
    image_recognition_file = os.path.join(var_choose_folder.get(), "image_recognition_file.json")
    with open(image_recognition_file, "r") as json_file:
        data = json.load(json_file)
    sep_frame_completed = data['info']['ecoassist_metadata']['frame_completion_info']['sep_frame_completed']
    # ... and show warning
    if sep_frame_completed:
        mb.showinfo("Files are separated", "Because the images are separated, labelImg "
                "doesn't know which folder to open first.\n\nYou'll have to mannualy set"
                " the options 'Open Dir' and 'Change Save Dir' to the folder you want to"
                " inspect (top left of window), and then double-click an image in the file"
                " list (bottom right of window).")
        root.destroy()

    # log
    print(f"chosen_dir: {chosen_dir}")
    print(f"path_to_labelImg: {path_to_labelImg}")
    print(f"path_to_classes_txt: {path_to_classes_txt}")
    print(f"sys.executable: {sys.executable}")
    
    # run commands
    if os.name == "nt":
        # prepare command
        path_to_labelImg_command_Windows = os.path.join(EcoAssist_files, "EcoAssist", "Windows_open_LabelImg.bat")
        labelImg_command = [path_to_labelImg_command_Windows, chosen_dir, path_to_classes_txt]

        # log command
        print(f"command:\n\n{labelImg_command}\n\n")
        
        # run command
        with Popen(labelImg_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=1,
                shell=True,
                universal_newlines=True) as p:
            for line in p.stdout:
                
                # log stdout and stderr
                print(line, end='')
                
                # report traceback when error
                if line.startswith("Traceback "): 
                    mb.showerror("Error opening labelImg", message="An error occured while opening the "
                                 "annotation software labelImg. Please send an email to petervanlunteren@hotmail.com"
                                 " to resolve this bug.")

    else:
        # prepare command
        path_to_labelImg_command_MacOS_Linux = os.path.join(EcoAssist_files, "EcoAssist", "MacOS_Linux_open_LabelImg.command")
        labelImg_command = [f"bash '{path_to_labelImg_command_MacOS_Linux}' '{chosen_dir}' '{path_to_classes_txt}'"]
        
        # log command
        print(f"command:\n\n{labelImg_command}\n\n")
        
        # run command
        with Popen(labelImg_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=1,
                shell=True,
                universal_newlines=True) as p:
            for line in p.stdout:
                
                # log stdout and stderr
                print(line, end='')
                
                # report traceback when error
                if line.startswith("Traceback "): 
                    mb.showerror("Error opening labelImg", message="An error occured while opening the "
                                 "annotation software labelImg. Please send an email to petervanlunteren@hotmail.com"
                                 " to resolve this bug.")

# view results after processing
def view_results(frame):
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})")
    print(f"frame text: {frame.cget('text')}\n")
    
    # convert path separators
    chosen_folder = os.path.normpath(var_choose_folder.get())
    
    # set json paths
    image_recognition_file = os.path.join(chosen_folder, "image_recognition_file.json")
    video_recognition_file = os.path.join(chosen_folder, "video_recognition_file.json")

    # open json files at step 2
    if frame.cget('text').startswith(' Step 2'):
        if os.path.isfile(image_recognition_file):
            open_file_or_folder(image_recognition_file)
        if os.path.isfile(video_recognition_file):
            open_file_or_folder(video_recognition_file)
    
    # open separated_files folder at file separation
    if frame.cget('text').startswith(' Separate'):
        sep_folder = os.path.join(chosen_folder, 'separated_files')
        if os.path.isdir(sep_folder):
            open_file_or_folder(sep_folder)
        else:
            open_file_or_folder(chosen_folder)
    
    # at visualization open visualized_images if present in root, otherwise root
    if frame.cget('text').startswith(' Draw'):
        vis_folder = os.path.join(chosen_folder, 'visualized_images')
        if os.path.isdir(vis_folder):
            open_file_or_folder(vis_folder)
        else:
            open_file_or_folder(chosen_folder)
    
    # at cropping open cropped_images if present in root, otherwise root
    if frame.cget('text').startswith(' Crop'):
        crp_folder = os.path.join(chosen_folder, 'cropped_images')
        if os.path.isdir(crp_folder):
            open_file_or_folder(crp_folder)
        else:
            open_file_or_folder(chosen_folder)
    
    # open labelImg folder at xml_frame
    if frame.cget('text').startswith(' Create'):
        open_labelImg()

# open file or folder on windows, mac and linux
def open_file_or_folder(path):
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")
    
    # open file
    if platform.system() == 'Darwin':
        try:
            subprocess.call(('open', path))
        except:
            mb.showerror("Error opening results", f"Could not open '{path}'. "
                         "You'll have to find it yourself...")
    elif platform.system() == 'Windows':
        try:
            os.startfile(path)
        except:
            mb.showerror("Error opening results", f"Could not open '{path}'. "
                         "You'll have to find it yourself...")
    else:
        try:
            subprocess.call(('xdg-open', path))
        except:
            try:
                subprocess.call(('gnome-open', path))
            except:
                mb.showerror("Error opening results", f"Could not open '{path}'."
                             " Neither the 'xdg-open' nor 'gnome-open' command"
                             " worked. You'll have to find it yourself...")

##############################################
############# FRONTEND FUNCTIONS #############
##############################################

# set cancel variable to true
def cancel():
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")
    
    global cancel_var
    cancel_var = True

# set all children of frame to disabled state
def disable_widgets(frame):
    children = frame.winfo_children()
    for child in children:
        # labelframes have no state
        if child.winfo_class() != "Labelframe":
            child.config(state=DISABLED)

# set all children of frame to normal state
def enable_widgets(frame):
    children = frame.winfo_children()
    for child in children:
        # labelframes have no state
        if child.winfo_class() != "Labelframe":
            child.config(state=NORMAL)

# show warning and toggle megadetector threshold option
md_thresh_warning = True
def toggle_md_thresh():
    global md_thresh_warning
    if var_excl_detecs.get() and not md_thresh_warning:
        place_md_thresh()
    elif var_excl_detecs.get() and md_thresh_warning:
        md_thresh_warning = False
        if mb.askyesno("Warning", "It is strongly advised to not exclude detections from the MegaDetector output file. "
                       "Only set the confidence threshold to a very small value if you really know what you're doing. "
                       "The MegaDetector output should include just about everything that MegaDetector produces. If you,"
                       " because for some reason, want an extra-small output file, you would typically use a threshold of"
                       " 0.01 or 0.05.\n\nIf you want to use a threshold for post-processing features (visualization / "
                       "folder separation / cropping / annotation), please use the associated thresholds there.\n\nDo "
                       "you still want to exclude detections from the MegaDetector output file?"):
            place_md_thresh()
        else:
            var_excl_detecs.set(False)
            remove_md_thresh()
    else:
        remove_md_thresh()

# show warning for absolute paths option
shown_abs_paths_warning = True
def abs_paths_warning():
    global shown_abs_paths_warning
    if var_abs_paths.get() and shown_abs_paths_warning:
        mb.showinfo("Warning", "It is not recommended to use absolute paths in the output file. Third party software (such "
                    "as Timelapse, Agouti etc.) will not be able to read the json file if the paths are absolute. Only enable"
                    " this option if you know what you are doing.")
        shown_abs_paths_warning = False

# place megadetector threshold
def place_md_thresh():    
    lbl_md_thresh.grid(row=3, sticky='w', pady=round(5*pady_of_labels_and_widgets_factor))
    scl_md_thresh.grid(row=3, column=1, sticky='e', padx=5)
    dsp_md_thresh.grid(row=3, column=0, sticky='e', padx=5)

# remove megadetector threshold
def remove_md_thresh():
    lbl_md_thresh.grid_remove()
    scl_md_thresh.grid_remove()
    dsp_md_thresh.grid_remove()

# toggle image subframe
def toggle_img_frame():
    if var_process_img.get():
        enable_widgets(img_frame)
        toggle_checkpoint_freq()
        img_frame.configure(fg='black')
    else:
        disable_widgets(img_frame)
        img_frame.configure(fg='grey80')

# toggle video subframe
def toggle_vid_frame():
    if var_process_vid.get():
        enable_widgets(vid_frame)
        toggle_nth_frame()
        vid_frame.configure(fg='black')
    else:
        disable_widgets(vid_frame)
        vid_frame.configure(fg='grey80')

# convert frame to completed
def complete_frame(frame):
    global check_mark_one_row
    global check_mark_two_rows
    # adjust frames
    frame.configure(relief = 'groove')
    if frame.cget('text').startswith(' Step'):
        # all step frames
        frame.configure(fg='green3')
    if frame.cget('text').startswith(' Step 2'):
        # snd_step
        img_frame.configure(relief = 'groove')
        vid_frame.configure(relief = 'groove')
    if frame.cget('text').startswith(' Step 1'):
        # fst_step
        dsp_choose_folder.config(image=check_mark_one_row, compound='left')
        btn_choose_folder.config(text="Change folder?")
    else:
        # the rest
        if not frame.cget('text').startswith(' Step'):
            # sub frames of trd_step only
            frame.configure(fg='green3')
        # add check mark
        lbl_check_mark = Label(frame, image=check_mark_two_rows)
        lbl_check_mark.image = check_mark_two_rows
        lbl_check_mark.grid(row=0, column=0, rowspan=15, columnspan=2, sticky='nesw')
        # add buttons
        btn_view_results = Button(master=frame, text="View results", height=1, width=10, command=lambda: view_results(frame))
        btn_view_results.grid(row=0, column=1, sticky='e')
        btn_uncomplete = Button(master=frame, text="Again?", height=1, width=10, command=lambda: enable_frame(frame))
        btn_uncomplete.grid(row=1, column=1, sticky='e')

# enable a frame
def enable_frame(frame):
    uncomplete_frame(frame)
    enable_widgets(frame)
    # all frames
    frame.configure(relief = 'solid')
    if frame.cget('text').startswith(' Step'):
        # fst_step, snd_step and trd_step
        frame.configure(fg='darkblue')
    if frame.cget('text').startswith(' Step 2'):
        # snd_step only
        toggle_img_frame()
        img_frame.configure(relief = 'solid')
        toggle_vid_frame()
        vid_frame.configure(relief = 'solid')

# remove checkmarks and complete buttons
def uncomplete_frame(frame):
    if not frame.cget('text').startswith(' Step'):
        # subframes in trd_step only
        frame.configure(fg='black')
    if not frame.cget('text').startswith(' Step 1'):
        # all except step 1
        children = frame.winfo_children()
        for child in children:
            if child.winfo_class() == "Button" or child.winfo_class() == "Label":
                if child.cget('text') == "Again?" or child.cget('text') == "View results" or child.cget('image') != "":
                    child.grid_remove()

# disable a frame
def disable_frame(frame):
    uncomplete_frame(frame)
    disable_widgets(frame)
    # all frames
    frame.configure(fg='grey80')
    frame.configure(relief = 'flat')
    if frame.cget('text').startswith(' Step 2'):
        # snd_step only
        disable_widgets(img_frame)
        img_frame.configure(fg='grey80')
        img_frame.configure(relief = 'flat')
        disable_widgets(vid_frame)
        vid_frame.configure(fg='grey80')
        vid_frame.configure(relief = 'flat')

# check if checkpoint is present and set checkbox accordingly
def disable_chb_cont_checkpnt():
    if var_cont_checkpnt.get():
        var_cont_checkpnt.set(check_checkpnt())

# set minimum row size for all rows in a frame
def set_minsize_rows(frame):
    row_count = frame.grid_size()[1]
    for row in range(row_count):
        frame.grid_rowconfigure(row, minsize=minsize_all_rows)

# check if steps are completed already
def check_which_frames_are_completed():
    # start fresh
    fst_step_completed = False
    snd_step_completed = False
    sep_frame_completed = False
    vis_frame_completed = False
    crp_frame_completed = False
    xml_frame_completed = False
    
    # set json paths
    image_recognition_file = os.path.join(var_choose_folder.get(), "image_recognition_file.json")
    video_recognition_file = os.path.join(var_choose_folder.get(), "video_recognition_file.json")
    
    # is folder specified?
    if os.path.isdir(var_choose_folder.get()):
        fst_step_completed = True
    
    # is a json file present?
    if fst_step_completed:
        if os.path.isfile(image_recognition_file) or os.path.isfile(video_recognition_file):
            snd_step_completed = True
    
    # check other vars in image json file since they depend on json file
    if fst_step_completed:
        if os.path.isfile(image_recognition_file):
            # get them from image json if present
            with open(image_recognition_file, "r") as json_file:
                data = json.load(json_file)
            sep_frame_completed = data['info']['ecoassist_metadata']['frame_completion_info']['sep_frame_completed']
            vis_frame_completed = data['info']['ecoassist_metadata']['frame_completion_info']['vis_frame_completed']
            crp_frame_completed = data['info']['ecoassist_metadata']['frame_completion_info']['crp_frame_completed']
            xml_frame_completed = data['info']['ecoassist_metadata']['frame_completion_info']['xml_frame_completed']
        elif os.path.isfile(video_recognition_file):
            # otherwise from video json
            with open(video_recognition_file, "r") as json_file:
                data = json.load(json_file)
            sep_frame_completed = data['info']['ecoassist_metadata']['frame_completion_info']['sep_frame_completed']
    
    # return results
    return [fst_step_completed,
            snd_step_completed,
            sep_frame_completed,
            vis_frame_completed,
            crp_frame_completed,
            xml_frame_completed]

# start with a fresh screen and update all frames from there (the long way)
def reset_frame_states():
    # fetch bools
    fst_step_completed, \
        snd_step_completed, \
            sep_frame_completed, \
                vis_frame_completed, \
                    crp_frame_completed, \
                        xml_frame_completed \
                            = check_which_frames_are_completed()
    
    # always start with this ...
    enable_frame(fst_step)
    disable_frame(snd_step)
    disable_frame(trd_step)
    disable_frame(sep_frame)
    disable_frame(vis_frame)
    disable_frame(crp_frame)
    disable_frame(xml_frame)
       
    # ... and adjust frame states accordingly
    if fst_step_completed:
        complete_frame(fst_step)
        enable_frame(snd_step)
    if snd_step_completed:
        complete_frame(snd_step)
        enable_frame(trd_step)
        enable_frame(sep_frame)
        enable_frame(vis_frame)
        enable_frame(crp_frame)
        enable_frame(xml_frame)
    if sep_frame_completed:
        complete_frame(sep_frame)
    if vis_frame_completed:
        complete_frame(vis_frame)
    if crp_frame_completed:
        complete_frame(crp_frame)
    if xml_frame_completed:
        complete_frame(xml_frame)
    if all([sep_frame_completed,
            vis_frame_completed,
            crp_frame_completed,
            xml_frame_completed]):
        trd_step.configure(fg='green3')
        trd_step.configure(relief = 'groove')

# update only the next step or frame (the short way)
def update_frame_states():
    # fetch bools
    fst_step_completed, \
        snd_step_completed, \
            sep_frame_completed, \
                vis_frame_completed, \
                    crp_frame_completed, \
                        xml_frame_completed \
                            = check_which_frames_are_completed()
    
    # update screen based on these bools
    if fst_step_completed and not any([snd_step_completed,
                                       sep_frame_completed,
                                       vis_frame_completed,
                                       crp_frame_completed,
                                       xml_frame_completed]):
        # only step 1 completed ...
        complete_frame(fst_step)
        enable_frame(snd_step)
    elif fst_step_completed and snd_step_completed and not any([sep_frame_completed,
                                                                vis_frame_completed,
                                                                crp_frame_completed,
                                                                xml_frame_completed]):
        # ... now also step 2 completed ...
        complete_frame(snd_step)
        enable_frame(trd_step)
        enable_frame(sep_frame)
        enable_frame(vis_frame)
        enable_frame(crp_frame)
        enable_frame(xml_frame)
    else:
        # ... now we are at the post-processing features
        if xml_frame_completed:
            complete_frame(xml_frame)
        if crp_frame_completed:
            complete_frame(crp_frame)
        if vis_frame_completed:
            complete_frame(vis_frame)
        if sep_frame_completed:
            complete_frame(sep_frame)
        if all([sep_frame_completed,
                vis_frame_completed,
                crp_frame_completed,
                xml_frame_completed]):
                trd_step.configure(fg='green3')
                trd_step.configure(relief = 'groove')

# toggle state of checkpoint frequency
def toggle_checkpoint_freq():
    if var_use_checkpnts.get():
        lbl_checkpoint_freq.config(state=NORMAL)
        ent_checkpoint_freq.config(state=NORMAL)
    else:
        lbl_checkpoint_freq.config(state=DISABLED)
        ent_checkpoint_freq.config(state=DISABLED)

# toggle state of nth frame
def toggle_nth_frame():
    if var_not_all_frames.get():
        lbl_nth_frame.config(state=NORMAL)
        ent_nth_frame.config(state=NORMAL)
    else:
        lbl_nth_frame.config(state=DISABLED)
        ent_nth_frame.config(state=DISABLED)

# entry boxes event focus in
def checkpoint_freq_focus_in(_):
    ent_checkpoint_freq.delete(0, tk.END)
    ent_checkpoint_freq.config(fg='black')
def nth_frame_focus_in(_):
    ent_nth_frame.delete(0, tk.END)
    ent_nth_frame.config(fg='black')

# entry boxes event focus out
def checkpoint_freq_focus_out(_):
    root.focus()
def nth_frame_focus_out(_):
    root.focus()

# entry boxes event press enter
def checkpoint_freq_enter(txt):
    root.focus()
def nth_frame_enter(txt):
    root.focus()
    
##########################################
############# TKINTER WINDOW #############
##########################################

# make it look similar on different systems
if os.name == "nt": # windows
    text_font = "TkDefaultFont"
    resize_img_factor = 0.95
    textbox_height_adjustment_factor = 0.65
    textbox_width_adjustment_factor = 1
    text_size_adjustment_factor = 0.83
    pady_of_labels_and_widgets_factor = 0.5
    slider_width_pixels = 10
    first_level_frame_font_size = 15
    second_level_frame_font_size = 13
    first_level_frame_column_0_min_size = 350
    first_level_frame_column_1_min_size = 0
    second_level_frame_column_0_min_size = 350
    second_level_frame_column_1_min_size = 0
    minsize_all_rows = 28
elif sys.platform == "linux" or sys.platform == "linux2": # linux
    text_font = "Times"
    resize_img_factor = 1
    textbox_height_adjustment_factor = 0.85
    textbox_width_adjustment_factor = 1
    text_size_adjustment_factor = 0.7
    pady_of_labels_and_widgets_factor = 0.5
    slider_width_pixels = 10
    first_level_frame_font_size = 15
    second_level_frame_font_size = 13
    first_level_frame_column_0_min_size = 350
    first_level_frame_column_1_min_size = 0
    second_level_frame_column_0_min_size = 350
    second_level_frame_column_1_min_size = 0
    minsize_all_rows = 28
else: # macOS
    text_font = "TkDefaultFont"
    resize_img_factor = 1
    textbox_height_adjustment_factor = 0.8
    textbox_width_adjustment_factor = 1
    text_size_adjustment_factor = 1
    pady_of_labels_and_widgets_factor = 0.5
    slider_width_pixels = 10
    first_level_frame_font_size = 15
    second_level_frame_font_size = 13
    first_level_frame_column_0_min_size = 350
    first_level_frame_column_1_min_size = 120
    second_level_frame_column_0_min_size = 350
    second_level_frame_column_1_min_size = 120
    minsize_all_rows = 28

# tkinter main window
root = Tk()
root.title(f"EcoAssist v{version}")
root.geometry()
root.configure(background="white")
tabControl = ttk.Notebook(root)

# prepare logo
logo_path = os.path.join(EcoAssist_files,'EcoAssist', 'imgs', 'logo.png')
logo = Image.open(logo_path)
logo = logo.resize((int(logo.size[0] / 3), int(logo.size[1] / 3)), Image.Resampling.LANCZOS)
white_bg_logo = Image.new("RGBA", logo.size, "WHITE")
white_bg_logo.paste(logo, (0, 0), logo)
white_bg_logo.convert('RGB')
white_bg_logo = ImageTk.PhotoImage(white_bg_logo)
grey_bg_logo = ImageTk.PhotoImage(logo)

# prepare fox image
fox = Image.open(os.path.join(EcoAssist_files, 'EcoAssist', 'imgs', 'fox.jpg'))
full_width, full_height = fox.size
chosen_width = full_width
chosen_height = full_width * 0.2
top = 700
bottom = top + chosen_height
left = 0
right = chosen_width
fox = fox.crop((left, top, right, bottom))
fox = fox.resize((int(resize_img_factor * 422), 84), Image.Resampling.LANCZOS)
rad = 10
back = Image.new('RGB', (fox.size[0] + rad, fox.size[1]), (255, 255, 255))
back.paste(fox, (0, 0))
mask = Image.new('L', (fox.size[0] + rad, fox.size[1]), 255)
blck = Image.new('L', (fox.size[0] - rad, fox.size[1]), 0)
mask.paste(blck, (0, 0))
blur = back.filter(ImageFilter.GaussianBlur(rad / 2))
back.paste(blur, mask=mask)
fox = ImageTk.PhotoImage(back)

# prepare ocelot image
ocelot = Image.open(os.path.join(EcoAssist_files, 'EcoAssist', 'imgs', 'ocelot.jpg'))
full_width, full_height = ocelot.size
chosen_width = full_width
chosen_height = full_width * 0.2
top = 310
bottom = top + chosen_height
left = 0
right = chosen_width
ocelot = ocelot.crop((left, top, right, bottom))
ocelot = ocelot.resize((int(resize_img_factor * 422), 84), Image.Resampling.LANCZOS) 
back = Image.new('RGB', (ocelot.size[0], ocelot.size[1]), (255, 255, 255))
back.paste(ocelot, (rad, 0))
mask = Image.new('L', (ocelot.size[0], ocelot.size[1]), 255)
blck = Image.new('L', (ocelot.size[0], ocelot.size[1]), 0)
mask.paste(blck, (2 * rad, 0))
blur = back.filter(ImageFilter.GaussianBlur(rad / 2))
back.paste(blur, mask=mask)
ocelot = ImageTk.PhotoImage(back)

# print the images on the tkinter window
logo_widget = tk.Label(root, image=white_bg_logo, bg="white", highlightthickness=0, highlightbackground="white")
fox_widget = tk.Label(root, image=fox, bg="white", highlightthickness=0, highlightbackground="white")
ocelot_widget = tk.Label(root, image=ocelot, bg="white", highlightthickness=0, highlightbackground="white")
logo_widget.grid(column=0, row=0, sticky='ns', pady=(3, 3), padx=(0, 0))
fox_widget.grid(column=0, row=0, sticky='wns', pady=(3, 3), padx=(3, 0))
ocelot_widget.grid(column=0, row=0, sticky='ens', pady=(3, 3), padx=(0, 3))

# prepare check mark for later use
check_mark = Image.open(os.path.join(EcoAssist_files, 'EcoAssist', 'imgs', 'check_mark.png'))
check_mark_one_row = check_mark.resize((22, 22), Image.Resampling.LANCZOS)
check_mark_one_row = ImageTk.PhotoImage(check_mark_one_row)
check_mark_two_rows = check_mark.resize((45, 45), Image.Resampling.LANCZOS)
check_mark_two_rows = ImageTk.PhotoImage(check_mark_two_rows)

# tabs
param_tab = ttk.Frame(tabControl)
param_tab.columnconfigure(0, weight=1, minsize=500)
param_tab.columnconfigure(1, weight=1, minsize=500)
help_tab = ttk.Frame(tabControl)
about_tab = ttk.Frame(tabControl)
tabControl.add(param_tab, text='Parameters')
tabControl.add(help_tab, text='Help')
tabControl.add(about_tab, text='About')
tabControl.grid()

#### parameter tab
### first step
fst_step_txt = "Step 1: Choose folder to analyse"
fst_step = LabelFrame(param_tab, text=" " + fst_step_txt + " ", pady=2, padx=5, relief='solid', highlightthickness=5, font=100, fg='darkblue', borderwidth=2)
fst_step.configure(font=(text_font, first_level_frame_font_size, "bold"))
fst_step.grid(column=0, row=1, columnspan=2, sticky='ew')

# choose folder
var_choose_folder = StringVar()
var_choose_folder_short = StringVar()
dsp_choose_folder = Label(master=fst_step, textvariable=var_choose_folder_short)
btn_choose_folder = Button(master=fst_step, text="Browse", command=browse_dir_button)
btn_choose_folder.grid(row=0, column=0, sticky='w', padx=5)

### second step
snd_step_txt = "Step 2: Run MegaDetector"
snd_step = LabelFrame(param_tab, text=" " + snd_step_txt + " ", pady=2, padx=5, relief='solid', highlightthickness=5, font=100, fg='darkblue', borderwidth=2)
snd_step.configure(font=(text_font, first_level_frame_font_size, "bold"))
snd_step.grid(column=0, row=2, sticky='nesw')
snd_step.columnconfigure(0, weight=1, minsize=first_level_frame_column_0_min_size)
snd_step.columnconfigure(1, weight=1, minsize=first_level_frame_column_1_min_size)

# choose model
lbl_model_txt = "Model"
lbl_model = Label(master=snd_step, text=lbl_model_txt)
lbl_model.grid(row=0, sticky='w', pady=round(5*pady_of_labels_and_widgets_factor))
dpd_options_model = ["MDv5a", "MDv5b", "Custom"]
var_model = StringVar(snd_step)
var_model.set(dpd_options_model[0])
var_model_short = StringVar()
dpd_model = OptionMenu(snd_step, var_model, *dpd_options_model, command=model_options)
dpd_model.config(width=5)
dpd_model.grid(row=0, column=1, sticky='e', padx=5)
dsp_model = Label(master=snd_step, textvariable=var_model_short, fg='darkred')

# include subdirectories
lbl_exclude_subs_txt = "Don't process subdirectories"
lbl_exclude_subs = Label(snd_step, text=lbl_exclude_subs_txt)
lbl_exclude_subs.grid(row=1, sticky='w', pady=round(5*pady_of_labels_and_widgets_factor))
var_exclude_subs = BooleanVar()
var_exclude_subs.set(False)
chb_exclude_subs = Checkbutton(snd_step, variable=var_exclude_subs)
chb_exclude_subs.grid(row=1, column=1, sticky='e', padx=5)

# limit detections
lbl_excl_detecs_txt = "Exclude detections from output file"
lbl_excl_detecs = Label(snd_step, text=lbl_excl_detecs_txt)
lbl_excl_detecs.grid(row=2, sticky='w', pady=round(5*pady_of_labels_and_widgets_factor))
var_excl_detecs = BooleanVar()
var_excl_detecs.set(False)
chb_excl_detecs = Checkbutton(snd_step, variable=var_excl_detecs, command=toggle_md_thresh)
chb_excl_detecs.grid(row=2, column=1, sticky='e', padx=5)

# threshold for megadetector (not grid by deafult)
lbl_md_thresh_txt = "Confidence threshold"
lbl_md_thresh = Label(snd_step, text=" ↳ " + lbl_md_thresh_txt)
var_md_thresh = DoubleVar()
var_md_thresh.set(0.01)
scl_md_thresh = Scale(snd_step, from_=0.005, to=1, resolution=0.005, orient=HORIZONTAL, length=120, variable=var_md_thresh, showvalue=0, width=slider_width_pixels)
dsp_md_thresh = Label(snd_step, textvariable=var_md_thresh)
dsp_md_thresh.config(fg="darkred")

# use absolute paths
lbl_abs_paths_txt = "Use absolute paths in output file"
lbl_abs_paths = Label(snd_step, text=lbl_abs_paths_txt)
lbl_abs_paths.grid(row=4, sticky='w', pady=round(5*pady_of_labels_and_widgets_factor))
var_abs_paths = BooleanVar()
var_abs_paths.set(False)
chb_abs_paths = Checkbutton(snd_step, variable=var_abs_paths, command=abs_paths_warning)
chb_abs_paths.grid(row=4, column=1, sticky='e', padx=5)

# process images
lbl_process_img_txt = "Process all images in the folder specified"
lbl_process_img = Label(snd_step, text=lbl_process_img_txt)
lbl_process_img.grid(row=5, sticky='w', pady=round(5*pady_of_labels_and_widgets_factor))
var_process_img = BooleanVar()
var_process_img.set(False)
chb_process_img = Checkbutton(snd_step, variable=var_process_img, command=toggle_img_frame, anchor="e")
chb_process_img.grid(row=5, column=1, sticky='e', padx=5)

## image option frame (dsiabled by default)
img_frame_txt = "Image options"
img_frame = LabelFrame(snd_step, text=" ↳ " + img_frame_txt + " ", pady=2, padx=5, relief='solid', highlightthickness=5, font=100, borderwidth=1, fg="grey80")
img_frame.configure(font=(text_font, second_level_frame_font_size, "bold"))
img_frame.grid(row=6, column=0, columnspan=2, sticky = 'ew')
img_frame.columnconfigure(0, weight=1, minsize=second_level_frame_column_0_min_size)
img_frame.columnconfigure(1, weight=1, minsize=second_level_frame_column_1_min_size)

# use checkpoints
lbl_use_checkpnts_txt = "Use checkpoints while running"
lbl_use_checkpnts = Label(img_frame, text="    " + lbl_use_checkpnts_txt, pady=round(5*pady_of_labels_and_widgets_factor), state=DISABLED)
lbl_use_checkpnts.grid(row=0, sticky='w')
var_use_checkpnts = BooleanVar()
var_use_checkpnts.set(False)
chb_use_checkpnts = Checkbutton(img_frame, variable=var_use_checkpnts, command=toggle_checkpoint_freq, state=DISABLED)
chb_use_checkpnts.grid(row=0, column=1, sticky='e', padx=5)

# checkpoint frequency
lbl_checkpoint_freq_txt = "Checkpoint frequency"
lbl_checkpoint_freq = tk.Label(img_frame, text="       ↳ " + lbl_checkpoint_freq_txt, pady=round(5*pady_of_labels_and_widgets_factor), state=DISABLED)
lbl_checkpoint_freq.grid(row=1, sticky='w')
var_checkpoint_freq = StringVar()
ent_checkpoint_freq = tk.Entry(img_frame, width=9, textvariable=var_checkpoint_freq, fg='grey', state=NORMAL)
ent_checkpoint_freq.grid(row=1, column=1, sticky='e', padx=5)
ent_checkpoint_freq.insert(0, "E.g.: 100")
ent_checkpoint_freq.bind("<FocusIn>", checkpoint_freq_focus_in)
ent_checkpoint_freq.bind("<FocusOut>", checkpoint_freq_focus_out)
ent_checkpoint_freq.bind("<Return>", checkpoint_freq_enter)
ent_checkpoint_freq.config(state=DISABLED)

# continue from checkpoint file
lbl_cont_checkpnt_txt = "Continue from last checkpoint file onwards"
lbl_cont_checkpnt = Label(img_frame, text="    " + lbl_cont_checkpnt_txt, pady=round(5*pady_of_labels_and_widgets_factor), state=DISABLED)
lbl_cont_checkpnt.grid(row=2, sticky='w')
var_cont_checkpnt = BooleanVar()
var_cont_checkpnt.set(False)
chb_cont_checkpnt = Checkbutton(img_frame, variable=var_cont_checkpnt, state=DISABLED, command=disable_chb_cont_checkpnt)
chb_cont_checkpnt.grid(row=2, column=1, sticky='e', padx=5)

# process videos
lbl_process_vid_txt = "Process all videos in the folder specified"
lbl_process_vid = Label(snd_step, text=lbl_process_vid_txt)
lbl_process_vid.grid(row=7, sticky='w', pady=round(5*pady_of_labels_and_widgets_factor))
var_process_vid = BooleanVar()
var_process_vid.set(False)
chb_process_vid = Checkbutton(snd_step, variable=var_process_vid, command=toggle_vid_frame)
chb_process_vid.grid(row=7, column=1, sticky='e', padx=5)

## video option frame (disabled by default)
vid_frame_txt = "Video options"
vid_frame = LabelFrame(snd_step, text=" ↳ " + vid_frame_txt + " ", pady=2, padx=5, relief='solid', highlightthickness=5, font=100, borderwidth=1, fg="grey80")
vid_frame.configure(font=(text_font, second_level_frame_font_size, "bold"))
vid_frame.grid(row=8, column=0, columnspan=2, sticky='ew')
vid_frame.columnconfigure(0, weight=1, minsize=second_level_frame_column_0_min_size)
vid_frame.columnconfigure(1, weight=1, minsize=second_level_frame_column_1_min_size)

# dont process all frames
lbl_not_all_frames_txt = "Don't process every frame"
lbl_not_all_frames = Label(vid_frame, text="    " + lbl_not_all_frames_txt, pady=round(5*pady_of_labels_and_widgets_factor), state=DISABLED)
lbl_not_all_frames.grid(row=0, sticky='w')
var_not_all_frames = BooleanVar()
var_not_all_frames.set(False)
chb_not_all_frames = Checkbutton(vid_frame, variable=var_not_all_frames, command=toggle_nth_frame, state=DISABLED)
chb_not_all_frames.grid(row=0, column=1, sticky='e', padx=5)

# process every nth frame
lbl_nth_frame_txt = "Analyse every Nth frame"
lbl_nth_frame = tk.Label(vid_frame, text="       ↳ " + lbl_nth_frame_txt, pady=round(5*pady_of_labels_and_widgets_factor), state=DISABLED)
lbl_nth_frame.grid(row=1, sticky='w')
var_nth_frame = StringVar()
ent_nth_frame = tk.Entry(vid_frame, width=9, textvariable=var_nth_frame, fg='grey', state=NORMAL)
ent_nth_frame.grid(row=1, column=1, sticky='e', padx=5)
ent_nth_frame.insert(0, "E.g.: 10")
ent_nth_frame.bind("<FocusIn>", nth_frame_focus_in)
ent_nth_frame.bind("<FocusOut>", nth_frame_focus_out)
ent_nth_frame.bind("<Return>", nth_frame_enter)
ent_nth_frame.config(state=DISABLED)

# button start MegaDetector
btn_start_md = Button(snd_step, text="Process files", command=start_md)
btn_start_md.grid(row=9, column=0, columnspan=2, sticky='ew')

### third step
trd_step_txt = "Step 3: Post-processing (optional)"
trd_step = LabelFrame(param_tab, text=" " + trd_step_txt + " ", pady=2, padx=5, relief='solid', highlightthickness=5, font=100, fg='darkblue', borderwidth=2)
trd_step.configure(font=(text_font, first_level_frame_font_size, "bold"))
trd_step.grid(column=1, row=2, sticky='nesw')
trd_step.columnconfigure(0, weight=1, minsize=first_level_frame_column_0_min_size)
trd_step.columnconfigure(1, weight=1, minsize=first_level_frame_column_1_min_size)

## separation frame
sep_frame_txt = "Separate files into subdirectories based on detections"
sep_frame = LabelFrame(trd_step, text=" " + sep_frame_txt + " ", pady=2, padx=5, relief='solid', highlightthickness=5, font=100, borderwidth=1)
sep_frame.configure(font=(text_font, second_level_frame_font_size, "bold"))
sep_frame.grid(column=0, row=0, columnspan=2, sticky='ew')
sep_frame.columnconfigure(0, weight=1, minsize=second_level_frame_column_0_min_size)
sep_frame.columnconfigure(1, weight=1, minsize=second_level_frame_column_1_min_size)

# method of file placement
lbl_file_placement_txt = "Method of file placement"
lbl_file_placement = Label(sep_frame, text=lbl_file_placement_txt, pady=round(5*pady_of_labels_and_widgets_factor))
lbl_file_placement.grid(row=0, sticky='w')
var_file_placement = IntVar()
var_file_placement.set(2)
rad_file_placement_move = Radiobutton(sep_frame, text="Copy", variable=var_file_placement, value=2)
rad_file_placement_move.grid(row=0, column=1, sticky='w', padx=5)
rad_file_placement_copy = Radiobutton(sep_frame, text="Move", variable=var_file_placement, value=1)
rad_file_placement_copy.grid(row=0, column=1, sticky='e', padx=5)

# separate per confidence
lbl_sep_conf_txt = "Sort results based on confidence"
lbl_sep_conf = Label(sep_frame, text=lbl_sep_conf_txt)
lbl_sep_conf.grid(row=1, sticky='w', pady=round(5*pady_of_labels_and_widgets_factor))
var_sep_conf = BooleanVar()
var_sep_conf.set(True)
chb_sep_conf = Checkbutton(sep_frame, variable=var_sep_conf, anchor="e")
chb_sep_conf.grid(row=1, column=1, sticky='e', padx=5)

# threshold for separation
lbl_sep_thresh_txt = "Confidence threshold"
lbl_sep_thresh = Label(sep_frame, text=lbl_sep_thresh_txt)
lbl_sep_thresh.grid(row=2, sticky='w', pady=round(5*pady_of_labels_and_widgets_factor))
var_sep_thresh = DoubleVar()
var_sep_thresh.set(0.2)
scl_sep_thresh = Scale(sep_frame, from_=0.005, to=1, resolution=0.005, orient=HORIZONTAL, length=120, variable=var_sep_thresh, showvalue=0, width=slider_width_pixels)
scl_sep_thresh.grid(row=2, column=1, sticky='e', padx=5)
dsp_sep_thresh = Label(sep_frame, textvariable=var_sep_thresh)
dsp_sep_thresh.config(fg="darkred")
dsp_sep_thresh.grid(row=2, column=0, sticky='e', padx=5)

# button start separation
btn_start_sep = Button(sep_frame, text="Separate files", command=start_sep)
btn_start_sep.grid(row=3, column=0, columnspan=2, sticky='ew')

## visualization frame
vis_frame_txt = "Draw boxes around the detections and show confidences"
vis_frame = LabelFrame(trd_step, text=" " + vis_frame_txt + " ", pady=2, padx=5, relief='solid', highlightthickness=5, font=100, borderwidth=1)
vis_frame.configure(font=(text_font, second_level_frame_font_size, "bold"))
vis_frame.grid(column=0, row=1, columnspan=2, sticky='ew')
vis_frame.columnconfigure(0, weight=1, minsize=second_level_frame_column_0_min_size)
vis_frame.columnconfigure(1, weight=1, minsize=second_level_frame_column_1_min_size)

# threshold for visualization
lbl_vis_thresh_txt = "Confidence threshold"
lbl_vis_thresh = Label(vis_frame, text=lbl_vis_thresh_txt)
lbl_vis_thresh.grid(row=0, sticky='w', pady=round(5*pady_of_labels_and_widgets_factor))
var_vis_thresh = DoubleVar()
var_vis_thresh.set(0.2)
scl_vis_thresh = Scale(vis_frame, from_=0.005, to=1, resolution=0.005, orient=HORIZONTAL, length=120, variable=var_vis_thresh, showvalue=0, width=slider_width_pixels)
scl_vis_thresh.grid(row=0, column=1, sticky='e', padx=5)
dsp_vis_thresh = Label(vis_frame, textvariable=var_vis_thresh)
dsp_vis_thresh.config(fg="darkred")
dsp_vis_thresh.grid(row=0, column=0, sticky='e', padx=5)

# button start visaration
btn_start_vis = Button(vis_frame, text="Visualize files", command=start_vis)
btn_start_vis.grid(row=1, column=0, columnspan=2, sticky='ew')

## crop frame
crp_frame_txt = "Crop detections"
crp_frame = LabelFrame(trd_step, text=" " + crp_frame_txt + " ", pady=2, padx=5, relief='solid', highlightthickness=5, font=100, borderwidth=1)
crp_frame.configure(font=(text_font, second_level_frame_font_size, "bold"))
crp_frame.grid(column=0, row=2, columnspan=2, sticky='ew')
crp_frame.columnconfigure(0, weight=1, minsize=second_level_frame_column_0_min_size)
crp_frame.columnconfigure(1, weight=1, minsize=second_level_frame_column_1_min_size)

# threshold for cropping
lbl_crp_thresh_txt = "Confidence threshold"
lbl_crp_thresh = Label(crp_frame, text=lbl_crp_thresh_txt)
lbl_crp_thresh.grid(row=0, sticky='w', pady=round(5*pady_of_labels_and_widgets_factor))
var_crp_thresh = DoubleVar()
var_crp_thresh.set(0.2)
scl_crp_thresh = Scale(crp_frame, from_=0.005, to=1, resolution=0.005, orient=HORIZONTAL, length=120, variable=var_crp_thresh, showvalue=0, width=slider_width_pixels)
scl_crp_thresh.grid(row=0, column=1, sticky='e', padx=5)
dsp_crp_thresh = Label(crp_frame, textvariable=var_crp_thresh)
dsp_crp_thresh.config(fg="darkred")
dsp_crp_thresh.grid(row=0, column=0, sticky='e', padx=5)

# button start cropping
btn_start_crp = Button(crp_frame, text="Crop files", command=start_crp)
btn_start_crp.grid(row=1, column=0, columnspan=2, sticky='ew')

## xml frame
xml_frame_txt = "Create annotations in Pascal VOC format (.xml files)"
xml_frame = LabelFrame(trd_step, text=" " + xml_frame_txt + " ", pady=2, padx=5, relief='solid', highlightthickness=5, font=100, borderwidth=1)
xml_frame.configure(font=(text_font, second_level_frame_font_size, "bold"))
xml_frame.grid(column=0, row=3, columnspan=2, sticky='ew')
xml_frame.columnconfigure(0, weight=1, minsize=second_level_frame_column_0_min_size)
xml_frame.columnconfigure(1, weight=1, minsize=second_level_frame_column_1_min_size)

# threshold for xml annotation
lbl_xml_thresh_txt = "Confidence threshold"
lbl_xml_thresh = Label(xml_frame, text=lbl_xml_thresh_txt)
lbl_xml_thresh.grid(row=0, sticky='w', pady=round(5*pady_of_labels_and_widgets_factor))
var_xml_thresh = DoubleVar()
var_xml_thresh.set(0.2)
scl_xml_thresh = Scale(xml_frame, from_=0.005, to=1, resolution=0.005, orient=HORIZONTAL, length=120, variable=var_xml_thresh, showvalue=0, width=slider_width_pixels)
scl_xml_thresh.grid(row=0, column=1, sticky='e', padx=5)
dsp_xml_thresh = Label(xml_frame, textvariable=var_xml_thresh)
dsp_xml_thresh.config(fg="darkred")
dsp_xml_thresh.grid(row=0, column=0, sticky='e', padx=5)

# button create xml files
btn_start_xml = Button(xml_frame, text="Create annotation files", command=start_xml)
btn_start_xml.grid(row=1, column=0, columnspan=2, sticky='ew')

# set minsize for all rows inside labelframes
set_minsize_rows(fst_step)
set_minsize_rows(snd_step)
snd_step.grid_rowconfigure(3, minsize=0) # hidden md tresh
set_minsize_rows(img_frame)
set_minsize_rows(vid_frame)
set_minsize_rows(trd_step)
set_minsize_rows(sep_frame)
set_minsize_rows(vis_frame)
set_minsize_rows(crp_frame)
set_minsize_rows(xml_frame)

# help tab
scroll = Scrollbar(help_tab)
help_text = Text(help_tab, width=int(130 * textbox_width_adjustment_factor), height=int(36 * textbox_height_adjustment_factor), wrap=WORD, yscrollcommand=scroll.set) 
help_text.config(spacing1=2, spacing2=3, spacing3=2)
help_text.tag_config('frame', font=f'{text_font} {int(15 * text_size_adjustment_factor)} bold', foreground='darkblue', lmargin1=10, lmargin2=10) 
help_text.tag_config('feature', font=f'{text_font} {int(14 * text_size_adjustment_factor)} normal', foreground='black', lmargin1=20, lmargin2=20, underline = True) 
help_text.tag_config('explanation', font=f'{text_font} {int(13 * text_size_adjustment_factor)} normal', lmargin1=40, lmargin2=40)
hyperlink1 = HyperlinkManager(help_text)
line_number = 1 

# first step
help_text.insert(END, f"{fst_step_txt}\n")
help_text.tag_add('frame', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.insert(END, f"Browse\n")
help_text.insert(END, "Here you can browse for a folder which contains camera trap images or video\'s. All features will be performed on this directory.\n\n")
help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# second step
help_text.insert(END, f"{snd_step_txt}\n")
help_text.tag_add('frame', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1

# model
help_text.insert(END, f"{lbl_model_txt}\n")
help_text.insert(END, "Here, you can indicate the model that you want to use to analyse the data. 'MDv5a' and 'MDv5b' stand for the MegaDetector models version 5a"
                 " and b. These models differ only in their training data. Each MDv5 model can outperform the other slightly, depending on your data. Try them both"
                 " and see which one works best for you. If you really don't have a clue, just stick with the default MDv5a. More info ")
help_text.insert(INSERT, "here", hyperlink1.add(partial(webbrowser.open, "https://github.com/microsoft/CameraTraps/blob/main/megadetector.md#megadetector-v50-20220615")))
help_text.insert(END, ". It is also possible to choose your own custom yolov5 model when running inference (e.g. a model trained for specific species). More info "
                 "about how to train your custom model ")
help_text.insert(INSERT, "here", hyperlink1.add(partial(webbrowser.open, "https://github.com/PetervanLunteren/EcoAssist#custom-model-support")))
help_text.insert(END, ".\n\n")
help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# exclude subs
help_text.insert(END, f"{lbl_exclude_subs_txt}\n")
help_text.insert(END, "By default, MegaDetector will recurse into subdirectories. Select this option if you want to ignore the subdirectories and process only the"
                 " files directly in your chosen folder.\n\n")
help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# exclude detections
help_text.insert(END, f"{lbl_excl_detecs_txt} / {lbl_md_thresh_txt}\n")
help_text.insert(END, "This option will exclude detections from the output file. Please don't use this confidence threshold in order to set post-processing features"
                 " or third party software. The idea is that the output file contains everything that MegaDetector can find, and all processes which use this output "
                 "file will have their own ways of handling the confidence values. Once detections are excluded from the output file, there is no way of getting it"
                 " back. It is strongly advised to not exclude detections from the MegaDetector output file. Only set the confidence threshold to a very small value"
                 " if you really know what you're doing. If you, because for some reason, want an extra-small output file, you would typically use a threshold of 0.01"
                 " or 0.05. To adjust the threshold value, you can drag the slider or press either sides next to the slider for a 0.005 reduction or increment. "
                 "Confidence values are within the [0.005, 1] interval. \n\n")
help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# use absolute paths
help_text.insert(END, f"{lbl_abs_paths_txt}\n")
help_text.insert(END, "By default, the paths in the output file are relative (i.e. 'image.jpg') instead of absolute (i.e. '/path/to/some/folder/image.jpg'). This "
                 "option will make sure the output file contains absolute paths, but it is not recommended. Third party software (such as ")
help_text.insert(INSERT, "Timelapse", hyperlink1.add(partial(webbrowser.open, "https://saul.cpsc.ucalgary.ca/timelapse/")))
help_text.insert(END, ") will not be able to read the output file if the paths are absolute. Only enable this option if you know what you are doing. More information"
                 " how to use Timelapse in conjunction with MegaDetector, see the ")
help_text.insert(INSERT, "Timelapse Image Recognition Guide", hyperlink1.add(partial(webbrowser.open, "https://saul.cpsc.ucalgary.ca/timelapse/uploads/Guides/TimelapseImageRecognitionGuide.pdf")))
help_text.insert(END, ".\n\n")
help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# use checkpoints
help_text.insert(END, f"{lbl_use_checkpnts_txt}\n")
help_text.insert(END, "This is a functionality to save results to checkpoints intermittently, in case a technical hiccup arises. That way, you won't have to restart"
                 " the entire process again when the process is interrupted.\n\n")
help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# checkpoint frequency
help_text.insert(END, f"{lbl_checkpoint_freq_txt}\n")
help_text.insert(END, "Fill in how often you want to save the results to checkpoints. The number indicates the number of images after which checkpoints will be saved."
                 " The entry must contain only numeric characters.\n\n")
help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# continue from checkpoint
help_text.insert(END, f"{lbl_cont_checkpnt_txt}\n")
help_text.insert(END, "Here you can choose to continue from the last saved checkpoint onwards so that the algorithm can continue where it left off. Checkpoints are"
                 " saved into the main folder and look like 'checkpoint_<timestamp>.json'. When choosing this option, it will search for a valid"
                 " checkpoint file and prompt you if it can't find it.\n\n")
help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# don't process every frame
help_text.insert(END, f"{lbl_not_all_frames_txt}\n")
help_text.insert(END,
         "When processing every frame of a video, it can take a long, long time to finish. Here, you can specify whether you want to analyse only a selection of frames."
         f" At '{lbl_nth_frame_txt}' you can specify how many frames you want to be analysed.\n\n")
help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# analyse every nth frame
help_text.insert(END, f"{lbl_nth_frame_txt}\n")
help_text.insert(END, "Specify how many frames you want to process. By entering 2, you will process every 2nd frame and thus cut process time by half. By entering 10, "
                 "you will shorten process time to 1/10, et cetera. However, keep in mind that the chance of detecting something is also cut to 1/10.\n\n")
help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# third step
help_text.insert(END, f"{trd_step_txt}\n")
help_text.tag_add('frame', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1

# separate files
help_text.insert(END, f"{sep_frame_txt}\n")
help_text.insert(END, "This function divides the images into subdirectories based on their detections. Please be warned that this will be done automatically based"
                 " on the detections made by MegaDetector. There will not be an option to review and adjust the detections before the images will be moved. If you "
                 "want that (a human in the loop), take a look at ")
help_text.insert(INSERT, "Timelapse", hyperlink1.add(partial(webbrowser.open, "https://saul.cpsc.ucalgary.ca/timelapse/")))
help_text.insert(END, ", which offers such a feature. More information about that ")
help_text.insert(INSERT, "here", hyperlink1.add(partial(webbrowser.open, "https://saul.cpsc.ucalgary.ca/timelapse/uploads/Guides/TimelapseImageRecognitionGuide.pdf")))
help_text.insert(END," (starting on page 9). The process of importing the output file produced by EcoAssist into Timelapse is described ")
help_text.insert(INSERT, "here", hyperlink1.add(partial(webbrowser.open, "https://saul.cpsc.ucalgary.ca/timelapse/pmwiki.php?n=Main.DownloadMegadetector")))
help_text.insert(END,".\n\n")
help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# method of file placement
help_text.insert(END, f"{lbl_file_placement_txt}\n")
help_text.insert(END, "Here you can choose whether to move the files into subdirectories, or copy them so that the originals remain untouched.\n\n")
help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# sort results based on confidence
help_text.insert(END, f"{lbl_sep_conf_txt}\n")
help_text.insert(END, "This feature will further separate the files based on its confidence value (in tenth decimal intervals). That means that each class will"
                      " have subdirectories like e.g. 'conf_0.6-0.7', 'conf_0.7-0.8', 'conf_0.8-0.9', etc.\n\n")
help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# sep confidence threshold
help_text.insert(END, f"{lbl_sep_thresh_txt} of the separation process\n")
help_text.insert(END, f"Detections below this value will not count for the separation process. To adjust the threshold value you can drag the slider or press either"
                       " sides next to the slider for a 0.005 reduction or increment. Confidence values are within the [0.005, 1] interval. If you set the confidence "
                       "threshold too high, you will miss some detections. On the other hand, if you set the threshold too low, you will get false positives. When "
                       "choosing a threshold for your project, it is important to choose a threshold based on your own data. My advice is to first visualize your data"
                       f" ('{vis_frame_txt}') with a low threshold to get a feeling of the confidence values in your data. This will show you how sure the model is about"
                       " its detections and will give you an insight into which threshold will work best for you. If you really don't know, 0.2 is probably a conservative"
                       " threshold for most ecosystems.\n\n")
help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# visualize files
help_text.insert(END, f"{vis_frame_txt}\n")
help_text.insert(END, "This functionality draws boxes around the detections, prints their confidence values and saves them in the subdirectory 'visualized_images'."
                      " This can be useful to visually check the results. Videos can't be visualized using this tool.\n\n")
help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# confidence threshold for visualization
help_text.insert(END, f"{lbl_vis_thresh_txt} of the visualization process\n")
help_text.insert(END, f"Detections below this value will not be visualized. To adjust the threshold, value you can drag the slider or press either"
                       " sides next to the slider for a 0.005 reduction or increment. Confidence values are within the [0.005, 1] interval.\n\n")
help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# crop files
help_text.insert(END, f"{crp_frame_txt}\n")
help_text.insert(END, "This feature will crop the detections and save them as separate images in the subdirectory 'cropped_images'. These cropped images can be used"
                      " to train your own species classifier. Not applicable for videos.\n\n")
help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# confidence threshold for cropping
help_text.insert(END, f"{lbl_crp_thresh_txt} of the cropping process\n")
help_text.insert(END, f"Detections below this value will not be cropped. To adjust the threshold value, you can drag the slider or press either"
                       " sides next to the slider for a 0.005 reduction or increment. Confidence values are within the [0.005, 1] interval.\n\n")
help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# annotate files
help_text.insert(END, f"{xml_frame_txt}\n")
help_text.insert(END, "When training your own model using machine learning, the images generally need to be annotated with .xml files in Pascal VOC format. Here you can "
                      "create these annotation files. Pressing 'View results' after the process is finished will open the open-source annotation software ")
help_text.insert(INSERT, "LabelImg", hyperlink1.add(partial(webbrowser.open, "https://github.com/tzutalin/labelImg")))
help_text.insert(END, ". This application makes it easy to visually review annotations and adjust their labels. It's possible to change the default labels to your own "
                      f"by changing (the hidden file) {os.path.join(EcoAssist_files, 'labelImg', 'data', 'predefined_classes.txt')}. LabelImg will automatically open the "
                      "directory specified at step 1. However, if the files are separated into subfolders, labelImg doesn't know which folder to open first. In that case "
                      "you'll have to manually set the labelImg options 'Open Dir' and 'Change Save Dir' to the folder you want to inspect (top left of labelImg window), "
                      "and then double-click an image in the file list (bottom right of labelImg window). Not applicable to videos.\n\n")
help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# confidence threshold for annotating
help_text.insert(END, f"{lbl_xml_thresh_txt} of the annotation process\n")
help_text.insert(END, f"Detections below this value will not be included in the annotation file. To adjust the threshold value, you can drag the slider or press either"
                       " sides next to the slider for a 0.005 reduction or increment. Confidence values are within the [0.005, 1] interval.\n\n")
help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# config help_text
help_text.grid(row=0, column=0, sticky="nesw")
help_text.configure(font=(text_font, 11, "bold"), state=DISABLED)
scroll.config(command=help_text.yview)

# about tab
about_scroll = Scrollbar(about_tab)
about_text = Text(about_tab, width=int(130 * textbox_width_adjustment_factor), height=int(36 * textbox_height_adjustment_factor), wrap=WORD, yscrollcommand=scroll.set)
about_text.config(spacing1=2, spacing2=3, spacing3=2)
about_text.tag_config('title', font=f'{text_font} {int(15 * text_size_adjustment_factor)} bold', foreground='darkblue', lmargin1=10, lmargin2=10) 
about_text.tag_config('info', font=f'{text_font} {int(13 * text_size_adjustment_factor)} normal', lmargin1=20, lmargin2=20)
about_text.tag_config('citation', font=f'{text_font} {int(13 * text_size_adjustment_factor)} normal', lmargin1=30, lmargin2=50)
hyperlink = HyperlinkManager(about_text)
text_line_number=1

# the application
about_text.insert(END, "The application\n")
about_text.insert(END,
            "EcoAssist is a freely available and open-source application with the aim of helping ecologists with their camera trap data without the need of any "
            "programming skills. It uses a deep learning algorithm trained to detect the presence of animals, people and vehicles in camera trap data. Help me to "
            "keep improving EcoAssist and let me know about any improvements, bugs, or new features so that I can continue to keep it up-to-date. Also, I would also"
            " very much like to know who uses the tool and for what reason. Please email me on ")
about_text.insert(INSERT, "petervanlunteren@hotmail.com", hyperlink.add(partial(webbrowser.open, "mailto:petervanlunteren@hotmail.com")))
about_text.insert(END, ".\n\n")
about_text.tag_add('title', str(text_line_number) + '.0', str(text_line_number) + '.end');text_line_number+=1
about_text.tag_add('info', str(text_line_number) + '.0', str(text_line_number) + '.end');text_line_number+=2
about_text.grid(row=0, column=0, sticky="nesw")

# the model
about_text.insert(END, "The model\n")
about_text.insert(END, "For this application, I used ")
about_text.insert(INSERT, "MegaDetector", hyperlink.add(partial(webbrowser.open, "https://github.com/microsoft/CameraTraps/blob/master/megadetector.md")))
about_text.insert(END,
            " to detect animals, people, and vehicles. It does not identify animals, it just finds them. The model is created by Beery, Morris, and Yang (2019) and is"
            " based on the YOLOv5 architecture. The model was trained using several hundred thousand bounding boxes from a variety of ecosystems. On a typical laptop "
            "(bought in 2021) it takes somewhere between 3 and 8 seconds per image. This works out to being able to process something like 10000 to 25000 images per "
            "day. If you have a dedicated deep learning GPU, you can probably process along the lines of half a million images per day. The model is free, and it makes"
            " the creators super-happy when people use it, so I put their email address here for your convenience: ")
about_text.insert(INSERT, "cameratraps@lila.science", hyperlink.add(partial(webbrowser.open, "mailto:cameratraps@lila.science")))
about_text.insert(END, ".\n\n")
about_text.tag_add('title', str(text_line_number) + '.0', str(text_line_number) + '.end');text_line_number+=1
about_text.tag_add('info', str(text_line_number) + '.0', str(text_line_number) + '.end');text_line_number+=2

# citation
about_text.insert(END, "Citation\n")
about_text.insert(END, "If you use EcoAssist in your research, don't forget to cite the model and the EcoAssist software itself:\n")
about_text.insert(END, "- Beery, S., Morris, D., & Yang, S. (2019). Efficient pipeline for camera trap image review. ArXiv preprint arXiv:1907.06772.\n")
about_text.insert(END, "- van Lunteren, P. (2022). EcoAssist: An application for detecting animals in camera trap images using the MegaDetector model. [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.7223363\n\n")
about_text.tag_add('title', str(text_line_number) + '.0', str(text_line_number) + '.end');text_line_number+=1
about_text.tag_add('info', str(text_line_number) + '.0', str(text_line_number) + '.end');text_line_number+=1
about_text.tag_add('citation', str(text_line_number) + '.0', str(text_line_number) + '.end');text_line_number+=1
about_text.tag_add('citation', str(text_line_number) + '.0', str(text_line_number) + '.end');text_line_number+=2

# image credits
about_text.insert(END, "Image credits\n")
about_text.insert(END, "The beautiful camera trap images of the fox and ocelot displayed at the top were taken from the ")
about_text.insert(INSERT, "WCS Camera Traps dataset", hyperlink.add(partial(webbrowser.open, "https://lila.science/datasets/wcscameratraps")))
about_text.insert(END, " provided by the ")
about_text.insert(INSERT, "Wildlife Conservation Society", hyperlink.add(partial(webbrowser.open, "https://www.wcs.org/")))
about_text.insert(END, ".\n\n")
about_text.tag_add('title', str(text_line_number) + '.0', str(text_line_number) + '.end');text_line_number+=1
about_text.tag_add('info', str(text_line_number) + '.0', str(text_line_number) + '.end');text_line_number+=2

# config about_text
about_text.grid(row=0, column=0, sticky="nesw")
about_text.configure(font=(text_font, 11, "bold"), state=DISABLED)
scroll.config(command=about_text.yview)

# main function
def main():
    reset_frame_states()
    root.mainloop()

# executable as script
if __name__ == "__main__":
    main()
