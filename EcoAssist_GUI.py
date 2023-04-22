# Non-code GUI platform for training and deploying object detection models.
# Written by Peter van Lunteren, 23 Apr 2023 (latest edit)

# import packages like a christmas tree
import os
import re
import sys
import cv2
import git
import json
import math
import time
import torch
import random
import signal
import shutil
import platform
import datetime
import traceback
import subprocess
import webbrowser
import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import *
from pathlib import Path
from random import randint
from functools import partial
from subprocess import Popen, PIPE
import xml.etree.cElementTree as ET
from PIL import ImageTk, Image, ImageFilter
from bounding_box import bounding_box as bb
from tkinter import filedialog, ttk, messagebox as mb

# set global variables
version = "4.0"
EcoAssist_files = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# insert pythonpath
sys.path.insert(0, os.path.join(EcoAssist_files))
sys.path.insert(0, os.path.join(EcoAssist_files, "ai4eutils"))
sys.path.insert(0, os.path.join(EcoAssist_files, "yolov5"))
sys.path.insert(0, os.path.join(EcoAssist_files, "cameratraps"))

# log pythonpath
print(sys.path)

##########################################
############# MAIN FUNCTIONS #############
##########################################

# post-process files
def postprocess(src_dir, dst_dir, thresh, sep, file_placement, sep_conf, vis, crp, yol, csv, data_type):
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")

    # prepare data specific vars
    if data_type == "img":
        recognition_file = os.path.join(src_dir, "image_recognition_file.json")
        progress_postprocess_frame = img_progress_postprocess_frame
        progress_postprocess_progbar = img_progress_postprocess_progbar
        progress_postprocess_stats = img_progress_postprocess_stats
    else:
        recognition_file = os.path.join(src_dir, "video_recognition_file.json")
        progress_postprocess_frame = vid_progress_postprocess_frame
        progress_postprocess_progbar = vid_progress_postprocess_progbar
        progress_postprocess_stats = vid_progress_postprocess_stats

    # init vars
    global cancel_var
    start_time = time.time()
    nloop = 1

    # warn user
    if data_type == "vid":
        if vis or crp or yol:
            check_json_presence_and_warn_user("visualize, crop or annotate", "visualizing, cropping or annotating", "visualization, cropping, and annotation")
            vis, crp, yol = [False] * 3

    # fetch label map
    label_map = fetch_label_map_from_json(recognition_file)
    inverted_label_map = {v: k for k, v in label_map.items()}

    # create list with colours for visualisation
    if vis:
        colors = ["fuchsia", "blue", "orange", "yellow", "green", "red"]
        length_diff = len(colors) - len(label_map)
        if length_diff > 0:
            # first 6 classes get default colors
            colors = colors[:length_diff]
        if length_diff < 0:
            # all classes after that get random color
            for i in range(abs(length_diff)):
                colors.append('#%06X' % randint(0, 0xFFFFFF))
    
    # make sure json has relative paths
    json_paths_converted = False
    if check_json_paths(recognition_file) != "relative":
        make_json_relative(recognition_file)
        json_paths_converted = True
    
    # add cancel button
    cancel_var = False
    btn_cancel = Button(progress_postprocess_frame, text="Cancel", command=cancel)
    btn_cancel.grid(row=9, column=0, columnspan=2)

    # create classes.txt
    if yol:
        classes_txt = os.path.join(dst_dir, "classes.txt")
        with open(classes_txt, 'w') as f:
            for key in label_map:
                f.write(f"{label_map[key]}\n")
    
    # open json file
    with open(recognition_file) as image_recognition_file_content:
        data = json.load(image_recognition_file_content)
    n_images = len(data['images'])

    # initialise the csv files
    if csv:
        # for files
        csv_for_files = os.path.join(dst_dir, f"results_files.csv")
        if not os.path.isfile(csv_for_files):
            df = pd.DataFrame(list(), columns=["absolute_path", "relative_path", "data_type", "n_detections", "max_confidence"])
            df.to_csv(csv_for_files, encoding='utf-8', index=False)
        
        # for detections
        csv_for_detections = os.path.join(dst_dir, f"results_detections.csv")
        if not os.path.isfile(csv_for_detections):
            df = pd.DataFrame(list(), columns=["absolute_path", "relative_path", "data_type", "label", "confidence", "bbox_left", "bbox_top", "bbox_right", "bbox_bottom", "file_height", "file_width"])
            df.to_csv(csv_for_detections, encoding='utf-8', index=False)
    
    # loop through images
    for image in data['images']:

        # cancel process if required
        if cancel_var:
            break
        
        # check for failure
        if "failure" in image:
            mb.showwarning("Warning", f"FILE: '{image['file']}'\n\nFAILURE: '{image['failure']}'\n\nThis file will be skipped.")
            continue
        
        # get image info
        file = image['file']
        detections_list = image['detections']
        n_detections = len(detections_list)
        progress_postprocess_progbar['value'] += 100 / n_images

        # init vars
        max_detection_conf = 0.0
        unique_labels = []
        bbox_info = []
        csv_detectons = []
        csv_files = []

        # open files
        if vis or crp or yol or csv:
            if data_type == "img":
                im_to_vis = cv2.imread(os.path.join(src_dir, file))
                im_to_crop_path = os.path.join(src_dir, file)
            else:
                vid = cv2.VideoCapture(os.path.join(src_dir, file))

        # loop through detections
        for detection in image['detections']:

            # get confidence
            conf = detection["conf"]

            # write max conf
            if conf > max_detection_conf:
                max_detection_conf = conf

            # if above user specified thresh
            if conf >= thresh:

                # get detection info
                category = detection["category"]
                label = label_map[category]
                if sep:
                    unique_labels.append(label)
                    unique_labels = sorted(list(set(unique_labels)))

                # get bbox info
                if vis or crp or yol or csv:
                    if data_type == "img":
                        height, width = im_to_vis.shape[:2]
                    else:
                        height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))

                    w_box = detection['bbox'][2]
                    h_box = detection['bbox'][3]
                    xo = detection['bbox'][0] + (w_box/2)
                    yo = detection['bbox'][1] + (h_box/2)
                    left = int(round(detection['bbox'][0] * width))
                    top = int(round(detection['bbox'][1] * height))
                    right = int(round(w_box * width)) + left
                    bottom = int(round(h_box * height)) + top

                    # store in list
                    bbox_info.append([label, conf, left, top, right, bottom, height, width, xo, yo, w_box, h_box])

        # separate files
        if sep:
            if n_detections == 0:
                file = move_files(file, "empty", file_placement, max_detection_conf, sep_conf, dst_dir, src_dir)
            else:
                if len(unique_labels) > 1:
                    labels_str = "_".join(unique_labels)
                    file = move_files(file, labels_str, file_placement, max_detection_conf, sep_conf, dst_dir, src_dir)
                elif len(unique_labels) == 0:
                    file = move_files(file, "empty", file_placement, max_detection_conf, sep_conf, dst_dir, src_dir)
                else:
                    file = move_files(file, label, file_placement, max_detection_conf, sep_conf, dst_dir, src_dir)
        
        # collect info for csv files
        if csv:
            # file info
            row = pd.DataFrame([[src_dir, file, data_type, len(bbox_info), max_detection_conf]])
            row.to_csv(csv_for_files, encoding='utf-8', mode='a', index=False, header=False)

            # detections info
            rows = []
            for bbox in bbox_info:
                row = [src_dir, file, data_type, *bbox[:8]]
                rows.append(row)
            rows = pd.DataFrame(rows)
            rows.to_csv(csv_for_detections, encoding='utf-8', mode='a', index=False, header=False)
    
        # visualize images
        if vis and len(bbox_info) > 0:
            for bbox in bbox_info:
                vis_label = f"{bbox[0]} {bbox[1]}"
                color = colors[int(inverted_label_map[bbox[0]])-1]
                bb.add(im_to_vis, *bbox[2:6], vis_label, color)
            im = os.path.join(dst_dir, file)
            Path(os.path.dirname(im)).mkdir(parents=True, exist_ok=True)
            cv2.imwrite(im, im_to_vis)
        
        # crop images
        if crp and len(bbox_info) > 0:
            counter = 1
            for bbox in bbox_info:
                im_to_crp = Image.open(im_to_crop_path)
                crp_im = im_to_crp.crop((bbox[2:6]))
                im_to_crp.close()
                filename, file_extension = os.path.splitext(file)
                im_path = os.path.join(dst_dir, filename + '_crop' + str(counter) + '_' + bbox[0] + file_extension)
                Path(os.path.dirname(im_path)).mkdir(parents=True, exist_ok=True)
                crp_im.save(im_path)
                counter += 1

        # create yolo annotations
        if yol and len(bbox_info) > 0:
            filename, file_extension = os.path.splitext(file)
            annot_file = os.path.join(dst_dir, filename + ".txt")
            Path(os.path.dirname(annot_file)).mkdir(parents=True, exist_ok=True)
            with open(annot_file, 'w') as f:
                for bbox in bbox_info:
                    class_id = int(inverted_label_map[bbox[0]])-1
                    f.write(f"{class_id} {bbox[8]} {bbox[9]} {bbox[10]} {bbox[11]}\n")

        # calculate stats
        elapsed_time_sep = str(datetime.timedelta(seconds=round(time.time() - start_time)))
        time_left_sep = str(datetime.timedelta(seconds=round(((time.time() - start_time) * n_images / nloop) - (time.time() - start_time))))
        progress_postprocess_stats['text'] = create_postprocess_lbl(elapsed_time_sep, time_left_sep, command="running")
        nloop += 1
        root.update()

    # remove cancel button
    btn_cancel.grid_remove()
    
    # change json paths back, if converted earlier
    if json_paths_converted:
        make_json_absolute(recognition_file)
    
    # let the user know it's done
    progress_postprocess_stats['text'] = create_postprocess_lbl(elapsed_time_sep, time_left_sep, command="done")
    root.update()

# open progress window and initiate the post-process
def start_postprocess():
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")
        
    # set global variables
    global img_progress_postprocess_frame
    global vid_progress_postprocess_frame
    
    # fix user input
    src_dir = var_choose_folder.get()
    dst_dir = var_output_dir.get()
    thresh = var_thresh.get()
    sep = var_separate_files.get()
    file_placement = var_file_placement.get()
    sep_conf = var_sep_conf.get()
    vis = var_vis_files.get()
    crp = var_crp_files.get()
    yol = var_yol_files.get()
    csv = var_csv.get()

    # check which json files are present
    img_json = False
    if os.path.isfile(os.path.join(src_dir, "image_recognition_file.json")):
        img_json = True
    vid_json = False
    if os.path.isfile(os.path.join(src_dir, "video_recognition_file.json")):
        vid_json = True
    if not img_json and not vid_json:
        mb.showerror("Error", "No model output file present. Make sure you run step "
                     "2 before post-processing the files.")
        return
    
    # check if destination dir is valid and set to input dir if not
    if dst_dir in ["", "/", "\\", ".", "~", ":"] or not os.path.isdir(dst_dir):
        mb.showerror("Destination folder not set", "Destination folder not set.\n\n You have not specified where the post-processing results should "
                     "be placed or the set folder does not exist. This is required.")
        return

    # warn user if the original files will be overwritten with visualized files
    if dst_dir == src_dir and vis and not sep:
        if not mb.askyesno("Original images will be overwritten", 
                      f"WARNING! The visualized images will be placed in the folder with the original data: '{src_dir}'. By doing this, you will overwrite the original images"
                      " with the visualized ones. Are you sure you want to continue?"):
            return

    # open new window with progress bar and stats
    pp_process_window = Toplevel(root)
    pp_process_window.title("Post-process progress")
    pp_process_window.geometry()

    # logo
    logo = tk.Label(pp_process_window, image=grey_bg_logo)
    logo.grid(column=0, row=0, columnspan=2, sticky='ew', pady=(5, 0))

    # add image progress
    if img_json:
        img_progress_postprocess_frame = LabelFrame(pp_process_window, text=" Postprocessing images ", pady=2, padx=5, relief='solid', highlightthickness=5, font=100, fg='darkblue')
        img_progress_postprocess_frame.configure(font=(text_font, 15, "bold"))
        img_progress_postprocess_frame.grid(column=0, row=1, columnspan=2, sticky='ew')
        img_progress_postprocess_frame.columnconfigure(0, weight=3, minsize=115)
        img_progress_postprocess_frame.columnconfigure(1, weight=1, minsize=115)
        global img_progress_postprocess_progbar
        img_progress_postprocess_progbar = ttk.Progressbar(master=img_progress_postprocess_frame, orient='horizontal', mode='determinate', length=280)
        img_progress_postprocess_progbar.grid(column=0, row=0, columnspan=2, padx=5, pady=(3,0))
        global img_progress_postprocess_stats
        img_progress_postprocess_stats = ttk.Label(master=img_progress_postprocess_frame, text=create_postprocess_lbl())
        img_progress_postprocess_stats.grid(column=0, row=1, padx=5, pady=(0,3), columnspan=2)

    # add video progress
    if vid_json:
        vid_progress_postprocess_frame = LabelFrame(pp_process_window, text=" Postprocessing videos ", pady=2, padx=5, relief='solid', highlightthickness=5, font=100, fg='darkblue')
        vid_progress_postprocess_frame.configure(font=(text_font, 15, "bold"))
        vid_progress_postprocess_frame.grid(column=0, row=2, columnspan=2, sticky='ew')
        vid_progress_postprocess_frame.columnconfigure(0, weight=3, minsize=115)
        vid_progress_postprocess_frame.columnconfigure(1, weight=1, minsize=115)
        global vid_progress_postprocess_progbar
        vid_progress_postprocess_progbar = ttk.Progressbar(master=vid_progress_postprocess_frame, orient='horizontal', mode='determinate', length=280)
        vid_progress_postprocess_progbar.grid(column=0, row=0, columnspan=2, padx=5, pady=(3,0))
        global vid_progress_postprocess_stats
        vid_progress_postprocess_stats = ttk.Label(master=vid_progress_postprocess_frame, text=create_postprocess_lbl())
        vid_progress_postprocess_stats.grid(column=0, row=1, padx=5, pady=(0,3), columnspan=2)
    
    try:
        # postprocess images
        if img_json:
            postprocess(src_dir, dst_dir, thresh, sep, file_placement, sep_conf, vis, crp, yol, csv, data_type = "img")

        # postprocess videos
        if vid_json:
            postprocess(src_dir, dst_dir, thresh, sep, file_placement, sep_conf, vis, crp, yol, csv, data_type = "vid")
        
        # complete
        complete_frame(trd_step)

        # close progress window
        pp_process_window.destroy()
    
    except Exception as error:
        # log error
        print("ERROR:\n" + str(error) + "\n\nDETAILS:\n" + str(traceback.format_exc()) + "\n\n")
        
        # show error
        mb.showerror(title="Error",
                     message="An error has occurred (EcoAssist v" + version + "): '" + str(error) + "'.",
                     detail=traceback.format_exc())
        
        # close window
        pp_process_window.destroy()

# check data and prepare for training
def prepare_data_for_training(data_folder, prop_to_test, prop_to_val):
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")

    # get list of all images in dir
    data_folder = os.path.normpath(data_folder)
    files = [f for f in os.listdir(data_folder) if os.path.isfile(os.path.join(data_folder, f)) and not f.endswith(".DS_Store") and f.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif'))]

    # calculate amounts
    total_n = len(files)
    n_test = int(total_n * prop_to_test)
    n_val = int(total_n * prop_to_val)

    # select random files
    random.shuffle(files)
    test_files = files[:n_test]
    val_files = files[n_test:n_test+n_val]
    train_files = files[n_test+n_val:]

    # remove files for previous training
    old_files = ["dataset.yaml", "train_selection.txt", "train_selection.cache", "train_selection.cache.npy", "val_selection.txt", "val_selection.cache",
                 "val_selection.cache.npy", "test_selection.txt", "test_selection.cache", "test_selection.cache.npy"]
    for filename in old_files:
        old_file = os.path.join(data_folder, filename)
        if os.path.isfile(old_file):
            os.remove(old_file)

    # write text files with images
    for elem in [[train_files, "train"], [val_files, "val"], [test_files, "test"]]:
        counter = 0
        with open(os.path.join(data_folder, elem[1] + "_selection.txt"), 'w') as f:
            for file in elem[0]:
                f.write("./" + file + "\n")
                counter += 1
        send_to_output_window(f"\nWill use {counter} images as {elem[1]}");root.update()

    # read class names
    with open(os.path.join(data_folder, "classes.txt")) as f:
        lines = f.readlines()
        names = [line.rstrip('\n') for line in lines]
    nc = len(names)

    # create dataset.yaml
    if prop_to_test == 0:
        yaml_content = f"# set paths\npath: '{data_folder}'\ntrain: ./train_selection.txt\nval: ./val_selection.txt\n\n# n classes\nnc: {nc}\n\n# class names\nnames: {names}\n"
    else:
        yaml_content = f"# set paths\npath: '{data_folder}'\ntrain: ./train_selection.txt\nval: ./val_selection.txt\ntest: ./test_selection.txt\n\n# n classes\nnc: {nc}\n\n# class names\nnames: {names}\n"
    yaml_file = os.path.join(data_folder, "dataset.yaml")
    with open(yaml_file, 'w') as f:
        f.write(yaml_content)
        send_to_output_window(f"\nWritten {yaml_file} with content:\n\n{yaml_content}\n");root.update()

# check input and execute train command
def start_training():
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")

    # set button states
    cancel_training_bool.set(False)
    set_buttons_to_training()

    # checkout yolov5 repo to new models
    switch_yolov5_git_to("new models")

    # build command
    send_to_output_window("Building train command...");root.update()
    command_args = []
    command_args.append(sys.executable)
    command_args.append(os.path.join(EcoAssist_files, "yolov5", "train.py"))

    # resume existing training
    if var_train_type.get() == dpd_train_type_options[1]: 
        # resume from file
        checkpoint_file = var_resume_checkpoint_path.get()
        if not os.path.isfile(checkpoint_file):
            mb.showerror("Error", message="Please specify the last checkpoint file to resume from.")
            set_buttons_to_idle()
            return
        command_args.append(f"--resume={checkpoint_file}")
    
        # extract output folder from checkpoint file
        results_dir =  os.path.dirname(
                            os.path.dirname(
                                os.path.dirname(
                                    os.path.dirname(
                                        os.path.normpath(
                                            checkpoint_file)))))
        
    # start new training
    elif var_train_type.get() == dpd_train_type_options[0]: 
        # set retrain from
        command_args.append(f"--weights={var_learning_model_path.get()}")

        # prepare data for training
        send_to_output_window("Preparing data training set...");root.update()
        data_dir = var_annotated_data.get()
        if data_dir in ["", "/", "\\", ".", "~", ":"] or not os.path.isdir(data_dir):
            mb.showerror("Error", message="Please specify a directory with annotated data to train on.")
            set_buttons_to_idle()
            return
        prepare_data_for_training(data_dir, var_test_prop.get(), var_val_prop.get())

        # add data argument
        command_args.append(f"--data={os.path.normpath(os.path.join(data_dir, 'dataset.yaml'))}")
        
        # select gpu if available
        if var_train_gpu.get():
            send_to_output_window("Searching for GPU...");root.update()

            # for windows machines
            if torch.cuda.is_available():
                send_to_output_window("\tCUDA is available.");root.update()
                command_args.append(f"--device=0")
            else:
                send_to_output_window("\tCUDA is not available.");root.update()
                
            # for apple silicon machines
            try:
                if torch.backends.mps.is_built() and torch.backends.mps.is_available():
                    send_to_output_window("\tGPU (MPS) is available.");root.update()
                    command_args.append(f"--device=mps")
                else:
                    send_to_output_window("\tGPU (MPS) is not available.");root.update()
            except AttributeError:
                pass
        
        # number of epochs
        if not var_n_epochs.get().isdecimal() or var_n_epochs.get() == "":
            invalid_value_warning("number of epochs")
            set_buttons_to_idle()
            return
        command_args.append(f"--epochs={var_n_epochs.get()}")

        # batch size
        if no_user_input(var_batch_size):
            command_args.append("--batch-size=-1")
        elif not var_batch_size.get().isdecimal():
            invalid_value_warning("batch size")
            set_buttons_to_idle()
            return
        else:
            command_args.append(f"--batch-size={var_batch_size.get()}")

        # number of dataloader workers
        if no_user_input(var_n_workers):
            command_args.append("--workers=4")
        elif not var_n_workers.get().isdecimal():
            invalid_value_warning("number of workers")
            set_buttons_to_idle()
            return
        else:
            command_args.append(f"--workers={var_n_workers.get()}")

        # image size
        if no_user_input(var_img_size) == False:
            if not var_img_size.get().isdecimal():
                invalid_value_warning("image size")
                set_buttons_to_idle()
                return
            else:
                command_args.append(f"--img={var_img_size.get()}")
        elif var_learning_model.get() == dpd_learning_model_options[0] or var_learning_model.get() == dpd_learning_model_options[1]:
            # megadetector models
            command_args.append(f"--img=1280")
        
        # frozen layers
        if var_learning_model.get() == dpd_learning_model_options[0] or var_learning_model.get() == dpd_learning_model_options[1]:
            # megadetector models
            command_args.append(f"--freeze=12")
        elif var_learning_model.get() == dpd_learning_model_options[7]:
            # custom model
            if no_user_input(var_n_freeze_layers) == False:
                if not var_n_freeze_layers.get().isdecimal():
                    invalid_value_warning("number of frozen layers")
                    set_buttons_to_idle()
                    return
                else:
                    command_args.append(f"--freeze={var_n_freeze_layers.get()}")
        
        # model architecture
        if var_learning_model.get() == dpd_learning_model_options[8]:
            # from scratch
            if not var_model_architecture.get() == dpd_model_architecture_options[6]:
                # not "none" selected
                command_args.append(f"--cfg={var_model_architecture_path.get()}")

        # check user input for destination folder
        results_dir = var_results_dir.get()
        if results_dir in ["", "/", "\\", ".", "~", ":"] or not os.path.isdir(results_dir):
            mb.showerror("Error", message="Please specify the destination directory.")
            set_buttons_to_idle()
            return

        # project name
        if no_user_input(var_project_name):
            invalid_value_warning("project name", numeric = False)
            set_buttons_to_idle()
            return
        command_args.append(f"--project={var_project_name.get()}")
            
        # name of the run
        if no_user_input(var_run_name) == False:
            command_args.append(f"--name={var_run_name.get()}")

        # hyperparameter file
        if var_hyper_file_path.get() != "":
            command_args.append(f"--hyp={var_hyper_file_path.get()}")

        # cache images
        if var_cache_imgs.get():
            command_args.append(f"--cache")

        # evolve
        if var_evolve.get():
            # get n generations
            if no_user_input(var_n_generations) == False:
                if not var_n_generations.get().isdecimal():
                    invalid_value_warning("number of generations")
                    set_buttons_to_idle()
                    return
                command_args.append(f"--evolve={var_n_generations.get()}")
            else:
                command_args.append(f"--evolve=300")
    
    # change directory to the destination folder
    os.chdir(results_dir)

    # adjust command for unix OS
    if os.name != 'nt':
        command_args = "'" + "' '".join(command_args) + "'"
    
    # log command
    send_to_output_window(f"\ncommand_args : {command_args}\n");root.update()
    send_to_output_window("\nStarting training process...\n");root.update()

    # run command
    p = Popen(command_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=1,
                shell=True,
                universal_newlines=True)
    
    # read the output
    skip = False
    for line in p.stdout:

        # send to console but only update the window for the lines that matter
        send_to_output_window(line)

        # skip the model summary 
        if line.split() == ["from", "n", "params", "module", "arguments"]:
            skip = True
        if line.startswith("Model summary: "):
            skip = False

        # skip the freezing process
        if not line.startswith("freezing ") and not skip:

            # pause process for unix OS
            if os.name != 'nt':
                p.send_signal(signal.SIGSTOP)
            
            # check if user cancelled the training
            if cancel_training_bool.get():
                send_to_output_window("TRAINING CANCELLED BY USER...")
                set_buttons_to_idle()
                return
            
            # update root so that console output will be updated for the user
            root.update()

            # continue process for unix OS
            if os.name != 'nt':
                p.send_signal(signal.SIGCONT)
    
    # let user know when it's done
    send_to_output_window(f"TRAINING IS DONE! Results are saved to {results_dir}.")

    # set button states
    cancel_training_bool.set(False)
    set_buttons_to_idle()

# create required files and open the LabelImg software
def start_annotation():
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")

    # set vars
    images_dir = var_annot_dir.get()
    classes_txt = os.path.join(images_dir, "classes.txt")

    # check if images dir is valid
    if images_dir in ["", "/", "\\", ".", "~", ":"] or not os.path.isdir(images_dir):
        mb.showerror("Error", message="Please specify a directory with images to annotate.")
        return

    # check if user specified classes
    if not os.path.isfile(classes_txt) and no_user_input(var_annot_classes):
        invalid_value_warning("classes", numeric = False)
        return

    # create classes.txt if required
    if not os.path.isfile(classes_txt):
        classes_list = ent_annot_classes.get().split(",")
        classes_list = [s.strip() for s in classes_list]
        with open(classes_txt, 'w') as fp:
            for elem in classes_list:
                fp.write(f"{elem}\n")

    # locate open script
    if os.name == 'nt':
        labelImg_script = os.path.join(EcoAssist_files, "EcoAssist", "label.bat")
    else:
        labelImg_script = os.path.join(EcoAssist_files, "EcoAssist", "label.command")

    # create command
    command_args = []
    command_args.append(labelImg_script)
    command_args.append(images_dir)
    command_args.append(classes_txt)

    # adjust command for unix OS
    if os.name != 'nt':
        command_args = "'" + "' '".join(command_args) + "'"
    
    # log command
    print(command_args)

    # run command
    p = Popen(command_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=1,
                shell=True,
                universal_newlines=True)
    for line in p.stdout:
        # log stdout and stderr
        print(line, end='')
        
        # report traceback when error
        if line.startswith("Traceback "): 
            mb.showerror("Error opening labelImg", message="An error occured while opening the "
                            "annotation software labelImg. Please send an email to petervanlunteren@hotmail.com"
                            " to resolve this bug.")

# delpoy model and create json output files 
def deploy_model(path_to_image_folder, selected_options, data_type):
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
    if var_model.get() == dpd_options_model[0]: 
        # set model file
        model_file = os.path.join(EcoAssist_files, "pretrained_models", "md_v5a.0.0.pt")
        
        # set yolov5 git to accommodate old models
        switch_yolov5_git_to("old models")
        
    elif var_model.get() == dpd_options_model[1]:
        # set model file
        model_file = os.path.join(EcoAssist_files, "pretrained_models", "md_v5b.0.0.pt")
        
        # set yolov5 git to accommodate old models
        switch_yolov5_git_to("old models")
    else:
        # set model file
        model_file = var_model_path.get()
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
        
        # catch model errors
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
            mb.showerror("Error", "Model error:\n\n" + line)
        if "Warning:" in line and not '%' in line[0:4]:
            if not "could not determine MegaDetector version" in line and not "no metadata for unknown detector version" in line:
                mb.showerror("Warning", "Model warning:\n\n" + line)
        
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
                                                  "custom_model" : custom_model_bool,
                                                  "custom_model_info" : {}}}
    if custom_model_bool:
        ecoassist_metadata["ecoassist_metadata"]["custom_model_info"] = {"model_name" : os.path.basename(os.path.normpath(model_file)),
                                                                         "label_map" : label_map}
    
    # write metadata to json and make abosulte if specified
    image_recognition_file = os.path.join(chosen_folder, "image_recognition_file.json")
    video_recognition_file = os.path.join(chosen_folder, "video_recognition_file.json")
    if data_type == "img" and os.path.isfile(image_recognition_file):
        append_to_json(image_recognition_file, ecoassist_metadata)
        if var_abs_paths.get():
            make_json_absolute(image_recognition_file)
    if data_type == "vid" and os.path.isfile(video_recognition_file):
        append_to_json(video_recognition_file, ecoassist_metadata)
        if var_abs_paths.get():
            make_json_absolute(video_recognition_file)

# open progress window and initiate the model deployment
def start_deploy():
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
                        "enter numberic characters.\n\nDo you want to proceed with the default value 500?"):
            var_checkpoint_freq.set("500")
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
    md_progress_window.title("Deploy progress")
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
            deploy_model(var_choose_folder.get(), additional_img_options, data_type = "img")
        # ... and/or videos
        if var_process_vid.get():
            deploy_model(var_choose_folder.get(), additional_vid_options, data_type = "vid")
        
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

############################################
############# HELPER FUNCTIONS #############
############################################

# set button states to training
def set_buttons_to_training():
    btn_cancel_training.config(state=NORMAL)
    btn_start_training.config(state=DISABLED)

# set button states to idle
def set_buttons_to_idle():
    btn_cancel_training.config(state=DISABLED)
    btn_start_training.config(state=NORMAL)

# browse file and display result
def browse_file(var, var_short, var_path, dsp, filetype, cut_off_length, options, nrow):
    # choose file
    file = filedialog.askopenfilename(filetypes=filetype)
    
    # shorten if needed
    dsp_file = os.path.basename(file)
    if len(dsp_file) > cut_off_length:
        dsp_file = "..." + dsp_file[0 - cut_off_length + 3:]
    
    # set variables
    var_short.set(dsp_file)

    # reset to default if faulty
    if file != "":
        dsp.grid(column=0, row=nrow, sticky='e')
        var_path.set(file)
    else:
        var.set(options[0])

# switch beteen versions of yolov5 git to accommodate either old or new models
def switch_yolov5_git_to(model_type):
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")
    
    # checkout repo
    repository = git.Repo(os.path.join(EcoAssist_files, "yolov5"))
    if model_type == "old models":
        if platform.processor() == "arm" and os.name != "nt": # M1 and M2
            repository.git.checkout("868c0e9bbb45b031e7bfd73c6d3983bcce07b9c1")
        else:
            repository.git.checkout("c23a441c9df7ca9b1f275e8c8719c949269160d1")
    elif model_type == "new models":
        repository.git.checkout("3e55763d45f9c5f8217e4dad5ba1e6c1f42e3bf8")

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
        # open
        with open(path_to_json, "r") as json_file:
            data = json.load(json_file)
        
        # adjust
        for image in data['images']:
            absolute_path = image['file']
            relative_path = absolute_path.replace(os.path.normpath(var_choose_folder.get()), "")[1:]
            image['file'] = relative_path
        
        # write
        with open(path_to_json, "w") as json_file:
            json.dump(data, json_file, indent=1)
            
# make json paths absolute
def make_json_absolute(path_to_json):
    if check_json_paths(path_to_json) == "relative":
        # open
        with open(path_to_json, "r") as json_file:
            data = json.load(json_file)
        
        # adjust
        for image in data['images']:
            relative_path = image['file']
            absolute_path = os.path.normpath(os.path.join(var_choose_folder.get(), relative_path))
            image['file'] = absolute_path
        
        # write
        with open(path_to_json, "w") as json_file:
            json.dump(data, json_file, indent=1)

# add information to json file
def append_to_json(path_to_json, object_to_be_appended):
    # open
    with open(path_to_json, "r") as json_file:
        data = json.load(json_file)
    
    # adjust
    data['info'].update(object_to_be_appended)

    # write
    with open(path_to_json, "w") as json_file:
        json.dump(data, json_file, indent=1)

# show warning for video post-processing
def check_json_presence_and_warn_user(infinitive, continuous, noun):
    # check json presence
    img_json = False
    if os.path.isfile(os.path.join(var_choose_folder.get(), "image_recognition_file.json")):
        img_json = True
    vid_json = False
    if os.path.isfile(os.path.join(var_choose_folder.get(), "video_recognition_file.json")):
        vid_json = True
    
    # show warning
    if not img_json:
        if vid_json:
            mb.showerror("Error", f"{noun.capitalize()} is not supported for videos.")
            return True
        if not vid_json:
            mb.showerror("Error", f"No model output file present. Make sure you run step "
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

# move files into subdirectories
def move_files(file, detection_type, var_file_placement, max_detection_conf, var_sep_conf, dst_root, src_dir):
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")

    # squeeze in extra dir if sorting on confidence
    if var_sep_conf and detection_type != "empty":
        global conf_dirs
        ceiled_confidence = math.ceil(max_detection_conf * 10) / 10.0
        confidence_dir = conf_dirs[ceiled_confidence]
        new_file = os.path.join(detection_type, confidence_dir, file)
    else:
        new_file = os.path.join(detection_type, file)
    
    # set paths
    src = os.path.join(src_dir, file)
    dst = os.path.join(dst_root, new_file)
    
    # create subfolder
    Path(os.path.dirname(dst)).mkdir(parents=True, exist_ok=True)
    
    # place image or video in subfolder
    if var_file_placement == 1: # move
        shutil.move(src, dst)
    elif var_file_placement == 2: # copy
        shutil.copy2(src, dst)
        
    # return new relative file path
    return(new_file)

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

# order statistics from model output and return string
def create_md_progress_lbl(elapsed_time="",
                           time_left="",
                           current_im="",
                           total_im="",
                           processing_speed="",
                           percentage="",
                           GPU_param="",
                           data_type="",
                           command=""):

    # set unit
    if data_type == "img":
        unit = "image"
    else:
        unit = "frame"
    
    # translate processing speed 
    if "it/s" in processing_speed:
        speed_prefix = f"{unit.capitalize()} per sec:"
        speed_suffix = processing_speed.replace("it/s", "")
    elif "s/it" in processing_speed:
        speed_prefix = f"Sec per {unit}: "
        speed_suffix = processing_speed.replace("s/it", "")
    else:
        speed_prefix = ""
        speed_suffix = ""
        
    # loading
    if command == "load":
        return f"Algorithm is starting up..."
    
    # running (OS dependant)
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
    
    # done
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
def browse_dir(var, var_short, dsp, cut_off_length, n_row, n_column, str_sticky):
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")

    # choose directory
    chosen_dir = filedialog.askdirectory()

    # set choice to variable
    var.set(chosen_dir)
    
    # shorten, set and grid display
    dsp_chosen_dir = chosen_dir
    if len(dsp_chosen_dir) > cut_off_length:
        dsp_chosen_dir = "..." + dsp_chosen_dir[0 - cut_off_length + 3:]
    if var == var_choose_folder:
        dsp_chosen_dir = "  " + dsp_chosen_dir
    var_short.set(dsp_chosen_dir)
    dsp.grid(column=n_column, row=n_row, sticky=str_sticky)

# load a custom yolov5 model
def model_options(self):
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")
    
    # if custom model is selected
    if var_model.get() == dpd_options_model[2]:
        
        # choose, display and set global var
        browse_file(var_model,
                    var_model_short,
                    var_model_path,
                    dsp_model,
                    [("Yolov5 model","*.pt")],
                    30,
                    dpd_options_model,
                    row_model)

    else:
        var_model_short.set("")

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
    
    # open destination folder at step 3
    if frame.cget('text').startswith(' Step 3'):
        open_file_or_folder(var_output_dir.get())

# open file or folder
def open_file_or_folder(path):
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")
    
    # open file
    if platform.system() == 'Darwin': # mac  
        try:
            subprocess.call(('open', path))
        except:
            mb.showerror("Error opening results", f"Could not open '{path}'. "
                         "You'll have to find it yourself...")
    elif platform.system() == 'Windows': # windows
        try:
            os.startfile(path)
        except:
            mb.showerror("Error opening results", f"Could not open '{path}'. "
                         "You'll have to find it yourself...")
    else: # linux
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

# update frame states
def update_frame_states():
    # check dir validity
    if var_choose_folder.get() not in ["", "/", "\\", ".", "~", ":"] and os.path.isdir(var_choose_folder.get()):
        complete_frame(fst_step)
    else:
        enable_frame(fst_step)

    # check json files
    img_json = False
    if os.path.isfile(os.path.join(var_choose_folder.get(), "image_recognition_file.json")):
        img_json = True
    vid_json = False
    if os.path.isfile(os.path.join(var_choose_folder.get(), "video_recognition_file.json")):
        vid_json = True
    
    # check if dir is already processed
    if img_json or vid_json:
        complete_frame(snd_step)
        enable_frame(trd_step)
    else:
        enable_frame(snd_step)
        disable_frame(trd_step)

# show entry box if classes.txt is not yet present
def grid_annot_classes():
    classes_txt = os.path.join(var_annot_dir.get(), "classes.txt")
    if not os.path.isfile(classes_txt):
        lbl_annot_classes.grid(row=row_annot_classes, sticky='nesw')
        ent_annot_classes.grid(row=row_annot_classes, column=1, sticky='nesw', padx=5)
    else:
        lbl_annot_classes.grid_remove()
        ent_annot_classes.grid_remove()

# set hyperparameter file variable based on user selection
def set_hyper_file(self):
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")

    # if "other" is selected
    if self == dpd_hyper_file_options[6]:
        browse_file(var_hyper_file,
                    var_hyper_file_short,
                    var_hyper_file_path,
                    dsp_hyper_file,
                    [("YAML file","*.yaml")],
                    20,
                    dpd_hyper_file_options,
                    row_hyper_file)
    
    # if one of the pre-defined files is selected
    else:
        yolo_hyps = os.path.join(EcoAssist_files, "yolov5", "data", "hyps")
        if self == dpd_hyper_file_options[0]:
            var_hyper_file_path.set("")
        elif self == dpd_hyper_file_options[1]:
            var_hyper_file_path.set(os.path.join(yolo_hyps, "hyp.scratch-low.yaml"))
        elif self == dpd_hyper_file_options[2]:
            var_hyper_file_path.set(os.path.join(yolo_hyps, "hyp.scratch-med.yaml"))
        elif self == dpd_hyper_file_options[3]:
            var_hyper_file_path.set(os.path.join(yolo_hyps, "hyp.scratch-high.yaml"))
        elif self == dpd_hyper_file_options[4]:
            var_hyper_file_path.set(os.path.join(yolo_hyps, "hyp.Objects365.yaml"))
        elif self == dpd_hyper_file_options[5]:
            var_hyper_file_path.set(os.path.join(yolo_hyps, "hyp.VOC.yaml"))

# set model architecture variable based on user selection
def set_model_architecture(self):
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")

    # if "other config" is selected
    if self == dpd_model_architecture_options[5]:
        browse_file(var_model_architecture,
                    var_model_architecture_short,
                    var_model_architecture_path,
                    dsp_model_architecture,
                    [("YAML file","*.yaml")],
                    20,
                    dpd_model_architecture_options,
                    row_model_architecture)
    
    # if one of the pre-defined archs is selected
    else:
        model_architectures = os.path.join(EcoAssist_files, "yolov5", "models")
        if self == dpd_model_architecture_options[0]:
            var_model_architecture_path.set(os.path.join(model_architectures, "yolov5n.yaml"))
        elif self == dpd_model_architecture_options[1]:
            var_model_architecture_path.set(os.path.join(model_architectures, "yolov5s.yaml"))
        elif self == dpd_model_architecture_options[2]:
            var_model_architecture_path.set(os.path.join(model_architectures, "yolov5m.yaml"))
        elif self == dpd_model_architecture_options[3]:
            var_model_architecture_path.set(os.path.join(model_architectures, "yolov5l.yaml"))
        elif self == dpd_model_architecture_options[4]:
            var_model_architecture_path.set(os.path.join(model_architectures, "yolov5x.yaml"))
        elif self == dpd_model_architecture_options[6]:
            var_model_architecture_path.set("")

# set learning model variable based on user selection
def set_learning_model(self):
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")

    # set variable
    choice = var_learning_model.get()

    # user selected custom model
    if choice == dpd_learning_model_options[7]:
        # choose file
        browse_file(var_learning_model,
                    var_learning_model_short,
                    var_learning_model_path,
                    dsp_learning_model,
                    [("Yolov5 model","*.pt")],
                    20,
                    dpd_learning_model_options,
                    row_learning_model)

        # add widget to freeze layers if custom model is selected
        if not var_learning_model_path.get().startswith(os.path.join(EcoAssist_files, "pretrained_models")):
            lbl_n_freeze_layers.grid(row=row_n_freeze_layers, sticky='nesw')
            ent_n_freeze_layers.grid(row=row_n_freeze_layers, column=1, sticky='nesw', padx=5)
    
    # user selected pre-defined model or from scratch
    else:
        var_learning_model_short.set("")
        lbl_n_freeze_layers.grid_forget()
        ent_n_freeze_layers.grid_forget()

    # show scratch learning widgets
    if choice == dpd_learning_model_options[8]:
        lbl_model_architecture.grid(row=row_model_architecture, sticky='nesw', pady=2)
        dpd_model_architecture.grid(row=row_model_architecture, column=1, sticky='nesw', padx=5)

    # hide scratch learning widgets
    else:
        lbl_model_architecture.grid_forget()
        dpd_model_architecture.grid_forget()
        dsp_model_architecture.grid_forget()
    
    # set path to model
    pretrained_models = os.path.join(EcoAssist_files, "pretrained_models")
    if choice == dpd_learning_model_options[0]:
        var_learning_model_path.set(os.path.join(pretrained_models, "md_v5a.0.0.pt"))
    elif choice == dpd_learning_model_options[1]:
        var_learning_model_path.set(os.path.join(pretrained_models, "md_v5b.0.0.pt"))
    elif choice == dpd_learning_model_options[2]:
        var_learning_model_path.set(os.path.join(pretrained_models, "yolov5n.pt"))
    elif choice == dpd_learning_model_options[3]:
        var_learning_model_path.set(os.path.join(pretrained_models, "yolov5s.pt"))
    elif choice == dpd_learning_model_options[4]:
        var_learning_model_path.set(os.path.join(pretrained_models, "yolov5m.pt"))
    elif choice == dpd_learning_model_options[5]:
        var_learning_model_path.set(os.path.join(pretrained_models, "yolov5l.pt"))
    elif choice == dpd_learning_model_options[6]:
        var_learning_model_path.set(os.path.join(pretrained_models, "yolov5xl.pt"))
    elif choice == dpd_learning_model_options[8]:
        var_learning_model_path.set("")

# set global cancel var to end training
def cancel_training():
    cancel_training_bool.set(True)

# check if user entered text in entry widget
def no_user_input(var):
    if var.get() == "" or var.get().startswith("E.g.:"):
        return True
    else:
        return False

# send text to output window and log 
def send_to_output_window(txt):
    # show user
    txt_train_output.configure(state=NORMAL)
    txt_train_output.insert(END, f"{txt}\n")
    txt_train_output.see("end")
    txt_train_output.configure(state=DISABLED)

    # log
    print(txt)

# show warning if not valid input
def invalid_value_warning(str, numeric = True):
    string = f"You either entered an invalid value for the {str}, or none at all." 
    if numeric:
        string += " You can only enter numberic characters."
    mb.showerror("Invalid value", string)

# show and hide project widget depending on existing projects and user input
def grid_project_name():
    # set vars
    global var_project_name
    global ent_project_name

    # remove all project name widgets
    project_name_widgets = [*req_params.grid_slaves(row_project_name, 0), *req_params.grid_slaves(row_project_name, 1)]
    for widget in project_name_widgets:
        widget.grid_forget()

    # check if any existing projects
    dpd_project_name_options = sorted([o for o in os.listdir(var_results_dir.get()) if os.path.isdir(os.path.join(var_results_dir.get(), o))])

    # shared label widget
    lbl_project_name_txt = "Project name"
    lbl_project_name = tk.Label(req_params, text=lbl_project_name_txt, pady=2, width=1, anchor="w")
    lbl_project_name.grid(row=row_project_name, sticky='nesw')

    # if existing projects: dropdown menu
    if len(dpd_project_name_options) != 0:
        dpd_project_name_options.append("<new project>")
        dpd_project_name = OptionMenu(req_params, var_project_name, *dpd_project_name_options, command=swtich_dropdown_to_entry)
        dpd_project_name.configure(width=1)
        dpd_project_name.grid(row=row_project_name, column=1, sticky='nesw', padx=5)
        var_project_name.set(dpd_project_name_options[0])

    # if no existing projects: entry box
    else:
        ent_project_name.grid(row=row_project_name, column=1, sticky='nesw', padx=5)
        var_project_name.set("")

        # first time user will see this entry box
        if ent_project_name.cget("fg") == "grey":
            ent_project_name.insert(0, "E.g.: Tiger ID")
            ent_project_name.bind("<FocusIn>", project_name_focus_in)

# show entry box when user selected to add a new project from dropdown menu
def swtich_dropdown_to_entry(self):
    # set vars
    global var_project_name
    global ent_project_name

    # remove all project name widgets
    if self == "<new project>":
        project_name_widgets = [*req_params.grid_slaves(row_project_name, 0), *req_params.grid_slaves(row_project_name, 1)]
        for widget in project_name_widgets:
            widget.grid_forget()

        # add entry widget, label and button
        lbl_project_name_txt = "Project name"
        lbl_project_name = tk.Label(req_params, text=lbl_project_name_txt, pady=2, width=1, anchor="w")
        lbl_project_name.grid(row=row_project_name, sticky='nesw')
        var_project_name.set("")
        ent_project_name.grid(row=row_project_name, column=1, sticky='nesw', padx=5)
        ent_project_name.configure(fg="black")
        btn_project_name = Button(req_params, text="x", command=grid_project_name)
        btn_project_name.grid(row=row_project_name, column=0, sticky='e', padx=5)

# create hyperlinks (thanks marvin from GitHub) 
class HyperlinkManager:
    def __init__(self, text):
        self.text = text
        self.text.tag_config("hyper", foreground="blue", underline=1)
        self.text.tag_bind("hyper", "<Enter>", self._enter)
        self.text.tag_bind("hyper", "<Leave>", self._leave)
        self.text.tag_bind("hyper", "<Button-1>", self._click)
        self.reset()

    def reset(self):
        self.links = {}

    def add(self, action):
        tag = "hyper-%d" % len(self.links)
        self.links[tag] = action
        return "hyper", tag

    def _enter(self, event):
        self.text.config(cursor="hand2")

    def _leave(self, event):
        self.text.config(cursor="")

    def _click(self, event):
        for tag in self.text.tag_names(CURRENT):
            if tag[:6] == "hyper-":
                self.links[tag]()
                return

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

# toggle options to resume from existing training
def toggle_train_type(self):
    if var_train_type.get() == dpd_train_type_options[0]:
        # start new training
        for child in req_params.winfo_children():
            child.config(state=NORMAL)
        for child in adv_params.winfo_children():
            child.config(state=NORMAL)
        lbl_resume_checkpoint.grid_remove()
        btn_resume_checkpoint.grid_remove()
        dsp_resume_checkpoint.grid_remove()
    if var_train_type.get() == dpd_train_type_options[1]:
        # resume existing training
        for child in req_params.winfo_children():
            child.config(state=DISABLED)
        for child in adv_params.winfo_children():
            child.config(state=DISABLED)
        lbl_train_type.config(state=NORMAL)
        dpd_train_type.config(state=NORMAL)
        lbl_resume_checkpoint.grid(row=row_resume_checkpoint, sticky='nesw', pady=2)
        lbl_resume_checkpoint.config(state=NORMAL)
        btn_resume_checkpoint.grid(row=row_resume_checkpoint, column=1, sticky='nesw', padx=5)
        btn_resume_checkpoint.config(state=NORMAL)
        dsp_resume_checkpoint.config(state=NORMAL)
        var_resume_checkpoint_path.set("")

# show warning and toggle model threshold option
md_thresh_warning = True
def toggle_md_thresh():
    global md_thresh_warning
    if var_excl_detecs.get() and not md_thresh_warning:
        place_md_thresh()
    elif var_excl_detecs.get() and md_thresh_warning:
        md_thresh_warning = False
        if mb.askyesno("Warning", "It is strongly advised to not exclude detections from the model output file. "
                       "Only set the confidence threshold to a very small value if you really know what you're doing. "
                       "The model output should include just about everything that the model produces. If you,"
                       " because for some reason, want an extra-small output file, you would typically use a threshold of"
                       " 0.01 or 0.05.\n\nIf you want to use a threshold for post-processing features (visualization / "
                       "folder separation / cropping / annotation), please use the associated thresholds there.\n\nDo "
                       "you still want to exclude detections from the model output file?"):
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

# place model threshold
def place_md_thresh():    
    lbl_md_thresh.grid(row=row_md_thresh, sticky='nesw', pady=2)
    scl_md_thresh.grid(row=row_md_thresh, column=1, sticky='ew', padx=10)
    dsp_md_thresh.grid(row=row_md_thresh, column=0, sticky='e', padx=0)

# remove model threshold
def remove_md_thresh():
    lbl_md_thresh.grid_remove()
    scl_md_thresh.grid_remove()
    dsp_md_thresh.grid_remove()

# toggle separation subframe
def toggle_sep_frame():
    if var_separate_files.get():
        enable_widgets(sep_frame)
        sep_frame.configure(fg='black')
    else:
        disable_widgets(sep_frame)
        sep_frame.configure(fg='grey80')

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
    if frame.cget('text').startswith(' Step 3'):
        # trd_step only
        toggle_sep_frame()
        sep_frame.configure(relief = 'solid')

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
    if frame.cget('text').startswith(' Step 3'):
        # trd_step only
        disable_widgets(sep_frame)
        sep_frame.configure(fg='grey80')
        sep_frame.configure(relief = 'flat')
    
# check if checkpoint is present and set checkbox accordingly
def disable_chb_cont_checkpnt():
    if var_cont_checkpnt.get():
        var_cont_checkpnt.set(check_checkpnt())

# set minimum row size for all rows in a frame
def set_minsize_rows(frame):
    row_count = frame.grid_size()[1]
    for row in range(row_count):
        frame.grid_rowconfigure(row, minsize=minsize_rows)

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

# toggle hyperparameter evolution
def toggle_n_evolutions():
    mb.showwarning("Warning", "Note that evolution is generally expensive and time consuming, as the base scenario is trained hundreds of times."
                              " Be aware that it can take weeks or months to finish.")
    if var_evolve.get():
        lbl_n_generations.grid(row=row_n_generations, sticky='nesw')
        ent_n_generations.grid(row=row_n_generations, column=1, sticky='nesw', padx=5)
    else:
        lbl_n_generations.grid_forget()
        ent_n_generations.grid_forget()

# functions to delete the grey text in the entry boxes for the...
# ... checkpoint frequency
checkpoint_freq_init = True
def checkpoint_freq_focus_in(_):
    global checkpoint_freq_init
    if checkpoint_freq_init:
        ent_checkpoint_freq.delete(0, tk.END)
        ent_checkpoint_freq.config(fg='black')
    checkpoint_freq_init = False

# ... nth frame
nth_frame_init = True
def nth_frame_focus_in(_):
    global nth_frame_init
    if nth_frame_init:
        ent_nth_frame.delete(0, tk.END)
        ent_nth_frame.config(fg='black')
    nth_frame_init = False

# ... project name
project_name_init = True
def project_name_focus_in(_):
    global project_name_init
    if project_name_init:
        ent_project_name.delete(0, tk.END)
        ent_project_name.config(fg='black')
    project_name_init = False

# ... run name
run_name_init = True
def run_name_focus_in(_):
    global run_name_init
    if run_name_init:
        ent_run_name.delete(0, tk.END)
        ent_run_name.config(fg='black')
    run_name_init = False

# ... number of epochs
n_epochs_init = True
def n_epochs_focus_in(_):
    global n_epochs_init
    if n_epochs_init:
        ent_n_epochs.delete(0, tk.END)
        ent_n_epochs.config(fg='black')
    n_epochs_init = False

# ... number of layers to freeze
n_freeze_layers_init = True
def n_freeze_layers_focus_in(_):
    global n_freeze_layers_init
    if n_freeze_layers_init:
        ent_n_freeze_layers.delete(0, tk.END)
        ent_n_freeze_layers.config(fg='black')
    n_freeze_layers_init = False

# ... batch size
batch_size_init = True
def batch_size_focus_in(_):
    global batch_size_init
    if batch_size_init:
        ent_batch_size.delete(0, tk.END)
        ent_batch_size.config(fg='black')
    batch_size_init = False

# ... number of generations
n_generations_init = True
def n_generations_focus_in(_):
    global n_generations_init
    if n_generations_init:
        ent_n_generations.delete(0, tk.END)
        ent_n_generations.config(fg='black')
    n_generations_init = False

# ... image size
img_size_init = True
def img_size_focus_in(_):
    global img_size_init
    if img_size_init:
        ent_img_size.delete(0, tk.END)
        ent_img_size.config(fg='black')
    img_size_init = False

# ... annotation classes
annot_classes_init = True
def annot_classes_focus_in(_):
    global annot_classes_init
    if annot_classes_init:
        ent_annot_classes.delete(0, tk.END)
        ent_annot_classes.config(fg='black')
    annot_classes_init = False
    
# ... n dataloader workers
n_workers_init = True
def n_workers_focus_in(_):
    global n_workers_init
    if n_workers_init:
        ent_n_workers.delete(0, tk.END)
        ent_n_workers.config(fg='black')
    n_workers_init = False

##########################################
############# TKINTER WINDOW #############
##########################################

# make it look similar on different systems
if os.name == "nt": # windows
    text_font = "TkDefaultFont"
    resize_img_factor = 0.95
    text_size_adjustment_factor = 0.83
    first_level_frame_font_size = 13
    second_level_frame_font_size = 11
    label_width = 320
    widget_width = 150
    frame_width = label_width + widget_width + 50
    minsize_rows = 28
elif sys.platform == "linux" or sys.platform == "linux2": # linux
    text_font = "Times"
    resize_img_factor = 1
    text_size_adjustment_factor = 0.7
    first_level_frame_font_size = 15
    second_level_frame_font_size = 13
    label_width = 330
    widget_width = 160
    frame_width = label_width + widget_width + 50
    minsize_rows = 28
else: # macOS
    text_font = "TkDefaultFont"
    resize_img_factor = 1
    text_size_adjustment_factor = 1
    first_level_frame_font_size = 15
    second_level_frame_font_size = 13
    label_width = 320
    widget_width = 150
    frame_width = label_width + widget_width + 50
    minsize_rows = 28

# tkinter main window
root = Tk()
root.title(f"EcoAssist v{version}")
root.geometry()
root.configure(background="white")
tabControl = ttk.Notebook(root)

# prepare logo
logo_path = os.path.join(EcoAssist_files,'EcoAssist', 'imgs', 'logo.png')
logo = Image.open(logo_path)
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
deploy_tab = ttk.Frame(tabControl)
deploy_tab.columnconfigure(0, weight=1, minsize=frame_width)
deploy_tab.columnconfigure(1, weight=1, minsize=frame_width)
train_tab = ttk.Frame(tabControl)
train_tab.columnconfigure(0, weight=1, minsize=frame_width)
train_tab.columnconfigure(1, weight=1, minsize=frame_width)
annotate_tab = ttk.Frame(tabControl)
annotate_tab.columnconfigure(0, weight=1, minsize=frame_width)
annotate_tab.columnconfigure(1, weight=1, minsize=frame_width)
help_tab = ttk.Frame(tabControl)
about_tab = ttk.Frame(tabControl)
tabControl.add(deploy_tab, text='Deploy')
tabControl.add(train_tab, text='Train')
tabControl.add(annotate_tab, text='Annotate')
tabControl.add(help_tab, text='Help')
tabControl.add(about_tab, text='About')
tabControl.grid()

#### deploy tab
### first step
fst_step_txt = "Step 1: Choose folder to analyse"
row_fst_step = 1
fst_step = LabelFrame(deploy_tab, text=" " + fst_step_txt + " ", pady=2, padx=5, relief='solid', highlightthickness=5, font=100, fg='darkblue', borderwidth=2)
fst_step.configure(font=(text_font, first_level_frame_font_size, "bold"))
fst_step.grid(column=0, row=row_fst_step, columnspan=2, sticky='ew')

# choose folder
row_choose_folder = 0
var_choose_folder = StringVar()
var_choose_folder_short = StringVar()
dsp_choose_folder = Label(master=fst_step, textvariable=var_choose_folder_short)
btn_choose_folder = Button(master=fst_step, text="Browse", command=lambda: [browse_dir(var_choose_folder, var_choose_folder_short, dsp_choose_folder, 100, row_choose_folder, 1, 'w'), complete_frame(fst_step), update_frame_states()])
btn_choose_folder.grid(row=row_choose_folder, column=0, sticky='w', padx=5)

### second step
snd_step_txt = "Step 2: Run model"
row_snd_step = 2
snd_step = LabelFrame(deploy_tab, text=" " + snd_step_txt + " ", pady=2, padx=5, relief='solid', highlightthickness=5, font=100, fg='darkblue', borderwidth=2)
snd_step.configure(font=(text_font, first_level_frame_font_size, "bold"))
snd_step.grid(column=0, row=row_snd_step, sticky='nesw')
snd_step.columnconfigure(0, weight=1, minsize=label_width)
snd_step.columnconfigure(1, weight=1, minsize=widget_width)

# choose model
lbl_model_txt = "Model"
row_model = 0
lbl_model = Label(master=snd_step, text=lbl_model_txt, width=1, anchor="w")
lbl_model.grid(row=row_model, sticky='nesw', pady=2)
dpd_options_model = ["MegaDetector 5a", "MegaDetector 5b", "Custom model"]
var_model = StringVar(snd_step)
var_model.set(dpd_options_model[0])
var_model_short = StringVar()
var_model_path = StringVar()
dpd_model = OptionMenu(snd_step, var_model, *dpd_options_model, command=model_options)
dpd_model.configure(width=1)
dpd_model.grid(row=row_model, column=1, sticky='nesw', padx=5)
dsp_model = Label(master=snd_step, textvariable=var_model_short, fg='darkred')

# include subdirectories
lbl_exclude_subs_txt = "Don't process subdirectories"
row_exclude_subs = 1
lbl_exclude_subs = Label(snd_step, text=lbl_exclude_subs_txt, width=1, anchor="w")
lbl_exclude_subs.grid(row=row_exclude_subs, sticky='nesw', pady=2)
var_exclude_subs = BooleanVar()
var_exclude_subs.set(False)
chb_exclude_subs = Checkbutton(snd_step, variable=var_exclude_subs, anchor="w")
chb_exclude_subs.grid(row=row_exclude_subs, column=1, sticky='nesw', padx=5)

# limit detections
lbl_excl_detecs_txt = "Exclude detections from output file"
row_excl_detecs = 2
lbl_excl_detecs = Label(snd_step, text=lbl_excl_detecs_txt, width=1, anchor="w")
lbl_excl_detecs.grid(row=row_excl_detecs, sticky='nesw', pady=2)
var_excl_detecs = BooleanVar()
var_excl_detecs.set(False)
chb_excl_detecs = Checkbutton(snd_step, variable=var_excl_detecs, command=toggle_md_thresh, anchor="w")
chb_excl_detecs.grid(row=row_excl_detecs, column=1, sticky='nesw', padx=5)

# threshold for model deploy (not grid by deafult)
lbl_md_thresh_txt = "Confidence threshold"
row_md_thresh = 3
lbl_md_thresh = Label(snd_step, text=" ↳ " + lbl_md_thresh_txt, width=1, anchor="w")
var_md_thresh = DoubleVar()
var_md_thresh.set(0.01)
scl_md_thresh = Scale(snd_step, from_=0.005, to=1, resolution=0.005, orient=HORIZONTAL, variable=var_md_thresh, showvalue=0, width=10, length=1)
dsp_md_thresh = Label(snd_step, textvariable=var_md_thresh)
dsp_md_thresh.config(fg="darkred")

# use absolute paths
lbl_abs_paths_txt = "Use absolute paths in output file"
row_abs_path = 4
lbl_abs_paths = Label(snd_step, text=lbl_abs_paths_txt, width=1, anchor="w")
lbl_abs_paths.grid(row=row_abs_path, sticky='nesw', pady=2)
var_abs_paths = BooleanVar()
var_abs_paths.set(False)
chb_abs_paths = Checkbutton(snd_step, variable=var_abs_paths, command=abs_paths_warning, anchor="w")
chb_abs_paths.grid(row=row_abs_path, column=1, sticky='nesw', padx=5)

# process images
lbl_process_img_txt = "Process all images in the folder specified"
row_process_img = 5
lbl_process_img = Label(snd_step, text=lbl_process_img_txt, width=1, anchor="w")
lbl_process_img.grid(row=row_process_img, sticky='nesw', pady=2)
var_process_img = BooleanVar()
var_process_img.set(False)
chb_process_img = Checkbutton(snd_step, variable=var_process_img, command=toggle_img_frame, anchor="w")
chb_process_img.grid(row=row_process_img, column=1, sticky='nesw', padx=5)

## image option frame (dsiabled by default)
img_frame_txt = "Image options"
img_frame_row = 6
img_frame = LabelFrame(snd_step, text=" ↳ " + img_frame_txt + " ", pady=2, padx=5, relief='solid', highlightthickness=5, font=100, borderwidth=1, fg="grey80")
img_frame.configure(font=(text_font, second_level_frame_font_size, "bold"))
img_frame.grid(row=img_frame_row, column=0, columnspan=2, sticky = 'ew')
img_frame.columnconfigure(0, weight=1, minsize=label_width)
img_frame.columnconfigure(1, weight=1, minsize=widget_width)

# use checkpoints
lbl_use_checkpnts_txt = "Use checkpoints while running"
row_use_checkpnts = 0
lbl_use_checkpnts = Label(img_frame, text="     " + lbl_use_checkpnts_txt, pady=2, state=DISABLED, width=1, anchor="w")
lbl_use_checkpnts.grid(row=row_use_checkpnts, sticky='nesw')
var_use_checkpnts = BooleanVar()
var_use_checkpnts.set(False)
chb_use_checkpnts = Checkbutton(img_frame, variable=var_use_checkpnts, command=toggle_checkpoint_freq, state=DISABLED, anchor="w")
chb_use_checkpnts.grid(row=row_use_checkpnts, column=1, sticky='nesw', padx=5)

# checkpoint frequency
lbl_checkpoint_freq_txt = "Checkpoint frequency"
row_checkpoint_freq = 1
lbl_checkpoint_freq = tk.Label(img_frame, text="        ↳ " + lbl_checkpoint_freq_txt, pady=2, state=DISABLED, width=1, anchor="w")
lbl_checkpoint_freq.grid(row=row_checkpoint_freq, sticky='nesw')
var_checkpoint_freq = StringVar()
ent_checkpoint_freq = tk.Entry(img_frame, textvariable=var_checkpoint_freq, fg='grey', state=NORMAL, width=1)
ent_checkpoint_freq.grid(row=row_checkpoint_freq, column=1, sticky='nesw', padx=5)
ent_checkpoint_freq.insert(0, "E.g.: 500")
ent_checkpoint_freq.bind("<FocusIn>", checkpoint_freq_focus_in)
ent_checkpoint_freq.config(state=DISABLED)

# continue from checkpoint file
lbl_cont_checkpnt_txt = "Continue from last checkpoint file"
row_cont_checkpnt = 2
lbl_cont_checkpnt = Label(img_frame, text="     " + lbl_cont_checkpnt_txt, pady=2, state=DISABLED, width=1, anchor="w")
lbl_cont_checkpnt.grid(row=row_cont_checkpnt, sticky='nesw')
var_cont_checkpnt = BooleanVar()
var_cont_checkpnt.set(False)
chb_cont_checkpnt = Checkbutton(img_frame, variable=var_cont_checkpnt, state=DISABLED, command=disable_chb_cont_checkpnt, anchor="w")
chb_cont_checkpnt.grid(row=row_cont_checkpnt, column=1, sticky='nesw', padx=5)

# process videos
lbl_process_vid_txt = "Process all videos in the folder specified"
row_process_vid = 7
lbl_process_vid = Label(snd_step, text=lbl_process_vid_txt, width=1, anchor="w")
lbl_process_vid.grid(row=row_process_vid, sticky='nesw', pady=2)
var_process_vid = BooleanVar()
var_process_vid.set(False)
chb_process_vid = Checkbutton(snd_step, variable=var_process_vid, command=toggle_vid_frame, anchor="w")
chb_process_vid.grid(row=row_process_vid, column=1, sticky='nesw', padx=5)

## video option frame (disabled by default)
vid_frame_txt = "Video options"
vid_frame_row = 8
vid_frame = LabelFrame(snd_step, text=" ↳ " + vid_frame_txt + " ", pady=2, padx=5, relief='solid', highlightthickness=5, font=100, borderwidth=1, fg="grey80")
vid_frame.configure(font=(text_font, second_level_frame_font_size, "bold"))
vid_frame.grid(row=vid_frame_row, column=0, columnspan=2, sticky='ew')
vid_frame.columnconfigure(0, weight=1, minsize=label_width)
vid_frame.columnconfigure(1, weight=1, minsize=widget_width)

# dont process all frames
lbl_not_all_frames_txt = "Don't process every frame"
row_not_all_frames = 0
lbl_not_all_frames = Label(vid_frame, text="     " + lbl_not_all_frames_txt, pady=2, state=DISABLED, width=1, anchor="w")
lbl_not_all_frames.grid(row=row_not_all_frames, sticky='nesw')
var_not_all_frames = BooleanVar()
var_not_all_frames.set(False)
chb_not_all_frames = Checkbutton(vid_frame, variable=var_not_all_frames, command=toggle_nth_frame, state=DISABLED, anchor="w")
chb_not_all_frames.grid(row=row_not_all_frames, column=1, sticky='nesw', padx=5)

# process every nth frame
lbl_nth_frame_txt = "Analyse every Nth frame"
row_nth_frame = 1
lbl_nth_frame = tk.Label(vid_frame, text="        ↳ " + lbl_nth_frame_txt, pady=2, state=DISABLED, width=1, anchor="w")
lbl_nth_frame.grid(row=row_nth_frame, sticky='nesw')
var_nth_frame = StringVar()
ent_nth_frame = tk.Entry(vid_frame, textvariable=var_nth_frame, fg='grey', state=NORMAL, width=1)
ent_nth_frame.grid(row=row_nth_frame, column=1, sticky='nesw', padx=5)
ent_nth_frame.insert(0, "E.g.: 10")
ent_nth_frame.bind("<FocusIn>", nth_frame_focus_in)
ent_nth_frame.config(state=DISABLED)

# button start deploy
row_btn_start_deploy = 9
btn_start_deploy = Button(snd_step, text="Deploy model", command=start_deploy)
btn_start_deploy.grid(row=row_btn_start_deploy, column=0, columnspan=2, sticky='ew')

### third step
trd_step_txt = "Step 3: Post-processing (optional)"
trd_step_row = 2
trd_step = LabelFrame(deploy_tab, text=" " + trd_step_txt + " ", pady=2, padx=5, relief='solid', highlightthickness=5, font=100, fg='darkblue', borderwidth=2)
trd_step.configure(font=(text_font, first_level_frame_font_size, "bold"))
trd_step.grid(column=1, row=trd_step_row, sticky='nesw')
trd_step.columnconfigure(0, weight=1, minsize=label_width)
trd_step.columnconfigure(1, weight=1, minsize=widget_width)

# folder for results
lbl_output_dir_txt = "Destination folder"
row_output_dir = 0
lbl_output_dir = Label(master=trd_step, text=lbl_output_dir_txt, width=1, anchor="w")
lbl_output_dir.grid(row=row_output_dir, sticky='nesw', pady=2)
var_output_dir = StringVar()
var_output_dir.set("")
var_output_dir_short = StringVar()
dsp_output_dir = Label(master=trd_step, textvariable=var_output_dir_short, fg='darkred')
btn_output_dir = Button(master=trd_step, text="Browse", width=1, command=lambda: browse_dir(var_output_dir, var_output_dir_short, dsp_output_dir, 25, row_output_dir, 0, 'e'))
btn_output_dir.grid(row=row_output_dir, column=1, sticky='nesw', padx=5)

# separate files
lbl_separate_files_txt = "Separate files into subdirectories"
row_separate_files = 1
lbl_separate_files = Label(trd_step, text=lbl_separate_files_txt, width=1, anchor="w")
lbl_separate_files.grid(row=row_separate_files, sticky='nesw', pady=2)
var_separate_files = BooleanVar()
var_separate_files.set(False)
chb_separate_files = Checkbutton(trd_step, variable=var_separate_files, command=toggle_sep_frame, anchor="w")
chb_separate_files.grid(row=row_separate_files, column=1, sticky='nesw', padx=5)

## separation frame
sep_frame_txt = "Separation options"
sep_frame_row = 2
sep_frame = LabelFrame(trd_step, text=" ↳ " + sep_frame_txt + " ", pady=2, padx=5, relief='solid', highlightthickness=5, font=100, borderwidth=1, fg="grey80")
sep_frame.configure(font=(text_font, second_level_frame_font_size, "bold"))
sep_frame.grid(row=sep_frame_row, column=0, columnspan=2, sticky = 'ew')
sep_frame.columnconfigure(0, weight=1, minsize=label_width)
sep_frame.columnconfigure(1, weight=1, minsize=widget_width)

# # method of file placement
lbl_file_placement_txt = "Method of file placement"
row_file_placement = 0
lbl_file_placement = Label(sep_frame, text="     " + lbl_file_placement_txt, pady=2, width=1, anchor="w")
lbl_file_placement.grid(row=row_file_placement, sticky='nesw')
var_file_placement = IntVar()
var_file_placement.set(2)
rad_file_placement_move = Radiobutton(sep_frame, text="Copy", variable=var_file_placement, value=2)
rad_file_placement_move.grid(row=row_file_placement, column=1, sticky='w', padx=5)
rad_file_placement_copy = Radiobutton(sep_frame, text="Move", variable=var_file_placement, value=1)
rad_file_placement_copy.grid(row=row_file_placement, column=1, sticky='e', padx=5)

# separate per confidence
lbl_sep_conf_txt = "Sort results based on confidence"
row_sep_conf = 1
lbl_sep_conf = Label(sep_frame, text="     " + lbl_sep_conf_txt, width=1, anchor="w")
lbl_sep_conf.grid(row=row_sep_conf, sticky='nesw', pady=2)
var_sep_conf = BooleanVar()
var_sep_conf.set(False)
chb_sep_conf = Checkbutton(sep_frame, variable=var_sep_conf, anchor="w")
chb_sep_conf.grid(row=row_sep_conf, column=1, sticky='nesw', padx=5)

## visualize images
lbl_vis_files_txt = "Draw bounding boxes and confidences"
row_vis_files = 3
lbl_vis_files = Label(trd_step, text=lbl_vis_files_txt, width=1, anchor="w")
lbl_vis_files.grid(row=row_vis_files, sticky='nesw', pady=2)
var_vis_files = BooleanVar()
var_vis_files.set(False)
chb_vis_files = Checkbutton(trd_step, variable=var_vis_files, command=toggle_sep_frame, anchor="w")
chb_vis_files.grid(row=row_vis_files, column=1, sticky='nesw', padx=5)

## crop images
lbl_crp_files_txt = "Crop detections"
row_crp_files = 4
lbl_crp_files = Label(trd_step, text=lbl_crp_files_txt, width=1, anchor="w")
lbl_crp_files.grid(row=row_crp_files, sticky='nesw', pady=2)
var_crp_files = BooleanVar()
var_crp_files.set(False)
chb_crp_files = Checkbutton(trd_step, variable=var_crp_files, command=toggle_sep_frame, anchor="w")
chb_crp_files.grid(row=row_crp_files, column=1, sticky='nesw', padx=5)

# annotate images
lbl_yol_files_txt = "Create annotations in YOLO format"
row_yol_files = 5
lbl_yol_files = Label(trd_step, text=lbl_yol_files_txt, width=1, anchor="w")
lbl_yol_files.grid(row=row_yol_files, sticky='nesw', pady=2)
var_yol_files = BooleanVar()
var_yol_files.set(False)
chb_yol_files = Checkbutton(trd_step, variable=var_yol_files, command=toggle_sep_frame, anchor="w")
chb_yol_files.grid(row=row_yol_files, column=1, sticky='nesw', padx=5)

# create csv files
lbl_csv_txt = "Export results in csv files"
row_csv = 6
lbl_csv = Label(trd_step, text=lbl_csv_txt, width=1, anchor="w")
lbl_csv.grid(row=row_csv, sticky='nesw', pady=2)
var_csv = BooleanVar()
var_csv.set(False)
chb_csv = Checkbutton(trd_step, variable=var_csv, command=toggle_sep_frame, anchor="w")
chb_csv.grid(row=row_csv, column=1, sticky='nesw', padx=5)

# threshold
lbl_thresh_txt = "Confidence threshold"
row_lbl_thresh = 7
lbl_thresh = Label(trd_step, text=lbl_thresh_txt, width=1, anchor="w")
lbl_thresh.grid(row=row_lbl_thresh, sticky='nesw', pady=2)
var_thresh = DoubleVar()
var_thresh.set(0.2)
scl_thresh = Scale(trd_step, from_=0.01, to=1, resolution=0.01, orient=HORIZONTAL, variable=var_thresh, showvalue=0, width=10, length=1)
scl_thresh.grid(row=row_lbl_thresh, column=1, sticky='ew', padx=10)
dsp_thresh = Label(trd_step, textvariable=var_thresh)
dsp_thresh.config(fg="darkred")
dsp_thresh.grid(row=row_lbl_thresh, column=0, sticky='e', padx=0)

# postprocessing button
row_start_postprocess = 8
btn_start_postprocess = Button(trd_step, text="Post-process files", command=start_postprocess)
btn_start_postprocess.grid(row=row_start_postprocess, column=0, columnspan = 2, sticky='ew')

#### train tab
### required parameters
req_params_txt = "Required parameters"
req_params_row = 1
req_params = LabelFrame(train_tab, text=" " + req_params_txt + " ", pady=2, padx=5, relief='solid', highlightthickness=5, font=100, fg='darkblue', borderwidth=2)
req_params.configure(font=(text_font, first_level_frame_font_size, "bold"))
req_params.grid(column=0, row=req_params_row, sticky='nesw')
req_params.columnconfigure(0, weight=1, minsize=label_width)
req_params.columnconfigure(1, weight=1, minsize=widget_width)

# train type
lbl_train_type_txt = "Training type"
row_train_type = 0
lbl_train_type = Label(req_params, text=lbl_train_type_txt, pady=2, width=1, anchor="w")
lbl_train_type.grid(row=row_train_type, sticky='nesw', pady=2)
dpd_train_type_options = ["Start new training", "Resume existing"]
var_train_type = StringVar(req_params)
var_train_type.set(dpd_train_type_options[0])
dpd_train_type = OptionMenu(req_params, var_train_type, *dpd_train_type_options, command=toggle_train_type)
dpd_train_type.configure(width=1)
dpd_train_type.grid(row=row_train_type, column=1, sticky='nesw', padx=5)

# folder with annotated data
lbl_annotated_data_txt = "Folder with labeled data"
row_annotated_data = 1
lbl_annotated_data = Label(master=req_params, text=lbl_annotated_data_txt, width=1, anchor="w")
lbl_annotated_data.grid(row=row_annotated_data, sticky='nesw', pady=2)
var_annotated_data = StringVar()
var_annotated_data_short = StringVar()
dsp_annotated_data = Label(master=req_params, textvariable=var_annotated_data_short, fg='darkred')
btn_annotated_data = Button(master=req_params, text="Browse", width=1, command=lambda: browse_dir(var_annotated_data, var_annotated_data_short, dsp_annotated_data, 25, row_annotated_data, 0, 'e'))
btn_annotated_data.grid(row=row_annotated_data, column=1, sticky='nesw', padx=5)

# transfer learning model
lbl_learning_model_txt = "Retrain from"
row_learning_model = 2
lbl_learning_model = Label(req_params, text=lbl_learning_model_txt, pady=2, width=1, anchor="w")
lbl_learning_model.grid(row=row_learning_model, sticky='nesw', pady=2)
dpd_learning_model_options = ["MegaDetector 5a", "MegaDetector 5b", "YOLOv5 Nano", "YOLOv5 Small", "YOLOv5 Medium", "YOLOv5 Large", "YOLOv5 XLarge", "Custom model", "Scratch"]
var_learning_model = StringVar(req_params)
var_learning_model.set(dpd_learning_model_options[0])
var_learning_model_short = StringVar()
var_learning_model_path = StringVar()
var_learning_model_path.set(os.path.join(EcoAssist_files, "pretrained_models", "md_v5a.0.0.pt"))
dpd_learning_model = OptionMenu(req_params, var_learning_model, *dpd_learning_model_options, command=set_learning_model)
dpd_learning_model.configure(width=1)
dpd_learning_model.grid(row=row_learning_model, column=1, sticky='nesw', padx=5)
dsp_learning_model = Label(master=req_params, textvariable=var_learning_model_short, fg='darkred')

# model architecture
lbl_model_architecture_txt = "Model architecture"
row_model_architecture = 3
lbl_model_architecture = Label(req_params, text=lbl_model_architecture_txt, pady=2, width=1, anchor="w")
dpd_model_architecture_options = ["YOLOv5 Nano", "YOLOv5 Small", "YOLOv5 Medium", "YOLOv5 Large", "YOLOv5 XLarge", "Other config", "None"]
var_model_architecture = StringVar(req_params)
var_model_architecture.set(dpd_model_architecture_options[2])
var_model_architecture_short = StringVar()
var_model_architecture_path = StringVar()
var_model_architecture_path.set(os.path.join(EcoAssist_files, "yolov5", "models", "yolov5m.yaml"))
dpd_model_architecture = OptionMenu(req_params, var_model_architecture, *dpd_model_architecture_options, command=set_model_architecture)
dpd_model_architecture.configure(width=1)
dsp_model_architecture = Label(master=req_params, textvariable=var_model_architecture_short, fg='darkred')

# number of epochs
lbl_n_epochs_txt = "Number of epochs"
row_n_epochs = 4
lbl_n_epochs = tk.Label(req_params, text=lbl_n_epochs_txt, pady=2, width=1, anchor="w")
lbl_n_epochs.grid(row=row_n_epochs, sticky='nesw')
var_n_epochs = StringVar()
ent_n_epochs = tk.Entry(req_params, textvariable=var_n_epochs, fg='grey', width=1)
ent_n_epochs.grid(row=row_n_epochs, column=1, sticky='nesw', padx=5)
ent_n_epochs.insert(0, "E.g.: 300")
ent_n_epochs.bind("<FocusIn>", n_epochs_focus_in)

# folder for results
lbl_results_dir_txt = "Destination folder"
row_results_dir = 5
lbl_results_dir = Label(master=req_params, text=lbl_results_dir_txt, width=1, anchor="w")
lbl_results_dir.grid(row=row_results_dir, sticky='nesw', pady=2)
var_results_dir = StringVar()
var_results_dir_short = StringVar()
dsp_results_dir = Label(master=req_params, textvariable=var_results_dir_short, fg='darkred')
btn_results_dir = Button(master=req_params, text="Browse", width=1, command=lambda: [browse_dir(var_results_dir, var_results_dir_short, dsp_results_dir, 25, row_results_dir, 0, 'e'), grid_project_name()])
btn_results_dir.grid(row=row_results_dir, column=1, sticky='nesw', padx=5)

# specify resume checkpoint
lbl_resume_checkpoint_txt = "Specify resume checkpoint"
row_resume_checkpoint = 6
lbl_resume_checkpoint = Label(master=req_params, text=lbl_resume_checkpoint_txt, width=1, anchor="w")
var_resume_checkpoint = StringVar()
var_resume_checkpoint_short = StringVar()
var_resume_checkpoint_path = StringVar()
var_resume_checkpoint_path.set("")
dsp_resume_checkpoint = Label(master=req_params, textvariable=var_resume_checkpoint_short, fg='darkred')
btn_resume_checkpoint = Button(master=req_params, text="Browse", width=1, command=lambda: browse_file(var_resume_checkpoint, var_resume_checkpoint_short, var_resume_checkpoint_path, dsp_resume_checkpoint, [("Model file","*.pt")], 20, ["dummy"], row_resume_checkpoint))

# name of the project
row_project_name = 7
var_project_name = StringVar()
ent_project_name = tk.Entry(req_params, textvariable=var_project_name, fg='grey', width=1)
# the entry box, dropdown menu and button are created through grid_project_name() and swtich_dropdown_to_entry()

### advanced settings
adv_params_txt = "Advanced settings (optional)"
adv_params_row = 2
adv_params = LabelFrame(train_tab, text=" " + adv_params_txt + " ", pady=2, padx=5, relief='solid', highlightthickness=5, font=100, fg='darkblue', borderwidth=2)
adv_params.configure(font=(text_font, first_level_frame_font_size, "bold"))
adv_params.grid(column=0, row=adv_params_row, sticky='nesw')
adv_params.columnconfigure(0, weight=1, minsize=label_width)
adv_params.columnconfigure(1, weight=1, minsize=widget_width)

# proportion of validation data
lbl_val_prop_txt = "Proportion as validation data"
row_lbl_val_prop = 0
lbl_val_prop = Label(adv_params, text=lbl_val_prop_txt, width=1, anchor="w")
lbl_val_prop.grid(row=row_lbl_val_prop, sticky='nesw', pady=2)
var_val_prop = DoubleVar()
var_val_prop.set(0.1)
scl_val_prop = Scale(adv_params, from_=0.01, to=1, resolution=0.01, orient=HORIZONTAL, variable=var_val_prop, showvalue=0, width=10, length=1)
scl_val_prop.grid(row=row_lbl_val_prop, column=1, sticky='ew', padx=10)
dsp_val_prop = Label(adv_params, textvariable=var_val_prop)
dsp_val_prop.config(fg="darkred")
dsp_val_prop.grid(row=row_lbl_val_prop, column=0, sticky='e', padx=0)

# proportion of test data
lbl_test_prop_txt = "Proportion as test data"
row_lbl_test_prop = 1
lbl_test_prop = Label(adv_params, text=lbl_test_prop_txt, width=1, anchor="w")
lbl_test_prop.grid(row=row_lbl_test_prop, sticky='nesw', pady=2)
var_test_prop = DoubleVar()
var_test_prop.set(0.2)
scl_test_prop = Scale(adv_params, from_=0.000000001, to=1, resolution=0.01, orient=HORIZONTAL, variable=var_test_prop, showvalue=0, width=10, length=1) # not 0 because display needs two digits
scl_test_prop.grid(row=row_lbl_test_prop, column=1, sticky='ew', padx=10)
dsp_test_prop = Label(adv_params, textvariable=var_test_prop)
dsp_test_prop.config(fg="darkred")
dsp_test_prop.grid(row=row_lbl_test_prop, column=0, sticky='e', padx=0)

# use GPU for training
lbl_train_gpu_txt = "Search for GPU and use if available"
row_train_gpu = 2
lbl_train_gpu = Label(adv_params, text=lbl_train_gpu_txt, width=1, anchor="w")
lbl_train_gpu.grid(row=row_train_gpu, sticky='nesw', pady=2)
var_train_gpu = BooleanVar()
if platform.system() == 'Darwin': # Apple Silicon still has some issues with running on MPS 
    var_train_gpu.set(False)
else:
    var_train_gpu.set(True)
chb_train_gpu = Checkbutton(adv_params, variable=var_train_gpu, anchor = "w")
chb_train_gpu.grid(row=row_train_gpu, column=1, sticky='nesw', padx=5)

# batch size
lbl_batch_size_txt = "Batch size"
row_batch_size = 3
lbl_batch_size = tk.Label(adv_params, text=lbl_batch_size_txt + " (leave blank for auto detect maximum)", pady=2, width=1, anchor="w")
lbl_batch_size.grid(row=row_batch_size, sticky='nesw')
var_batch_size = StringVar()
ent_batch_size = tk.Entry(adv_params, textvariable=var_batch_size, fg='grey', width=1)
ent_batch_size.grid(row=row_batch_size, column=1, sticky='nesw', padx=5)
ent_batch_size.insert(0, "E.g.: 8")
ent_batch_size.bind("<FocusIn>", batch_size_focus_in)

# number of workers
lbl_n_workers_txt = "Number of workers"
row_n_workers = 4
lbl_n_workers = tk.Label(adv_params, text=lbl_n_workers_txt + " (leave blank for default 4)", pady=2, width=1, anchor="w")
lbl_n_workers.grid(row=row_n_workers, sticky='nesw')
var_n_workers = StringVar()
ent_n_workers = tk.Entry(adv_params, textvariable=var_n_workers, fg='grey', width=1)
ent_n_workers.grid(row=row_n_workers, column=1, sticky='nesw', padx=5)
ent_n_workers.insert(0, "E.g.: 2")
ent_n_workers.bind("<FocusIn>", n_workers_focus_in)

# image size
lbl_img_size_txt = "Image size"
row_img_size = 5
lbl_img_size = tk.Label(adv_params, text=lbl_img_size_txt + " (leave blank for auto selection)", pady=2, width=1, anchor="w")
lbl_img_size.grid(row=row_img_size, sticky='nesw')
var_img_size = StringVar()
ent_img_size = tk.Entry(adv_params, textvariable=var_img_size, fg='grey', width=1)
ent_img_size.grid(row=row_img_size, column=1, sticky='nesw', padx=5)
ent_img_size.insert(0, "E.g.: 1280")
ent_img_size.bind("<FocusIn>", img_size_focus_in)

# cache images
lbl_cache_imgs_txt = "Cache images for faster training"
row_cache_imgs = 6
lbl_cache_imgs = Label(adv_params, text=lbl_cache_imgs_txt, width=1, anchor="w")
lbl_cache_imgs.grid(row=row_cache_imgs, sticky='nesw', pady=2)
var_cache_imgs = BooleanVar()
var_cache_imgs.set(False)
chb_cache_imgs = Checkbutton(adv_params, variable=var_cache_imgs, anchor = "w")
chb_cache_imgs.grid(row=row_cache_imgs, column=1, sticky='nesw', padx=5)

# hyperparameters config file
lbl_hyper_file_txt = "Hyperparameter configuration file"
row_hyper_file = 7
lbl_hyper_file = Label(adv_params, text=lbl_hyper_file_txt, pady=2, width=1, anchor="w")
lbl_hyper_file.grid(row=row_hyper_file, sticky='nesw', pady=2)
dpd_hyper_file_options = ["None", "Low augmentation", "Med augmentation", "High augmentation", "Objects365 training", "VOC training", "Other"]
var_hyper_file = StringVar(adv_params)
var_hyper_file.set(dpd_hyper_file_options[0])
var_hyper_file_short = StringVar()
var_hyper_file_path = StringVar()
var_hyper_file_path.set("")
dpd_hyper_file = OptionMenu(adv_params, var_hyper_file, *dpd_hyper_file_options, command=set_hyper_file)
dpd_hyper_file.configure(width=1)
dpd_hyper_file.grid(row=row_hyper_file, column=1, sticky='nesw', padx=5)
dsp_hyper_file = Label(master=adv_params, textvariable=var_hyper_file_short, fg='darkred')

# evolve hyperparameters
lbl_evolve_txt = "Evolve hyperparameters"
row_evolve = 8
lbl_evolve = Label(adv_params, text=lbl_evolve_txt, width=1, anchor="w")
lbl_evolve.grid(row=row_evolve, sticky='nesw', pady=2)
var_evolve = BooleanVar()
var_evolve.set(False)
chb_evolve = Checkbutton(adv_params, variable=var_evolve, command=toggle_n_evolutions, anchor = "w")
chb_evolve.grid(row=row_evolve, column=1, sticky='nesw', padx=5)

# number of generations to evolve
lbl_n_generations_txt = "Number of generations"
row_n_generations = 9
lbl_n_generations = tk.Label(adv_params, text=lbl_n_generations_txt + " (leave blank for default 300)", pady=2, width=1, anchor="w")
var_n_generations = StringVar()
ent_n_generations = tk.Entry(adv_params, textvariable=var_n_generations, fg='grey', width=1)
ent_n_generations.insert(0, "E.g.: 500")
ent_n_generations.bind("<FocusIn>", n_generations_focus_in)

# name of the run
lbl_run_name_txt = "Run name"
row_run_name = 10
lbl_run_name = tk.Label(adv_params, text=lbl_run_name_txt + " (leave blank for auto iterate)", pady=2, width=1, anchor="w")
lbl_run_name.grid(row=row_run_name, sticky='nesw')
var_run_name = StringVar()
ent_run_name = tk.Entry(adv_params, textvariable=var_run_name, fg='grey', width=1)
ent_run_name.grid(row=row_run_name, column=1, sticky='nesw', padx=5)
ent_run_name.insert(0, "E.g.: Initial run")
ent_run_name.bind("<FocusIn>", run_name_focus_in)

# number of frozen layers
lbl_n_freeze_layers_txt = "Number of layers to freeze (leave blank for all)"
row_n_freeze_layers = 11
lbl_n_freeze_layers = tk.Label(adv_params, text=lbl_n_freeze_layers_txt, pady=2, width=1, anchor="w")
var_n_freeze_layers = StringVar()
ent_n_freeze_layers = tk.Entry(adv_params, textvariable=var_n_freeze_layers, fg='grey', width=1)
ent_n_freeze_layers.insert(0, "E.g.: 12")
ent_n_freeze_layers.bind("<FocusIn>", n_freeze_layers_focus_in)

# create command button
row_start_training = 5
btn_start_training = Button(train_tab, text="Start training", command=start_training)
btn_start_training.grid(row=row_start_training, column=0, sticky='ew')

### console output
train_output_txt = "Console output"
row_train_output = 0
train_output = LabelFrame(train_tab, text=" " + train_output_txt + " ", pady=2, padx=5, relief='solid', highlightthickness=5, font=100, fg='darkblue', borderwidth=2)
train_output.configure(font=(text_font, first_level_frame_font_size, "bold"))
train_output.grid(column=1, row=row_train_output, rowspan=4, sticky='nesw')
txt_train_output = Text(train_output, wrap=WORD, width=1, height=1)
txt_train_output.pack(fill="both", expand=True)
cancel_training_bool = BooleanVar()
cancel_training_bool.set(False)

# cancel button
row_cancel_training = 5
btn_cancel_training = Button(train_tab, text="Cancel training", command=cancel_training)
btn_cancel_training.grid(row=row_cancel_training, column=1, sticky='ew')
btn_cancel_training.config(state=DISABLED)

#### annotate tab
annotate_text = Text(annotate_tab, width=1, height=1, wrap=WORD) 
annotate_text.tag_config('frame', font=f'{text_font} {int(15 * text_size_adjustment_factor)} bold', foreground='darkblue', lmargin1=10, lmargin2=10) 
annotate_text.tag_config('explanation', font=f'{text_font} {int(13 * text_size_adjustment_factor)} normal', lmargin1=40, lmargin2=40)
annotate_text.tag_config('bulletpoint', font=f'{text_font} {int(13 * text_size_adjustment_factor)} normal', lmargin1=40, lmargin2=60)
hyperlink3 = HyperlinkManager(annotate_text)
line_number = 1 

# labelimg software
annotate_text.insert(END, "LabelImg software\n")
annotate_text.tag_add('frame', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
annotate_text.insert(END, "Here you can annotate your images using the open-source annotation software ")
annotate_text.insert(INSERT, "LabelImg", hyperlink3.add(partial(webbrowser.open, "https://github.com/tzutalin/labelImg")))
annotate_text.insert(END, " created by Tzutalin. This application makes it easy to visually review annotations and adjust their labels, which are required to train your own object detection model.\n\n")
annotate_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# steps
annotate_text.insert(END, "Steps\n")
annotate_text.tag_add('frame', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
annotate_text.insert(END, "1. Select a folder with images you would like to annotate using the 'Browse' button below.\n")
annotate_text.tag_add('bulletpoint', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
annotate_text.insert(END, "2. If the classes are not yet defined in a file named 'classes.txt' inside this folder, you will be asked to fill in the classes you'd like to work with. Don't worry, you can always add more classes if you need to. Removing classes is difficult though, so choose wisely.\n")
annotate_text.tag_add('bulletpoint', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
annotate_text.insert(END, "3. Click the 'Start annotation' button to open the program. It will open the images (and annotation files, if present) specified in step 1.\n")
annotate_text.tag_add('bulletpoint', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
annotate_text.insert(END, "4. Make sure LabelImg is set to save the annotations in 'YOLO' format. Right below the 'Save' button in the toolbar, check if 'YOLO' is set. If not, click the 'PascalVOC' or 'CreateML' button to switch to 'YOLO' format.\n")
annotate_text.tag_add('bulletpoint', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
annotate_text.insert(END, "5. See ")
annotate_text.insert(INSERT, "this website", hyperlink3.add(partial(webbrowser.open, "https://github.com/heartexlabs/labelImg#hotkeys")))
annotate_text.insert(END, " for hotkeys and more information.\n\n")
annotate_text.tag_add('bulletpoint', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# note
annotate_text.insert(END, "Note\n")
annotate_text.tag_add('frame', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
annotate_text.insert(END, "- After annotation, each image containing a detection will have a separate txt file with the annotation information. This txt file has the same file name as the image. That is how the software knows the two belong together. So, after annotation, you can't change the file names anymore.\n")
annotate_text.tag_add('bulletpoint', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
annotate_text.insert(END, "- A file named 'classes.txt' defines the list of class names that your YOLO label refers to. That means that you can't change the order, or remove classes. However, adding an extra class to the end of the list is possible via LabelImg itself or by manually adding a class at the bottom of the list in a text editor. In the latter case, you'll have to restart the application for it to have effect.\n")
annotate_text.tag_add('bulletpoint', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# configure annotation text
annotate_text.pack(fill="both", expand=True)
annotate_text.configure(font=(text_font, 11, "bold"), state=DISABLED)

# frame
annot_frame_txt = "Required input"
row_annot_frame = 0
annot_frame = LabelFrame(annotate_tab, text=" " + annot_frame_txt + " ", pady=2, padx=5, relief='solid', highlightthickness=5, font=100, fg='darkblue', borderwidth=2)
annot_frame.configure(font=(text_font, first_level_frame_font_size, "bold"))
annot_frame.pack(fill="x", anchor = "s", expand=False)
annot_frame.columnconfigure(0, weight=1, minsize=label_width*2)
annot_frame.columnconfigure(1, weight=1, minsize=widget_width*2)

# select folder
lbl_annot_dir_txt = "Select folder with images to annotate"
row_annot_dir = 0
lbl_annot_dir = Label(master=annot_frame, text=lbl_annot_dir_txt, width=1, anchor="w")
lbl_annot_dir.grid(row=row_annot_dir, sticky='nesw', pady=2)
var_annot_dir = StringVar()
var_annot_dir_short = StringVar()
dsp_annot_dir = Label(master=annot_frame, textvariable=var_annot_dir_short, fg='darkred')
btn_annot_dir = Button(master=annot_frame, text="Browse", width=1, command=lambda: [browse_dir(var_annot_dir, var_annot_dir_short, dsp_annot_dir, 50, row_annot_dir, 0, 'e'), grid_annot_classes()])
btn_annot_dir.grid(row=row_annot_dir, column=1, sticky='nesw', padx=5)

# provide classes
lbl_annot_classes_txt = "Provide classes (separated by commas)"
row_annot_classes = 1
lbl_annot_classes = tk.Label(annot_frame, text=lbl_annot_classes_txt, pady=2, width=1, anchor="w")
var_annot_classes = StringVar()
ent_annot_classes = tk.Entry(annot_frame, width=1, textvariable=var_annot_classes, fg='grey')
ent_annot_classes.insert(0, "E.g.: dog, cat, cow, polar bear, rat")
ent_annot_classes.bind("<FocusIn>", annot_classes_focus_in)

# button
btn_start_annot = Button(annotate_tab, text="Start annotation", command=start_annotation)
btn_start_annot.pack()

# set minsize for all rows inside labelframes...
for frame in [fst_step, snd_step, img_frame, vid_frame, trd_step, sep_frame, req_params, adv_params, annot_frame]:
    set_minsize_rows(frame)

# ... but not for the hidden rows
snd_step.grid_rowconfigure(row_md_thresh, minsize=0) # model tresh
req_params.grid_rowconfigure(row_model_architecture, minsize=0) # model architecture
adv_params.grid_rowconfigure(row_n_freeze_layers, minsize=0) # n frozen layers
adv_params.grid_rowconfigure(row_n_generations, minsize=0) # n generations

# help tab
scroll = Scrollbar(help_tab)
help_text = Text(help_tab, width=1, height=1, wrap=WORD, yscrollcommand=scroll.set) 
help_text.config(spacing1=2, spacing2=3, spacing3=2)
help_text.tag_config('intro', font=f'{text_font} {int(13 * text_size_adjustment_factor)} italic', foreground='black', lmargin1=10, lmargin2=10, underline = False) 
help_text.tag_config('tab', font=f'{text_font} {int(16 * text_size_adjustment_factor)} bold', foreground='black', lmargin1=10, lmargin2=10, underline = True) 
help_text.tag_config('frame', font=f'{text_font} {int(15 * text_size_adjustment_factor)} bold', foreground='darkblue', lmargin1=15, lmargin2=15) 
help_text.tag_config('feature', font=f'{text_font} {int(14 * text_size_adjustment_factor)} normal', foreground='black', lmargin1=20, lmargin2=20, underline = True) 
help_text.tag_config('explanation', font=f'{text_font} {int(13 * text_size_adjustment_factor)} normal', lmargin1=25, lmargin2=25)
hyperlink1 = HyperlinkManager(help_text)
line_number = 1 

# intro sentence
help_text.insert(END, "Below you can find detailed documentation for each setting. If you have any questions, feel free to contact me on ")
help_text.insert(INSERT, "petervanlunteren@hotmail.com", hyperlink1.add(partial(webbrowser.open, "mailto:petervanlunteren@hotmail.com")))
help_text.insert(END, " or raise an issue on the ")
help_text.insert(INSERT, "GitHub page", hyperlink1.add(partial(webbrowser.open, "https://github.com/PetervanLunteren/EcoAssist/issues")))
help_text.insert(END, ".\n\n")
help_text.tag_add('intro', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# deploy tab
help_text.insert(END, "DEPLOY TAB\n")
help_text.tag_add('tab', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1

# first step
help_text.insert(END, f"{fst_step_txt}\n")
help_text.tag_add('frame', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.insert(END, f"Browse\n")
help_text.insert(END, "Here you can browse for a folder which contains images and/or video\'s. The model will be deployed on this directory, as well as the post-processing analyses.\n\n")
help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# second step
help_text.insert(END, f"{snd_step_txt}\n")
help_text.tag_add('frame', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1

# model
help_text.insert(END, f"{lbl_model_txt}\n")
help_text.insert(END, "Here, you can indicate the yolov5 model that you want to deploy. If the dropdown option 'Custom model' is selected, you will be prompted to select "
                "a .pt model file. This can be a custom model trained via EcoAssist. The preloaded 'MegaDetector' models detect animals, people, and vehicles in camera "
                "trap imagery. It does not identify the animals; it just finds them. Version A and B differ only in their training data. Each model can outperform the "
                "other slightly, depending on your data. Try them both and see which one works best for you. If you really don't have a clue, just stick with the default"
                " 'MegaDetector 5a'. More info about MegaDetector models ")
help_text.insert(INSERT, "here", hyperlink1.add(partial(webbrowser.open, "https://github.com/microsoft/CameraTraps/blob/main/megadetector.md#megadetector-v50-20220615")))
help_text.insert(END, ".\n\n")
help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# exclude subs
help_text.insert(END, f"{lbl_exclude_subs_txt}\n")
help_text.insert(END, "By default, EcoAssist will recurse into subdirectories. Select this option if you want to ignore the subdirectories and process only the "
                "files directly in the chosen folder.\n\n")
help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# exclude detections
help_text.insert(END, f"{lbl_excl_detecs_txt} / {lbl_md_thresh_txt}\n")
help_text.insert(END, "This option will exclude detections from the output file. Please don't use this confidence threshold in order to set post-processing features"
                 " or third party software. The idea is that the output file contains everything that the model can find, and all processes which use this output file "
                 "will have their own ways of handling the confidence values. Once detections are excluded from the output file, there is no way of getting it back. "
                 "It is strongly advised to not exclude detections from the output file. Only set the confidence threshold to a very small value if you really know what"
                 " you're doing. If you, because for some reason, want an extra-small output file, you would typically use a threshold of 0.01 or 0.05. To adjust the "
                 "threshold value, you can drag the slider or press either sides next to the slider for a 0.005 reduction or increment. Confidence values are within the "
                 "[0.005, 1] interval.\n\n")
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
help_text.insert(END,"When processing every frame of a video, it can take a long time to finish. Here, you can specify whether you want to analyse only a selection of frames."
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

# destination folder
help_text.insert(END, f"{lbl_output_dir_txt}\n")
help_text.insert(END, "Here you can browse for a folder in which the results of the post-processing features will be placed. If nothing is selected, the folder "
                 "chosen at step one will be used as the destination folder.\n\n")
help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# separate files
help_text.insert(END, f"{lbl_separate_files_txt}\n")
help_text.insert(END, "This function divides the files into subdirectories based on their detections. Please be warned that this will be done automatically. "
                "There will not be an option to review and adjust the detections before the images will be moved. If you want that (a human in the loop), take a look at ")
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

# visualize files
help_text.insert(END, f"{lbl_vis_files_txt}\n")
help_text.insert(END, "This functionality draws boxes around the detections and prints their confidence values. This can be useful to visually check the results."
                 " Videos can't be visualized using this tool.\n\n")
help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# crop files
help_text.insert(END, f"{lbl_crp_files_txt}\n")
help_text.insert(END, "This feature will crop the detections and save them as separate images. Not applicable for videos.\n\n")
help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# create yolo annotations
help_text.insert(END, f"{lbl_yol_files_txt}\n")
help_text.insert(END, "When training your own model using machine learning using the yolov5 software, the images need to be annotated in yolo format. This feature "
                 "does that by creating individual text files for each image containing their detections, and one text file containing all the classes. If these "
                 "annotations are in the same folder as the images, you can visually review and adjust them using the Annotate tab. Not applicable to videos.\n\n")
help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# export csv files
help_text.insert(END, f"{lbl_csv_txt}\n")
help_text.insert(END, "This will translate the output files of step 2 into csv files. Can be opened in spreadsheet applications such as Excel and Numbers and imported"
                 " for further processing in R, Python, etc.\n\n")
help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# confidence threshold
help_text.insert(END, f"{lbl_md_thresh_txt}\n")
help_text.insert(END, "Detections below this value will not be post-processed. To adjust the threshold value, you can drag the slider or press either sides next to "
                 "the slider for a 0.005 reduction or increment. Confidence values are within the [0.005, 1] interval. If you set the confidence threshold too high, "
                 "you will miss some detections. On the other hand, if you set the threshold too low, you will get false positives. When choosing a threshold for your "
                 f"project, it is important to choose a threshold based on your own data. My advice is to first visualize your data ('{lbl_vis_files_txt}') with a low "
                 "threshold to get a feeling of the confidence values in your data. This will show you how sure the model is about its detections and will give you an "
                 "insight into which threshold will work best for you. If you really don't know, 0.2 is probably a conservative threshold for most projects.\n\n")
help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# train tab
help_text.insert(END, "TRAIN TAB\n")
help_text.tag_add('tab', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1

# training type
help_text.insert(END, f"{req_params_txt}\n")
help_text.tag_add('frame', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.insert(END, f"{lbl_train_type_txt}\n")
help_text.insert(END, "Here, you can specify whether you want to start a new training or resume an existing one. If you want to resume, you'll need to specify the checkpoint"
                 f" file at '{lbl_resume_checkpoint_txt}'.\n\n")
help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# folder with labelled data
help_text.insert(END, f"{lbl_annotated_data_txt}\n")
help_text.insert(END, "Browse the folder containing images and annotations in yolo format. All data should be in this folder, not in subfolders. EcoAssist will randomly partition"
                 " the data into a training, test and validation set (based on the proportions set by you). You can annotate your data using the 'Annotate' tab, or (if you"
                 f" already have a model which can detect the objects of interest) the post-processing feature '{lbl_yol_files_txt}' in the 'Deploy' tab.\n\n")
help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# retrain from
help_text.insert(END, f"{lbl_learning_model_txt}\n")
help_text.insert(END, "In machine learning, it is possible to reuse an existing model as the starting point for a new model. For example, the MegaDetector model is "
                 "excellent at detecting animals in camera trap images. We can transfer the knowledge of how an animal looks like to a new model which can, for example,"
                 " classify species. Here, you can specify which model you would like to transfer knowledge from. If your dataset is relatively small (i.e., not tens of "
                 "thousands of images), it is advised to train your own custom model using transfer learning. Besides MegaDetector 5a and b, you can choose from "
                 "five pre-trained yolov5 models (see image below). These go from small and fast to large and slow and are trained on the ")
help_text.insert(INSERT, "COCO dataset", hyperlink1.add(partial(webbrowser.open, "https://cocodataset.org/#home")))
help_text.insert(END, " consisting of more than 330,000 images of 80 classes. The larger the model, the better the results. The Nano model is the smallest and fastest and is "
                 "most suitable for mobile solutions and embedded devices. The small model is perfect for a laptop which doesn't have any GPU acceleration. The medium-sized "
                 "model provides a good balance between speed and accuracy, but you'll probably want a GPU for this. The large model is ideal for detecting small objects, and "
                 "the extra-large model is the most accurate of them all (but it takes time and quite some processing power to train and deploy). The last two models are "
                 "recommended for cloud deployments. You can also specify a custom model or choose to train from scratch, but it is usually not recommended. Only train"
                 " from scratch if you know what you are doing and have a very large dataset (i.e., around 150.000 images or more).\n\n")
help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# image of yolo models
yolo_models=Image.open(os.path.join(EcoAssist_files, "EcoAssist", "imgs", "yolo_models.png"))
yolo_models=yolo_models.resize((int(yolo_models.size[0] / 5), int(yolo_models.size[1] / 5)))
yolo_models=ImageTk.PhotoImage(yolo_models)
help_text.image_create(tk.END, image = yolo_models)
help_text.insert(END, "\n\n")
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# model architecture
help_text.insert(END, f"{lbl_model_architecture_txt}\n")
help_text.insert(END, "When training from scratch, you can specify the model architecture here. The options link to the architectures of the models depicted above.\n\n")
help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# n epochs
help_text.insert(END, f"{lbl_n_epochs_txt}\n")
help_text.insert(END, "An epoch is one cycle in which all the training data is processed once. The number of epochs required depends on the project. It is recommended to"
                 " start with 300 epochs and then check the results for overfitting. Reduce the number of epochs if the data is overfitted, and increase if not. Overfitting"
                 " is indicated by increasing validation losses. You can see this these validation losses in the 'results.png' file located in the destination folder after "
                 "completing a training. Increase the amount of data or use data augmentation to avoid overfitting. \n\n")
help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# destination folder
help_text.insert(END, f"{lbl_output_dir_txt}\n")
help_text.insert(END, "Select the folder in which you want the results to be placed.\n\n")
help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# project name
help_text.insert(END, "Project name\n")
help_text.insert(END, "Specify the name of the project. Results will be saved in the folder <destination folder>\<project name>\<run name>\.\n\n")
help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# resume checkpoint
help_text.insert(END, f"{lbl_resume_checkpoint_txt}\n")
help_text.insert(END, "If your training was interrupted and you want to resume where you left off, you can specify the resume checkpoint here. It is the last.pt file"
                 " in the weights subfolder of the training you want to resume. For example: Project_name\exp\weights\last.pt. \n\n")
help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# validation prop
help_text.insert(END, f"{adv_params_txt}\n")
help_text.tag_add('frame', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.insert(END, f"{lbl_val_prop_txt}\n")
help_text.insert(END, "Here, you can select the proportion of images which will be randomly selected to become the validation subset. Validation images are required,"
                 " so choosing 0 is not allowed. To adjust the value, you can drag the slider or press either sides next to the slider for a 0.01 reduction or increment."
                 " Values are within the [0.01, 1] interval.\n\n")
help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# test prop
help_text.insert(END, f"{lbl_test_prop_txt}\n")
help_text.insert(END, "Here, you can select the proportion of images which will be randomly selected to become the test subset. Test images are not required, so choosing"
                 " 0 is allowed. To adjust the value, you can drag the slider or press either sides next to the slider for a 0.01 reduction or increment. Values are within"
                 " the [0, 1] interval.\n\n")
help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# search for GPU
help_text.insert(END, f"{lbl_train_gpu_txt}\n")
help_text.insert(END, "If enabled, EcoAssist will check your device for any suitable GPU and use it to train on.\n\n")
help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# batch size
help_text.insert(END, f"{lbl_batch_size_txt}\n")
help_text.insert(END, "The batch size is the number of training examples used in one iteration. The larger the batch size, the more processing power you'll need. For "
                 "the best results, use the largest batch size that your hardware allows for. Leave the entry box empty to automatically check and use the maximum batch"
                 " size your device can handle. If your device has no GPU acceleration, the default is 16. Try lowering this if you run into out-of-memory errors.\n\n")
help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# number of dataloader workers
help_text.insert(END, f"{lbl_n_workers_txt}\n")
help_text.insert(END, "Usually, not all images can be loaded into your computers RAM at once. Subsets of the images are therefore loaded at every iteration. This number "
                 "indicates the maximum amount of workers being set for this dataloading task. Normally, the default of 4 should be fine for most computers, but if you run"
                 " into out-of-memory errors, it might help to lower the number of dataloaders.\n\n")
help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# image size
help_text.insert(END, f"{lbl_img_size_txt}\n")
help_text.insert(END, "Larger image sizes usually lead to better results, but take longer to process. Training on smaller images will cost less computing power. An image"
                 " that is twice as large will have 4 times as many pixels to learn from. Resizing images is therefore a crucial part of object detection. Best results are"
                 " obtained if the same image size is used as the original model you are retraining. Therefore, if you leave the image size entry box empty, EcoAssist will"
                 " take the image size of the pretrained model you selected (1280 for MegaDetector and 640 for the YOLO models). If you selected a custom model or are "
                 "training from scratch, the default is 640. \n\n")
help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# cache
help_text.insert(END, f"{lbl_cache_imgs_txt}\n")
help_text.insert(END, "This feature caches the dataset into your RAM for faster load times.\n\n")
help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# hyperparam file
help_text.insert(END, f"{lbl_hyper_file_txt}\n")
help_text.insert(END, "Here, you can select an existing or custom hyperparameter configuration file. This consists of parameters like learning rate and data augmentations"
                 f" options. It's recommened to train with default hyperparameters first ('{dpd_hyper_file_options[0]}') before trying others. A few ready-to-use options are "
                 "preloaded into EcoAsisst:\n"
                 f"  - '{dpd_hyper_file_options[0]}' to not specify any hyperparameters and use the default settings\n"
                 f"  - '{dpd_hyper_file_options[1]}' for small models like {dpd_learning_model_options[2]} and {dpd_learning_model_options[3]}\n"
                 f"  - '{dpd_hyper_file_options[2]}' for medium sized models like {dpd_learning_model_options[4]}\n"
                 f"  - '{dpd_hyper_file_options[3]}' for large models like {dpd_learning_model_options[5]}, {dpd_learning_model_options[6]} and MegaDetector\n"
                 f"  - '{dpd_hyper_file_options[4]}' when training on the ")
help_text.insert(INSERT, "Objects365 dataset", hyperlink1.add(partial(webbrowser.open, "https://paperswithcode.com/dataset/objects365")))
help_text.insert(END, "\n")
help_text.insert(END, 
                 f"  - '{dpd_hyper_file_options[5]}' for training on the ")
help_text.insert(INSERT, "VOC dataset", hyperlink1.add(partial(webbrowser.open, "http://host.robots.ox.ac.uk/pascal/VOC/")))
help_text.insert(END, "\n")
help_text.insert(END, 
                 f"  - '{dpd_hyper_file_options[6]}' to select a custom hyperparameter file\n"
                 f"Please be aware that the optimal settings are project-specific and the '{lbl_evolve_txt}' option should be used to finetune them for the best results. "
                 "Hyperparameter evolution can, however, be very time and energy consuming and therefore not always preferable. "
                 "In general, increasing augmentation hyperparameters will reduce and delay overfitting, allowing for longer trainings and higher final accuracy. YOLOv5 "
                 "applies online imagespace and colorspace augmentations to present a new and unique augmented mosaic. Images are never presented twice in the same way."
                 " You can view the effect of your augmentation policy in your train_batch*.jpg images once training starts. These images will be in your train logging "
                 "directory.\n\n")
help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# data augmentation image
data_augs=Image.open(os.path.join(EcoAssist_files, "EcoAssist", "imgs", "data_augmentations.jpg"))
data_augs=data_augs.resize((int(data_augs.size[0] / 5), int(data_augs.size[1] / 5)))
data_augs=ImageTk.PhotoImage(data_augs)
help_text.image_create(tk.END, image = data_augs)
help_text.insert(END, "\n\n")
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# evolve
help_text.insert(END, f"{lbl_evolve_txt}\n")
help_text.insert(END, "Use this feature to fine-tune the hyperparameters for maximum fitness. It will run the base training multiple times and slightly adjust the "
                 "hyperparameters to find the optimum values. The resulting hyperparameter file is the 'hyp_evolve.yaml' in your train logging directory and"
                 f" can be used for subsequent trainings. To do so, select the 'hyp_evolve.yaml' file as option under '{dpd_hyper_file_options[6]}' at '{lbl_hyper_file_txt}'. "
                 "Please note that evolution is generally expensive and time-consuming. It can take weeks or months to finish, depending on the number of generations "
                 "you select and your processing power.\n\n")
help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# n generations
help_text.insert(END, f"{lbl_n_generations_txt}\n")
help_text.insert(END, "Here, you can specify how often you want the base scenario to be trained during the evolution. A minimum of 300 generations of evolution is "
                 "recommended for best results. The default 300 is used when the entry box is left blank.\n\n")
help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# run name
help_text.insert(END, f"{lbl_run_name_txt}\n")
help_text.insert(END, "Here you can specify the name of the run. Results will be saved in the folder <destination folder>\<project name>\<run name>. If you leave this "
                 "entry box blank, it will automatically iterate new names: exp, exp2, exp3, etc.\n\n")
help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

# config help_text
help_text.pack(fill="both", expand=True)
help_text.configure(font=(text_font, 11, "bold"), state=DISABLED)
scroll.config(command=help_text.yview)

# about tab
about_scroll = Scrollbar(about_tab)
about_text = Text(about_tab, width=1, height=1, wrap=WORD, yscrollcommand=scroll.set)
about_text.config(spacing1=2, spacing2=3, spacing3=2)
about_text.tag_config('title', font=f'{text_font} {int(15 * text_size_adjustment_factor)} bold', foreground='darkblue', lmargin1=10, lmargin2=10) 
about_text.tag_config('info', font=f'{text_font} {int(13 * text_size_adjustment_factor)} normal', lmargin1=20, lmargin2=20)
about_text.tag_config('citation', font=f'{text_font} {int(13 * text_size_adjustment_factor)} normal', lmargin1=30, lmargin2=50)
hyperlink = HyperlinkManager(about_text)
text_line_number=1

# contact
about_text.insert(END, "Contact\n")
about_text.insert(END, "Please also help me to keep improving EcoAssist and let me know about any improvements, bugs, or new features so that I can keep it up-to-date. You can contact me at ")
about_text.insert(INSERT, "petervanlunteren@hotmail.com", hyperlink.add(partial(webbrowser.open, "mailto:petervanlunteren@hotmail.com")))
about_text.insert(END, " or raise an issue on the ")
about_text.insert(INSERT, "GitHub page", hyperlink.add(partial(webbrowser.open, "https://github.com/PetervanLunteren/EcoAssist/issues")))
about_text.insert(END, ".\n\n")
about_text.tag_add('title', str(text_line_number) + '.0', str(text_line_number) + '.end');text_line_number+=1
about_text.tag_add('info', str(text_line_number) + '.0', str(text_line_number) + '.end');text_line_number+=2

# ecoassist citation
about_text.insert(END, "EcoAssist citation\n")
about_text.insert(END, "If you used EcoAssist in your research, please use the following citation.\n")
about_text.insert(END, "- van Lunteren, P. (2022). EcoAssist: An application for detecting animals in camera trap images using the MegaDetector model. [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.7223363\n\n")
about_text.tag_add('title', str(text_line_number) + '.0', str(text_line_number) + '.end');text_line_number+=1
about_text.tag_add('info', str(text_line_number) + '.0', str(text_line_number) + '.end');text_line_number+=1
about_text.tag_add('citation', str(text_line_number) + '.0', str(text_line_number) + '.end');text_line_number+=2

# megadetector citation
about_text.insert(END, "MegaDetector citation\n")
about_text.insert(END, "If you used the MegaDetector model to analyse images or retrain your model, please use the following citation.\n")
about_text.insert(END, "- Beery, S., Morris, D., & Yang, S. (2019). Efficient pipeline for camera trap image review. ArXiv preprint arXiv:1907.06772.\n\n")
about_text.tag_add('title', str(text_line_number) + '.0', str(text_line_number) + '.end');text_line_number+=1
about_text.tag_add('info', str(text_line_number) + '.0', str(text_line_number) + '.end');text_line_number+=1
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
about_text.pack(fill="both", expand=True)
about_text.configure(font=(text_font, 11, "bold"), state=DISABLED)
scroll.config(command=about_text.yview)

# main function
def main():
    # initialise start screen
    enable_frame(fst_step)
    disable_frame(snd_step)
    disable_frame(trd_step)

    # run
    root.mainloop()

# executable as script
if __name__ == "__main__":
    main()
