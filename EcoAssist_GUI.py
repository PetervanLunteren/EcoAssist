# GUI to simplify camera trap image analysis with species recognition models
# https://addaxdatascience.com/ecoassist/
# Created by Peter van Lunteren
# Latest edit by Peter van Lunteren on 12 Feb 2024

# TODO: EXIF - try running new version of MegaDetector and extracting exif directly. Then write to CSV file from json. 
# TODO: ERROR HANDLING - height, width = im_to_vis.shape[:2] (line 332) AttributeError: 'NoneType' object has no attribute 'shape'. Try except and write to error to file.
# TODO: RESULTS - add dashboard feature with some graphs (map, piechart, dates, % empties, etc)
# TODO: INFO - add a messagebox when the deployment is done via advanced mode. Now it just says there were errors. Perhaps just one messagebox with extra text if there are errors or warnings. And some counts. 
# TODO: TWO CHECKPOINT FILES - if you restart from checkpoint file and again write checkpoints, there will be two checkpoint files. It should take the most recent one, instead of the first one.
# TODO: SCRIPT COMPILING - dummy start ecoassist directly after installation so all the scripts are already compiled
# TODO: ENVIRONMENTS - implement the automatic installs of env.yml files for new models
# TODO: ANNOTATION - improve annotation experience
    # - make one progress windows in stead of all separate pbars when using large jsons
    # - convert pyqt5 to pyqt6 for apple silicon so we don't need to install it via homebrew
    # - implement image progress status into main labelimg window, so you don't have two separate windows
    # - apparently you still get images in which a class is found under the annotation threshold,
    #         it should count only the images that have classes above the set annotation threshold,
    #         at this point it only checks whether it should draw an bbox or not, but still shows the image


# import packages like a very pointy half christmas tree
import os
import re
import sys
import cv2
import git
import json
import math
import time
import glob
import random
import signal
import shutil
import pickle
import platform
import requests
import tempfile
import datetime
import traceback
import subprocess
import webbrowser
import numpy as np
import PIL.ExifTags
import pandas as pd
import tkinter as tk
import customtkinter
import seaborn as sns
from tqdm import tqdm
from tkinter import *
from pathlib import Path
from subprocess import Popen
from functools import partial
from tkinter.font import Font
from GPSPhoto import gpsphoto
from CTkTable import CTkTable
import matplotlib.pyplot as plt
import xml.etree.cElementTree as ET
from PIL import ImageTk, Image, ImageFile
from RangeSlider.RangeSlider import RangeSliderH
from tkinter import filedialog, ttk, messagebox as mb
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# set versions
current_EA_version = "5.0"
corresponding_model_info_version = "1"

# set global variables
EcoAssist_files = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
ImageFile.LOAD_TRUNCATED_IMAGES = True
CLS_DIR = os.path.join(EcoAssist_files, "models", "cls")
DET_DIR = os.path.join(EcoAssist_files, "models", "det")

# colors and images
EA_blue_color = '#3B8ED0'
EA_green_color = '#96CF7A'
PIL_gradient = PIL.Image.open(os.path.join(EcoAssist_files, "EcoAssist", "imgs", "gradient.png"))
PIL_logo = PIL.Image.open(os.path.join(EcoAssist_files, "EcoAssist", "imgs", "logo_small_bg.png"))
PIL_advanc_top_banner = PIL.Image.open(os.path.join(EcoAssist_files, "EcoAssist", "imgs", "advanc_top_banner.png"))
PIL_simple_top_banner = PIL.Image.open(os.path.join(EcoAssist_files, "EcoAssist", "imgs", "simple_top_banner.png"))
PIL_checkmark = PIL.Image.open(os.path.join(EcoAssist_files, "EcoAssist", "imgs", "checkmark.png"))
PIL_dir_image = PIL.Image.open(os.path.join(EcoAssist_files, "EcoAssist", "imgs", "image-gallery.png"))
PIL_mdl_image = PIL.Image.open(os.path.join(EcoAssist_files, "EcoAssist", "imgs", "tech.png"))
PIL_spp_image = PIL.Image.open(os.path.join(EcoAssist_files, "EcoAssist", "imgs", "paw.png"))
PIL_run_image = PIL.Image.open(os.path.join(EcoAssist_files, "EcoAssist", "imgs", "shuttle.png"))

# insert pythonpath
sys.path.insert(0, os.path.join(EcoAssist_files))
sys.path.insert(0, os.path.join(EcoAssist_files, "ai4eutils"))
sys.path.insert(0, os.path.join(EcoAssist_files, "yolov5"))
sys.path.insert(0, os.path.join(EcoAssist_files, "cameratraps"))

# import modules from forked repositories
from visualise_detection.bounding_box import bounding_box as bb

# log pythonpath
print(sys.path)

# load previous settings
def load_global_vars():
    var_file = os.path.join(EcoAssist_files, "EcoAssist", "global_vars.json")
    with open(var_file, 'r') as file:
        variables = json.load(file)
    return variables
global_vars = load_global_vars()

# language settings
languages_available = ['English', 'Español']
lang_idx = global_vars["lang_idx"]
step_txt = ['Step', 'Paso']
browse_txt = ['Browse', 'Examinar']
cancel_txt = ["Cancel", "Cancelar"]
change_folder_txt = ['Change folder', '¿Cambiar carpeta']
view_results_txt = ['View results', 'Ver resultados']
custom_model_txt = ['Custom model', "Otro modelo"]
again_txt = ['Again?', '¿Otra vez?']
eg_txt = ['E.g.', 'Ejem.']
show_txt = ["Show", "Mostrar"]
new_project_txt = ["<new project>", "<nuevo proyecto>"]
warning_txt = ["Warning", "Advertencia"]
information_txt = ["Information", "Información"]
error_txt = ["Error", "Error"]
select_txt = ["Select", "Seleccionar"]
invalid_value_txt = ["Invalid value", "Valor no válido"]
none_txt = ["None", "Ninguno"]
of_txt = ["of", "de"]
suffixes_for_sim_none = [" - just show me where the animals are",
                         " - muéstrame dónde están los animales"]

#############################################
############# BACKEND FUNCTIONS #############
#############################################

# post-process files
def postprocess(src_dir, dst_dir, thresh, sep, file_placement, sep_conf, vis, crp, exp, exp_format, data_type):
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")

    # update progress window
    progress_window.update_values(process = f"{data_type}_pst", status = "load")

    # get correct json file
    if data_type == "img":
        recognition_file = os.path.join(src_dir, "image_recognition_file.json")
    else:
        recognition_file = os.path.join(src_dir, "video_recognition_file.json")

    # check if user is not in the middle of an annotation session
    if data_type == "img" and get_hitl_var_in_json(recognition_file) == "in-progress":
        if not mb.askyesno("Verification session in progress", f"Your verification session is not yet done. You can finish the session "
                                                               f"by clicking 'Continue' at '{lbl_hitl_main_txt[lang_idx]}', or just continue to post-process "
                                                               "with the results as they are now.\n\nDo you want to continue to post-process?"):
            return

    # init vars
    global cancel_var
    start_time = time.time()
    nloop = 1

    # warn user
    if data_type == "vid":
        if vis or crp:
            check_json_presence_and_warn_user(["visualize or crop", "visualizar 0 recortar"][lang_idx],
                                              ["visualizing or cropping", "visualizando o recortando"][lang_idx],
                                              ["visualization and cropping", "visualización y recorte"][lang_idx])
            vis, crp = [False] * 2

    # fetch label map
    label_map = fetch_label_map_from_json(recognition_file)
    inverted_label_map = {v: k for k, v in label_map.items()}

    # create list with colours for visualisation
    if vis:
        colors = ["fuchsia", "blue", "orange", "yellow", "green", "red", "aqua", "navy", "teal", "olive", "lime", "maroon", "purple"]
        colors = colors * 30
    
    # make sure json has relative paths
    json_paths_converted = False
    if check_json_paths(recognition_file) != "relative":
        make_json_relative(recognition_file)
        json_paths_converted = True
    
    # set cancel bool
    cancel_var = False
    
    # open json file
    with open(recognition_file) as image_recognition_file_content:
        data = json.load(image_recognition_file_content)
    n_images = len(data['images'])

    # initialise the csv files
    # csv files are always created, no matter what the user specified as export format
    # these csv files are then converted to the desired format and deleted, if required
    if exp:
        # for files
        csv_for_files = os.path.join(dst_dir, "results_files.csv")
        if not os.path.isfile(csv_for_files):
            df = pd.DataFrame(list(), columns=["absolute_path", "relative_path", "data_type", "n_detections", "max_confidence", "human_verified",
                                               'DateTimeOriginal', 'DateTime', 'DateTimeDigitized', 'Latitude', 'Longitude', 'GPSLink', 'Altitude', 'Make',
                                               'Model', 'Flash', 'ExifOffset', 'ResolutionUnit', 'YCbCrPositioning', 'XResolution', 'YResolution',
                                               'ExifVersion', 'ComponentsConfiguration', 'FlashPixVersion', 'ColorSpace', 'ExifImageWidth',
                                               'ISOSpeedRatings', 'ExifImageHeight', 'ExposureMode', 'WhiteBalance', 'SceneCaptureType',
                                               'ExposureTime', 'Software', 'Sharpness', 'Saturation', 'ReferenceBlackWhite'])
            df.to_csv(csv_for_files, encoding='utf-8', index=False)
        
        # for detections
        csv_for_detections = os.path.join(dst_dir, "results_detections.csv")
        if not os.path.isfile(csv_for_detections):
            df = pd.DataFrame(list(), columns=["absolute_path", "relative_path", "data_type", "label", "confidence", "human_verified", "bbox_left",
                                               "bbox_top", "bbox_right", "bbox_bottom", "file_height", "file_width", 'DateTimeOriginal', 'DateTime',
                                               'DateTimeDigitized', 'Latitude', 'Longitude', 'GPSLink', 'Altitude', 'Make', 'Model', 'Flash', 'ExifOffset',
                                               'ResolutionUnit', 'YCbCrPositioning', 'XResolution', 'YResolution', 'ExifVersion', 'ComponentsConfiguration',
                                               'FlashPixVersion', 'ColorSpace', 'ExifImageWidth', 'ISOSpeedRatings', 'ExifImageHeight', 'ExposureMode',
                                               'WhiteBalance', 'SceneCaptureType', 'ExposureTime', 'Software', 'Sharpness', 'Saturation', 'ReferenceBlackWhite'])
            df.to_csv(csv_for_detections, encoding='utf-8', index=False)

    # set global vars
    global postprocessing_error_log
    postprocessing_error_log = os.path.join(dst_dir, "postprocessing_error_log.txt")

    # loop through images
    for image in data['images']:

        # cancel process if required
        if cancel_var:
            break
        
        # check for failure
        if "failure" in image:
            
            # write warnings to log file
            with open(postprocessing_error_log, 'a+') as f:
                f.write(f"File '{image['file']}' was skipped by post processing features because '{image['failure']}'\n")
            f.close()

            # skip this iteration
            continue
        
        # get image info
        file = image['file']
        detections_list = image['detections']
        n_detections = len(detections_list)

        # check if it has been manually verified
        manually_checked = False
        if 'manually_checked' in image:
            if image['manually_checked']:
                manually_checked = True

        # init vars
        max_detection_conf = 0.0
        unique_labels = []
        bbox_info = []

        # open files
        if vis or crp or exp:
            if data_type == "img":
                im_to_vis = cv2.imread(os.path.join(src_dir, file))
                im_to_crop_path = os.path.join(src_dir, file)
                
                 # load old image and extract EXIF
                origImage = Image.open(os.path.join(src_dir, file))
                try:
                    exif = origImage.info['exif']
                except:
                    exif = None

                origImage.close()
            else:
                vid = cv2.VideoCapture(os.path.join(src_dir, file))

            # try to read exif data
            if exp:
                try:
                    img_for_exif = PIL.Image.open(os.path.join(src_dir, file))
                    exif_data = {
                        PIL.ExifTags.TAGS[k]: v
                        for k, v in img_for_exif._getexif().items()
                        if k in PIL.ExifTags.TAGS
                    }
                    img_for_exif.close()
                    gpsinfo = gpsphoto.getGPSData(os.path.join(src_dir, file))
                    if 'Latitude' in gpsinfo and 'Longitude' in gpsinfo:
                        gpsinfo['GPSLink'] = f"https://maps.google.com/?q={gpsinfo['Latitude']},{gpsinfo['Longitude']}"
                    exif_data = {**exif_data, **gpsinfo}
                except:
                    exif_data = None

                # check if datetime values can be found
                exif_params = []
                for param in ['DateTimeOriginal', 'DateTime', 'DateTimeDigitized', 'Latitude', 'Longitude', 'GPSLink', 'Altitude', 'Make', 'Model',
                              'Flash', 'ExifOffset', 'ResolutionUnit', 'YCbCrPositioning', 'XResolution', 'YResolution', 'ExifVersion',
                              'ComponentsConfiguration', 'FlashPixVersion', 'ColorSpace', 'ExifImageWidth', 'ISOSpeedRatings',
                              'ExifImageHeight', 'ExposureMode', 'WhiteBalance', 'SceneCaptureType', 'ExposureTime', 'Software',
                              'Sharpness', 'Saturation', 'ReferenceBlackWhite']:
                    try:
                        if param.startswith('DateTime'):
                            datetime_raw = str(exif_data[param])
                            param_value = datetime.datetime.strptime(datetime_raw, '%Y:%m:%d %H:%M:%S').strftime('%d/%m/%y %H:%M:%S')
                        else:
                            param_value = str(exif_data[param])
                    except:
                        param_value = "NA"
                    exif_params.append(param_value)

        # loop through detections
        if 'detections' in image:
            for detection in image['detections']:

                # get confidence
                conf = detection["conf"]

                # write max conf
                if manually_checked:
                    max_detection_conf = "NA"
                elif conf > max_detection_conf:
                    max_detection_conf = conf

                # if above user specified thresh
                if conf >= thresh:

                    # change conf to string for verified images
                    if manually_checked:
                        conf = "NA"

                    # get detection info
                    category = detection["category"]
                    label = label_map[category]
                    if sep:
                        unique_labels.append(label)
                        unique_labels = sorted(list(set(unique_labels)))

                    # get bbox info
                    if vis or crp or exp:
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
                        bbox_info.append([label, conf, manually_checked, left, top, right, bottom, height, width, xo, yo, w_box, h_box])

        # separate files
        if sep:
            if n_detections == 0:
                file = move_files(file, "empty", file_placement, max_detection_conf, sep_conf, dst_dir, src_dir, manually_checked)
            else:
                if len(unique_labels) > 1:
                    labels_str = "_".join(unique_labels)
                    file = move_files(file, labels_str, file_placement, max_detection_conf, sep_conf, dst_dir, src_dir, manually_checked)
                elif len(unique_labels) == 0:
                    file = move_files(file, "empty", file_placement, max_detection_conf, sep_conf, dst_dir, src_dir, manually_checked)
                else:
                    file = move_files(file, label, file_placement, max_detection_conf, sep_conf, dst_dir, src_dir, manually_checked)
        
        # collect info to append to csv files
        if exp:
            # file info
            row = pd.DataFrame([[src_dir, file, data_type, len(bbox_info), max_detection_conf, manually_checked, *exif_params]])
            row.to_csv(csv_for_files, encoding='utf-8', mode='a', index=False, header=False)

            # detections info
            rows = []
            for bbox in bbox_info:
                row = [src_dir, file, data_type, *bbox[:9], *exif_params]
                rows.append(row)
            rows = pd.DataFrame(rows)
            rows.to_csv(csv_for_detections, encoding='utf-8', mode='a', index=False, header=False)
    
        # visualize images
        if vis and len(bbox_info) > 0:
            for bbox in bbox_info:
                if manually_checked:
                    vis_label = f"{bbox[0]} (verified)"
                else:
                    vis_label = f"{bbox[0]} {round(bbox[1], 3)}"
                color = colors[int(inverted_label_map[bbox[0]])]
                bb.add(im_to_vis, *bbox[3:7], vis_label, color)
            im = os.path.join(dst_dir, file)
            Path(os.path.dirname(im)).mkdir(parents=True, exist_ok=True)
            cv2.imwrite(im, im_to_vis)

            # load new image and save exif
            if (exif != None):
                image_new = Image.open(im)
                image_new.save(im, exif=exif)
                image_new.close()
        
        # crop images
        if crp and len(bbox_info) > 0:
            counter = 1
            for bbox in bbox_info:

                # if files have been moved
                if sep:
                    im_to_crp = Image.open(os.path.join(dst_dir,file))                    
                else:
                    im_to_crp = Image.open(im_to_crop_path)
                crp_im = im_to_crp.crop((bbox[3:7]))
                im_to_crp.close()
                filename, file_extension = os.path.splitext(file)
                im_path = os.path.join(dst_dir, filename + '_crop' + str(counter) + '_' + bbox[0] + file_extension)
                Path(os.path.dirname(im_path)).mkdir(parents=True, exist_ok=True)
                crp_im.save(im_path)
                counter += 1

                 # load new image and save exif
                if (exif != None):
                    image_new = Image.open(im_path)
                    image_new.save(im_path, exif=exif)
                    image_new.close()

        # calculate stats
        elapsed_time_sep = str(datetime.timedelta(seconds=round(time.time() - start_time)))
        time_left_sep = str(datetime.timedelta(seconds=round(((time.time() - start_time) * n_images / nloop) - (time.time() - start_time))))
        progress_window.update_values(process = f"{data_type}_pst",
                                        status = "running",
                                        cur_it = nloop,
                                        tot_it = n_images,
                                        time_ela = elapsed_time_sep,
                                        time_rem = time_left_sep,
                                        cancel_func = cancel)

        nloop += 1
        root.update()

    # create summary csv
    if exp:
        csv_for_summary = os.path.join(dst_dir, "results_summary.csv")
        if os.path.exists(csv_for_summary):
            os.remove(csv_for_summary)
        det_info = pd.DataFrame(pd.read_csv(csv_for_detections))
        summary = pd.DataFrame(det_info.groupby(['label', 'data_type']).size().sort_values(ascending=False).reset_index(name='n_detections'))
        summary.to_csv(csv_for_summary, encoding='utf-8', mode='w', index=False, header=True)

    # convert csv to xlsx if required
    if exp and exp_format == dpd_options_exp_format[lang_idx][0]: # if exp_format is the first option in the dropdown menu -> XLSX
        xlsx_path = os.path.join(dst_dir, "results.xlsx")

        # check if the excel file exists, e.g. when processing both img and vid
        dfs = []
        for result_type in ['detections', 'files', 'summary']:
            csv_path = os.path.join(dst_dir, f"results_{result_type}.csv")
            if os.path.isfile(xlsx_path):

                #  if so, add new rows to existing ones
                df_xlsx = pd.read_excel(xlsx_path, sheet_name=result_type)
                df_csv = pd.read_csv(os.path.join(dst_dir, f"results_{result_type}.csv"))
                df = pd.concat([df_xlsx, df_csv], ignore_index=True)
            else:
                df = pd.read_csv(os.path.join(dst_dir, f"results_{result_type}.csv"))
            dfs.append(df)
            if os.path.isfile(csv_path):
                os.remove(csv_path)

        # overwrite rows to xlsx file
        with pd.ExcelWriter(xlsx_path, engine='openpyxl') as writer:
            for idx, result_type in enumerate(['detections', 'files', 'summary']):
                df = dfs[idx]
                if result_type in ['detections', 'files']:
                    df['DateTimeOriginal'] = pd.to_datetime(df['DateTimeOriginal'], format='%d/%m/%y %H:%M:%S')
                    df['DateTime'] = pd.to_datetime(df['DateTime'], format='%d/%m/%y %H:%M:%S')
                    df['DateTimeDigitized'] = pd.to_datetime(df['DateTimeDigitized'], format='%d/%m/%y %H:%M:%S')
                df.to_excel(writer, sheet_name=result_type, index=None, header=True)
    
    # change json paths back, if converted earlier
    if json_paths_converted:
        make_json_absolute(recognition_file)
    
    # let the user know it's done
    progress_window.update_values(process = f"{data_type}_pst", status = "done")
    root.update()

# open progress window and initiate the post-process progress window
def start_postprocess():
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")

    # save settings for next time
    write_global_vars({
        "lang_idx": lang_idx,
        "var_separate_files": var_separate_files.get(),
        "var_file_placement": var_file_placement.get(),
        "var_sep_conf": var_sep_conf.get(),
        "var_vis_files": var_vis_files.get(),
        "var_crp_files": var_crp_files.get(),
        "var_exp": var_exp.get(),
        "var_exp_format_idx": dpd_options_exp_format[lang_idx].index(var_exp_format.get()),
        "var_thresh": var_thresh.get()
    })
    
    # fix user input
    src_dir = var_choose_folder.get()
    dst_dir = var_output_dir.get()
    thresh = var_thresh.get()
    sep = var_separate_files.get()
    file_placement = var_file_placement.get()
    sep_conf = var_sep_conf.get()
    vis = var_vis_files.get()
    crp = var_crp_files.get()
    exp = var_exp.get()
    exp_format = var_exp_format.get()

    # check which json files are present
    img_json = False
    if os.path.isfile(os.path.join(src_dir, "image_recognition_file.json")):
        img_json = True
    vid_json = False
    if os.path.isfile(os.path.join(src_dir, "video_recognition_file.json")):
        vid_json = True
    if not img_json and not vid_json:
        mb.showerror(error_txt[lang_idx], ["No model output file present. Make sure you run step 2 before post-processing the files.",
                                       "No hay archivo de salida del modelo. Asegúrese de ejecutar el paso 2 antes de postprocesar"
                                       " los archivos."][lang_idx])
        return
    
    # check if destination dir is valid and set to input dir if not
    if dst_dir in ["", "/", "\\", ".", "~", ":"] or not os.path.isdir(dst_dir):
        mb.showerror(["Destination folder not set", "Carpeta de destino no establecida."][lang_idx],
                        ["Destination folder not set.\n\n You have not specified where the post-processing results should be placed or the set "
                        "folder does not exist. This is required.",
                        "Carpeta de destino no establecida. No ha especificado dónde deben colocarse los resultados del postprocesamiento o la "
                        "carpeta establecida no existe. Esto opción es obligatoria."][lang_idx])
        return

    # warn user if the original files will be overwritten with visualized files
    if os.path.normpath(dst_dir) == os.path.normpath(src_dir) and vis and not sep:
        if not mb.askyesno(["Original images will be overwritten", "Las imágenes originales se sobrescribirán."][lang_idx], 
                      [f"WARNING! The visualized images will be placed in the folder with the original data: '{src_dir}'. By doing this, you will overwrite the original images"
                      " with the visualized ones. Visualizing is permanent and cannot be undone. Are you sure you want to continue?",
                      f"ATENCIÓN. Las imágenes visualizadas se colocarán en la carpeta con los datos originales: '{src_dir}'. Al hacer esto, se sobrescribirán las imágenes "
                      "originales con las visualizadas. La visualización es permanente y no se puede deshacer. ¿Está seguro de que desea continuar?"][lang_idx]):
            return
    
    # warn user if images will be moved and visualized
    if sep and file_placement == 1 and vis:
        if not mb.askyesno(["Original images will be overwritten", "Las imágenes originales se sobrescribirán."][lang_idx], 
                      [f"WARNING! You specified to visualize the original images. Visualizing is permanent and cannot be undone. If you don't want to visualize the original "
                      f"images, please select 'Copy' as '{lbl_file_placement_txt}'. Are you sure you want to continue with the current settings?",
                      "ATENCIÓN. Ha especificado visualizar las imágenes originales. La visualización es permanente y no puede deshacerse. Si no desea visualizar las "
                      f"imágenes originales, seleccione 'Copiar' como '{lbl_file_placement_txt}'. ¿Está seguro de que desea continuar con la configuración actual?"][lang_idx]):
            return

    # initialise progress window with processes
    processes = []
    if img_json:
        processes.append("img_pst")
    if vid_json:
        processes.append("vid_pst")
    global progress_window
    progress_window = ProgressWindow(processes = processes)
    progress_window.open()

    try:
        # postprocess images
        if img_json:
            postprocess(src_dir, dst_dir, thresh, sep, file_placement, sep_conf, vis, crp, exp, exp_format, data_type = "img")

        # postprocess videos
        if vid_json and not cancel_var:
            postprocess(src_dir, dst_dir, thresh, sep, file_placement, sep_conf, vis, crp, exp, exp_format, data_type = "vid")
        
        # complete
        complete_frame(fth_step)

        # check if there are postprocessing errors written
        if os.path.isfile(postprocessing_error_log): 
            mb.showwarning(warning_txt[lang_idx], [f"One or more files failed to be analysed by the model (e.g., corrupt files) and will be skipped by "
                                                f"post-processing features. See\n\n'{postprocessing_error_log}'\n\nfor more info.",
                                                f"Uno o más archivos no han podido ser analizados por el modelo (por ejemplo, ficheros corruptos) y serán "
                                                f"omitidos por las funciones de post-procesamiento. Para más información, véase\n\n'{postprocessing_error_log}'"][lang_idx])


        # close progress window
        progress_window.close()
    
    except Exception as error:
        # log error
        print("ERROR:\n" + str(error) + "\n\nDETAILS:\n" + str(traceback.format_exc()) + "\n\n")
        
        # show error
        mb.showerror(title=error_txt[lang_idx],
                     message=["An error has occurred", "Ha ocurrido un error"][lang_idx] + " (EcoAssist v" + current_EA_version + "): '" + str(error) + "'.",
                     detail=traceback.format_exc())
        
        # close window
        progress_window.close()

# open human-in-the-loop verification windows
def open_annotation_windows(recognition_file, class_list_txt, file_list_txt, label_map):
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")

    # check if file list exists
    if not os.path.isfile(file_list_txt):
        mb.showerror(["No images to verify", "No hay imágenes para verificar"][lang_idx],
                     ["There are no images to verify with the selected criteria. Use the 'Update counts' button to see how many "
                     "images you need to verify with the selected criteria.", "No hay imágenes para verificar con los criterios "
                     "seleccionados. Utilice el botón 'Actualizar recuentos' para ver cuántas imágenes necesita verificar con "
                     "los criterios seleccionados."][lang_idx])
        return

    # check number of images to verify
    total_n_files = 0
    with open(file_list_txt) as f:
        for line in f:
            total_n_files += 1
    if total_n_files == 0:
        mb.showerror(["No images to verify", "No hay imágenes para verificar"][lang_idx],
                     ["There are no images to verify with the selected criteria. Use the 'Update counts' button to see how many "
                     "images you need to verify with the selected criteria.", "No hay imágenes para verificar con los criterios "
                     "seleccionados. Utilice el botón 'Actualizar recuentos' para ver cuántas imágenes necesita verificar con "
                     "los criterios seleccionados."][lang_idx])
        return

    # read label map from json
    label_map = fetch_label_map_from_json(recognition_file)
    inverted_label_map = {v: k for k, v in label_map.items()}

    # count n verified files and locate images that need converting
    n_verified_files = 0
    if get_hitl_var_in_json(recognition_file) != "never-started":
        init_dialog = PatienceDialog(total = total_n_files, text = ["Initializing...", "Inicializando..."][lang_idx])
        init_dialog.open()
        init_current = 1
        imgs_needing_converting = []
        with open(file_list_txt) as f:
            for line in f:
                img = line.rstrip()
                annotation = return_xml_path(img)

                # check which need converting to json
                if check_if_img_needs_converting(img):
                    imgs_needing_converting.append(img)

                # check how many are verified
                if verification_status(annotation):
                    n_verified_files += 1

                # update progress window
                init_dialog.update_progress(current = init_current, percentage = True)
                init_current += 1
        init_dialog.close()

    # track hitl progress in json
    change_hitl_var_in_json(recognition_file, "in-progress")

    # close settings window if open
    try:
        hitl_settings_window.destroy()
    except NameError:
        print("hitl_settings_window not defined -> nothing to destroy()")
        
    # init window
    hitl_progress_window = Toplevel(root)
    hitl_progress_window.title(["Manual check overview", "Verificación manual"][lang_idx])
    hitl_progress_window.geometry("+1+1")

    # explenation frame
    hitl_explenation_frame = LabelFrame(hitl_progress_window, text=[" Explanation ", " Explicación "][lang_idx],
                                            pady=2, padx=5, relief='solid', highlightthickness=5, font=100, fg=EA_blue_color)
    hitl_explenation_frame.configure(font=(text_font, 15, "bold"))
    hitl_explenation_frame.grid(column=0, row=1, columnspan=2, sticky='ew')
    hitl_explenation_frame.columnconfigure(0, weight=3, minsize=115)
    hitl_explenation_frame.columnconfigure(1, weight=1, minsize=115)

    # explenation text
    text_hitl_explenation_frame = Text(master=hitl_explenation_frame, wrap=WORD, width=1, height=15 * explanation_text_box_height_factor) 
    text_hitl_explenation_frame.grid(column=0, row=0, columnspan=5, padx=5, pady=5, sticky='ew')
    text_hitl_explenation_frame.tag_config('explanation', font=f'{text_font} {int(13 * text_size_adjustment_factor)} normal', lmargin1=10, lmargin2=10)
    text_hitl_explenation_frame.insert(END, ["This is where you do the actual verification. You'll have to make sure that all objects in all images are correctly "
                                            "labeled. That also includes classes that you did not select but are on the image by chance. If an image is verified, "
                                            "you'll have to let EcoAssist know by pressing the space bar. If all images are verified and up-to-date, you can close "
                                            "the window. EcoAssist will prompt you for the final step. You can also close the window and continue at a later moment.", 
                                            "Deberá asegurarse de que todos los objetos en todas las imágenes estén "
                                            "etiquetados correctamente. Eso también incluye clases que no seleccionaste pero que están en la imagen por casualidad. "
                                            "Si se verifica una imagen, deberá informar a EcoAssist presionando la barra espaciadora. Si todas las imágenes están "
                                            "verificadas y actualizadas, puede cerrar la ventana. EcoAssist le indicará el paso final. También puedes cerrar la "
                                            "ventana y continuar en otro momento."][lang_idx])
    text_hitl_explenation_frame.tag_add('explanation', '1.0', '1.end')

    # shortcuts frame
    hitl_shortcuts_frame = LabelFrame(hitl_progress_window, text=[" Shortcuts ", " Atajos "][lang_idx],
                                        pady=2, padx=5, relief='solid', highlightthickness=5, font=100, fg=EA_blue_color)
    hitl_shortcuts_frame.configure(font=(text_font, 15, "bold"))
    hitl_shortcuts_frame.grid(column=0, row=2, columnspan=2, sticky='ew')
    hitl_shortcuts_frame.columnconfigure(0, weight=3, minsize=115)
    hitl_shortcuts_frame.columnconfigure(1, weight=1, minsize=115)

    # shortcuts label
    shortcut_labels = [["Next image:", "Previous image:", "Create box:", "Edit box:", "Delete box:", "Verify, save, and next image:"],
                       ["Imagen siguiente:", "Imagen anterior:", "Crear cuadro:", "Editar cuadro:", "Eliminar cuadro:", "Verificar, guardar, y siguiente imagen:"]][lang_idx]
    shortcut_values = ["d", "a", "w", "s", "del", ["space", "espacio"][lang_idx]]
    for i in range(len(shortcut_labels)):
        ttk.Label(master=hitl_shortcuts_frame, text=shortcut_labels[i]).grid(column=0, row=i, columnspan=1, sticky='w')
        ttk.Label(master=hitl_shortcuts_frame, text=shortcut_values[i]).grid(column=1, row=i, columnspan=1, sticky='e')

    # numbers frame
    hitl_stats_frame = LabelFrame(hitl_progress_window, text=[" Progress ", " Progreso "][lang_idx],
                                    pady=2, padx=5, relief='solid', highlightthickness=5, font=100, fg=EA_blue_color)
    hitl_stats_frame.configure(font=(text_font, 15, "bold"))
    hitl_stats_frame.grid(column=0, row=3, columnspan=2, sticky='ew')
    hitl_stats_frame.columnconfigure(0, weight=3, minsize=115)
    hitl_stats_frame.columnconfigure(1, weight=1, minsize=115)

    # progress bar 
    hitl_progbar = ttk.Progressbar(master=hitl_stats_frame, orient='horizontal', mode='determinate', length=280)
    hitl_progbar.grid(column=0, row=0, columnspan=2, padx=5, pady=(3,0))

    # percentage done
    lbl_hitl_stats_percentage = ttk.Label(master=hitl_stats_frame, text=["Percentage done:", "Porcentaje realizado:"][lang_idx])
    lbl_hitl_stats_percentage.grid(column=0, row=1, columnspan=1, sticky='w')
    value_hitl_stats_percentage = ttk.Label(master=hitl_stats_frame, text="")
    value_hitl_stats_percentage.grid(column=1, row=1, columnspan=1, sticky='e')

    # total n images to verify
    lbl_hitl_stats_verified = ttk.Label(master=hitl_stats_frame, text=["Files verified:", "Archivos verificados:"][lang_idx])
    lbl_hitl_stats_verified.grid(column=0, row=2, columnspan=1, sticky='w')
    value_hitl_stats_verified = ttk.Label(master=hitl_stats_frame, text="")
    value_hitl_stats_verified.grid(column=1, row=2, columnspan=1, sticky='e')

    # show window
    percentage = round((n_verified_files/total_n_files)*100)
    hitl_progbar['value'] = percentage
    value_hitl_stats_percentage.configure(text = f"{percentage}%")
    value_hitl_stats_verified.configure(text = f"{n_verified_files}/{total_n_files}")
    hitl_progress_window.update_idletasks()
    
    # locate open script
    if os.name == 'nt':
        labelImg_script = os.path.join(EcoAssist_files, "EcoAssist", "label.bat")
    else:
        labelImg_script = os.path.join(EcoAssist_files, "EcoAssist", "label.command")

    # create command
    command_args = []
    command_args.append(labelImg_script)
    command_args.append(class_list_txt)
    command_args.append(file_list_txt)

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

    # read the output
    for line in p.stdout:
        print(line, end='')

        if "<EA>" in line:
            ver_diff = re.search('<EA>(.)<EA>', line).group().replace('<EA>', '')

            # adjust verification count
            if ver_diff == '+':
                n_verified_files += 1
            elif ver_diff == '-':
                n_verified_files -= 1

            # update labels
            percentage = round((n_verified_files/total_n_files)*100)
            hitl_progbar['value'] = percentage
            value_hitl_stats_percentage.configure(text = f"{percentage}%")
            value_hitl_stats_verified.configure(text = f"{n_verified_files}/{total_n_files}")

            # show window
            hitl_progress_window.update()
        
        # set save status
        try:
            hitl_progress_window.update_idletasks()
            hitl_progress_window.update()
        
        # python can throw a TclError if user closes the window because the widgets are destroyed - nothing to worry about
        except Exception as error:
            print("\nWhen closing the annotation window, there was an error. python can throw a TclError if user closes "
                                                "the window because the widgets are destroyed - nothing to worry about.")
            print("ERROR:\n" + str(error) + "\n\nDETAILS:\n" + str(traceback.format_exc()) + "\n\n")

    # close accompanying window
    hitl_progress_window.destroy()
    bind_scroll_to_deploy_canvas()

    # update frames of root
    update_frame_states()

    # check if the json has relative paths
    if check_json_paths(recognition_file) == "relative":
        json_paths_are_relative = True
    else:
        json_paths_are_relative = False

    # open patience window
    # TODO: dit moet een progresswindow worden die heen en weer gaat. Maar daar heb ik een grote json voor nodig.
    converting_patience_dialog = PatienceDialog(total = 1,
                                                text = ["Running verification...", "Verificación de funcionamiento..."][lang_idx])
    converting_patience_dialog.open()

    # check which images need converting
    imgs_needing_converting = []
    with open(file_list_txt) as f:
        for line in f:
            img = line.rstrip()
            annotation = return_xml_path(img)
            if check_if_img_needs_converting(img):
                imgs_needing_converting.append(img)
    converting_patience_dialog.update_progress(current = 1)
    converting_patience_dialog.close()

    # open json
    with open(recognition_file, "r") as image_recognition_file_content:
        n_img_in_json = len(json.load(image_recognition_file_content)['images'])

    # open patience window
    patience_dialog = PatienceDialog(total = len(imgs_needing_converting) + n_img_in_json, text = ["Checking results...", "Comprobando resultados"][lang_idx])
    patience_dialog.open()
    current = 1

    # convert
    update_json_from_img_list(imgs_needing_converting, inverted_label_map, recognition_file, patience_dialog, current)
    current += len(imgs_needing_converting)

    # open json
    with open(recognition_file, "r") as image_recognition_file_content:
        data = json.load(image_recognition_file_content)

    # check if there are images that the user first verified and then un-verified
    for image in data['images']:
        image_path = image['file']
        patience_dialog.update_progress(current = current, percentage = True)
        current += 1
        if json_paths_are_relative:
            image_path = os.path.join(os.path.dirname(recognition_file), image_path)
        if 'manually_checked' in image:
            if image['manually_checked']:
                # image has been manually checked in json ...
                xml_path = return_xml_path(image_path)
                if os.path.isfile(xml_path):
                    # ... but not anymore in xml
                    if not verification_status(xml_path):
                        # set check flag in json
                        image['manually_checked'] = False
                        # reset confidence from 1.0 to arbitrary value 
                        if 'detections' in image:
                            for detection in image['detections']:
                                detection['conf'] = 0.7
    
    # write json
    image_recognition_file_content.close()
    with open(recognition_file, "w") as json_file:
        json.dump(data, json_file, indent=1)
    image_recognition_file_content.close()
    patience_dialog.close()

    # finalise things if all images are verified
    if n_verified_files == total_n_files:
        if mb.askyesno(title=["Are you done?", "¿Ya terminaste?"][lang_idx],
                       message=["All images are verified and the 'image_recognition_file.json' is up-to-date.\n\nDo you want to close this "
                                "verification session and proceed to the final step?", "Todas las imágenes están verificadas y "
                                "'image_recognition_file.json' está actualizado.\n\n¿Quieres cerrar esta sesión de verificación"
                                " y continuar con el paso final?"][lang_idx]):
            # close window
            hitl_progress_window.destroy()
            bind_scroll_to_deploy_canvas()

            # get plot from xml files
            fig = produce_graph(file_list_txt = file_list_txt)

            # init window
            hitl_final_window = Toplevel(root)
            hitl_final_window.title("Overview")
            hitl_final_window.geometry()

            # add plot
            chart_type = FigureCanvasTkAgg(fig, hitl_final_window)
            chart_type.get_tk_widget().grid(row = 0, column = 0)

            # button frame
            hitl_final_actions_frame = LabelFrame(hitl_final_window, text=[" Do you want to export these verified images as training data? ",
                                                                           " ¿Quieres exportar estas imágenes verificadas como datos de entrenamiento? "][lang_idx],
                                                                           pady=2, padx=5, relief='solid', highlightthickness=5, font=100, fg=EA_blue_color, labelanchor = 'n')
            hitl_final_actions_frame.configure(font=(text_font, 15, "bold"))
            hitl_final_actions_frame.grid(column=0, row=3, columnspan=2, sticky='ew')
            hitl_final_actions_frame.columnconfigure(0, weight=1, minsize=115)
            hitl_final_actions_frame.columnconfigure(1, weight=1, minsize=115)

            # buttons
            btn_hitl_final_export_y = Button(master=hitl_final_actions_frame, text=["Yes - choose folder and create training data",
                                                                                    "Sí - elija la carpeta y crear datos de entrenamiento"][lang_idx], 
                                    width=1, command = lambda: [uniquify_and_move_img_and_xml_from_filelist(file_list_txt = file_list_txt, recognition_file = recognition_file, hitl_final_window = hitl_final_window),
                                                                update_frame_states()])
            btn_hitl_final_export_y.grid(row=0, column=0, rowspan=1, sticky='nesw', padx=5)

            btn_hitl_final_export_n = Button(master=hitl_final_actions_frame, text=["No - go back to the main EcoAssist window",
                                                                                    "No - regrese a la ventana principal de EcoAssist"][lang_idx], 
                                    width=1, command = lambda: [delete_temp_folder(file_list_txt),
                                                                hitl_final_window.destroy(),
                                                                change_hitl_var_in_json(recognition_file, "done"),
                                                                update_frame_states()])
            btn_hitl_final_export_n.grid(row=0, column=1, rowspan=1, sticky='nesw', padx=5)

# get the images and xmls from annotation session and store them with unique filename
def uniquify_and_move_img_and_xml_from_filelist(file_list_txt, recognition_file, hitl_final_window):
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")

    # choose destination
    dst_dir = filedialog.askdirectory()

    # ask to move or copy
    window = TextButtonWindow(["Method of file placement", "Método de colocación de archivos"][lang_idx],
                              [f"Do you want to copy or move the images to\n'{dst_dir}'?",
                              f"¿Quieres copiar o mover las imágenes a\n'{dst_dir}'?"][lang_idx],
                              [["Move", "Mover"][lang_idx], ["Copy", "Copiar"][lang_idx], ["Cancel", "Cancelar"][lang_idx]])
    user_input = window.run()
    if user_input == "Cancel" or user_input == "Cancelar":
        return
    else:
        if user_input == "Move" or user_input == "Mover":
            copy_or_move = "Move"
        if user_input == "Copy" or user_input == "Copiar":
            copy_or_move = "Copy"

    # init vars
    src_dir = os.path.normpath(var_choose_folder.get())
    
    # loop through the images
    with open(file_list_txt) as f:

        # count total number of images without loading to memory
        n_imgs = 0
        for i in f:
            n_imgs += 1
        
        # reset file index
        f.seek(0)

        # open patience window
        patience_dialog = PatienceDialog(total = n_imgs, text = ["Writing files...", "Escribir archivos..."][lang_idx])
        patience_dialog.open()
        current = 1

        # loop
        for img in f:

            # get relative path
            img_rel_path = os.path.relpath(img.rstrip(), src_dir)

            # uniquify image
            src_img = os.path.join(src_dir, img_rel_path)
            dst_img = os.path.join(dst_dir, img_rel_path)
            Path(os.path.dirname(dst_img)).mkdir(parents=True, exist_ok=True)
            if copy_or_move == "Move":
                shutil.move(src_img, dst_img)
            elif copy_or_move == "Copy":
                shutil.copy2(src_img, dst_img)

            # uniquify annotation
            ann_rel_path = os.path.splitext(img_rel_path)[0] + ".xml"
            src_ann = return_xml_path(os.path.join(src_dir, img_rel_path))
            dst_ann = os.path.join(dst_dir, ann_rel_path)
            Path(os.path.dirname(dst_ann)).mkdir(parents=True, exist_ok=True)
            shutil.move(src_ann, dst_ann)

            # update dialog
            patience_dialog.update_progress(current)
            current += 1
        f.close()
    
    # finalize
    patience_dialog.close()
    delete_temp_folder(file_list_txt)
    hitl_final_window.destroy()
    change_hitl_var_in_json(recognition_file, "done")

# get size of file in appropriate unit
def get_size(path):
    size = os.path.getsize(path)
    if size < 1024:
        return f"{size} bytes"
    elif size < pow(1024,2):
        return f"{round(size/1024, 2)} KB"
    elif size < pow(1024,3):
        return f"{round(size/(pow(1024,2)), 2)} MB"
    elif size < pow(1024,4):
        return f"{round(size/(pow(1024,3)), 2)} GB"

# check if the user is already in progress of verifying, otherwise start new session
def start_or_continue_hitl():

    # early exit if only video json
    selected_dir = var_choose_folder.get()
    path_to_image_json = os.path.join(selected_dir, "image_recognition_file.json")

    # warn user if the json file is very large
    json_size = os.path.getsize(path_to_image_json)
    if json_size > 500000:
        mb.showwarning(warning_txt[lang_idx], [f"The JSON file is very large ({get_size(path_to_image_json)}). This can cause the verification"
                                            " step to perform very slow. It will work, but you'll have to have patience. ", "El archivo "
                                            f"JSON es muy grande ({get_size(path_to_image_json)}). Esto puede hacer que el paso de verificación"
                                            " funcione muy lentamente. Funcionará, pero tendrás que tener paciencia. "][lang_idx])

    # check requirements
    check_json_presence_and_warn_user(["verify", "verificar"][lang_idx],
                                      ["verifying", "verificando"][lang_idx],
                                      ["verification", "verificación"][lang_idx])
    if not os.path.isfile(path_to_image_json):
        return

    # check hitl status
    status = get_hitl_var_in_json(path_to_image_json)

    # start first session
    if status == "never-started":
        # open window to select criteria
        open_hitl_settings_window()
    
    # continue previous session
    elif status == "in-progress":

        # read selection criteria from last time
        annotation_arguments_pkl = os.path.join(selected_dir, 'temp-folder', 'annotation_information.pkl')
        with open(annotation_arguments_pkl, 'rb') as fp:
            annotation_arguments = pickle.load(fp)
        
        # update class_txt_file from json in case user added classes last time
        class_list_txt = annotation_arguments['class_list_txt']
        label_map = fetch_label_map_from_json(os.path.join(var_choose_folder.get(), 'image_recognition_file.json'))
        if os.path.isfile(class_list_txt):
            os.remove(class_list_txt)
        with open(class_list_txt, 'a') as f:
            for k, v in label_map.items():
                f.write(f"{v}\n")
            f.close()

        # ask user 
        if not mb.askyesno(["Verification session in progress", "Sesión de verificación en curso"][lang_idx],
                            ["Do you want to continue with the previous verification session? If you press 'No', you will start a new session.", 
                            "¿Quieres continuar con la sesión de verificación anterior? Si presiona 'No', iniciará una nueva sesión."][lang_idx]):
            delete_temp_folder(annotation_arguments['file_list_txt'])
            change_hitl_var_in_json(path_to_image_json, "never-started") # if user closes window, it can start fresh next time
            open_hitl_settings_window()

        # start human in the loop process and skip selection window
        else:
            try:
                open_annotation_windows(recognition_file = annotation_arguments['recognition_file'],
                                        class_list_txt = annotation_arguments['class_list_txt'],
                                        file_list_txt = annotation_arguments['file_list_txt'],
                                        label_map = annotation_arguments['label_map'])
            except Exception as error:
                # log error
                print("ERROR:\n" + str(error) + "\n\nDETAILS:\n" + str(traceback.format_exc()) + "\n\n")
                
                # show error
                mb.showerror(title=error_txt[lang_idx],
                            message=["An error has occurred", "Ha ocurrido un error"][lang_idx] + " (EcoAssist v" + current_EA_version + "): '" + str(error) + "'.",
                            detail=traceback.format_exc())
    
    # start new session
    elif status == "done":
        if mb.askyesno(["Previous session is done", "Sesión anterior terminada."][lang_idx], ["It seems like you have completed the previous manual "
                        "verification session. Do you want to start a new session?", "Parece que has completado la sesión de verificación manual "
                        "anterior. ¿Quieres iniciar una nueva sesión?"][lang_idx]):
            open_hitl_settings_window()

# open xml and check if the data is already in the json
def check_if_img_needs_converting(img_file): 
    # open xml
    root = ET.parse(return_xml_path(img_file)).getroot()

    # read verification status
    try:
        verification_status = True if root.attrib['verified'] == 'yes' else False
    except:
        verification_status = False
    
    # read json update status
    try:
        json_update_status = True if root.attrib['json_updated'] == 'yes' else False
    except:
        json_update_status = False

    # return whether or not it needs converting to json
    if verification_status == True and json_update_status == False: 
        return True
    else:
        return False

# converts individual xml to coco
def convert_xml_to_coco(xml_path, inverted_label_map):
    # open
    tree = ET.parse(xml_path)
    root = tree.getroot()
    try:
        verification_status = True if root.attrib['verified'] == 'yes' else False
    except:
        verification_status = False
    path = root.findtext('path')
    size = root.find('size')
    im_width = int(size.findtext('width'))
    im_height = int(size.findtext('height'))

    # fetch objects
    verified_detections = []
    new_class = False
    for obj in root.findall('object'):
        name = obj.findtext('name')

        # check if new class
        if name in inverted_label_map:
            new_class = False
        else:
            new_class = True
            highest_index = 0
            for key, value in inverted_label_map.items():
                value = int(value)
                if value > highest_index:
                    highest_index = value
            inverted_label_map[name] = str(highest_index + 1)
        category = inverted_label_map[name]

        # read 
        bndbox = obj.find('bndbox')
        xmin = int(float(bndbox.findtext('xmin')))
        ymin = int(float(bndbox.findtext('ymin')))
        xmax = int(float(bndbox.findtext('xmax')))
        ymax = int(float(bndbox.findtext('ymax')))

        # convert
        w_box = round(abs(xmax - xmin) / im_width, 5)
        h_box = round(abs(ymax - ymin) / im_height, 5)
        xo = round(xmin / im_width, 5)
        yo = round(ymin / im_height, 5)
        bbox = [xo, yo, w_box, h_box]

        # compile
        verified_detection = {'category' : category,
                              'conf' : 1.0,
                              'bbox' : bbox}
        verified_detections.append(verified_detection)

    verified_image = {'file' : path,
                      'detections' : verified_detections}
    
    # return
    return [verified_image, verification_status, new_class, inverted_label_map]

# update json from list with verified images
def update_json_from_img_list(verified_images, inverted_label_map, recognition_file, patience_dialog, current): 

        # check if the json has relative paths
        if check_json_paths(recognition_file) == "relative":
            json_paths_are_relative = True
        else:
            json_paths_are_relative = False

        # open
        print(recognition_file)
        with open(recognition_file, "r") as image_recognition_file_content:
            data = json.load(image_recognition_file_content)

        # adjust
        for image in data['images']:
            image_path = image['file']
            if json_paths_are_relative:
                image_path = os.path.normpath(os.path.join(os.path.dirname(recognition_file), image_path))
            if image_path in verified_images:

                # update progress
                patience_dialog.update_progress(current = current, percentage = True)
                current += 1

                # read
                xml = return_xml_path(image_path)
                coco, verification_status, new_class, inverted_label_map = convert_xml_to_coco(xml, inverted_label_map)
                image['manually_checked'] = verification_status
                if new_class:
                    data['detection_categories'] = {v: k for k, v in inverted_label_map.items()}
                if verification_status:
                    image['detections'] = coco['detections']

                    # adjust xml file
                    tree = ET.parse(xml)
                    root = tree.getroot()
                    root.set('json_updated', 'yes')
                    indent(root)
                    tree.write(xml)
        image_recognition_file_content.close()

        # write
        print(recognition_file)
        with open(recognition_file, "w") as json_file:
            json.dump(data, json_file, indent=1)
        image_recognition_file_content.close()

# write model specific vaiables to file 
def write_model_vars(model_type="cls", new_values = None):
    # exit is no cls is selected
    if var_cls_model.get() in none_txt:
        return

    # adjust
    variables = load_model_vars(model_type)
    if new_values is not None:
        for key, value in new_values.items():
            if key in variables:
                variables[key] = value
            else:
                print(f"Warning: Variable {key} not found in the loaded model variables.")

    # write
    model_dir = var_cls_model.get() if model_type == "cls" else var_det_model.get()
    var_file = os.path.join(EcoAssist_files, "models", model_type, model_dir, "variables.json")
    with open(var_file, 'w') as file:
        json.dump(variables, file, indent=4)

# take MD json and classify detections
def classify_detections(json_fpath, data_type, simple_mode = False):
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")

    # show user it's loading
    progress_window.update_values(process = f"{data_type}_cls", status = "load")
    root.update()

    # locate script
    if os.name == 'nt':
        classify_detections_script = os.path.join(EcoAssist_files, "EcoAssist", "classification_utils", "start_class_inference.bat")
    else:
        classify_detections_script = os.path.join(EcoAssist_files, "EcoAssist", "classification_utils", "start_class_inference.command")
        
    # load model specific variables
    model_vars = load_model_vars() 
    cls_model_fname = model_vars["model_fname"]
    cls_model_type = model_vars["type"]
    cls_model_fpath = os.path.join(EcoAssist_files, "models", "cls", var_cls_model.get(), cls_model_fname)

    # get param values
    if simple_mode:
        cls_disable_GPU = False
        cls_detec_thresh = model_vars["var_cls_detec_thresh_default"]
        cls_class_thresh = model_vars["var_cls_class_thresh_default"]
        cls_animal_smooth = False
    else:
        cls_disable_GPU = var_disable_GPU.get()
        cls_detec_thresh = var_cls_detec_thresh.get() 
        cls_class_thresh = var_cls_class_thresh.get()
        cls_animal_smooth = False # var_smooth_cls_animal.get()

    # create command
    command_args = []
    command_args.append(classify_detections_script)
    command_args.append(str(cls_disable_GPU))
    command_args.append(cls_model_type)
    command_args.append(EcoAssist_files)
    command_args.append(cls_model_fpath)
    command_args.append(str(cls_detec_thresh))
    command_args.append(str(cls_class_thresh))
    command_args.append(str(cls_animal_smooth))
    command_args.append(json_fpath)
    try:
        command_args.append(temp_frame_folder)
    except NameError:
        command_args.append("None")
        pass

    # adjust command for unix OS
    if os.name != 'nt':
        command_args = "'" + "' '".join(command_args) + "'"

    # log command
    print(command_args)

    # prepare process and cancel method per OS
    if os.name == 'nt':
        # run windows command
        p = Popen(command_args,
                  stdout=subprocess.PIPE,
                  stderr=subprocess.STDOUT,
                  bufsize=1,
                  shell=True,
                  universal_newlines=True)

    else:
        # run unix command
        p = Popen(command_args,
                  stdout=subprocess.PIPE,
                  stderr=subprocess.STDOUT,
                  bufsize=1,
                  shell=True,
                  universal_newlines=True,
                  preexec_fn=os.setsid)

    # set global vars
    global subprocess_output
    subprocess_output = ""

    # calculate metrics while running
    for line in p.stdout:

        # save output if something goes wrong
        subprocess_output = subprocess_output + line
        subprocess_output = subprocess_output[-1000:]

        # log
        print(line, end='')

        # catch early exit if there are no detections that meet the requirmentents to classify
        if line.startswith("n_crops_to_classify is zero. Nothing to classify."):
            mb.showinfo(warning_txt[lang_idx], ["There are no animal detections that meet the criteria. You either "
                                                "have selected images without any animals present, or you have set "
                                                "your detection confidence threshold to high.", "No hay detecciones"
                                                " de animales que cumplan los criterios. O bien ha seleccionado "
                                                "imágenes sin presencia de animales, o bien ha establecido el umbral"
                                                " de confianza de detección en alto."][lang_idx])
            elapsed_time = "00:00",
            time_left = "00:00",
            current_im = "0",
            total_im = "0",
            processing_speed = "0it/s",
            percentage = "100",
            GPU_param = "Unknown",
            data_type = data_type,
            break

        # catch smoothening info lines
        if "<EA>" in line:
            smooth_output_line = re.search('<EA>(.+)<EA>', line).group().replace('<EA>', '')
            smooth_output_file = os.path.join(os.path.dirname(json_fpath), "smooth-output.txt")
            with open(smooth_output_file, 'a+') as f:
                f.write(f"{smooth_output_line}\n")
            f.close()

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

            # print stats
            progress_window.update_values(process = f"{data_type}_cls",
                                            status = "running",
                                            cur_it = int(current_im),
                                            tot_it = int(total_im),
                                            time_ela = elapsed_time,
                                            time_rem = time_left,
                                            speed = processing_speed,
                                            hware = GPU_param,
                                            cancel_func = lambda: cancel_subprocess(p))
        root.update()

    # process is done
    progress_window.update_values(process = f"{data_type}_cls",
                                       status = "done",
                                       time_ela = elapsed_time,
                                       speed = processing_speed)

    root.update()

# quit popen process
def cancel_subprocess(process):
    global cancel_deploy_model_pressed
    global btn_start_deploy
    global sim_run_btn
    if os.name == 'nt':
        Popen(f"TASKKILL /F /PID {process.pid} /T")
    else:
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
    btn_start_deploy.configure(state=NORMAL)
    sim_run_btn.configure(state=NORMAL)
    cancel_deploy_model_pressed = True
    progress_window.close()

# delpoy model and create json output files 
def deploy_model(path_to_image_folder, selected_options, data_type, simple_mode = False):
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")
    
    # display loading window
    progress_window.update_values(process = f"{data_type}_det", status = "load")

    # prepare variables
    chosen_folder = str(Path(path_to_image_folder))
    run_detector_batch_py = os.path.join(EcoAssist_files, "cameratraps", "detection", "run_detector_batch.py")
    image_recognition_file = os.path.join(chosen_folder, "image_recognition_file.json")
    process_video_py = os.path.join(EcoAssist_files, "cameratraps", "detection", "process_video.py")
    video_recognition_file = "--output_json_file=" + os.path.join(chosen_folder, "video_recognition_file.json")
    GPU_param = "Unknown"

    # select model based on user input via dropdown menu, or take MDv5a for simple mode 
    custom_model_bool = False
    if simple_mode:
        det_model_fpath = os.path.join(DET_DIR, "MegaDetector 5a", "md_v5a.0.0.pt")
        switch_yolov5_git_to("old models")
    elif var_det_model.get() != dpd_options_model[lang_idx][-1]: # if not chosen the last option, which is "custom model"
        det_model_fname = load_model_vars("det")["model_fname"]
        det_model_fpath = os.path.join(DET_DIR, var_det_model.get(), det_model_fname)
        switch_yolov5_git_to("old models")
    else:
        # set model file
        det_model_fpath = var_det_model_path.get()
        custom_model_bool = True

        # set yolov5 git to accommodate new models (checkout depending on how you retrain MD)
        switch_yolov5_git_to("new models") 
        
        # extract classes
        label_map = extract_label_map_from_model(det_model_fpath)

        # write labelmap to separate json
        json_object = json.dumps(label_map, indent=1)
        native_model_classes_json_file = os.path.join(chosen_folder, "native_model_classes.json")
        with open(native_model_classes_json_file, "w") as outfile:
            outfile.write(json_object)
        
        # add argument to command call
        selected_options.append("--class_mapping_filename=" + native_model_classes_json_file)

    # create commands for Windows
    if os.name == 'nt':
        if selected_options == []:
            img_command = [sys.executable, run_detector_batch_py, det_model_fpath, chosen_folder, image_recognition_file]
            vid_command = [sys.executable, process_video_py, video_recognition_file, det_model_fpath, chosen_folder]
        else:
            img_command = [sys.executable, run_detector_batch_py, det_model_fpath, *selected_options, chosen_folder, image_recognition_file]
            vid_command = [sys.executable, process_video_py, *selected_options, video_recognition_file, det_model_fpath, chosen_folder]

     # create command for MacOS and Linux
    else:
        if selected_options == []:
            img_command = [f"'{sys.executable}' '{run_detector_batch_py}' '{det_model_fpath}' '{chosen_folder}' '{image_recognition_file}'"]
            vid_command = [f"'{sys.executable}' '{process_video_py}' '{video_recognition_file}' '{det_model_fpath}' '{chosen_folder}'"]
        else:
            selected_options = "' '".join(selected_options)
            img_command = [f"'{sys.executable}' '{run_detector_batch_py}' '{det_model_fpath}' '{selected_options}' '{chosen_folder}' '{image_recognition_file}'"]
            vid_command = [f"'{sys.executable}' '{process_video_py}' '{selected_options}' '{video_recognition_file}' '{det_model_fpath}' '{chosen_folder}'"]

    # pick one command
    if data_type == "img":
        command = img_command
    else:
        command = vid_command

    # if user specified to disable GPU, prepend and set system variable
    if var_disable_GPU.get() and not simple_mode:
        if os.name == 'nt': # windows
            command[:0] = ['set', 'CUDA_VISIBLE_DEVICES=""', '&']
        elif platform.system() == 'Darwin': # macos
            mb.showwarning(warning_txt[lang_idx],
                           ["Disabling GPU processing is currently only supported for CUDA devices on Linux and Windows "
                            "machines, not on macOS. Proceeding without GPU disabled.", "Deshabilitar el procesamiento de "
                            "la GPU actualmente sólo es compatible con dispositivos CUDA en máquinas Linux y Windows, no en"
                            " macOS. Proceder sin GPU desactivada."][lang_idx])
            var_disable_GPU.set(False)
        else: # linux
            command = "CUDA_VISIBLE_DEVICES='' " + command

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

    else:
        # run unix command
        p = Popen(command,
                  stdout=subprocess.PIPE,
                  stderr=subprocess.STDOUT,
                  bufsize=1,
                  shell=True,
                  universal_newlines=True,
                  preexec_fn=os.setsid)
    
    # set global vars
    global cancel_deploy_model_pressed
    cancel_deploy_model_pressed = False
    global subprocess_output
    subprocess_output = ""
    previous_processed_img = ["There is no previously processed image. The problematic character is in the first image to analyse.",
                              "No hay ninguna imagen previamente procesada. El personaje problemático está en la primera imagen a analizar."][lang_idx]

    # read output
    for line in p.stdout:
        
        # save output if something goes wrong
        subprocess_output = subprocess_output + line
        subprocess_output = subprocess_output[-1000:]

        # log
        print(line, end='')
        
        # catch model errors
        if line.startswith("No image files found"):
            mb.showerror(["No images found", "No se han encontrado imágenes"][lang_idx],
                        [f"There are no images found in '{chosen_folder}'. \n\nAre you sure you specified the correct folder?"
                        f" If the files are in subdirectories, make sure you don't tick '{lbl_exclude_subs_txt[lang_idx]}'.",
                        f"No se han encontrado imágenes en '{chosen_folder}'. \n\n¿Está seguro de haber especificado la carpeta correcta?"][lang_idx])
            return
        if line.startswith("No videos found"):
            mb.showerror(["No videos found", "No se han encontrado vídeos"][lang_idx],
                        line + [f"\n\nAre you sure you specified the correct folder? If the files are in subdirectories, make sure you don't tick '{lbl_exclude_subs_txt[lang_idx]}'.",
                                "\n\n¿Está seguro de haber especificado la carpeta correcta?"][lang_idx])
            return
        if line.startswith("No frames extracted"):
            mb.showerror(["Could not extract frames", "No se pueden extraer fotogramas"][lang_idx],
                        line + ["\n\nConverting the videos to .mp4 might fix the issue.",
                                "\n\nConvertir los vídeos a .mp4 podría solucionar el problema."][lang_idx])
            return
        if line.startswith("UnicodeEncodeError:"):
            mb.showerror("Unparsable special character",
                         [f"{line}\n\nThere seems to be a special character in a filename that cannot be parsed. Unfortunately, it's not"
                          " possible to point you to the problematic file directly, but I can tell you that the last successfully analysed"
                          f" image was\n\n{previous_processed_img}\n\nThe problematic character should be in the file or folder name of "
                          "the next image, alphabetically. Please remove any special charachters from the path and try again.", 
                          f"{line}\n\nParece que hay un carácter especial en un nombre de archivo que no se puede analizar. Lamentablemente,"
                          " no es posible indicarle directamente el archivo problemático, pero puedo decirle que la última imagen analizada "
                          f"con éxito fue\n\n{previous_processed_img}\n\nEl carácter problemático debe estar en el nombre del archivo o "
                          "carpeta de la siguiente imagen, alfabéticamente. Elimine los caracteres especiales de la ruta e inténtelo de "
                          "nuevo."][lang_idx])
            return
        if line.startswith("Processing image "):
            previous_processed_img = line.replace("Processing image ", "")

        # write errors to log file
        if "Exception:" in line:
            with open(model_error_log, 'a+') as f:
                f.write(f"{line}\n")
            f.close()

        # write warnings to log file
        if "Warning:" in line:
            if not "could not determine MegaDetector version" in line \
                and not "no metadata for unknown detector version" in line \
                and not "using user-supplied image size" in line:
                with open(model_warning_log, 'a+') as f:
                    f.write(f"{line}\n")
                f.close()
        
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

            # show progress
            progress_window.update_values(process = f"{data_type}_det",
                                            status = "running",
                                            cur_it = int(current_im),
                                            tot_it = int(total_im),
                                            time_ela = elapsed_time,
                                            time_rem = time_left,
                                            speed = processing_speed,
                                            hware = GPU_param,
                                            cancel_func = lambda: cancel_subprocess(p))
        root.update()
    
    # process is done
    progress_window.update_values(process = f"{data_type}_det", status = "done")
    root.update()
    
    # create ecoassist metadata
    ecoassist_metadata = {"ecoassist_metadata" : {"version" : current_EA_version,
                                                  "custom_model" : custom_model_bool,
                                                  "custom_model_info" : {}}}
    if custom_model_bool:
        ecoassist_metadata["ecoassist_metadata"]["custom_model_info"] = {"model_name" : os.path.basename(os.path.normpath(det_model_fpath)),
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
    
    # classify detections if specified by user
    if not cancel_deploy_model_pressed:
        if var_cls_model.get() not in none_txt:
            if data_type == "img":
                classify_detections(os.path.join(chosen_folder, "image_recognition_file.json"), data_type, simple_mode = simple_mode)
            else:
                classify_detections(os.path.join(chosen_folder, "video_recognition_file.json"), data_type, simple_mode = simple_mode)

    # remove frames.json file
    frames_video_recognition_file = os.path.join(chosen_folder, "video_recognition_file.frames.json")
    if os.path.isfile(frames_video_recognition_file):
        os.remove(frames_video_recognition_file)

# pop up window showing the user that an EcoAssist update is required for a particular model
def show_update_info(model_vars, model_name):

    # create window
    su_root = customtkinter.CTkToplevel(root)
    su_root.title("Update required")
    su_root.columnconfigure(0, weight=1, minsize=300)
    su_root.columnconfigure(1, weight=1, minsize=300)
    lbl1 = customtkinter.CTkLabel(su_root, text=f"Update required for model {model_name}", font = main_label_font)
    lbl1.grid(row=0, column=0, padx=PADX, pady=(PADY, PADY/2), columnspan = 2, sticky="nsew")
    lbl2 = customtkinter.CTkLabel(su_root, text=f"Minimum EcoAssist version required is v{model_vars['min_version']}, while your current version is v{current_EA_version}.")
    lbl2.grid(row=1, column=0, padx=PADX, pady=(0, PADY), columnspan = 2, sticky="nsew")

    # define functions
    def close():
        su_root.destroy()
    def read_more():
        webbrowser.open("https://addaxdatascience.com/ecoassist/")
        su_root.destroy()

    # buttons frame
    btns_frm = customtkinter.CTkFrame(master=su_root)
    btns_frm.columnconfigure(0, weight=1, minsize=10)
    btns_frm.columnconfigure(1, weight=1, minsize=10)
    btns_frm.grid(row=5, column=0, padx=PADX, pady=(0, PADY), columnspan = 2,sticky="nswe")
    close_btn = customtkinter.CTkButton(btns_frm, text="Cancel", command=close)
    close_btn.grid(row=2, column=0, padx=PADX, pady=PADY, sticky="nswe")
    lmore_btn = customtkinter.CTkButton(btns_frm, text="Update", command=read_more)
    lmore_btn.grid(row=2, column=1, padx=(0, PADX), pady=PADY, sticky="nwse")

# pop up window showing the user that a particular model needs downloading
def model_needs_downloading(model_vars, model_type):
    model_name = var_cls_model.get() if model_type == "cls" else var_det_model.get()
    if model_name not in none_txt:
        model_fpath = os.path.join(EcoAssist_files, "models", model_type, model_name, load_model_vars(model_type)["model_fname"])
        if os.path.isfile(model_fpath):
            # the model file is already present
            return [False, ""]
        else:
            # the model is not present yet
            min_version = model_vars["min_version"]

            # let's check if the model works with the current EA version
            if needs_EA_update(min_version):
                show_update_info(model_vars, model_name)
                return [None, ""]
            else:
                return [True, os.path.dirname(model_fpath)]
    else:
        # user selected none
        return [False, ""]

# open progress window and initiate the model deployment
def start_deploy(simple_mode = False):
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")

    # check which processes need to be listed on the progress window
    if simple_mode:
        processes = ["img_det"]
        if var_cls_model.get() not in none_txt:
            processes.append("img_cls")
        processes.append("img_pst")
    else:
        processes = []
        if var_process_img.get():
            processes.append("img_det")
            if var_cls_model.get() not in none_txt:
                processes.append("img_cls")
        if var_process_vid.get():
            processes.append("vid_det")
            if var_cls_model.get() not in none_txt:
                processes.append("vid_cls")

    # redicrect warnings and error to log files
    chosen_folder = var_choose_folder.get()
    global model_error_log
    model_error_log = os.path.join(chosen_folder, "model_error_log.txt")
    global model_warning_log
    model_warning_log = os.path.join(chosen_folder, "model_warning_log.txt")

    # set global variable
    temp_frame_folder_created = False

    # make sure user doesn't press the button twice
    btn_start_deploy.configure(state=DISABLED)
    sim_run_btn.configure(state=DISABLED)
    root.update()

    # check if models need to be downloaded
    types_to_check = ["cls"] if simple_mode else ["cls", "det"]
    # no need to check the selected detection model for simple mode, because it will take MD5a which is installed by default
    for model_type in types_to_check:
        model_vars = load_model_vars(model_type = model_type)
        if model_vars == {}: # if selected model is None
            continue
        bool, dirpath = model_needs_downloading(model_vars, model_type)
        if bool is None: # EA needs updating, return to window
            btn_start_deploy.configure(state=NORMAL)
            sim_run_btn.configure(state=NORMAL)
            return 
        elif bool: # model can be downloaded, ask user 
            user_wants_to_download = download_model(dirpath)
            if not user_wants_to_download:
                btn_start_deploy.configure(state=NORMAL)
                sim_run_btn.configure(state=NORMAL)
                return  # user doesn't want to download

    # run some checks that make sense for both simple and advanced mode
    # check if chosen folder is valid
    if chosen_folder in ["", "/", "\\", ".", "~", ":"] or not os.path.isdir(chosen_folder):
        mb.showerror(error_txt[lang_idx],
            message=["Please specify a directory with data to be processed.",
                     "Por favor, especifique un directorio con los datos a procesar."][lang_idx])
        btn_start_deploy.configure(state=NORMAL)
        sim_run_btn.configure(state=NORMAL)
        return

    # save simple settings for next time
    write_global_vars({
        "lang_idx": lang_idx,
        "var_cls_model_idx": dpd_options_cls_model[lang_idx].index(var_cls_model.get())
    })

    # open progress window with frames for each process that needs to be done
    global progress_window
    progress_window = ProgressWindow(processes = processes)
    progress_window.open()

    # start building the command
    additional_img_options = ["--output_relative_filenames"]

    # if user deployed from simple mode everything will be default, so easy
    if simple_mode:
        additional_img_options.append("--recursive")

    # if the user comes from the advanced mode, there are more settings to be checked
    else:
        # save advanced settings for next time
        write_global_vars({
            "var_det_model_idx": dpd_options_model[lang_idx].index(var_det_model.get()),
            "var_det_model_path": var_det_model_path.get(),
            "var_det_model_short": var_det_model_short.get(),
            "var_exclude_subs": var_exclude_subs.get(),
            "var_use_custom_img_size_for_deploy": var_use_custom_img_size_for_deploy.get(),
            "var_image_size_for_deploy": var_image_size_for_deploy.get() if var_image_size_for_deploy.get().isdigit() else "",
            "var_abs_paths": var_abs_paths.get(),
            "var_disable_GPU": var_disable_GPU.get(),
            "var_process_img": var_process_img.get(),
            "var_use_checkpnts": var_use_checkpnts.get(),
            "var_checkpoint_freq": var_checkpoint_freq.get() if var_checkpoint_freq.get().isdecimal() else "",
            "var_cont_checkpnt": var_cont_checkpnt.get(),
            "var_process_vid": var_process_vid.get(),
            "var_not_all_frames": var_not_all_frames.get(),
            "var_nth_frame": var_nth_frame.get() if var_nth_frame.get().isdecimal() else ""
        })
        
        # check if user selected to process either images or videos
        if not var_process_img.get() and not var_process_vid.get():
            mb.showerror(["Nothing selected to be processed", "No se ha seleccionado nada para procesar"][lang_idx],
                            message=["You selected neither images nor videos to be processed.",
                                    "No ha seleccionado ni imágenes ni vídeos para procesar."][lang_idx])
            btn_start_deploy.configure(state=NORMAL)
            sim_run_btn.configure(state=NORMAL)
            return
        
        # check if checkpoint entry is valid
        if var_use_custom_img_size_for_deploy.get() and not var_image_size_for_deploy.get().isdecimal():
            mb.showerror(invalid_value_txt[lang_idx],
                        ["You either entered an invalid value for the image size, or none at all. You can only "
                        "enter numberic characters.",
                        "Ha introducido un valor no válido para el tamaño de la imagen o no ha introducido ninguno. "
                        "Sólo puede introducir caracteres numéricos."][lang_idx])
            btn_start_deploy.configure(state=NORMAL)
            sim_run_btn.configure(state=NORMAL)
            return

        # check if checkpoint entry is valid
        if var_use_checkpnts.get() and not var_checkpoint_freq.get().isdecimal():
            if mb.askyesno(invalid_value_txt[lang_idx],
                            ["You either entered an invalid value for the checkpoint frequency, or none at all. You can only "
                            "enter numberic characters.\n\nDo you want to proceed with the default value 500?",
                            "Ha introducido un valor no válido para la frecuencia del punto de control o no ha introducido ninguno. "
                            "Sólo puede introducir caracteres numéricos.\n\n¿Desea continuar con el valor por defecto 500?"][lang_idx]):
                var_checkpoint_freq.set("500")
                ent_checkpoint_freq.configure(fg='black')
            else:
                btn_start_deploy.configure(state=NORMAL)
                sim_run_btn.configure(state=NORMAL)
                return
        
        # check if the nth frame entry is valid
        if var_not_all_frames.get() and not var_nth_frame.get().isdecimal():
            if mb.askyesno(invalid_value_txt[lang_idx],
                            [f"You either entered an invalid value for '{lbl_nth_frame_txt[lang_idx]}', or none at all. You can only "
                            "enter numberic characters.\n\nDo you want to proceed with the default value 10?\n\n"
                            "That means you process only 1 out of 10 frames, making the process time 10 times faster.",
                            f"Ha introducido un valor no válido para '{lbl_nth_frame_txt[lang_idx]}', o no ha introducido ninguno. Sólo "
                            "puede introducir caracteres numéricos.\n\n¿Desea continuar con el valor por defecto 10?. Eso significa "
                            "que sólo se procesa 1 de cada 10 fotogramas, con lo que el tiempo de proceso es 10 veces más rápido."][lang_idx]):
                var_nth_frame.set("10")
                ent_nth_frame.configure(fg='black')
            else:
                btn_start_deploy.configure(state=NORMAL)
                sim_run_btn.configure(state=NORMAL)
                return

        # create command for the image process to be passed on to run_detector_batch.py
        if not var_exclude_subs.get():
            additional_img_options.append("--recursive")
        if var_use_checkpnts.get():
            additional_img_options.append("--checkpoint_frequency=" + var_checkpoint_freq.get())
        if var_cont_checkpnt.get():
            check_checkpnt()
            additional_img_options.append("--resume_from_checkpoint=" + loc_chkpnt_file)
        if var_use_custom_img_size_for_deploy.get():
            additional_img_options.append("--image_size=" + var_image_size_for_deploy.get())

        # create command for the video process to be passed on to process_video.py
        additional_vid_options = []
        additional_vid_options.append("--json_confidence_threshold=0.01")
        if not var_exclude_subs.get():
            additional_vid_options.append("--recursive")
        if var_not_all_frames.get():
            additional_vid_options.append("--frame_sample=" + var_nth_frame.get())
        temp_frame_folder_created = False
        if var_process_vid.get():
            if var_cls_model.get() not in none_txt:
                global temp_frame_folder
                temp_frame_folder_obj = tempfile.TemporaryDirectory()
                temp_frame_folder_created = True
                temp_frame_folder = temp_frame_folder_obj.name
                additional_vid_options.append("--frame_folder=" + temp_frame_folder)
                additional_vid_options.append("--keep_extracted_frames")
    
    try:

        # if not deployed through simple mode, check the input values
        if not simple_mode:
            # detect images ...
            if var_process_img.get():
                deploy_model(chosen_folder, additional_img_options, data_type = "img", simple_mode = simple_mode)

            # ... and/or videos
            if var_process_vid.get() and not simple_mode:
                deploy_model(chosen_folder, additional_vid_options, data_type = "vid", simple_mode = simple_mode)
        
        # if deployed through simple mode, analyse images and add predefined postprocess for simple mode directly after deployment and classification
        else:
            deploy_model(chosen_folder, additional_img_options, data_type = "img", simple_mode = simple_mode)
            postprocess(src_dir = chosen_folder,
                         dst_dir = chosen_folder,
                         thresh = global_vars["var_thresh_default"],
                         sep = False,
                         file_placement = 1,
                         sep_conf = False,
                         vis = False,
                         crp = False,
                         exp = True,
                         exp_format = "XLSX",
                         data_type = "img")
            show_result_info(os.path.join(chosen_folder, "results.xlsx"))

        # reset window
        update_frame_states()
        
        # close progress window
        progress_window.close()

        # clean up temp folder with frames
        if temp_frame_folder_created:
            temp_frame_folder_obj.cleanup()

        # show model error pop up window
        if os.path.isfile(model_error_log):
            mb.showerror(error_txt[lang_idx], [f"There were one or more model errors. See\n\n'{model_error_log}'\n\nfor more information.",
                                            f"Se han producido uno o más errores de modelo. Consulte\n\n'{model_error_log}'\n\npara obtener más información."][lang_idx])

        # show model warning pop up window
        if os.path.isfile(model_warning_log):
            mb.showerror(error_txt[lang_idx], [f"There were one or more model warnings. See\n\n'{model_warning_log}'\n\nfor more information.",
                                        f"Se han producido uno o más advertencias de modelo. Consulte\n\n'{model_warning_log}'\n\npara obtener más información."][lang_idx])

        # show postprocessing warning log
        global postprocessing_error_log
        postprocessing_error_log = os.path.join(chosen_folder, "postprocessing_error_log.txt")
        if os.path.isfile(postprocessing_error_log): 
            mb.showwarning(warning_txt[lang_idx], [f"One or more files failed to be analysed by the model (e.g., corrupt files) and will be skipped by "
                                                f"post-processing features. See\n\n'{postprocessing_error_log}'\n\nfor more info.",
                                                f"Uno o más archivos no han podido ser analizados por el modelo (por ejemplo, ficheros corruptos) y serán "
                                                f"omitidos por las funciones de post-procesamiento. Para más información, véase\n\n'{postprocessing_error_log}'"][lang_idx])

        # enable button
        btn_start_deploy.configure(state=NORMAL)
        sim_run_btn.configure(state=NORMAL)
        root.update()

    except Exception as error:

        # log error
        print("\n\nERROR:\n" + str(error) + "\n\nSUBPROCESS OUTPUT:\n" + subprocess_output + "\n\nTRACEBACK:\n" + traceback.format_exc() + "\n\n")
        print(f"cancel_deploy_model_pressed : {cancel_deploy_model_pressed}")

        if cancel_deploy_model_pressed:
            pass
        
        else:
            # show error
            mb.showerror(title=error_txt[lang_idx],
                        message=["An error has occurred", "Ha ocurrido un error"][lang_idx] + " (EcoAssist v" + current_EA_version + "): '" + str(error) + "'.",
                        detail=subprocess_output + "\n" + traceback.format_exc())
            
            # close window
            progress_window.close()

            # enable button
            btn_start_deploy.configure(state=NORMAL)
            sim_run_btn.configure(state=NORMAL)

# get data from file list and create graph
def produce_graph(file_list_txt = None, dir = None):
    
    # if a list with images is specified
    if file_list_txt:
        count_dict = {}

        # loop through the files
        with open(file_list_txt) as f:
            for line in f:

                # open xml 
                img = line.rstrip()
                annotation = return_xml_path(img)
                tree = ET.parse(annotation)
                root = tree.getroot()

                # loop through detections
                for obj in root.findall('object'):

                    # add detection to dict
                    name = obj.findtext('name')
                    if name not in count_dict:
                        count_dict[name] = 0
                    count_dict[name] += 1
            f.close()

        # create plot
        classes = list(count_dict.keys())
        counts = list(count_dict.values())
        fig = plt.figure(figsize = (10, 5))
        plt.bar(classes, counts, width = 0.4)
        plt.ylabel(["No. of instances verified", "No de instancias verificadas"][lang_idx])
        plt.close()

        # return results
        return fig

# create pascal voc annotation files from a list of detections
def create_pascal_voc_annotation(image_path, annotation_list, human_verified):

    # init vars
    image_path = Path(image_path)
    img = np.array(Image.open(image_path).convert('RGB'))
    annotation = ET.Element('annotation')

    # set verified flag if been verified in a previous session
    if human_verified:
        annotation.set('verified', 'yes')

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
        xmin, ymin, xmax, ymax = cords[0], cords[1], cords[4], cords[5] # left, top, right, bottom

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
    xml_file_name = return_xml_path(image_path)
    Path(os.path.dirname(xml_file_name)).mkdir(parents=True, exist_ok=True)
    tree.write(xml_file_name)

# loop json and see which images and annotations fall in user-specified catgegory
def select_detections(selection_dict, prepare_files):
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")

    # open patience window
    steps_progress = PatienceDialog(total = 8, text = [f"Loading...", f"Cargando..."][lang_idx])
    steps_progress.open()
    current_step = 1
    steps_progress.update_progress(current_step);current_step += 1

    # init vars
    selected_dir = var_choose_folder.get()
    recognition_file = os.path.join(selected_dir, 'image_recognition_file.json')
    temp_folder = os.path.join(selected_dir, 'temp-folder')
    Path(temp_folder).mkdir(parents=True, exist_ok=True)
    file_list_txt = os.path.join(temp_folder, 'hitl_file_list.txt')
    class_list_txt = os.path.join(temp_folder, 'hitl_class_list.txt')
    steps_progress.update_progress(current_step);current_step += 1

    # make sure json has relative paths
    json_paths_converted = False
    if check_json_paths(recognition_file) != "relative":
        make_json_relative(recognition_file)
        json_paths_converted = True
    steps_progress.update_progress(current_step);current_step += 1

    # list selection criteria
    selected_categories = []
    min_confs = []
    max_confs = []
    ann_min_confs_specific = {}
    selected_files = {}
    rad_ann_val = rad_ann_var.get()
    ann_min_confs_generic = None
    steps_progress.update_progress(current_step);current_step += 1

    # class specific values
    for key, values in selection_dict.items():
        category = values['class']
        chb_val = values['chb_var'].get()
        min_conf = round(values['min_conf_var'].get(), 2)
        max_conf = round(values['max_conf_var'].get(), 2)
        ann_min_conf_specific = values['scl_ann_var_specific'].get()
        ann_min_confs_generic = values['scl_ann_var_generic'].get()
        ann_min_confs_specific[category] = ann_min_conf_specific
        
        # if class is selected
        if chb_val:
            selected_categories.append(category)
            min_confs.append(min_conf)
            max_confs.append(max_conf)
            selected_files[category] = []
    steps_progress.update_progress(current_step);current_step += 1

    # remove old file list if present
    if prepare_files:
        if os.path.isfile(file_list_txt):
            os.remove(file_list_txt)
    steps_progress.update_progress(current_step);current_step += 1

    # loop though images and list those which pass the criteria
    img_and_detections_dict = {}
    with open(recognition_file, "r") as image_recognition_file_content:
        data = json.load(image_recognition_file_content)
        label_map = fetch_label_map_from_json(recognition_file)

        # check all images...
        for image in data['images']:

            # set vars
            image_path = os.path.join(selected_dir, image['file'])
            annotations = []
            image_already_added = False

            # check if the image has already been human verified
            try:
                human_verified = image['manually_checked']
            except:
                human_verified = False
            
            # check all detections ...
            if 'detections' in image:
                for detection in image['detections']:
                    category_id = detection['category']
                    category = label_map[category_id]
                    conf = detection['conf']

                    # ... if they pass any of the criteria
                    for i in range(len(selected_categories)):
                        if category == selected_categories[i] and conf >= min_confs[i] and conf <= max_confs[i]:
                            
                            # this image contains one or more detections which pass
                            if not image_already_added:
                                selected_files[selected_categories[i]].append(image_path)
                                image_already_added = True

                    # prepare annotations
                    if prepare_files:
                        display_annotation = False

                        # if one annotation treshold for all classes is specified
                        if rad_ann_val == 1 and conf >= ann_min_confs_generic:
                            display_annotation = True
                        
                        # if class-specific annotation tresholds are specified
                        elif rad_ann_val == 2 and conf >= ann_min_confs_specific[category]: 
                            display_annotation = True

                        # add this detection to the list
                        if display_annotation:
                            im = Image.open(image_path)
                            width, height = im.size
                            left = int(round(detection['bbox'][0] * width)) # xmin
                            top = int(round(detection['bbox'][1] * height)) # ymin 
                            right = int(round(detection['bbox'][2] * width)) + left # width
                            bottom = int(round(detection['bbox'][3] * height)) + top # height
                            list = [left, top, None, None, right, bottom, None, category]
                            string = ','.join(map(str, list))
                            annotations.append(string)
                                    
            # create pascal voc annotation file for this image
            if prepare_files:
                img_and_detections_dict[image_path] = {"annotations": annotations, "human_verified": human_verified}
    steps_progress.update_progress(current_step);current_step += 1

    # update count widget
    total_imgs = 0
    for category, files in selected_files.items():
        label_map = fetch_label_map_from_json(recognition_file)
        classes_list = [v for k, v in label_map.items()]
        row = classes_list.index(category) + 2
        frame = selection_dict[row]['frame']
        lbl_n_img = selection_dict[row]['lbl_n_img']
        chb_var = selection_dict[row]['chb_var'].get()
        rad_var = selection_dict[row]['rad_var'].get()

        # if user specified a precentage of total images
        if chb_var and rad_var == 2:

            # check if entry is valid
            ent_per_var = selection_dict[row]['ent_per_var'].get()
            try:
                ent_per_var = float(ent_per_var)
            except:
                invalid_value_warning([f"percentage of images for class '{category}'", f"porcentaje de imágenes para la clase '{category}'"][lang_idx])
                return
            if ent_per_var == "" or ent_per_var < 0 or ent_per_var > 100:
                invalid_value_warning([f"percentage of images for class '{category}'", f"porcentaje de imágenes para la clase '{category}'"][lang_idx])
                return
            
            # randomly select percentage of images
            total_n = len(files)
            n_selected = int(total_n * (ent_per_var / 100))
            random.shuffle(files)
            files = files[:n_selected]

        # user specified a max number of images
        elif chb_var and rad_var == 3: 

            # check if entry is valid
            ent_amt_var = selection_dict[row]['ent_amt_var'].get()
            try:
                ent_amt_var = float(ent_amt_var)
            except:
                invalid_value_warning([f"number of images for class '{category}'", f"número de imágenes para la clase '{category}'"][lang_idx])
                return
            if ent_amt_var == "":
                invalid_value_warning([f"number of images for class '{category}'", f"número de imágenes para la clase '{category}'"][lang_idx])
                return

            # randomly select specified number of images
            total_n = len(files)
            n_selected = int(ent_amt_var)
            random.shuffle(files)
            files = files[:n_selected]

        # update label text 
        n_imgs = len(files)
        lbl_n_img.configure(text = str(n_imgs))
        total_imgs += n_imgs

        # loop through the ultimately selected images and create files
        if prepare_files and len(files) > 0:

            # open patience window
            patience_dialog = PatienceDialog(total = n_imgs, text = [f"Preparing files for {category}...", f"Preparando archivos para {category}..."][lang_idx])
            patience_dialog.open()
            current = 1
            
            # human sort images per class
            def atoi(text):
                return int(text) if text.isdigit() else text
            def natural_keys(text):
                return [atoi(c) for c in re.split('(\d+)', text)]
            files.sort(key=natural_keys)

            for img in files:

                # update patience window
                patience_dialog.update_progress(current)
                current += 1

                # create text file with images
                file_list_txt = os.path.normpath(file_list_txt)
                with open(file_list_txt, 'a') as f:
                    f.write(f"{os.path.normpath(img)}\n")
                    f.close()
                
                # # list annotaions 
                annotation_path = return_xml_path(img)

                # create xml file if not already present
                if not os.path.isfile(annotation_path):
                    create_pascal_voc_annotation(img, img_and_detections_dict[img]['annotations'], img_and_detections_dict[img]['human_verified'])

            # close patience window
            patience_dialog.close()      
    steps_progress.update_progress(current_step);current_step += 1
    steps_progress.close()

    # update total number of images
    lbl_n_total_imgs.configure(text = [f"TOTAL: {total_imgs}", f"TOTAL: {total_imgs}"][lang_idx])
    
    if prepare_files:

        # TODO: hier moet ook een progress window komen als het een grote file is

        # create file with classes
        with open(class_list_txt, 'a') as f:
            for k, v in label_map.items():
                f.write(f"{v}\n")
            f.close()

        # write arguments to file in case user quits and continues later
        annotation_arguments = {"recognition_file" : recognition_file,
                                "class_list_txt" : class_list_txt,
                                "file_list_txt" : file_list_txt,
                                "label_map" : label_map,
                                "img_and_detections_dict" : img_and_detections_dict}

        annotation_arguments_pkl = os.path.join(selected_dir, 'temp-folder', 'annotation_information.pkl')
        with open(annotation_arguments_pkl, 'wb') as fp:
            pickle.dump(annotation_arguments, fp)
            fp.close()

        # start human in the loop process
        try:
            open_annotation_windows(recognition_file = recognition_file,
                                    class_list_txt = class_list_txt,
                                    file_list_txt = file_list_txt,
                                    label_map = label_map)
        except Exception as error:
            # log error
            print("ERROR:\n" + str(error) + "\n\nDETAILS:\n" + str(traceback.format_exc()) + "\n\n")
            
            # show error
            mb.showerror(title=error_txt[lang_idx],
                        message=["An error has occurred", "Ha ocurrido un error"][lang_idx] + " (EcoAssist v" + current_EA_version + "): '" + str(error) + "'.",
                        detail=traceback.format_exc())

    # change json paths back, if converted earlier
    if json_paths_converted:
        make_json_absolute(recognition_file)

# count confidence values per class for histograms
def fetch_confs_per_class(json_fpath):
    label_map = fetch_label_map_from_json(os.path.join(var_choose_folder.get(), 'image_recognition_file.json'))
    confs = {}
    for key in label_map:
        confs[key] = []
    with open(json_fpath) as content:
        data = json.load(content)
        for image in data['images']:
            if 'detections' in image:
                for detection in image['detections']:
                    conf = detection["conf"]
                    category = detection["category"]
                    confs[category].append(conf)
    return confs

# open the human-in-the-loop settings window
def open_hitl_settings_window():
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")

    # fetch confs for histograms
    confs = fetch_confs_per_class(os.path.join(var_choose_folder.get(), 'image_recognition_file.json'))

    # set global vars
    global selection_dict
    global rad_ann_var
    global hitl_ann_selection_frame
    global hitl_settings_canvas
    global hitl_settings_window
    global lbl_n_total_imgs

    # init vars
    selected_dir = var_choose_folder.get()
    recognition_file = os.path.join(selected_dir, 'image_recognition_file.json')

    # init window
    hitl_settings_window = Toplevel(root)
    hitl_settings_window.title(["Verification selection settings", "Configuración de selección de verificación"][lang_idx])
    hitl_settings_window.geometry()
    hitl_settings_window.maxsize(width=ADV_WINDOW_WIDTH, height=800)

    # set scrollable frame
    hitl_settings_scroll_frame = Frame(hitl_settings_window)
    hitl_settings_scroll_frame.pack(fill=BOTH, expand=1)

    # set canvas
    hitl_settings_canvas = Canvas(hitl_settings_scroll_frame)
    hitl_settings_canvas.pack(side=LEFT, fill=BOTH, expand=1)

    # set scrollbar
    hitl_settings_scrollbar = tk.Scrollbar(hitl_settings_scroll_frame, orient=VERTICAL, command=hitl_settings_canvas.yview)
    hitl_settings_scrollbar.pack(side=RIGHT, fill=Y)

    # enable scroll on mousewheel 
    def hitl_settings_canvas_mousewheel(event):
        if os.name == 'nt':
            hitl_settings_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        else:
            hitl_settings_canvas.yview_scroll(int(-1 * (event.delta / 2)), 'units')

    # configure canvas and bind scroll events
    hitl_settings_canvas.configure(yscrollcommand=hitl_settings_scrollbar.set)
    hitl_settings_canvas.bind('<Configure>', lambda e: hitl_settings_canvas.configure(scrollregion=hitl_settings_canvas.bbox("all")))
    hitl_settings_canvas.bind_all("<MouseWheel>", hitl_settings_canvas_mousewheel)
    hitl_settings_canvas.bind_all("<Button-4>", hitl_settings_canvas_mousewheel) 
    hitl_settings_canvas.bind_all("<Button-5>", hitl_settings_canvas_mousewheel)

    # set labelframe to fill with widgets
    hitl_settings_main_frame = LabelFrame(hitl_settings_canvas)

    # img selection frame
    hitl_img_selection_frame = LabelFrame(hitl_settings_main_frame, text=[" Image selection criteria ", " Criterios de selección de imágenes "][lang_idx],
                                            pady=2, padx=5, relief='solid', highlightthickness=5, font=100, fg=EA_blue_color, labelanchor = 'n')
    hitl_img_selection_frame.configure(font=(text_font, 15, "bold"))
    hitl_img_selection_frame.grid(column=0, row=1, columnspan=2, sticky='ew')
    hitl_img_selection_frame.columnconfigure(0, weight=1, minsize=50)
    hitl_img_selection_frame.columnconfigure(1, weight=1, minsize=200)
    hitl_img_selection_frame.columnconfigure(2, weight=1, minsize=200)
    hitl_img_selection_frame.columnconfigure(3, weight=1, minsize=200)
    hitl_img_selection_frame.columnconfigure(4, weight=1, minsize=200)

    # show explanation and resize window
    def show_text_hitl_img_selection_explanation():
        text_hitl_img_selection_explanation.grid(column=0, row=0, columnspan=5, padx=5, pady=5, sticky='ew')
        hitl_settings_window.update()
        w = hitl_settings_main_frame.winfo_width() + 30
        h = hitl_settings_main_frame.winfo_height() + 10
        hitl_settings_window.geometry(f'{w}x{h}')
        hitl_settings_window.update()

    # img explanation
    Button(master=hitl_img_selection_frame, text="?", width=1, command=show_text_hitl_img_selection_explanation).grid(column=0, row=0, columnspan=1, padx=5, pady=5, sticky='ew')
    text_hitl_img_selection_explanation = Text(master=hitl_img_selection_frame, wrap=WORD, width=1, height=12 * explanation_text_box_height_factor) 
    text_hitl_img_selection_explanation.tag_config('explanation', font=f'{text_font} {int(13 * text_size_adjustment_factor)} normal', lmargin1=10, lmargin2=10)
    text_hitl_img_selection_explanation.insert(END, ["Here, you can specify which images you wish to review. If a detection aligns with the chosen criteria, the image will be "
                                                    "chosen for the verification process. In the review process, you’ll need to make sure all detections in the image are correct. "
                                                    "You have the option to select a subset of your images based on specific classes, confidence ranges, and selection methods. For "
                                                    "instance, the default settings will enable you to verify images with detections that the model is medium-sure about (with"
                                                    " confidences between 0.2 and 0.8). This means that you don’t review high-confidence detections of more than 0.8 confidence and "
                                                    "avoid wasting time on low-confidence detections of less than 0.2. Feel free to adjust these settings to suit your data. To "
                                                    "determine the number of images that will require verification based on the selected criteria, press the “Update counts” button "
                                                    "below. If required, you can specify a selection method that will randomly choose a subset based on a percentage or an absolute "
                                                    "number. Verification will adjust the results in the JSON file. This means that you can continue to use EcoAssist with verified "
                                                    "results and post-process as usual.", "Aquí puede especificar qué imágenes desea revisar. Si una detección se alinea con los "
                                                    "criterios elegidos, la imagen será elegida para el proceso de verificación. Tiene la opción de seleccionar un subconjunto de "
                                                    "sus imágenes según clases específicas, rangos de confianza y métodos de selección. Por ejemplo, la configuración"
                                                    " predeterminada le permitirá verificar imágenes con detecciones de las que el modelo está medio seguro "
                                                    "(con confianzas entre 0,2 y 0,8). Esto significa que no revisa las detecciones de alta confianza con "
                                                    "más de 0,8 de confianza y evita perder tiempo en detecciones de baja confianza de menos de 0,2. Siéntase"
                                                    " libre de ajustar estas configuraciones para adaptarlas a sus datos. Para determinar la cantidad de imágenes "
                                                    "que requerirán verificación según los criterios seleccionados, presione el botón 'Actualizar recuentos' a continuación. Si es "
                                                    "necesario, puede especificar un método de selección que elegirá aleatoriamente un subconjunto en función de un porcentaje o un "
                                                    "número absoluto. La verificación ajustará los resultados en el archivo JSON. Esto significa que puede continuar usando EcoAssist"
                                                    " con resultados verificados y realizar el posprocesamiento como de costumbre."][lang_idx])
    text_hitl_img_selection_explanation.tag_add('explanation', '1.0', '1.end')

    # img table headers
    ttk.Label(master=hitl_img_selection_frame, text="").grid(column=0, row=1)
    ttk.Label(master=hitl_img_selection_frame, text="Class", font=f'{text_font} 13 bold').grid(column=1, row=1)
    ttk.Label(master=hitl_img_selection_frame, text="Confidence range", font=f'{text_font} 13 bold').grid(column=2, row=1)
    ttk.Label(master=hitl_img_selection_frame, text="Selection method", font=f'{text_font} 13 bold').grid(column=3, row=1)
    ttk.Label(master=hitl_img_selection_frame, text="Number of images", font=f'{text_font} 13 bold').grid(column=4, row=1)

    # ann selection frame
    hitl_ann_selection_frame = LabelFrame(hitl_settings_main_frame, text=[" Annotation selection criteria ", " Criterios de selección de anotaciones "][lang_idx],
                                            pady=2, padx=5, relief='solid', highlightthickness=5, font=100, fg=EA_blue_color, labelanchor = 'n')
    hitl_ann_selection_frame.configure(font=(text_font, 15, "bold"))
    hitl_ann_selection_frame.grid(column=0, row=2, columnspan=2, sticky='ew')
    hitl_ann_selection_frame.columnconfigure(0, weight=1, minsize=50)
    hitl_ann_selection_frame.columnconfigure(1, weight=1, minsize=200)
    hitl_ann_selection_frame.columnconfigure(2, weight=1, minsize=200)
    hitl_ann_selection_frame.columnconfigure(3, weight=1, minsize=200)
    hitl_ann_selection_frame.columnconfigure(4, weight=1, minsize=200)

    # ann explanation
    text_hitl_ann_selection_explanation = Text(master=hitl_ann_selection_frame, wrap=WORD, width=1, height=5 * explanation_text_box_height_factor) 
    text_hitl_ann_selection_explanation.grid(column=0, row=0, columnspan=5, padx=5, pady=5, sticky='ew')
    text_hitl_ann_selection_explanation.tag_config('explanation', font=f'{text_font} {int(13 * text_size_adjustment_factor)} normal', lmargin1=10, lmargin2=10)
    text_hitl_ann_selection_explanation.insert(END, ["In the previous step, you selected which images to verify. In this frame, you can specify which annotations to display "
                                              "on these images. During the verification process, all instances of all classes need to be labeled. That is why you want to display "
                                              "all annotations above a reasonable confidence threshold. You can select generic or class-specific confidence thresholds. If you are"
                                              " uncertain, just stick with the default value. A threshold of 0.2 is probably a conservative threshold for most projects.",
                                              "En el paso anterior, seleccionó qué imágenes verificar. En este marco, puede especificar qué anotaciones mostrar en estas imágenes."
                                              " Durante el proceso de verificación, se deben etiquetar todas las instancias de todas las clases. Es por eso que desea mostrar todas"
                                              " las anotaciones por encima de un umbral de confianza razonable. Puede seleccionar umbrales de confianza genéricos o específicos de"
                                              " clase. Si no está seguro, siga con el valor predeterminado. Un umbral de 0,2 es un umbral conservador para la mayoría"
                                              " de los proyectos."][lang_idx])
    text_hitl_ann_selection_explanation.tag_add('explanation', '1.0', '1.end')

    # ann same thresh
    rad_ann_var = IntVar()
    rad_ann_var.set(1)
    rad_ann_same = Radiobutton(hitl_ann_selection_frame, text=["Same annotation confidence threshold for all classes",
                                                               "Mismo umbral de confianza para todas las clases"][lang_idx],
                                variable=rad_ann_var, value=1, command=lambda: toggle_hitl_ann_selection(rad_ann_var, hitl_ann_selection_frame))
    rad_ann_same.grid(row=1, column=1, columnspan=2, sticky='w')
    frame_ann_same = LabelFrame(hitl_ann_selection_frame, text="", pady=2, padx=5, relief=RAISED)
    frame_ann_same.grid(column=3, row=1, columnspan=2, sticky='ew')
    frame_ann_same.columnconfigure(0, weight=1, minsize=200)
    frame_ann_same.columnconfigure(1, weight=1, minsize=200)
    lbl_ann_same = ttk.Label(master=frame_ann_same, text=["All classes", "Todas las clases"][lang_idx])
    lbl_ann_same.grid(row=0, column=0, sticky='w')
    scl_ann_var_generic = DoubleVar()
    scl_ann_var_generic.set(0.60)
    scl_ann = Scale(frame_ann_same, from_=0, to=1, resolution=0.01, orient=HORIZONTAL, variable=scl_ann_var_generic, width=10, length=1, showvalue=0)
    scl_ann.grid(row=0, column=1, sticky='we')
    dsp_scl_ann = Label(frame_ann_same, textvariable=scl_ann_var_generic)
    dsp_scl_ann.grid(row=0, column=0, sticky='e', padx=5)

    # ann specific thresh
    rad_ann_gene = Radiobutton(hitl_ann_selection_frame, text=["Class-specific annotation confidence thresholds",
                                                               "Umbrales de confianza específicas de clase"][lang_idx],
                                variable=rad_ann_var, value=2, command=lambda: toggle_hitl_ann_selection(rad_ann_var, hitl_ann_selection_frame))
    rad_ann_gene.grid(row=2, column=1, columnspan=2, sticky='w')

    # create widgets and vars for each class
    label_map = fetch_label_map_from_json(recognition_file)
    selection_dict = {}
    for i, [k, v] in enumerate(label_map.items()):
        
        # image selection frame
        row = i + 2
        frame = LabelFrame(hitl_img_selection_frame, text="", pady=2, padx=5, relief=RAISED)
        frame.grid(column=0, row=1, columnspan=2, sticky='ew')
        frame.columnconfigure(0, weight=1, minsize=50)
        frame.columnconfigure(1, weight=1, minsize=200)
        frame.columnconfigure(2, weight=1, minsize=200)
        frame.columnconfigure(3, weight=1, minsize=200)
        frame.columnconfigure(4, weight=1, minsize=200)
        chb_var = BooleanVar()
        chb_var.set(False)
        chb = tk.Checkbutton(frame, variable=chb_var, command=lambda e=row:enable_selection_widgets(e))
        lbl_class = ttk.Label(master=frame, text=v, state=DISABLED)
        min_conf = DoubleVar(value = 0.2)
        max_conf = DoubleVar(value = 1.0)
        fig = plt.figure(figsize = (2, 0.3))
        plt.hist(confs[k], bins = 10, range = (0,1))
        plt.xticks([])
        plt.yticks([])
        dist_graph = FigureCanvasTkAgg(fig, frame)
        plt.close()
        rsl = RangeSliderH(frame, [min_conf, max_conf], padX=11, digit_precision='.2f', bgColor = '#ececec', Width = 180)
        rad_var = IntVar()
        rad_var.set(1)
        rad_all = Radiobutton(frame, text=["All images in range", "Todo dentro del rango"][lang_idx],
                                variable=rad_var, value=1, state=DISABLED, command=lambda e=row:enable_amt_per_ent(e))
        rad_per = Radiobutton(frame, text=["Subset percentage", "Subconjunto %"][lang_idx],
                                variable=rad_var, value=2, state=DISABLED, command=lambda e=row:enable_amt_per_ent(e))
        rad_amt = Radiobutton(frame, text=["Subset number", "Subconjunto no."][lang_idx],
                                variable=rad_var, value=3, state=DISABLED, command=lambda e=row:enable_amt_per_ent(e))
        ent_per_var = StringVar()
        ent_per = tk.Entry(frame, textvariable=ent_per_var, width=4, state=DISABLED)
        ent_amt_var = StringVar()
        ent_amt = tk.Entry(frame, textvariable=ent_amt_var, width=4, state=DISABLED)
        lbl_n_img = ttk.Label(master=frame, text="0", state=DISABLED)

        # annotation selection frame
        frame_ann = LabelFrame(hitl_ann_selection_frame, text="", pady=2, padx=5, relief=SUNKEN)
        frame_ann.grid(column=3, row=row, columnspan=2, sticky='ew')
        frame_ann.columnconfigure(0, weight=1, minsize=200)
        frame_ann.columnconfigure(1, weight=1, minsize=200)
        lbl_ann_gene = ttk.Label(master=frame_ann, text=v, state = DISABLED)
        lbl_ann_gene.grid(row=0, column=0, sticky='w')
        scl_ann_var_specific = DoubleVar()
        scl_ann_var_specific.set(0.60)
        scl_ann_gene = Scale(frame_ann, from_=0, to=1, resolution=0.01, orient=HORIZONTAL, variable=scl_ann_var_specific, width=10, length=1, showvalue=0, state = DISABLED)
        scl_ann_gene.grid(row=0, column=1, sticky='we')
        dsp_scl_ann_gene = Label(frame_ann, textvariable=scl_ann_var_specific, state = DISABLED)
        dsp_scl_ann_gene.grid(row=0, column=0, sticky='e', padx=5)
        
        # store info in a dictionary 
        item = {'row': row,
                'label_map_id': k,
                'class': v,
                'frame': frame,
                'min_conf_var': min_conf,
                'max_conf_var': max_conf,
                'chb_var': chb_var,
                'lbl_class': lbl_class,
                'range_slider_widget': rsl,
                'lbl_n_img': lbl_n_img,
                'rad_all': rad_all,
                'rad_per': rad_per,
                'rad_amt': rad_amt,
                'rad_var': rad_var,
                'ent_per_var': ent_per_var,
                'ent_per': ent_per,
                'ent_amt_var': ent_amt_var,
                'ent_amt': ent_amt,
                'scl_ann_var_specific': scl_ann_var_specific,
                'scl_ann_var_generic': scl_ann_var_generic}
        selection_dict[row] = item

        # place widgets
        frame.grid(row = row, column = 0, columnspan = 5)
        chb.grid(row = 1, column = 0)
        lbl_class.grid(row = 1, column = 1)
        rsl.lower()
        dist_graph.get_tk_widget().grid(row = 0, rowspan= 3, column = 2, sticky = 'n')
        rad_all.grid(row=0, column=3, sticky='w')
        rad_per.grid(row=1, column=3, sticky='w')
        ent_per.grid(row=1, column=3, sticky='e')
        rad_amt.grid(row=2, column=3, sticky='w')
        ent_amt.grid(row=2, column=3, sticky='e')
        lbl_n_img.grid(row = 1, column = 4)

        # set row minsize
        set_minsize_rows(frame)

        # update window
        hitl_settings_window.update_idletasks()

    # set minsize for rows
    row_count = hitl_img_selection_frame.grid_size()[1]
    for row in range(row_count):
        hitl_img_selection_frame.grid_rowconfigure(row, minsize=minsize_rows)

    # add row with total number of images to review
    total_imgs_frame = LabelFrame(hitl_img_selection_frame, text="", pady=2, padx=5, relief=RAISED)
    total_imgs_frame.columnconfigure(0, weight=1, minsize=50)
    total_imgs_frame.columnconfigure(1, weight=1, minsize=200)
    total_imgs_frame.columnconfigure(2, weight=1, minsize=200)
    total_imgs_frame.columnconfigure(3, weight=1, minsize=200)
    total_imgs_frame.columnconfigure(4, weight=1, minsize=200)
    total_imgs_frame.grid(row = row_count, column = 0, columnspan = 5)
    lbl_n_total_imgs = ttk.Label(master=total_imgs_frame, text="TOTAL: 0", state=NORMAL)
    lbl_n_total_imgs.grid(row = 1, column = 4)

    # button frame
    hitl_test_frame = LabelFrame(hitl_settings_main_frame, text=[" Actions ", " Acciones "][lang_idx],
                                    pady=2, padx=5, relief='solid', highlightthickness=5, font=100, fg=EA_blue_color, labelanchor = 'n')
    hitl_test_frame.configure(font=(text_font, 15, "bold"))
    hitl_test_frame.grid(column=0, row=3, columnspan=2, sticky='ew')
    hitl_test_frame.columnconfigure(0, weight=1, minsize=115)
    hitl_test_frame.columnconfigure(1, weight=1, minsize=115)
    hitl_test_frame.columnconfigure(2, weight=1, minsize=115)

    # shorten texts for linux
    if sys.platform == "linux" or sys.platform == "linux2":
        btn_hitl_update_txt = ["Update counts", "La actualización cuenta"][lang_idx]
        btn_hitl_show_txt = ["Show / hide annotation", "Mostrar / ocultar anotaciones"][lang_idx]
        btn_hitl_start_txt = ["Start review process", "Iniciar proceso de revisión"][lang_idx]
    else:
        btn_hitl_update_txt = ["Update counts", "La actualización cuenta"][lang_idx]
        btn_hitl_show_txt = ["Show / hide annotation selection criteria", "Mostrar / ocultar criterios de anotaciones"][lang_idx]
        btn_hitl_start_txt = ["Start review process with selected criteria", "Iniciar proceso de revisión"][lang_idx]

    # buttons
    btn_hitl_update = Button(master=hitl_test_frame, text=btn_hitl_update_txt, width=1, command=lambda: select_detections(selection_dict = selection_dict, prepare_files = False))
    btn_hitl_update.grid(row=0, column=0, rowspan=1, sticky='nesw', padx=5)
    btn_hitl_show = Button(master=hitl_test_frame, text=btn_hitl_show_txt, width=1, command = toggle_hitl_ann_selection_frame)
    btn_hitl_show.grid(row=0, column=1, rowspan=1, sticky='nesw', padx=5)
    btn_hitl_start = Button(master=hitl_test_frame, text=btn_hitl_start_txt, width=1, command=lambda: select_detections(selection_dict = selection_dict, prepare_files = True))
    btn_hitl_start.grid(row=0, column=2, rowspan=1, sticky='nesw', padx=5)
    
    # create scrollable canvas window
    hitl_settings_canvas.create_window((0, 0), window=hitl_settings_main_frame, anchor="nw")

    # hide annotation selection frame
    toggle_hitl_ann_selection_frame(cmd = "hide")

    # update counts after the window is created
    select_detections(selection_dict = selection_dict, prepare_files = False)

    # adjust window size to widgets
    w = hitl_settings_main_frame.winfo_width() + 30
    h = hitl_settings_main_frame.winfo_height() + 10
    hitl_settings_window.geometry(f'{w}x{h}')

# helper function to quickly check the verification status of xml
def verification_status(xml):
    tree = ET.parse(xml)
    root = tree.getroot()
    try:
        verification_status = True if root.attrib['verified'] == 'yes' else False
    except:
        verification_status = False
    return verification_status

# helper function to correctly indent pascal voc annotation files
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

# make sure the program quits when simple or advanced window is closed
def on_toplevel_close():
    write_global_vars({
        "lang_idx": lang_idx,
        "var_cls_model_idx": dpd_options_cls_model[lang_idx].index(var_cls_model.get())
        })
    root.destroy()

# convert pascal bbox to yolo
def convert_bbox_pascal_to_yolo(size, box):
    dw = 1./(size[0])
    dh = 1./(size[1])
    x = (box[0] + box[1])/2.0 - 1
    y = (box[2] + box[3])/2.0 - 1 
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x*dw
    w = w*dw
    y = y*dh
    h = h*dh
    return (x,y,w,h)

# special function because the sim dpd has a different value for 'None'
def sim_mdl_dpd_callback(self):
    var_cls_model.set(dpd_options_cls_model[lang_idx][sim_dpd_options_cls_model[lang_idx].index(self)])
    model_cls_animal_options(var_cls_model.get())

# return xml path with temp-folder squeezed in
def return_xml_path(img_path):
    head_path = var_choose_folder.get()
    tail_path = os.path.splitext(os.path.relpath(img_path, head_path))
    temp_xml_path = os.path.join(head_path, "temp-folder", tail_path[0] + ".xml")
    return os.path.normpath(temp_xml_path)

# temporary file which labelImg writes to notify EcoAssist that it should convert xml to coco
class LabelImgExchangeDir:
    def __init__(self, dir):
        self.dir = dir
        Path(self.dir).mkdir(parents=True, exist_ok=True)

    def create_file(self, content, idx):
        timestamp_miliseconds = str(str(datetime.date.today()) + str(datetime.datetime.now().strftime('%H%M%S%f'))).replace('-', '')
        temp_file = os.path.normpath(os.path.join(self.dir, f"{timestamp_miliseconds}-{idx}.txt"))
        with open(temp_file, 'w') as f:
            f.write(content)
    
    def read_file(self, fp):
        with open(fp, 'r') as f:
            content = f.read()
            return content

    def delete_file(self, fp):
        if os.path.exists(fp):
            os.remove(fp)

    def exist_file(self):
        filelist = glob.glob(os.path.normpath(os.path.join(self.dir, '*.txt')))
        for fn in sorted(filelist):
            return [True, fn]
        return [False, '']

# delete temp folder
def delete_temp_folder(file_list_txt):
    temp_folder = os.path.dirname(file_list_txt)
    if os.path.isdir(temp_folder):
        shutil.rmtree(temp_folder)

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
    if model_type == "old models": # MD
        if platform.processor() == "arm" and os.name != "nt": # M1 and M2
            repository.git.checkout("868c0e9bbb45b031e7bfd73c6d3983bcce07b9c1") 
        else:
            repository.git.checkout("c23a441c9df7ca9b1f275e8c8719c949269160d1")
    elif model_type == "new models": # models trained trough EA v3.4
        repository.git.checkout("3e55763d45f9c5f8217e4dad5ba1e6c1f42e3bf8")

# extract label map from custom model
def extract_label_map_from_model(model_file):
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})")

    # import module from cameratraps dir
    from cameratraps.detection.pytorch_detector import PTDetector

    # load model
    label_map_detector = PTDetector(model_file, force_cpu = True)
    
    # fetch classes
    try:
        CUSTOM_DETECTOR_LABEL_MAP = {}
        for id in label_map_detector.model.names:
            CUSTOM_DETECTOR_LABEL_MAP[id] = label_map_detector.model.names[id]
    except Exception as error:
        # log error
        print("ERROR:\n" + str(error) + "\n\nDETAILS:\n" + str(traceback.format_exc()) + "\n\n")
        
        # show error
        mb.showerror(title=error_txt[lang_idx],
                     message=["An error has occurred when trying to extract classes", "Se ha producido un error al intentar extraer las clases"][lang_idx] +
                                " (EcoAssist v" + current_EA_version + "): '" + str(error) + "'" +
                                [".\n\nWill try to proceed and produce the output json file, but post-processing features of EcoAssist will not work.",
                                 ".\n\nIntentará continuar y producir el archivo json de salida, pero las características de post-procesamiento de EcoAssist no funcionarán."][lang_idx],
                     detail=traceback.format_exc())
    
    # delete and free up memory
    del label_map_detector
    
    # log
    print(f"Label map: {CUSTOM_DETECTOR_LABEL_MAP})\n")

    # return label map
    return CUSTOM_DETECTOR_LABEL_MAP

# fetch label map from json
def fetch_label_map_from_json(path_to_json):
    with open(path_to_json, "r") as json_file:
        data = json.load(json_file)
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

# change human-in-the-loop prgress variable
def change_hitl_var_in_json(path_to_json, status):
    # open
    with open(path_to_json, "r") as json_file:
        data = json.load(json_file)
    
    # adjust
    data['info']["ecoassist_metadata"]["hitl_status"] = status

    # write
    with open(path_to_json, "w") as json_file:
        json.dump(data, json_file, indent=1)

# get human-in-the-loop prgress variable
def get_hitl_var_in_json(path_to_json):
    # open
    with open(path_to_json, "r") as json_file:
        data = json.load(json_file)
        ecoassist_metadata = data['info']["ecoassist_metadata"]
    
    # get status
    if "hitl_status" in ecoassist_metadata:
        status = ecoassist_metadata["hitl_status"]
    else:
        status = "never-started"

    # return
    return status

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
            mb.showerror(error_txt[lang_idx], [f"{noun.capitalize()} is not supported for videos.",
                                           f"{noun.capitalize()} no es compatible con vídeos."][lang_idx])
            return True
        if not vid_json:
            mb.showerror(error_txt[lang_idx], [f"No model output file present. Make sure you run step 2 before {continuous} the files. {noun.capitalize()} "
                                            "is only supported for images.",
                                           f"No hay archivos de salida del modelo. Asegúrese de ejecutar el paso 2 antes de {continuous} los archivos. "
                                           f"{noun.capitalize()} sólo es compatible con imágenes"][lang_idx])
            return True
    if img_json:
        if vid_json:
            mb.showinfo(warning_txt[lang_idx], [f"{noun.capitalize()} is not supported for videos. Will continue to only {infinitive} the images...",
                                            f"No se admiten {noun.capitalize()} para los vídeos. Continuará sólo {infinitive} las imágenes..."][lang_idx])

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
def move_files(file, detection_type, var_file_placement, max_detection_conf, var_sep_conf, dst_root, src_dir, manually_checked):
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")

    # squeeze in extra dir if sorting on confidence
    if var_sep_conf and detection_type != "empty":
        global conf_dirs
        if manually_checked:
            confidence_dir = "verified"
        else:
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

# check if checkpoint file is present and assign global variable
def check_checkpnt():
    global loc_chkpnt_file
    for filename in os.listdir(var_choose_folder.get()):
            if re.search('^checkpoint_\d+\.json$', filename):
                loc_chkpnt_file = os.path.join(var_choose_folder.get(), filename)
                return True
    mb.showinfo(["No checkpoint file found", "No se ha encontrado ningún archivo de puntos de control"][lang_idx],
                    ["There is no checkpoint file found. Cannot continue from checkpoint file...",
                    "No se ha encontrado ningún archivo de punto de control. No se puede continuar desde el archivo de punto de control..."][lang_idx])
    return False

# browse directory
def browse_dir(var, var_short, dsp, cut_off_length, n_row, n_column, str_sticky, source_dir = False):    
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")

    # choose directory
    chosen_dir = filedialog.askdirectory()

    # early exit
    if chosen_dir in ["", "/", "\\", ".", "~", ":"] or not os.path.isdir(chosen_dir):
        return

    # set choice to variable
    var.set(chosen_dir)
    
    # shorten, set and grid display
    dsp_chosen_dir = chosen_dir
    if len(dsp_chosen_dir) > cut_off_length:
        dsp_chosen_dir = "..." + dsp_chosen_dir[0 - cut_off_length + 3:]
    var_short.set(dsp_chosen_dir)
    dsp.grid(column=n_column, row=n_row, sticky=str_sticky)
    
    # also update simple mode if it regards the source dir
    if source_dir:
        global sim_dir_pth
        sim_dir_pth.configure(text = dsp_chosen_dir, text_color = "black")

# choose a custom classifier for animals
def model_cls_animal_options(self):
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")

    # set simple mode cls dropdown to the same index for its own dpd list
    sim_mdl_dpd.set(sim_dpd_options_cls_model[lang_idx][dpd_options_cls_model[lang_idx].index(self)])

    # remove or show widgets
    if self not in none_txt:
        cls_frame.grid(row=cls_frame_row, column=0, columnspan=2, sticky = 'ew')
    else:
        cls_frame.grid_forget()
    
    # get model specific variable values
    global sim_spp_scr
    if self not in none_txt:
        model_vars = load_model_vars()
        dsp_choose_classes.configure(text = f"{len(model_vars['selected_classes'])} of {len(model_vars['all_classes'])}")
        var_cls_detec_thresh.set(model_vars["var_cls_detec_thresh"])
        var_cls_class_thresh.set(model_vars["var_cls_class_thresh"])
    
        # adjust simple_mode window
        sim_spp_lbl.configure(text_color = "black")
        sim_spp_scr.grid_forget()
        sim_spp_scr = SpeciesSelectionFrame(master=sim_spp_frm,
                                            height=sim_spp_scr_height,
                                            all_classes=model_vars['all_classes'],
                                            selected_classes=model_vars['selected_classes'],
                                            command = on_spp_selection)
        sim_spp_scr._scrollbar.configure(height=0)
        sim_spp_scr.grid(row=1, column=0, padx=PADX, pady=(PADY/4, PADY), sticky="ew", columnspan = 2)

    else:
        # set selection frame to dummy spp again
        sim_spp_lbl.configure(text_color = "grey")
        sim_spp_scr.grid_forget()
        sim_spp_scr = SpeciesSelectionFrame(master=sim_spp_frm, height=sim_spp_scr_height, dummy_spp = True)
        sim_spp_scr._scrollbar.configure(height=0)
        sim_spp_scr.grid(row=1, column=0, padx=PADX, pady=(PADY/4, PADY), sticky="ew", columnspan = 2)

    # save settings
    write_global_vars({"var_cls_model_idx": dpd_options_cls_model[lang_idx].index(var_cls_model.get())}) # write index instead of value
 
    # finish up
    toggle_cls_frame()
    resize_canvas_to_content()

# load a custom yolov5 model
def model_options(self):
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")
   
    # if custom model is selected
    if var_det_model.get() in custom_model_txt:
        
        # choose, display and set global var
        browse_file(var_det_model,
                    var_det_model_short,
                    var_det_model_path,
                    dsp_model,
                    [("Yolov5 model","*.pt")],
                    30,
                    dpd_options_model[lang_idx],
                    row_model)

    else:
        var_det_model_short.set("")
        var_det_model_path.set("")

    # save settings
    write_global_vars({"var_det_model_idx": dpd_options_model[lang_idx].index(var_det_model.get()), # write index instead of value
                        "var_det_model_short": var_det_model_short.get(),
                        "var_det_model_path": var_det_model_path.get()})

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
    if frame.cget('text').startswith(f' {step_txt[lang_idx]} 2'):
        if os.path.isfile(image_recognition_file):
            open_file_or_folder(image_recognition_file)
        if os.path.isfile(video_recognition_file):
            open_file_or_folder(video_recognition_file)
    
    # open destination folder at step 4
    if frame.cget('text').startswith(f' {step_txt[lang_idx]} 4'):
        open_file_or_folder(var_output_dir.get())

# open file or folder
def open_file_or_folder(path):
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")
    
    # set language var
    error_opening_results_txt = ["Error opening results", "Error al abrir los resultados"]

    # open file
    if platform.system() == 'Darwin': # mac  
        try:
            subprocess.call(('open', path))
        except:
            mb.showerror(error_opening_results_txt[lang_idx], [f"Could not open '{path}'. You'll have to find it yourself...",
                                                           f"No se ha podido abrir '{path}'. Tendrás que encontrarlo tú mismo..."][lang_idx])
    elif platform.system() == 'Windows': # windows
        try:
            os.startfile(path)
        except:
            mb.showerror(error_opening_results_txt[lang_idx], [f"Could not open '{path}'. You'll have to find it yourself...",
                                                           f"No se ha podido abrir '{path}'. Tendrás que encontrarlo tú mismo..."][lang_idx])
    else: # linux
        try:
            subprocess.call(('xdg-open', path))
        except:
            try:
                subprocess.call(('gnome-open', path))
            except:
                mb.showerror(error_opening_results_txt[lang_idx], [f"Could not open '{path}'. Neither the 'xdg-open' nor 'gnome-open' command worked. "
                                                               "You'll have to find it yourself...",
                                                               f"No se ha podido abrir '{path}'. Ni el comando 'xdg-open' ni el 'gnome-open' funcionaron. "
                                                               "Tendrá que encontrarlo usted mismo..."][lang_idx])

# retrieve model specific vaiables from file 
def load_model_vars(model_type = "cls"):
    if var_cls_model.get() in none_txt and model_type == "cls":
        return {}
    model_dir = var_cls_model.get() if model_type == "cls" else var_det_model.get()
    var_file = os.path.join(EcoAssist_files, "models", model_type, model_dir, "variables.json")
    try:
        with open(var_file, 'r') as file:
            variables = json.load(file)
        return variables
    except:
        return {}

# write global vaiables to file 
def write_global_vars(new_values = None):
    # adjust
    variables = load_global_vars()
    if new_values is not None:
        for key, value in new_values.items():
            if key in variables:
                variables[key] = value
            else:
                print(f"Warning: Variable {key} not found in the loaded model variables.")

    # write
    var_file = os.path.join(EcoAssist_files, "EcoAssist", "global_vars.json")
    with open(var_file, 'w') as file:
        json.dump(variables, file, indent=4)

# check which models are known and should be listed in the dpd
def fetch_known_models(root_dir):
    return sorted([subdir for subdir in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, subdir))])

# convert plt graph to img via in-memory buffer
def fig2img(fig):
    import io
    buf = io.BytesIO()
    fig.savefig(buf)
    buf.seek(0)
    img = Image.open(buf)
    return img

# make piechart from results.xlsx
def create_pie_chart(file_path, looks, st_angle = 45):

    # log
    print(f"EXECUTED : {sys._getframe().f_code.co_name}({locals()})\n")

    df = pd.read_excel(file_path, sheet_name='summary')
    labels = df['label']
    detections = df['n_detections']
    total_detections = sum(detections)
    percentages = (detections / total_detections) * 100
    rows = []
    for i in range(len(labels.values.tolist())):
        rows.append([labels.values.tolist()[i],
                     detections.values.tolist()[i],
                     f"{round(percentages.values.tolist()[i], 1)}%"])
    _, ax = plt.subplots(figsize=(6, 3), subplot_kw=dict(aspect="equal"), facecolor="#CFCFCF")
    wedges, _ = ax.pie(detections, startangle=st_angle, colors=sns.color_palette('Set2'))
    bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
    if looks != "no-lines":
        kw = dict(arrowprops=dict(arrowstyle="-"),
                bbox=bbox_props, zorder=0, va="center")
    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1) / 2. + p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        connectionstyle = f"angle,angleA=0,angleB={ang}"
        if looks == "nice":
            kw["arrowprops"].update({"connectionstyle": connectionstyle}) # nicer, but sometimes raises bug: https://github.com/matplotlib/matplotlib/issues/12820
        elif looks == "simple":
            kw["arrowprops"].update({"arrowstyle": '-'})
        if looks != "no-lines":
            ax.annotate(labels[i], xy=(x, y), xytext=(1.35*np.sign(x), 1.4*y),
                        horizontalalignment=horizontalalignment, **kw)
    img = fig2img(plt)
    plt.close()
    return [img, rows]

# format the appropriate size unit
def format_size(size):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{round(size)} {unit}"
        size /= 1024.0

# function to create a dir and create a model_vars.json
# it does not yet download the model, but it will show up in the dropdown
def set_up_unkown_model(title, model_dict, model_type):
    model_dir = os.path.join(EcoAssist_files, "models", model_type, title)
    Path(model_dir).mkdir(parents=True, exist_ok=True)
    var_file = os.path.join(model_dir, "variables.json")
    with open(var_file, "w") as vars:
        json.dump(model_dict, vars, indent=2)

# check if this is the first startup since install 
def is_first_startup():
    return os.path.exists(os.path.join(EcoAssist_files, "first-startup.txt"))

# remove the first startup file
def remove_first_startup_file():
    first_startup_file = os.path.join(EcoAssist_files, "first-startup.txt")
    os.remove(first_startup_file)

# this function downloads a json with model info and tells the user is there is something new
def fetch_latest_model_info():
    start_time = time.time()
    model_info_url = f"https://raw.githubusercontent.com/PetervanLunteren/EcoAssist-model-info/main/model_info_v{corresponding_model_info_version}.json"
    model_info_local = os.path.join(EcoAssist_files, "EcoAssist", "model_info.json")

    # try downloading latest model info
    try:
        response = requests.get(model_info_url, timeout=1)
        if response.status_code == 200:
            with open(model_info_local, 'wb') as file:
                file.write(response.content)

            # log success
            print(f"Updated model_info.json successfully.")

            # check if there is a new model available
            model_info = json.load(open(model_info_local))
            for typ in ["det", "cls"]:
                model_dicts = model_info[typ] 
                all_models = list(model_dicts.keys())
                known_models = fetch_known_models(CLS_DIR if typ == "cls" else DET_DIR)
                unknown_models = [e for e in all_models if e not in known_models]
                
                # all models are treated unknown during first startup
                if is_first_startup():
                    unknown_models = all_models

                # show a description of all the unknown models, except if first startup
                if unknown_models != []:
                    for model_id in unknown_models:
                        model_dict = model_dicts[model_id]
                        if not is_first_startup():
                            show_model_info(title = model_id, model_dict = model_dict, new_model = True)
                        set_up_unkown_model(title = model_id, model_dict = model_dict, model_type = typ)
                
            # remove first startup file when its done
            if is_first_startup():
                remove_first_startup_file()

            # update root so that the new models show up in the dropdown menu
            update_model_dropdowns()

    except requests.exceptions.Timeout:
        print("Request timed out. File download stopped.")

    except Exception as e:
        print(f"Could not update model info: {e}")

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"model info updated in {round(elapsed_time, 2)} seconds")

# check if the user needs an update
def needs_EA_update(required_version):
    current_parts = list(map(int, current_EA_version.split('.')))
    required_parts = list(map(int, required_version.split('.')))

    # Pad the shorter version with zeros
    while len(current_parts) < len(required_parts):
        current_parts.append(0)
    while len(required_parts) < len(current_parts):
        required_parts.append(0)

    # Compare each part of the version
    for current, required in zip(current_parts, required_parts):
        if current < required:
            return True  # current_version is lower than required_version
        elif current > required:
            return False  # current_version is higher than required_version

    # All parts are equal, consider versions equal
    return False

# download required files for a particular model
def download_model(model_dir):
    # init vars
    model_title = os.path.basename(model_dir)
    model_type = os.path.basename(os.path.dirname(model_dir))
    model_vars = load_model_vars(model_type = model_type)
    download_info = model_vars["download_info"]

    # download
    try:
        try:
            # some models have multiple files to be downloaded
            # check the total size first
            total_size = 0
            for download_url, _ in download_info:
                response = requests.get(download_url, stream=True)
                response.raise_for_status()
                total_size += int(response.headers.get('content-length', 0))

        except Exception as error:
            # Let the user know there is no internet connection
            print("ERROR:\n" + str(error) + "\n\nDETAILS:\n" + str(traceback.format_exc()) + "\n\n")
            mb.showerror(["Download required", "Descarga necesaria"][lang_idx],
                         message = [f"The model '{model_title}' is not downloaded yet and it seems like there is no internet connection.",
                                    f"El modelo '{model_title}' aún no se ha descargado y parece que no hay conexión a Internet."][lang_idx],
                         detail = ["If you want to know the size of the model file and decide whether you want to download it, make "
                                   "sure you have an internet connection.", "Si desea conocer el tamaño del archivo del modelo y decidir si "
                                   "desea descargarlo, asegúrese de que dispone de conexión a Internet."][lang_idx])
            return False
           
        # check if the user wants to download
        if not mb.askyesno(["Download required", "Descarga necesaria"][lang_idx],
                        [f"The model {model_title} is not downloaded yet. It will take {format_size(total_size)}"
                            f" of storage. Do you want to download?", f"El modelo {model_title} aún no se ha descargado."
                            f" Ocupará {format_size(total_size)} de almacenamiento. ¿Desea descargarlo?"][lang_idx]):
            return False
        
        # if yes, initiate download and show progress
        progress_bar = tqdm(total=total_size, unit='B', unit_scale=True)
        download_popup = ModelDownloadProgressWindow(model_title = model_title, total_size_str = format_size(total_size))
        download_popup.open()
        for download_url, fname in download_info:
            file_path = os.path.join(model_dir, fname)
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            
            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        progress_bar.update(len(chunk))
                        percentage_done = progress_bar.n / total_size
                        download_popup.update_progress(percentage_done)
        progress_bar.close()
        download_popup.close()
        print(f"Download successful. File saved at: {file_path}")
        return True

    # catch errors
    except Exception as error:
        print("ERROR:\n" + str(error) + "\n\nDETAILS:\n" + str(traceback.format_exc()) + "\n\n")
        mb.showerror(title=error_txt[lang_idx],
                        message=[f"Something went wrong when trying to download the model '{model_title}'. Are you sure you are connected to the internet?",
                                 f"Algo ha ido mal al intentar descargar el modelo '{model_title}'. Está seguro de que está conectado a internet?"][lang_idx],
                        detail=["An error has occurred", "Ha ocurrido un error"][lang_idx] + " (EcoAssist v" + current_EA_version + "): '" + str(error) + "'.")

##############################################
############# FRONTEND FUNCTIONS #############
##############################################

# open frame to select species for advanc mode
def open_species_selection():

    # retrieve model specific variable values
    model_vars = load_model_vars()
    all_classes = model_vars['all_classes']
    selected_classes = model_vars['selected_classes']

    # on window closing
    def save():
        selected_classes = scrollable_checkbox_frame.get_checked_items()
        dsp_choose_classes.configure(text = f"{len(selected_classes)} of {len(all_classes)}")
        write_model_vars(new_values = {"selected_classes": selected_classes})
        model_cls_animal_options(var_cls_model.get())
        ss_root.withdraw()
    
    # on seleciton change
    def on_selection():
        selected_classes = scrollable_checkbox_frame.get_checked_items()
        lbl2.configure(text = f"{['Selected', 'Seleccionadas'][lang_idx]} {len(selected_classes)} {['of', 'de'][lang_idx]} {len(all_classes)}")

    # create window
    ss_root = customtkinter.CTkToplevel(root)
    ss_root.title("Species selection")
    # ss_root.attributes('-topmost',1)
    bring_window_to_top_but_not_for_ever(ss_root)
    spp_frm_1 = customtkinter.CTkFrame(master=ss_root)
    spp_frm_1.grid(row=0, column=0, padx=PADX, pady=PADY, sticky="nswe")
    spp_frm = customtkinter.CTkFrame(master=spp_frm_1, width=1000)
    spp_frm.grid(row=0, column=0, padx=PADX, pady=PADY, sticky="nswe")
    lbl1 = customtkinter.CTkLabel(spp_frm, text=["Which species are present in your project area?", 
                                                 "¿Qué especies están presentes en la zona de su proyecto?"][lang_idx],
                                                 font = main_label_font)
    lbl1.grid(row=0, column=0, padx=2*PADX, pady=PADY, columnspan = 2, sticky="nsw")
    lbl2 = customtkinter.CTkLabel(spp_frm, text="")
    lbl2.grid(row=1, column=0, padx=2*PADX, pady=0, columnspan = 2, sticky="nsw")
    scrollable_checkbox_frame = SpeciesSelectionFrame(master=spp_frm, command=on_selection,
                                                      height=400, width=500,
                                                      all_classes=all_classes,
                                                      selected_classes=selected_classes)
    scrollable_checkbox_frame._scrollbar.configure(height=0)
    scrollable_checkbox_frame.grid(row=2, column=0, padx=PADX, pady=PADY, sticky="ew")

    # toggle selection count with dummy event
    on_selection()

    # catch window close events
    close_button = customtkinter.CTkButton(ss_root, text="OK", command=save)
    close_button.grid(row=3, column=0, padx=PADX, pady=(0, PADY), columnspan = 2, sticky="nswe")
    ss_root.protocol("WM_DELETE_WINDOW", save)

class MyMainFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.columnconfigure(0, weight=1, minsize=70)
        self.columnconfigure(1, weight=1, minsize=350)

class MySubFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.columnconfigure(0, weight=1, minsize=250)
        self.columnconfigure(1, weight=1, minsize=250)

class MySubSubFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

class InfoButton(customtkinter.CTkButton):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color = ("#DBDBDB", "#333333"),
                       hover = False,
                       text_color = ("grey", "grey"),
                       height = 1,
                       width = 1)

def sim_dir_show_info():
    mb.showinfo(title = information_txt[lang_idx],
                message = ["Select the images to analyse", "Seleccionar las imágenes a analizar"][lang_idx],
                detail = ["Here you can select a folder containing camera trap images. It will process all images it can find, also in subfolders."
                          " Switch to advanced mode for more options.", " Aquí puede seleccionar una carpeta que contenga imágenes de cámaras trampa."
                          " Procesará todas las imágenes que encuentre, también en las subcarpetas. Cambia al modo avanzado para más opciones."][lang_idx])

def callback(url):
    webbrowser.open_new(url)

def sim_spp_show_info():
    mb.showinfo(title = information_txt[lang_idx],
                message = ["Select the species that are present", "Seleccione las especies presentes"][lang_idx],
                detail = ["Here, you can select and deselect the animals categories that are present in your project"
                          " area. If the animal category is not selected, it will be excluded from the results. The "
                          "category list will update according to the model selected.", "Aquí puede seleccionar y anular"
                          " la selección de las categorías de animales presentes en la zona de su proyecto. Si la "
                          "categoría de animales no está seleccionada, quedará excluida de los resultados. La lista de "
                          "categorías se actualizará según el modelo seleccionado."][lang_idx])

def on_spp_selection():
    selected_classes = sim_spp_scr.get_checked_items()
    all_classes = sim_spp_scr.get_all_items()
    write_model_vars(new_values = {"selected_classes": selected_classes})
    dsp_choose_classes.configure(text = f"{len(selected_classes)} of {len(all_classes)}")

def sim_mdl_show_info():
    if var_cls_model.get() in none_txt:
        mb.showinfo(title = information_txt[lang_idx],
                    message = ["Select the model to identify animals", "Seleccione el modelo para identificar animales"][lang_idx],
                    detail = ["Here, you can choose a model that can identify your target species. If you select ‘None’, it will find vehicles,"
                              " people, and animals, but will not further identify them. When a model is selected, press this button again to "
                              "read more about the model in question.", "Aquí, puede elegir un modelo que pueda identificar su especie objetivo."
                              " Si selecciona 'Ninguno', encontrará vehículos, personas y animales, pero no los identificará más. Cuando haya "
                              "seleccionado un modelo, vuelva a pulsar este botón para obtener más información sobre el modelo en cuestión."][lang_idx])
    else:
        show_model_info()


def checkbox_frame_event():
    print(f"checkbox frame modified: {sim_spp_scr.get_checked_items()}")

# class to list species with checkboxes
class SpeciesSelectionFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, all_classes = [], selected_classes = [], command=None, dummy_spp = False, **kwargs):
        super().__init__(master, **kwargs)
        self.dummy_spp = dummy_spp
        if dummy_spp:
            all_classes = [f"{['Species', 'Especies'][lang_idx]} {i+1}" for i in range(10)]
        self.command = command
        self.checkbox_list = []
        self.selected_classes = selected_classes
        for item in all_classes:
            self.add_item(item)

    def add_item(self, item):
        checkbox = customtkinter.CTkCheckBox(self, text=item)
        if self.dummy_spp:
            checkbox.configure(state="disabled")
        if item in self.selected_classes:
            checkbox.select()
        if self.command is not None:
            checkbox.configure(command=self.command)
        checkbox.grid(row=len(self.checkbox_list), column=0, pady=PADY, sticky="nsw")
        self.checkbox_list.append(checkbox)

    def get_checked_items(self):
        return [checkbox.cget("text") for checkbox in self.checkbox_list if checkbox.get() == 1]
    
    def get_all_items(self):
        return [checkbox.cget("text") for checkbox in self.checkbox_list]

# show download progress
class ModelDownloadProgressWindow:
    def __init__(self, model_title, total_size_str):
        self.dm_root = customtkinter.CTkToplevel(root)
        self.dm_root.title("Download progress")
        self.frm = customtkinter.CTkFrame(master=self.dm_root)
        self.frm.grid(row=1, column=0, padx=PADX, pady=PADY, sticky="nswe")
        self.frm.columnconfigure(0, weight=1, minsize=500)
        self.lbl = customtkinter.CTkLabel(self.dm_root, text=f"Downloading model '{model_title}' ({total_size_str})", 
                                          font = customtkinter.CTkFont(family='CTkFont', size=14, weight = 'bold'))
        self.lbl.grid(row=0, column=0, padx=PADX, pady=(PADY, 0), sticky="nsew")
        self.pbr = customtkinter.CTkProgressBar(self.frm, orientation="horizontal", height=28, corner_radius=5, width=1)
        self.pbr.set(0)
        self.pbr.grid(row=1, column=0, padx=PADX, pady=PADY, sticky="nsew")
        self.per = customtkinter.CTkLabel(self.frm, text=f" 0% ", height=5, fg_color=("#949BA2", "#4B4D50"), text_color="white")
        self.per.grid(row=1, column=0, padx=PADX, pady=PADY, sticky="")
        self.dm_root.withdraw()

    def open(self):
        self.dm_root.update()
        self.dm_root.deiconify()

    def update_progress(self, percentage):
        self.pbr.set(percentage)
        self.per.configure(text = f" {round(percentage * 100)}% ")
        if percentage > 0.5:
            self.per.configure(fg_color=("#3B8ECF", "#1F6BA5"))
        else:
            self.per.configure(fg_color=("#949BA2", "#4B4D50"))
        self.dm_root.update()

    def close(self):
        self.dm_root.destroy()

# make sure the window pops up in front initially, but does not stay on top if the users selects an other window
def bring_window_to_top_but_not_for_ever(master):
    def lift_toplevel():
        master.lift()
        master.attributes('-topmost', False)
    master.attributes('-topmost', True)
    master.after(100, lift_toplevel)

# open window with model info
def show_model_info(title = None, model_dict = None, new_model = False):
    
    # fetch current selected model if title and model_dict are not supplied
    if title is None:
        title = var_cls_model.get()
    if model_dict is None:
        model_dict = load_model_vars()

    # read vars from json
    description_var = model_dict.get("description", "")
    developer_var = model_dict.get("developer", "")
    classes_list = model_dict.get("all_classes", [])
    url_var = model_dict.get("info_url", "")
    min_version = model_dict.get("min_version", "1000.1")
    citation = model_dict.get("citation", "")
    citation_present = False if citation == "" else True
    needs_EA_update_bool = needs_EA_update(min_version)
    if needs_EA_update_bool:
        update_var = f"Your current EcoAssist version (v{current_EA_version}) will not be able to run this model. An update is required."
    else:
        update_var = f"Current version of EcoAssist (v{current_EA_version}) is able to use this model. No update required."
    
    # define functions
    def close():
        nm_root.destroy()
    def read_more():
        webbrowser.open(url_var)
    def update():
        webbrowser.open("https://addaxdatascience.com/ecoassist/")
    def cite():
        webbrowser.open(citation)

    # create window
    nm_root = customtkinter.CTkToplevel(root)
    nm_root.title("Model information")
    bring_window_to_top_but_not_for_ever(nm_root)

    # new model label
    if new_model:
        lbl = customtkinter.CTkLabel(nm_root, text="New model available!", font = main_label_font)
        lbl.grid(row=0, column=0, padx=PADX, pady=(PADY, PADY/4), columnspan = 2, sticky="nswe")

    # title frame
    title_frm_1 = model_info_frame(master=nm_root)
    title_frm_1.grid(row=1, column=0, padx=PADX, pady=PADY, sticky="nswe")
    title_frm_2 = model_info_frame(master=title_frm_1)
    title_frm_2.grid(row=0, column=1, padx=(0, PADX), pady=PADY, sticky="nswe")
    title_lbl_1 = customtkinter.CTkLabel(title_frm_1, text="Title", font = main_label_font)
    title_lbl_1.grid(row=0, column=0, padx=PADX, pady=(0, PADY/4), sticky="nse")
    title_lbl_2 = customtkinter.CTkLabel(title_frm_2, text=title)
    title_lbl_2.grid(row=0, column=0, padx=PADX, pady=(0, PADY/4), columnspan = 2, sticky="nsw")

    # developer frame
    devop_frm_1 = model_info_frame(master=nm_root)
    devop_frm_1.grid(row=2, column=0, padx=PADX, pady=(0, PADY), sticky="nswe")
    devop_frm_2 = model_info_frame(master=devop_frm_1)
    devop_frm_2.grid(row=0, column=1, padx=(0, PADX), pady=PADY, sticky="nswe")
    devop_lbl_1 = customtkinter.CTkLabel(devop_frm_1, text="Developer", font = main_label_font)
    devop_lbl_1.grid(row=0, column=0, padx=PADX, pady=(0, PADY/4), sticky="nse")
    devop_lbl_2 = customtkinter.CTkLabel(devop_frm_2, text=developer_var)
    devop_lbl_2.grid(row=0, column=0, padx=PADX, pady=(0, PADY/4), columnspan = 2, sticky="nsw")

    # description frame
    descr_frm_1 = model_info_frame(master=nm_root)
    descr_frm_1.grid(row=3, column=0, padx=PADX, pady=(0, PADY), sticky="nswe")
    descr_frm_2 = model_info_frame(master=descr_frm_1)
    descr_frm_2.grid(row=0, column=1, padx=(0, PADX), pady=PADY, sticky="nswe")
    descr_lbl_1 = customtkinter.CTkLabel(descr_frm_1, text="Description", font = main_label_font)
    descr_lbl_1.grid(row=0, column=0, padx=PADX, pady=(0, PADY/4), sticky="nse")
    descr_txt_1 = customtkinter.CTkTextbox(master=descr_frm_2, corner_radius=10, height = 150, wrap = "word", fg_color = "transparent")
    descr_txt_1.grid(row=0, column=0, padx=PADX/4, pady=(0, PADY/4), columnspan = 2, sticky="nswe")
    descr_txt_1.insert("0.0", description_var)
    descr_txt_1.configure(state="disabled")

    # classes frame
    class_frm_1 = model_info_frame(master=nm_root)
    class_frm_1.grid(row=4, column=0, padx=PADX, pady=(0, PADY), sticky="nswe")
    class_frm_2 = model_info_frame(master=class_frm_1)
    class_frm_2.grid(row=0, column=1, padx=(0, PADX), pady=PADY, sticky="nswe")
    class_lbl_1 = customtkinter.CTkLabel(class_frm_1, text="Classes", font = main_label_font)
    class_lbl_1.grid(row=0, column=0, padx=PADX, pady=(0, PADY/4), sticky="nse")
    class_txt_1 = customtkinter.CTkTextbox(master=class_frm_2, corner_radius=10, height = 150, wrap = "word", fg_color = "transparent")
    class_txt_1.grid(row=0, column=0, padx=PADX/4, pady=(0, PADY/4), columnspan = 2, sticky="nswe")
    for spp_class in classes_list:
        class_txt_1.insert(tk.END, f"• {spp_class}\n")
    class_txt_1.configure(state="disabled")

    # update frame
    updat_frm_1 = model_info_frame(master=nm_root)
    updat_frm_1.grid(row=5, column=0, padx=PADX, pady=(0, PADY), sticky="nswe")
    updat_frm_2 = model_info_frame(master=updat_frm_1)
    updat_frm_2.grid(row=0, column=1, padx=(0, PADX), pady=PADY, sticky="nswe")
    updat_lbl_1 = customtkinter.CTkLabel(updat_frm_1, text="Update", font = main_label_font)
    updat_lbl_1.grid(row=0, column=0, padx=PADX, pady=(0, PADY/4), sticky="nse")
    updat_lbl_2 = customtkinter.CTkLabel(updat_frm_2, text=update_var)
    updat_lbl_2.grid(row=0, column=0, padx=PADX, pady=(0, PADY/4), columnspan = 2, sticky="nsw")

    # buttons frame
    n_btns = 2
    if needs_EA_update_bool: n_btns += 1
    if citation_present: n_btns += 1
    btns_frm = customtkinter.CTkFrame(master=nm_root)
    for col in range(0, n_btns):
        btns_frm.columnconfigure(col, weight=1, minsize=10)
    btns_frm.grid(row=6, column=0, padx=PADX, pady=(0, PADY), sticky="nswe")
    close_btn = customtkinter.CTkButton(btns_frm, text="Close", command=close)
    close_btn.grid(row=0, column=0, padx=PADX, pady=PADY, sticky="nswe")
    lmore_btn = customtkinter.CTkButton(btns_frm, text="Learn more", command=read_more)
    lmore_btn.grid(row=0, column=1, padx=(0, PADX), pady=PADY, sticky="nwse")
    ncol = 2
    if needs_EA_update_bool:
        updat_btn = customtkinter.CTkButton(btns_frm, text="Update", command=update)
        updat_btn.grid(row=0, column=ncol, padx=(0, PADX), pady=PADY, sticky="nwse")
        ncol += 1
    if citation_present:
        citat_btn = customtkinter.CTkButton(btns_frm, text="Cite", command=cite)
        citat_btn.grid(row=0, column=ncol, padx=(0, PADX), pady=PADY, sticky="nwse")
        ncol += 1

# class frame for model window
class model_info_frame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.columnconfigure(0, weight=1, minsize=120)
        self.columnconfigure(1, weight=1, minsize=500)

# make sure the latest updated models also are listed in the dpd menu
def update_model_dropdowns():
    global dpd_options_cls_model
    cls_models = fetch_known_models(CLS_DIR)
    dpd_options_cls_model = [["None"] + cls_models, ["Ninguno"] + cls_models]
    update_dpd_options(dpd_cls_model, snd_step, var_cls_model, dpd_options_cls_model, model_cls_animal_options, row_cls_model, lbl_cls_model, lang_idx)
    global dpd_options_model
    det_models = fetch_known_models(DET_DIR)
    dpd_options_model = [det_models + ["Custom model"], det_models + ["Otro modelo"]]
    update_dpd_options(dpd_model, snd_step, var_det_model, dpd_options_model, model_options, row_model, lbl_model, lang_idx)
    model_cls_animal_options(var_cls_model.get())
    global sim_dpd_options_cls_model
    sim_dpd_options_cls_model = [[item[0] + suffixes_for_sim_none[i], *item[1:]] for i, item in enumerate(dpd_options_cls_model)]
    update_sim_mdl_dpd()
    root.update_idletasks()

# window for quick results info while running simple mode
def show_result_info(file_path):
    
    # define functions
    def close():
        rs_root.withdraw()
    def more_options():
        switch_mode()
        rs_root.withdraw()

    file_path = os.path.normpath(file_path)

    # read results for xlsx file
    # some combinations of eprcentages raises a bug: https://github.com/matplotlib/matplotlib/issues/12820
    # hence we're going to try the nicest layout with some different angles, then an OK layout, and no
    # lines as last resort
    try:
        graph_img, table_rows = create_pie_chart(file_path, looks = "nice", st_angle = 0)
    except ValueError:
        print("ValueError - trying again with different params.")
        try:
            graph_img, table_rows = create_pie_chart(file_path, looks = "nice", st_angle = 23)
        except ValueError:
            print("ValueError - trying again with different params.")
            try:
                graph_img, table_rows = create_pie_chart(file_path, looks = "nice", st_angle = 45)
            except ValueError:
                print("ValueError - trying again with different params.")
                try:
                    graph_img, table_rows = create_pie_chart(file_path, looks = "nice", st_angle = 90)
                except ValueError:
                    print("ValueError - trying again with different params.")
                    try:
                        graph_img, table_rows = create_pie_chart(file_path, looks = "simple")
                    except ValueError:
                        print("ValueError - trying again with different params.")
                        graph_img, table_rows = create_pie_chart(file_path, looks = "no-lines")

    # create window
    rs_root = customtkinter.CTkToplevel(root)
    rs_root.title("Results - quick view")
    result_bg_image = customtkinter.CTkImage(PIL_gradient, size=(RESULTS_WINDOW_WIDTH, RESULTS_WINDOW_HEIGHT))
    result_bg_image_label = customtkinter.CTkLabel(rs_root, image=result_bg_image)
    result_bg_image_label.grid(row=0, column=0)
    result_main_frame = customtkinter.CTkFrame(rs_root, corner_radius=0, fg_color = 'transparent')
    result_main_frame.grid(row=0, column=0, sticky="ns")

    # label
    lbl1 = customtkinter.CTkLabel(result_main_frame, text=["The images are processed!", "¡Las imágenes están procesadas!"][lang_idx], font = main_label_font, height=20)
    lbl1.grid(row=0, column=0, padx=PADX, pady=(PADY, PADY/4), columnspan = 2, sticky="nswe")
    lbl2 = customtkinter.CTkLabel(result_main_frame, text=[f"The results are saved at '{file_path}'.", f"Los resultados se guardan en '{file_path}'."][lang_idx], height=20)
    lbl2.grid(row=1, column=0, padx=PADX, pady=(PADY/4, PADY/4), columnspan = 2, sticky="nswe")
    lbl3 = customtkinter.CTkLabel(result_main_frame, text=[f"You can find a quick overview of the results below.", f"A continuación encontrará un resumen de los resultados."][lang_idx], height=20)
    lbl3.grid(row=2, column=0, padx=PADX, pady=(PADY/4, PADY/4), columnspan = 2, sticky="nswe")

    # graph frame
    graph_frm_1 = model_info_frame(master=result_main_frame)
    graph_frm_1.grid(row=3, column=0, padx=PADX, pady=PADY, sticky="nswe")
    graph_frm_2 = model_info_frame(master=graph_frm_1)
    graph_frm_2.grid(row=0, column=1, padx=(0, PADX), pady=PADY, sticky="nswe")
    graph_lbl_1 = customtkinter.CTkLabel(graph_frm_1, text=["Graph", "Gráfico"][lang_idx], font = main_label_font)
    graph_lbl_1.grid(row=0, column=0, padx=PADX, pady=(0, PADY/4), sticky="nse")
    graph_img = customtkinter.CTkImage(graph_img, size=(600, 300))
    graph_lbl_2 = customtkinter.CTkLabel(graph_frm_2, text="", image = graph_img)
    graph_lbl_2.grid(row=0, column=0, padx=PADX, pady=(0, PADY/4), columnspan = 2, sticky="nsw")

    # developer frame
    table_frm_1 = model_info_frame(master=result_main_frame)
    table_frm_1.grid(row=4, column=0, padx=PADX, pady=(0, PADY), sticky="nswe")
    table_lbl_1 = customtkinter.CTkLabel(table_frm_1, text=["Table", "Tabla"][lang_idx], font = main_label_font)
    table_lbl_1.grid(row=0, column=0, padx=PADX, pady=(0, PADY/4), sticky="nse")
    table_scr_frm = customtkinter.CTkScrollableFrame(table_frm_1, width = RESULTS_TABLE_WIDTH)
    table_scr_frm.grid(row=0, column=1, columnspan = 3, padx=(0, PADX), pady=PADY, sticky="nesw")
    table_header = CTkTable(master=table_scr_frm,
                      column=3,
                      values=[[["Species", "Especie"][lang_idx], ["Count", "Cuenta"][lang_idx], ["Percentage", "Porcentaje"][lang_idx]]],
                      font = main_label_font,
                      color_phase = "horizontal",
                      header_color = customtkinter.ThemeManager.theme["CTkFrame"]["top_fg_color"],
                      wraplength = 130)
    table_header.grid(row=0, column=0, padx=PADX, pady=(PADY/4, 0), columnspan = 2, sticky="nesw")
    table_values = CTkTable(master=table_scr_frm,
                      column=3, 
                      values=table_rows,
                      color_phase = "horizontal",
                      wraplength = 130,
                      width = RESULTS_TABLE_WIDTH / 3 - PADX)
    table_values.grid(row=1, column=0, padx=PADX, pady=(0, PADY/4), columnspan = 2, sticky="nesw")

    # buttons frame
    btns_frm = customtkinter.CTkFrame(master=result_main_frame)
    btns_frm.grid(row=5, column=0, padx=PADX, pady=(0, PADY), sticky="nswe")
    btns_frm.columnconfigure(0, weight=1, minsize=10)
    btns_frm.columnconfigure(1, weight=1, minsize=10)
    btns_frm.columnconfigure(2, weight=1, minsize=10)
    close_btn = customtkinter.CTkButton(btns_frm, text=["Close window", "Cerrar ventana"][lang_idx], command=close)
    close_btn.grid(row=0, column=0, padx=PADX, pady=PADY, sticky="nswe")
    openf_btn = customtkinter.CTkButton(btns_frm, text=["Open file", "Abrir archivo"][lang_idx], command=lambda: open_file_or_folder(file_path))
    openf_btn.grid(row=0, column=1, padx=(0, PADX), pady=PADY, sticky="nwse")
    moreo_btn = customtkinter.CTkButton(btns_frm, text=["More options", "Otras opciones"][lang_idx], command=more_options)
    moreo_btn.grid(row=0, column=2, padx=(0, PADX), pady=PADY, sticky="nwse")

# class for simple question with buttons
class TextButtonWindow:
    def __init__(self, title, text, buttons):
        self.root = Toplevel(root)
        self.root.title(title)
        
        self.text_label = tk.Label(self.root, text=text)
        self.text_label.pack(padx=10, pady=10)
        
        self.selected_button = None
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(padx=10, pady=10)
        
        for button_text in buttons:
            button = tk.Button(self.button_frame, text=button_text, command=lambda btn=button_text: self._button_click(btn))
            button.pack(side=tk.LEFT, padx=5)
        
    def _button_click(self, button_text):
        self.selected_button = button_text
        self.root.quit()
        
    def open(self):
        self.root.mainloop()
        
    def close(self):
        self.root.destroy()
        
    def run(self):
        self.open()
        self.root.destroy()
        return self.selected_button

# simple window to show progressbar
class PatienceDialog:
    def __init__(self, total, text):
        self.root = Toplevel(root)
        self.root.title("Have patience")
        self.total = total
        self.text = text
        self.label = tk.Label(self.root, text=text)
        self.label.pack(pady=10)
        self.progress = ttk.Progressbar(self.root, mode='determinate', length=200)
        self.progress.pack(pady=10, padx = 10)
        self.root.withdraw()

    def open(self):
        self.root.update()
        self.root.deiconify()

    def update_progress(self, current, percentage = False):
        # updating takes considerable time - only do this 100 times
        if current % math.ceil(self.total / 100) == 0:
            self.progress['value'] = (current / self.total) * 100
            if percentage:
                percentage_value = round((current/self.total) * 100)
                self.label.configure(text = f"{self.text}\n{percentage_value}%")
            else:
                self.label.configure(text = f"{self.text}\n{current} of {self.total}")
            self.root.update()

    def close(self):
        self.root.destroy()

# simple window class to pop up and be closed
class CustomWindow:
    def __init__(self, title="", text=""):
        self.title = title
        self.text = text
        self.root = None

    def open(self):
        self.root = Toplevel(root)
        self.root.title(self.title)

        label = tk.Label(self.root, text=self.text)
        label.pack(padx=10, pady=10)

        self.root.update_idletasks()
        self.root.update()

    def close(self):
        self.root.destroy()

# disable annotation frame
def disable_ann_frame(row, hitl_ann_selection_frame):
    labelframe = hitl_ann_selection_frame.grid_slaves(row=row, column=3)[0]
    labelframe.configure(relief=SUNKEN)
    for widget in labelframe.winfo_children():
        widget.configure(state = DISABLED)

# enable annotation frame
def enable_ann_frame(row, hitl_ann_selection_frame):
    labelframe = hitl_ann_selection_frame.grid_slaves(row=row, column=3)[0]
    labelframe.configure(relief=RAISED)
    for widget in labelframe.winfo_children():
        widget.configure(state = NORMAL)

# show hide the annotation selection frame in the human-in-the-loop settings window
def toggle_hitl_ann_selection_frame(cmd = None):
    is_vis = hitl_ann_selection_frame.grid_info()
    if cmd == "hide":
        hitl_ann_selection_frame.grid_remove()
    else:
        if is_vis != {}:
            hitl_ann_selection_frame.grid_remove()
        else:
            hitl_ann_selection_frame.grid(column=0, row=2, columnspan=2, sticky='ew')
    hitl_settings_window.update()
    hitl_settings_canvas.configure(scrollregion=hitl_settings_canvas.bbox("all"))

# enable or disable the options in the human-in-the-loop annotation selection frame
def toggle_hitl_ann_selection(rad_ann_var, hitl_ann_selection_frame):
    rad_ann_var = rad_ann_var.get()    
    cols, rows = hitl_ann_selection_frame.grid_size()
    if rad_ann_var == 1:
        enable_ann_frame(1, hitl_ann_selection_frame)
        for row in range(2, rows):
            disable_ann_frame(row, hitl_ann_selection_frame)
    elif rad_ann_var == 2:
        disable_ann_frame(1, hitl_ann_selection_frame)
        for row in range(2, rows):
            enable_ann_frame(row, hitl_ann_selection_frame)


# update counts of the subset functions of the human-in-the-loop image selection frame
def enable_amt_per_ent(row):
    global selection_dict
    rad_var = selection_dict[row]['rad_var'].get()
    ent_per = selection_dict[row]['ent_per']
    ent_amt = selection_dict[row]['ent_amt']
    if rad_var == 1:
        ent_per.configure(state = DISABLED)
        ent_amt.configure(state = DISABLED)      
    if rad_var == 2:
        ent_per.configure(state = NORMAL)
        ent_amt.configure(state = DISABLED)
    if rad_var == 3:
        ent_per.configure(state = DISABLED)
        ent_amt.configure(state = NORMAL)

# show or hide widgets in the human-in-the-loop image selection frame
def enable_selection_widgets(row):
    global selection_dict
    frame = selection_dict[row]['frame']
    chb_var = selection_dict[row]['chb_var'].get()
    lbl_class = selection_dict[row]['lbl_class']
    rsl = selection_dict[row]['range_slider_widget']
    rad_all = selection_dict[row]['rad_all']
    rad_per = selection_dict[row]['rad_per']
    rad_amt = selection_dict[row]['rad_amt']
    lbl_n_img = selection_dict[row]['lbl_n_img']
    if chb_var:
        frame.configure(relief = RAISED)
        lbl_class.configure(state = NORMAL)
        rsl.grid(row = 0, rowspan= 3, column = 2)
        rad_all.configure(state = NORMAL)
        rad_per.configure(state = NORMAL)
        rad_amt.configure(state = NORMAL)
        lbl_n_img.configure(state = NORMAL)
    else:
        frame.configure(relief = SUNKEN)
        lbl_class.configure(state = DISABLED)
        rsl.grid_remove()
        rad_all.configure(state = DISABLED)
        rad_per.configure(state = DISABLED)
        rad_amt.configure(state = DISABLED)
        lbl_n_img.configure(state = DISABLED)

# front end class for cancel button
class CancelButton(customtkinter.CTkButton):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color = ("#DBDBDB", "#4B4D50"),
                       hover_color = ("#949BA2", "#2B2B2B"),
                       text_color = ("black", "white"),
                       height = 10,
                       width = 120)

# open progress window for deploy and postprocess
class ProgressWindow:
    def __init__(self, processes):
        self.progress_top_level_window = customtkinter.CTkToplevel()
        self.progress_top_level_window.title("Analysis progress")
        lbl_height = 20

        # language settings
        in_queue_txt = ['In queue', 'En cola']
        processing_image_txt = ['Processing image', 'Procesamiento de imágenes']
        processing_animal_txt = ['Processing animal', 'Procesamiento de animales']
        processing_frame_txt = ['Processing frame', 'Procesamiento de fotogramas']
        images_per_second_txt = ['Images per second', 'Imágenes por segundo']
        animals_per_second_txt = ['Animals per second', 'Animales por segundo']
        frames_per_second_txt = ['Frames per second', 'Fotogramas por segundo']
        elapsed_time_txt = ["Elapsed time", "Tiempo transcurrido"]
        remaining_time_txt = ["Remaining time", "Tiempo restante"]
        running_on_txt = ["Running on", "Funcionando en"]

        # clarify titles if both images and videos are being processed
        if "img_det" in processes and "vid_det" in processes:
            img_det_extra_string = [" in images", " en imágenes"][lang_idx]
            vid_det_extra_string = [" in videos", " en vídeos"][lang_idx]
        else:
            img_det_extra_string = ""
            vid_det_extra_string = ""
        if "img_pst" in processes and "vid_pst" in processes:
            img_pst_extra_string = [" images", " de imágenes"][lang_idx]
            vid_pst_extra_string = [" videos", " de vídeos"][lang_idx]
        else:
            img_pst_extra_string = ""
            vid_pst_extra_string = ""

        # initialise image detection process
        if "img_det" in processes:
            self.img_det_frm = customtkinter.CTkFrame(master=self.progress_top_level_window)
            self.img_det_frm.grid(row=0, padx=PADX, pady=PADY, sticky="nswe")
            img_det_ttl_txt = [f'Localizing animals{img_det_extra_string}...', f'Localización de animales{img_det_extra_string}...']
            self.img_det_ttl = customtkinter.CTkLabel(self.img_det_frm, text=img_det_ttl_txt[lang_idx], 
                                            font = customtkinter.CTkFont(family='CTkFont', size=14, weight = 'bold'))
            self.img_det_ttl.grid(row=0, padx=PADX * 2, pady=(PADY, 0), columnspan = 2, sticky="nsw")
            self.img_det_sub_frm = customtkinter.CTkFrame(master=self.img_det_frm)
            self.img_det_sub_frm.grid(row=1, padx=PADX, pady=PADY, sticky="nswe", ipady=PADY/2)
            self.img_det_sub_frm.columnconfigure(0, weight=1, minsize=300)
            self.img_det_pbr = customtkinter.CTkProgressBar(self.img_det_sub_frm, orientation="horizontal", height=28, corner_radius=5, width=1)
            self.img_det_pbr.set(0)
            self.img_det_pbr.grid(row=0, padx=PADX, pady=PADY, sticky="nsew")
            self.img_det_per = customtkinter.CTkLabel(self.img_det_sub_frm, text=f" 0% ", height=5, fg_color=("#949BA2", "#4B4D50"), text_color="white")
            self.img_det_per.grid(row=0, padx=PADX, pady=PADY, sticky="")
            self.img_det_wai_lbl = customtkinter.CTkLabel(self.img_det_sub_frm, height = lbl_height, text=in_queue_txt[lang_idx])
            self.img_det_wai_lbl.grid(row=1, padx=PADX, pady=0, sticky="nsew")
            self.img_det_num_lbl = customtkinter.CTkLabel(self.img_det_sub_frm, height = lbl_height, text=f"{processing_image_txt[lang_idx]}:")
            self.img_det_num_lbl.grid(row=2, padx=PADX, pady=0, sticky="nsw")
            self.img_det_num_lbl.grid_remove()
            self.img_det_num_val = customtkinter.CTkLabel(self.img_det_sub_frm, height = lbl_height, text=f"")
            self.img_det_num_val.grid(row=2, padx=PADX, pady=0, sticky="nse")
            self.img_det_num_val.grid_remove()
            self.img_det_ela_lbl = customtkinter.CTkLabel(self.img_det_sub_frm, height = lbl_height, text=f"{elapsed_time_txt[lang_idx]}:")
            self.img_det_ela_lbl.grid(row=3, padx=PADX, pady=0, sticky="nsw")
            self.img_det_ela_lbl.grid_remove()
            self.img_det_ela_val = customtkinter.CTkLabel(self.img_det_sub_frm, height = lbl_height, text=f"")
            self.img_det_ela_val.grid(row=3, padx=PADX, pady=0, sticky="nse")     
            self.img_det_ela_val.grid_remove()
            self.img_det_rem_lbl = customtkinter.CTkLabel(self.img_det_sub_frm, height = lbl_height, text=f"{remaining_time_txt[lang_idx]}:")
            self.img_det_rem_lbl.grid(row=4, padx=PADX, pady=0, sticky="nsw")
            self.img_det_rem_lbl.grid_remove()
            self.img_det_rem_val = customtkinter.CTkLabel(self.img_det_sub_frm, height = lbl_height, text=f"")
            self.img_det_rem_val.grid(row=4, padx=PADX, pady=0, sticky="nse")
            self.img_det_rem_val.grid_remove()
            self.img_det_spe_lbl = customtkinter.CTkLabel(self.img_det_sub_frm, height = lbl_height, text=f"{images_per_second_txt[lang_idx]}:")
            self.img_det_spe_lbl.grid(row=5, padx=PADX, pady=0, sticky="nsw")
            self.img_det_spe_lbl.grid_remove()
            self.img_det_spe_val = customtkinter.CTkLabel(self.img_det_sub_frm, height = lbl_height, text=f"")
            self.img_det_spe_val.grid(row=5, padx=PADX, pady=0, sticky="nse")
            self.img_det_spe_val.grid_remove()
            self.img_det_hwa_lbl = customtkinter.CTkLabel(self.img_det_sub_frm, height = lbl_height, text=f"{running_on_txt[lang_idx]}:")
            self.img_det_hwa_lbl.grid(row=6, padx=PADX, pady=0, sticky="nsw")
            self.img_det_hwa_lbl.grid_remove()
            self.img_det_hwa_val = customtkinter.CTkLabel(self.img_det_sub_frm, height = lbl_height, text=f"")
            self.img_det_hwa_val.grid(row=6, padx=PADX, pady=0, sticky="nse")
            self.img_det_hwa_val.grid_remove()
            self.img_det_can_btn = CancelButton(master = self.img_det_sub_frm, text = "Cancel", command = lambda: print(""))
            self.img_det_can_btn.grid(row=7, padx=PADX, pady=(PADY, 0), sticky="ns")
            self.img_det_can_btn.grid_remove()

        # initialise image classification process
        if "img_cls" in processes:
            self.img_cls_frm = customtkinter.CTkFrame(master=self.progress_top_level_window)
            self.img_cls_frm.grid(row=1, padx=PADX, pady=PADY, sticky="nswe")
            img_cls_ttl_txt = [f'Identifying animals{img_det_extra_string}...', f'Identificación de animales{img_det_extra_string}...']
            self.img_cls_ttl = customtkinter.CTkLabel(self.img_cls_frm, text=img_cls_ttl_txt[lang_idx], 
                                            font = customtkinter.CTkFont(family='CTkFont', size=14, weight = 'bold'))
            self.img_cls_ttl.grid(row=0, padx=PADX * 2, pady=(PADY, 0), columnspan = 2, sticky="nsw")
            self.img_cls_sub_frm = customtkinter.CTkFrame(master=self.img_cls_frm)
            self.img_cls_sub_frm.grid(row=1, padx=PADX, pady=PADY, sticky="nswe", ipady=PADY/2)
            self.img_cls_sub_frm.columnconfigure(0, weight=1, minsize=300)
            self.img_cls_pbr = customtkinter.CTkProgressBar(self.img_cls_sub_frm, orientation="horizontal", height=28, corner_radius=5, width=1)
            self.img_cls_pbr.set(0)
            self.img_cls_pbr.grid(row=0, padx=PADX, pady=PADY, sticky="nsew")
            self.img_cls_per = customtkinter.CTkLabel(self.img_cls_sub_frm, text=f" 0% ", height=5, fg_color=("#949BA2", "#4B4D50"), text_color="white")
            self.img_cls_per.grid(row=0, padx=PADX, pady=PADY, sticky="")
            self.img_cls_wai_lbl = customtkinter.CTkLabel(self.img_cls_sub_frm, height = lbl_height, text=in_queue_txt[lang_idx])
            self.img_cls_wai_lbl.grid(row=1, padx=PADX, pady=0, sticky="nsew")
            self.img_cls_num_lbl = customtkinter.CTkLabel(self.img_cls_sub_frm, height = lbl_height, text=f"{processing_animal_txt[lang_idx]}:")
            self.img_cls_num_lbl.grid(row=2, padx=PADX, pady=0, sticky="nsw")
            self.img_cls_num_lbl.grid_remove()
            self.img_cls_num_val = customtkinter.CTkLabel(self.img_cls_sub_frm, height = lbl_height, text=f"")
            self.img_cls_num_val.grid(row=2, padx=PADX, pady=0, sticky="nse")
            self.img_cls_num_val.grid_remove()
            self.img_cls_ela_lbl = customtkinter.CTkLabel(self.img_cls_sub_frm, height = lbl_height, text=f"{elapsed_time_txt[lang_idx]}:")
            self.img_cls_ela_lbl.grid(row=3, padx=PADX, pady=0, sticky="nsw")
            self.img_cls_ela_lbl.grid_remove()
            self.img_cls_ela_val = customtkinter.CTkLabel(self.img_cls_sub_frm, height = lbl_height, text=f"")
            self.img_cls_ela_val.grid(row=3, padx=PADX, pady=0, sticky="nse")     
            self.img_cls_ela_val.grid_remove()
            self.img_cls_rem_lbl = customtkinter.CTkLabel(self.img_cls_sub_frm, height = lbl_height, text=f"{remaining_time_txt[lang_idx]}:")
            self.img_cls_rem_lbl.grid(row=4, padx=PADX, pady=0, sticky="nsw")
            self.img_cls_rem_lbl.grid_remove()
            self.img_cls_rem_val = customtkinter.CTkLabel(self.img_cls_sub_frm, height = lbl_height, text=f"")
            self.img_cls_rem_val.grid(row=4, padx=PADX, pady=0, sticky="nse")
            self.img_cls_rem_val.grid_remove()
            self.img_cls_spe_lbl = customtkinter.CTkLabel(self.img_cls_sub_frm, height = lbl_height, text=f"{animals_per_second_txt[lang_idx]}:")
            self.img_cls_spe_lbl.grid(row=5, padx=PADX, pady=0, sticky="nsw")
            self.img_cls_spe_lbl.grid_remove()
            self.img_cls_spe_val = customtkinter.CTkLabel(self.img_cls_sub_frm, height = lbl_height, text=f"")
            self.img_cls_spe_val.grid(row=5, padx=PADX, pady=0, sticky="nse")
            self.img_cls_spe_val.grid_remove()
            self.img_cls_hwa_lbl = customtkinter.CTkLabel(self.img_cls_sub_frm, height = lbl_height, text=f"{running_on_txt[lang_idx]}:")
            self.img_cls_hwa_lbl.grid(row=6, padx=PADX, pady=0, sticky="nsw")
            self.img_cls_hwa_lbl.grid_remove()
            self.img_cls_hwa_val = customtkinter.CTkLabel(self.img_cls_sub_frm, height = lbl_height, text=f"")
            self.img_cls_hwa_val.grid(row=6, padx=PADX, pady=0, sticky="nse")
            self.img_cls_hwa_val.grid_remove()
            self.img_cls_can_btn = CancelButton(master = self.img_cls_sub_frm, text = "Cancel", command = lambda: print(""))
            self.img_cls_can_btn.grid(row=7, padx=PADX, pady=(PADY, 0), sticky="ns")
            self.img_cls_can_btn.grid_remove()

        # initialise video detection process
        if "vid_det" in processes:
            self.vid_det_frm = customtkinter.CTkFrame(master=self.progress_top_level_window)
            self.vid_det_frm.grid(row=2, padx=PADX, pady=PADY, sticky="nswe")
            vid_det_ttl_txt = [f'Localizing animals{vid_det_extra_string}...', f'Localización de animales{vid_det_extra_string}...']
            self.vid_det_ttl = customtkinter.CTkLabel(self.vid_det_frm, text=vid_det_ttl_txt[lang_idx], 
                                            font = customtkinter.CTkFont(family='CTkFont', size=14, weight = 'bold'))
            self.vid_det_ttl.grid(row=0, padx=PADX * 2, pady=(PADY, 0), columnspan = 2, sticky="nsw")
            self.vid_det_sub_frm = customtkinter.CTkFrame(master=self.vid_det_frm)
            self.vid_det_sub_frm.grid(row=1, padx=PADX, pady=PADY, sticky="nswe", ipady=PADY/2)
            self.vid_det_sub_frm.columnconfigure(0, weight=1, minsize=300)
            self.vid_det_pbr = customtkinter.CTkProgressBar(self.vid_det_sub_frm, orientation="horizontal", height=28, corner_radius=5, width=1)
            self.vid_det_pbr.set(0)
            self.vid_det_pbr.grid(row=0, padx=PADX, pady=PADY, sticky="nsew")
            self.vid_det_per = customtkinter.CTkLabel(self.vid_det_sub_frm, text=f" 0% ", height=5, fg_color=("#949BA2", "#4B4D50"), text_color="white")
            self.vid_det_per.grid(row=0, padx=PADX, pady=PADY, sticky="")
            self.vid_det_wai_lbl = customtkinter.CTkLabel(self.vid_det_sub_frm, height = lbl_height, text=in_queue_txt[lang_idx])
            self.vid_det_wai_lbl.grid(row=1, padx=PADX, pady=0, sticky="nsew")
            self.vid_det_num_lbl = customtkinter.CTkLabel(self.vid_det_sub_frm, height = lbl_height, text=f"{processing_frame_txt[lang_idx]}:")
            self.vid_det_num_lbl.grid(row=2, padx=PADX, pady=0, sticky="nsw")
            self.vid_det_num_lbl.grid_remove()
            self.vid_det_num_val = customtkinter.CTkLabel(self.vid_det_sub_frm, height = lbl_height, text=f"")
            self.vid_det_num_val.grid(row=2, padx=PADX, pady=0, sticky="nse")
            self.vid_det_num_val.grid_remove()
            self.vid_det_ela_lbl = customtkinter.CTkLabel(self.vid_det_sub_frm, height = lbl_height, text=f"{elapsed_time_txt[lang_idx]}:")
            self.vid_det_ela_lbl.grid(row=3, padx=PADX, pady=0, sticky="nsw")
            self.vid_det_ela_lbl.grid_remove()
            self.vid_det_ela_val = customtkinter.CTkLabel(self.vid_det_sub_frm, height = lbl_height, text=f"")
            self.vid_det_ela_val.grid(row=3, padx=PADX, pady=0, sticky="nse")     
            self.vid_det_ela_val.grid_remove()
            self.vid_det_rem_lbl = customtkinter.CTkLabel(self.vid_det_sub_frm, height = lbl_height, text=f"{remaining_time_txt[lang_idx]}:")
            self.vid_det_rem_lbl.grid(row=4, padx=PADX, pady=0, sticky="nsw")
            self.vid_det_rem_lbl.grid_remove()
            self.vid_det_rem_val = customtkinter.CTkLabel(self.vid_det_sub_frm, height = lbl_height, text=f"")
            self.vid_det_rem_val.grid(row=4, padx=PADX, pady=0, sticky="nse")
            self.vid_det_rem_val.grid_remove()
            self.vid_det_spe_lbl = customtkinter.CTkLabel(self.vid_det_sub_frm, height = lbl_height, text=f"{frames_per_second_txt[lang_idx]}:")
            self.vid_det_spe_lbl.grid(row=5, padx=PADX, pady=0, sticky="nsw")
            self.vid_det_spe_lbl.grid_remove()
            self.vid_det_spe_val = customtkinter.CTkLabel(self.vid_det_sub_frm, height = lbl_height, text=f"")
            self.vid_det_spe_val.grid(row=5, padx=PADX, pady=0, sticky="nse")
            self.vid_det_spe_val.grid_remove()
            self.vid_det_hwa_lbl = customtkinter.CTkLabel(self.vid_det_sub_frm, height = lbl_height, text=f"{running_on_txt[lang_idx]}:")
            self.vid_det_hwa_lbl.grid(row=6, padx=PADX, pady=0, sticky="nsw")
            self.vid_det_hwa_lbl.grid_remove()
            self.vid_det_hwa_val = customtkinter.CTkLabel(self.vid_det_sub_frm, height = lbl_height, text=f"")
            self.vid_det_hwa_val.grid(row=6, padx=PADX, pady=0, sticky="nse")
            self.vid_det_hwa_val.grid_remove()
            self.vid_det_can_btn = CancelButton(master = self.vid_det_sub_frm, text = "Cancel", command = lambda: print(""))
            self.vid_det_can_btn.grid(row=7, padx=PADX, pady=(PADY, 0), sticky="ns")
            self.vid_det_can_btn.grid_remove()

        # initialise video classification process
        if "vid_cls" in processes:
            self.vid_cls_frm = customtkinter.CTkFrame(master=self.progress_top_level_window)
            self.vid_cls_frm.grid(row=3, padx=PADX, pady=PADY, sticky="nswe")
            vid_cls_ttl_txt = [f'Identifying animals{vid_det_extra_string}...', f'Identificación de animales{vid_det_extra_string}...']
            self.vid_cls_ttl = customtkinter.CTkLabel(self.vid_cls_frm, text=vid_cls_ttl_txt[lang_idx], 
                                            font = customtkinter.CTkFont(family='CTkFont', size=14, weight = 'bold'))
            self.vid_cls_ttl.grid(row=0, padx=PADX * 2, pady=(PADY, 0), columnspan = 2, sticky="nsw")
            self.vid_cls_sub_frm = customtkinter.CTkFrame(master=self.vid_cls_frm)
            self.vid_cls_sub_frm.grid(row=1, padx=PADX, pady=PADY, sticky="nswe", ipady=PADY/2)
            self.vid_cls_sub_frm.columnconfigure(0, weight=1, minsize=300)
            self.vid_cls_pbr = customtkinter.CTkProgressBar(self.vid_cls_sub_frm, orientation="horizontal", height=28, corner_radius=5, width=1)
            self.vid_cls_pbr.set(0)
            self.vid_cls_pbr.grid(row=0, padx=PADX, pady=PADY, sticky="nsew")
            self.vid_cls_per = customtkinter.CTkLabel(self.vid_cls_sub_frm, text=f" 0% ", height=5, fg_color=("#949BA2", "#4B4D50"), text_color="white")
            self.vid_cls_per.grid(row=0, padx=PADX, pady=PADY, sticky="")
            self.vid_cls_wai_lbl = customtkinter.CTkLabel(self.vid_cls_sub_frm, height = lbl_height, text=in_queue_txt[lang_idx])
            self.vid_cls_wai_lbl.grid(row=1, padx=PADX, pady=0, sticky="nsew")
            self.vid_cls_num_lbl = customtkinter.CTkLabel(self.vid_cls_sub_frm, height = lbl_height, text=f"{processing_animal_txt[lang_idx]}:")
            self.vid_cls_num_lbl.grid(row=2, padx=PADX, pady=0, sticky="nsw")
            self.vid_cls_num_lbl.grid_remove()
            self.vid_cls_num_val = customtkinter.CTkLabel(self.vid_cls_sub_frm, height = lbl_height, text=f"")
            self.vid_cls_num_val.grid(row=2, padx=PADX, pady=0, sticky="nse")
            self.vid_cls_num_val.grid_remove()
            self.vid_cls_ela_lbl = customtkinter.CTkLabel(self.vid_cls_sub_frm, height = lbl_height, text=f"{elapsed_time_txt[lang_idx]}:")
            self.vid_cls_ela_lbl.grid(row=3, padx=PADX, pady=0, sticky="nsw")
            self.vid_cls_ela_lbl.grid_remove()
            self.vid_cls_ela_val = customtkinter.CTkLabel(self.vid_cls_sub_frm, height = lbl_height, text=f"")
            self.vid_cls_ela_val.grid(row=3, padx=PADX, pady=0, sticky="nse")     
            self.vid_cls_ela_val.grid_remove()
            self.vid_cls_rem_lbl = customtkinter.CTkLabel(self.vid_cls_sub_frm, height = lbl_height, text=f"{remaining_time_txt[lang_idx]}:")
            self.vid_cls_rem_lbl.grid(row=4, padx=PADX, pady=0, sticky="nsw")
            self.vid_cls_rem_lbl.grid_remove()
            self.vid_cls_rem_val = customtkinter.CTkLabel(self.vid_cls_sub_frm, height = lbl_height, text=f"")
            self.vid_cls_rem_val.grid(row=4, padx=PADX, pady=0, sticky="nse")
            self.vid_cls_rem_val.grid_remove()
            self.vid_cls_spe_lbl = customtkinter.CTkLabel(self.vid_cls_sub_frm, height = lbl_height, text=f"{animals_per_second_txt[lang_idx]}:")
            self.vid_cls_spe_lbl.grid(row=5, padx=PADX, pady=0, sticky="nsw")
            self.vid_cls_spe_lbl.grid_remove()
            self.vid_cls_spe_val = customtkinter.CTkLabel(self.vid_cls_sub_frm, height = lbl_height, text=f"")
            self.vid_cls_spe_val.grid(row=5, padx=PADX, pady=0, sticky="nse")
            self.vid_cls_spe_val.grid_remove()
            self.vid_cls_hwa_lbl = customtkinter.CTkLabel(self.vid_cls_sub_frm, height = lbl_height, text=f"{running_on_txt[lang_idx]}:")
            self.vid_cls_hwa_lbl.grid(row=6, padx=PADX, pady=0, sticky="nsw")
            self.vid_cls_hwa_lbl.grid_remove()
            self.vid_cls_hwa_val = customtkinter.CTkLabel(self.vid_cls_sub_frm, height = lbl_height, text=f"")
            self.vid_cls_hwa_val.grid(row=6, padx=PADX, pady=0, sticky="nse")
            self.vid_cls_hwa_val.grid_remove()
            self.vid_cls_can_btn = CancelButton(master = self.vid_cls_sub_frm, text = "Cancel", command = lambda: print(""))
            self.vid_cls_can_btn.grid(row=7, padx=PADX, pady=(PADY, 0), sticky="ns")
            self.vid_cls_can_btn.grid_remove()

        # postprocessing for images
        if "img_pst" in processes:
            self.img_pst_frm = customtkinter.CTkFrame(master=self.progress_top_level_window)
            self.img_pst_frm.grid(row=4, padx=PADX, pady=PADY, sticky="nswe")
            img_pst_ttl_txt = [f'Postprocessing{img_pst_extra_string}...', f'Postprocesado{img_pst_extra_string}...']
            self.img_pst_ttl = customtkinter.CTkLabel(self.img_pst_frm, text=img_pst_ttl_txt[lang_idx], 
                                            font = customtkinter.CTkFont(family='CTkFont', size=14, weight = 'bold'))
            self.img_pst_ttl.grid(row=0, padx=PADX * 2, pady=(PADY, 0), columnspan = 2, sticky="nsw")
            self.img_pst_sub_frm = customtkinter.CTkFrame(master=self.img_pst_frm)
            self.img_pst_sub_frm.grid(row=1, padx=PADX, pady=PADY, sticky="nswe", ipady=PADY/2)
            self.img_pst_sub_frm.columnconfigure(0, weight=1, minsize=300)
            self.img_pst_pbr = customtkinter.CTkProgressBar(self.img_pst_sub_frm, orientation="horizontal", height=28, corner_radius=5, width=1)
            self.img_pst_pbr.set(0)
            self.img_pst_pbr.grid(row=0, padx=PADX, pady=PADY, sticky="nsew")
            self.img_pst_per = customtkinter.CTkLabel(self.img_pst_sub_frm, text=f" 0% ", height=5, fg_color=("#949BA2", "#4B4D50"), text_color="white")
            self.img_pst_per.grid(row=0, padx=PADX, pady=PADY, sticky="")
            self.img_pst_wai_lbl = customtkinter.CTkLabel(self.img_pst_sub_frm, height = lbl_height, text=in_queue_txt[lang_idx])
            self.img_pst_wai_lbl.grid(row=1, padx=PADX, pady=0, sticky="nsew")
            self.img_pst_ela_lbl = customtkinter.CTkLabel(self.img_pst_sub_frm, height = lbl_height, text=f"{elapsed_time_txt[lang_idx]}:")
            self.img_pst_ela_lbl.grid(row=2, padx=PADX, pady=0, sticky="nsw")
            self.img_pst_ela_lbl.grid_remove()
            self.img_pst_ela_val = customtkinter.CTkLabel(self.img_pst_sub_frm, height = lbl_height, text=f"")
            self.img_pst_ela_val.grid(row=2, padx=PADX, pady=0, sticky="nse")     
            self.img_pst_ela_val.grid_remove()
            self.img_pst_rem_lbl = customtkinter.CTkLabel(self.img_pst_sub_frm, height = lbl_height, text=f"{remaining_time_txt[lang_idx]}:")
            self.img_pst_rem_lbl.grid(row=3, padx=PADX, pady=0, sticky="nsw")
            self.img_pst_rem_lbl.grid_remove()
            self.img_pst_rem_val = customtkinter.CTkLabel(self.img_pst_sub_frm, height = lbl_height, text=f"")
            self.img_pst_rem_val.grid(row=3, padx=PADX, pady=0, sticky="nse")     
            self.img_pst_rem_val.grid_remove()
            self.img_pst_can_btn = CancelButton(master = self.img_pst_sub_frm, text = "Cancel", command = lambda: print(""))
            self.img_pst_can_btn.grid(row=7, padx=PADX, pady=(PADY, 0), sticky="ns")
            self.img_pst_can_btn.grid_remove()

        # postprocessing for videos
        if "vid_pst" in processes:
            self.vid_pst_frm = customtkinter.CTkFrame(master=self.progress_top_level_window)
            self.vid_pst_frm.grid(row=5, padx=PADX, pady=PADY, sticky="nswe")
            vid_pst_ttl_txt = [f'Postprocessing{vid_pst_extra_string}...', f'Postprocesado{vid_pst_extra_string}...']
            self.vid_pst_ttl = customtkinter.CTkLabel(self.vid_pst_frm, text=vid_pst_ttl_txt[lang_idx], 
                                            font = customtkinter.CTkFont(family='CTkFont', size=14, weight = 'bold'))
            self.vid_pst_ttl.grid(row=0, padx=PADX * 2, pady=(PADY, 0), columnspan = 2, sticky="nsw")
            self.vid_pst_sub_frm = customtkinter.CTkFrame(master=self.vid_pst_frm)
            self.vid_pst_sub_frm.grid(row=1, padx=PADX, pady=PADY, sticky="nswe", ipady=PADY/2)
            self.vid_pst_sub_frm.columnconfigure(0, weight=1, minsize=300)
            self.vid_pst_pbr = customtkinter.CTkProgressBar(self.vid_pst_sub_frm, orientation="horizontal", height=28, corner_radius=5, width=1)
            self.vid_pst_pbr.set(0)
            self.vid_pst_pbr.grid(row=0, padx=PADX, pady=PADY, sticky="nsew")
            self.vid_pst_per = customtkinter.CTkLabel(self.vid_pst_sub_frm, text=f" 0% ", height=5, fg_color=("#949BA2", "#4B4D50"), text_color="white")
            self.vid_pst_per.grid(row=0, padx=PADX, pady=PADY, sticky="")
            self.vid_pst_wai_lbl = customtkinter.CTkLabel(self.vid_pst_sub_frm, height = lbl_height, text=in_queue_txt[lang_idx])
            self.vid_pst_wai_lbl.grid(row=1, padx=PADX, pady=0, sticky="nsew")
            self.vid_pst_ela_lbl = customtkinter.CTkLabel(self.vid_pst_sub_frm, height = lbl_height, text=f"{elapsed_time_txt[lang_idx]}:")
            self.vid_pst_ela_lbl.grid(row=2, padx=PADX, pady=0, sticky="nsw")
            self.vid_pst_ela_lbl.grid_remove()
            self.vid_pst_ela_val = customtkinter.CTkLabel(self.vid_pst_sub_frm, height = lbl_height, text=f"")
            self.vid_pst_ela_val.grid(row=2, padx=PADX, pady=0, sticky="nse")     
            self.vid_pst_ela_val.grid_remove()
            self.vid_pst_rem_lbl = customtkinter.CTkLabel(self.vid_pst_sub_frm, height = lbl_height, text=f"{remaining_time_txt[lang_idx]}:")
            self.vid_pst_rem_lbl.grid(row=3, padx=PADX, pady=0, sticky="nsw")
            self.vid_pst_rem_lbl.grid_remove()
            self.vid_pst_rem_val = customtkinter.CTkLabel(self.vid_pst_sub_frm, height = lbl_height, text=f"")
            self.vid_pst_rem_val.grid(row=3, padx=PADX, pady=0, sticky="nse")     
            self.vid_pst_rem_val.grid_remove()
            self.vid_pst_can_btn = CancelButton(master = self.vid_pst_sub_frm, text = "Cancel", command = lambda: print(""))
            self.vid_pst_can_btn.grid(row=7, padx=PADX, pady=(PADY, 0), sticky="ns")
            self.vid_pst_can_btn.grid_remove()

        self.progress_top_level_window.update()

    def update_values(self,
                      process,
                      status,
                      cur_it = 1,
                      tot_it = 1,
                      time_ela = "",
                      time_rem = "",
                      speed = "",
                      hware = "",
                      cancel_func = lambda: print("")):
        
        # language settings
        algorithm_starting_txt = ["Algorithm is starting up...", 'El algoritmo está arrancando...']
        image_per_second_txt = ["Images per second:", "Imágenes por segundo:"]
        seconds_per_image_txt = ["Seconds per image:", "Segundos por imagen:"]
        animals_per_second_txt = ["Animals per second:", "Animales por segundo:"]
        seconds_per_animal_txt = ["Seconds per animal:", "Segundos por animal:"]
        frames_per_second_txt = ["Frames per second:", "Fotogramas por segundo:"]
        seconds_per_frame_txt = ["Seconds per frame:", "Segundos por fotograma:"]
        starting_up_txt = ["Starting up...", "Arrancando..."]

        # detection of images
        if process == "img_det":
            if status == "load":
                self.img_det_wai_lbl.configure(text = algorithm_starting_txt[lang_idx])
                self.just_shown_load_screen = True
            elif status == "running":
                if self.just_shown_load_screen:
                    self.img_det_wai_lbl.grid_remove()
                    self.img_det_num_lbl.grid()
                    self.img_det_num_val.grid()
                    self.img_det_ela_lbl.grid()
                    self.img_det_ela_val.grid()
                    self.img_det_rem_lbl.grid()
                    self.img_det_rem_val.grid()
                    self.img_det_spe_lbl.grid()
                    self.img_det_spe_val.grid()
                    self.img_det_hwa_lbl.grid()
                    self.img_det_hwa_val.grid()
                    self.img_det_can_btn.grid()
                    self.img_det_can_btn.configure(command = cancel_func)
                    self.just_shown_load_screen = False
                percentage = (cur_it / tot_it)
                self.img_det_pbr.set(percentage)
                self.img_det_per.configure(text = f" {round(percentage * 100)}% ")
                if percentage > 0.5:
                    self.img_det_per.configure(fg_color=("#3B8ECF", "#1F6BA5"))
                else:
                    self.img_det_per.configure(fg_color=("#949BA2", "#4B4D50"))
                self.img_det_num_val.configure(text = f"{cur_it} of {tot_it}")
                self.img_det_ela_val.configure(text = time_ela)
                self.img_det_rem_val.configure(text = time_rem)
                self.img_det_spe_lbl.configure(text = image_per_second_txt[lang_idx] if "it/s" in speed else seconds_per_image_txt[lang_idx])
                parsed_speed = speed.replace("it/s", "").replace("s/it", "")
                self.img_det_spe_val.configure(text = parsed_speed)
                self.img_det_hwa_val.configure(text = hware)
            elif status == "done":
                self.img_det_num_lbl.grid_remove()
                self.img_det_num_val.grid_remove()
                self.img_det_rem_lbl.grid_remove()
                self.img_det_rem_val.grid_remove()
                self.img_det_hwa_lbl.grid_remove()
                self.img_det_hwa_val.grid_remove()
                self.img_det_can_btn.grid_remove()
                self.img_det_ela_val.grid_remove()
                self.img_det_ela_lbl.grid_remove()
                self.img_det_spe_lbl.grid_remove()
                self.img_det_spe_val.grid_remove()
                self.img_det_pbr.grid_configure(pady=(PADY, 0))
                self.img_det_per.grid_configure(pady=(PADY, 0))

        # classification of images
        elif process == "img_cls":
            if status == "load":
                self.img_cls_wai_lbl.configure(text = algorithm_starting_txt[lang_idx])
                self.just_shown_load_screen = True
            elif status == "running":
                if self.just_shown_load_screen:
                    self.img_cls_wai_lbl.grid_remove()
                    self.img_cls_num_lbl.grid()
                    self.img_cls_num_val.grid()
                    self.img_cls_ela_lbl.grid()
                    self.img_cls_ela_val.grid()
                    self.img_cls_rem_lbl.grid()
                    self.img_cls_rem_val.grid()
                    self.img_cls_spe_lbl.grid()
                    self.img_cls_spe_val.grid()
                    self.img_cls_hwa_lbl.grid()
                    self.img_cls_hwa_val.grid()
                    self.img_cls_can_btn.grid()
                    self.img_cls_can_btn.configure(command = cancel_func)
                    self.just_shown_load_screen = False
                percentage = (cur_it / tot_it)
                self.img_cls_pbr.set(percentage)
                self.img_cls_per.configure(text = f" {round(percentage * 100)}% ")
                if percentage > 0.5:
                    self.img_cls_per.configure(fg_color=("#3B8ECF", "#1F6BA5"))
                else:
                    self.img_cls_per.configure(fg_color=("#949BA2", "#4B4D50"))
                self.img_cls_num_val.configure(text = f"{cur_it} of {tot_it}")
                self.img_cls_ela_val.configure(text = time_ela)
                self.img_cls_rem_val.configure(text = time_rem)
                self.img_cls_spe_lbl.configure(text = animals_per_second_txt[lang_idx] if "it/s" in speed else seconds_per_animal_txt[lang_idx])
                parsed_speed = speed.replace("it/s", "").replace("s/it", "")
                self.img_cls_spe_val.configure(text = parsed_speed)
                self.img_cls_hwa_val.configure(text = hware)
            elif status == "done":
                self.img_cls_num_lbl.grid_remove()
                self.img_cls_num_val.grid_remove()
                self.img_cls_rem_lbl.grid_remove()
                self.img_cls_rem_val.grid_remove()
                self.img_cls_hwa_lbl.grid_remove()
                self.img_cls_hwa_val.grid_remove()
                self.img_cls_can_btn.grid_remove()
                self.img_cls_ela_val.grid_remove()
                self.img_cls_ela_lbl.grid_remove()
                self.img_cls_spe_lbl.grid_remove()
                self.img_cls_spe_val.grid_remove()
                self.img_cls_pbr.grid_configure(pady=(PADY, 0))
                self.img_cls_per.grid_configure(pady=(PADY, 0))

        # detection of videos
        if process == "vid_det":
            if status == "load":
                self.vid_det_wai_lbl.configure(text = algorithm_starting_txt[lang_idx])
                self.just_shown_load_screen = True
            elif status == "running":
                if self.just_shown_load_screen:
                    self.vid_det_wai_lbl.grid_remove()
                    self.vid_det_num_lbl.grid()
                    self.vid_det_num_val.grid()
                    self.vid_det_ela_lbl.grid()
                    self.vid_det_ela_val.grid()
                    self.vid_det_rem_lbl.grid()
                    self.vid_det_rem_val.grid()
                    self.vid_det_spe_lbl.grid()
                    self.vid_det_spe_val.grid()
                    self.vid_det_hwa_lbl.grid()
                    self.vid_det_hwa_val.grid()
                    self.vid_det_can_btn.grid()
                    self.vid_det_can_btn.configure(command = cancel_func)
                    self.just_shown_load_screen = False
                percentage = (cur_it / tot_it)
                self.vid_det_pbr.set(percentage)
                self.vid_det_per.configure(text = f" {round(percentage * 100)}% ")
                if percentage > 0.5:
                    self.vid_det_per.configure(fg_color=("#3B8ECF", "#1F6BA5"))
                else:
                    self.vid_det_per.configure(fg_color=("#949BA2", "#4B4D50"))
                self.vid_det_num_val.configure(text = f"{cur_it} of {tot_it}")
                self.vid_det_ela_val.configure(text = time_ela)
                self.vid_det_rem_val.configure(text = time_rem)
                self.vid_det_spe_lbl.configure(text = frames_per_second_txt[lang_idx] if "it/s" in speed else seconds_per_frame_txt[lang_idx])
                parsed_speed = speed.replace("it/s", "").replace("s/it", "")
                self.vid_det_spe_val.configure(text = parsed_speed)
                self.vid_det_hwa_val.configure(text = hware)
            elif status == "done":
                self.vid_det_num_lbl.grid_remove()
                self.vid_det_num_val.grid_remove()
                self.vid_det_rem_lbl.grid_remove()
                self.vid_det_rem_val.grid_remove()
                self.vid_det_hwa_lbl.grid_remove()
                self.vid_det_hwa_val.grid_remove()
                self.vid_det_ela_val.grid_remove()
                self.vid_det_ela_lbl.grid_remove()
                self.vid_det_spe_lbl.grid_remove()
                self.vid_det_spe_val.grid_remove()
                self.vid_det_can_btn.grid_remove()
                self.vid_det_pbr.grid_configure(pady=(PADY, 0))
                self.vid_det_per.grid_configure(pady=(PADY, 0))

        # classification of videos
        elif process == "vid_cls":
            if status == "load":
                self.vid_cls_wai_lbl.configure(text = algorithm_starting_txt[lang_idx])
                self.just_shown_load_screen = True
            elif status == "running":
                if self.just_shown_load_screen:
                    self.vid_cls_wai_lbl.grid_remove()
                    self.vid_cls_num_lbl.grid()
                    self.vid_cls_num_val.grid()
                    self.vid_cls_ela_lbl.grid()
                    self.vid_cls_ela_val.grid()
                    self.vid_cls_rem_lbl.grid()
                    self.vid_cls_rem_val.grid()
                    self.vid_cls_spe_lbl.grid()
                    self.vid_cls_spe_val.grid()
                    self.vid_cls_hwa_lbl.grid()
                    self.vid_cls_hwa_val.grid()
                    self.vid_cls_can_btn.grid()
                    self.vid_cls_can_btn.configure(command = cancel_func)
                    self.just_shown_load_screen = False
                percentage = (cur_it / tot_it)
                self.vid_cls_pbr.set(percentage)
                self.vid_cls_per.configure(text = f" {round(percentage * 100)}% ")
                if percentage > 0.5:
                    self.vid_cls_per.configure(fg_color=("#3B8ECF", "#1F6BA5"))
                else:
                    self.vid_cls_per.configure(fg_color=("#949BA2", "#4B4D50"))
                self.vid_cls_num_val.configure(text = f"{cur_it} of {tot_it}")
                self.vid_cls_ela_val.configure(text = time_ela)
                self.vid_cls_rem_val.configure(text = time_rem)
                self.vid_cls_spe_lbl.configure(text = animals_per_second_txt[lang_idx] if "it/s" in speed else seconds_per_animal_txt[lang_idx])
                parsed_speed = speed.replace("it/s", "").replace("s/it", "")
                self.vid_cls_spe_val.configure(text = parsed_speed)
                self.vid_cls_hwa_val.configure(text = hware)
            elif status == "done":
                self.vid_cls_num_lbl.grid_remove()
                self.vid_cls_num_val.grid_remove()
                self.vid_cls_rem_lbl.grid_remove()
                self.vid_cls_rem_val.grid_remove()
                self.vid_cls_hwa_lbl.grid_remove()
                self.vid_cls_hwa_val.grid_remove()
                self.vid_cls_ela_val.grid_remove()
                self.vid_cls_ela_lbl.grid_remove()
                self.vid_cls_spe_lbl.grid_remove()
                self.vid_cls_spe_val.grid_remove()
                self.vid_cls_can_btn.grid_remove()
                self.vid_cls_pbr.grid_configure(pady=(PADY, 0))
                self.vid_cls_per.grid_configure(pady=(PADY, 0))

        # postprocessing of images
        elif process == "img_pst":
            if status == "load":
                self.img_pst_wai_lbl.configure(text = starting_up_txt[lang_idx])
                self.just_shown_load_screen = True
            elif status == "running":
                if self.just_shown_load_screen:
                    self.img_pst_wai_lbl.grid_remove()
                    self.img_pst_ela_lbl.grid()
                    self.img_pst_ela_val.grid()
                    self.img_pst_rem_lbl.grid()
                    self.img_pst_rem_val.grid()
                    self.img_pst_can_btn.grid()
                    self.img_pst_can_btn.configure(command = cancel_func)
                    self.just_shown_load_screen = False
                percentage = (cur_it / tot_it)
                self.img_pst_pbr.set(percentage)
                self.img_pst_per.configure(text = f" {round(percentage * 100)}% ")
                if percentage > 0.5:
                    self.img_pst_per.configure(fg_color=("#3B8ECF", "#1F6BA5"))
                else:
                    self.img_pst_per.configure(fg_color=("#949BA2", "#4B4D50"))
                self.img_pst_ela_val.configure(text = time_ela)
                self.img_pst_rem_val.configure(text = time_rem)
            elif status == "done":
                self.img_pst_rem_lbl.grid_remove()
                self.img_pst_rem_val.grid_remove()
                self.img_pst_ela_val.grid_remove()
                self.img_pst_ela_lbl.grid_remove()
                self.img_pst_can_btn.grid_remove()
                self.img_pst_pbr.grid_configure(pady=(PADY, 0))
                self.img_pst_per.grid_configure(pady=(PADY, 0))

        # postprocessing of videos
        elif process == "vid_pst":
            if status == "load":
                self.vid_pst_wai_lbl.configure(text = starting_up_txt[lang_idx])
                self.just_shown_load_screen = True
            elif status == "running":
                if self.just_shown_load_screen:
                    self.vid_pst_wai_lbl.grid_remove()
                    self.vid_pst_ela_lbl.grid()
                    self.vid_pst_ela_val.grid()
                    self.vid_pst_rem_lbl.grid()
                    self.vid_pst_rem_val.grid()
                    self.vid_pst_can_btn.grid()
                    self.vid_pst_can_btn.configure(command = cancel_func)
                    self.just_shown_load_screen = False
                percentage = (cur_it / tot_it)
                self.vid_pst_pbr.set(percentage)
                self.vid_pst_per.configure(text = f" {round(percentage * 100)}% ")
                if percentage > 0.5:
                    self.vid_pst_per.configure(fg_color=("#3B8ECF", "#1F6BA5"))
                else:
                    self.vid_pst_per.configure(fg_color=("#949BA2", "#4B4D50"))
                self.vid_pst_ela_val.configure(text = time_ela)
                self.vid_pst_rem_val.configure(text = time_rem)
            elif status == "done":
                self.vid_pst_rem_lbl.grid_remove()
                self.vid_pst_rem_val.grid_remove()
                self.vid_pst_ela_val.grid_remove()
                self.vid_pst_ela_lbl.grid_remove()
                self.vid_pst_can_btn.grid_remove()
                self.vid_pst_pbr.grid_configure(pady=(PADY, 0))
                self.vid_pst_per.grid_configure(pady=(PADY, 0))

        # update screen
        self.progress_top_level_window.update()

    def open(self):
        self.progress_top_level_window.deiconify()

    def close(self):
        self.progress_top_level_window.destroy()

# refresh dropdown menu options
def update_dpd_options(dpd, master, var, options, cmd, row, lbl, from_lang_idx):

    # recreate new option menu with updated options
    dpd.grid_forget()
    index = options[from_lang_idx].index(var.get()) # get dpd index
    var.set(options[lang_idx][index]) # set to previous index
    if cmd:
        dpd = OptionMenu(master, var, *options[lang_idx], command=cmd)
    else:
        dpd = OptionMenu(master, var, *options[lang_idx])
    dpd.configure(width=1)
    dpd.grid(row=row, column=1, sticky='nesw', padx=5)

    # give it same state as its label
    dpd.configure(state = str(lbl['state']))

# special refresh function for the model seleciton dropdown in simple mode because customtkinter works a bit different
def update_sim_mdl_dpd():
    global sim_mdl_dpd
    sim_mdl_dpd.grid_forget()
    sim_mdl_dpd = customtkinter.CTkOptionMenu(sim_mdl_frm, values=sim_dpd_options_cls_model[lang_idx], command=sim_mdl_dpd_callback, width = 1)
    sim_mdl_dpd.set(sim_dpd_options_cls_model[lang_idx][dpd_options_cls_model[lang_idx].index(var_cls_model.get())])
    sim_mdl_dpd.grid(row=1, column=0, padx=PADX, pady=(PADY/4, PADY), sticky="nswe", columnspan = 2)

# refresh ent texts
def update_ent_text(var, string):
    if var.get() == "":
        return
    if no_user_input(var):
        original_state = str(var['state'])
        var.configure(state=NORMAL, fg='grey')
        var.delete(0, tk.END)
        var.insert(0, string)
        var.configure(state=original_state)

# check next language to print on button when program starts
def set_lang_buttons(lang_idx):
    from_lang_idx = lang_idx
    to_lang_idx = 0 if from_lang_idx + 1 >= len(languages_available) else from_lang_idx + 1
    to_lang = languages_available[to_lang_idx]
    sim_btn_switch_lang.configure(text = f"{to_lang}")
    adv_btn_switch_lang.configure(text = f"{to_lang}")

# change language
def set_language():
    # calculate indeces
    global lang_idx
    from_lang_idx = lang_idx
    to_lang_idx = 0 if from_lang_idx + 1 >= len(languages_available) else from_lang_idx + 1
    next_lang_idx = 0 if to_lang_idx + 1 >= len(languages_available) else to_lang_idx + 1

    # log
    print(f"EXECUTED : {sys._getframe().f_code.co_name}({locals()})\n")

    # set the global variable to the new language
    lang_idx = to_lang_idx
    write_global_vars({"lang_idx": lang_idx})

    # update tab texts
    tabControl.tab(deploy_tab, text=deploy_tab_text[lang_idx])
    tabControl.tab(help_tab, text=help_tab_text[lang_idx])
    tabControl.tab(about_tab, text=about_tab_text[lang_idx])

    # update texts of deploy tab
    fst_step.configure(text=" " + fst_step_txt[lang_idx] + " ")
    lbl_choose_folder.configure(text=lbl_choose_folder_txt[lang_idx])
    btn_choose_folder.configure(text=browse_txt[lang_idx])
    snd_step.configure(text=" " + snd_step_txt[lang_idx] + " ")
    lbl_model.configure(text=lbl_model_txt[lang_idx])
    update_dpd_options(dpd_model, snd_step, var_det_model, dpd_options_model, model_options, row_model, lbl_model, from_lang_idx)
    lbl_exclude_subs.configure(text=lbl_exclude_subs_txt[lang_idx])
    lbl_use_custom_img_size_for_deploy.configure(text=lbl_use_custom_img_size_for_deploy_txt[lang_idx])
    lbl_image_size_for_deploy.configure(text=lbl_image_size_for_deploy_txt[lang_idx])
    update_ent_text(ent_image_size_for_deploy, f"{eg_txt[lang_idx]}: 640")
    lbl_abs_paths.configure(text=lbl_abs_paths_txt[lang_idx])
    lbl_disable_GPU.configure(text=lbl_disable_GPU_txt[lang_idx])
    lbl_process_img.configure(text=lbl_process_img_txt[lang_idx])
    lbl_cls_model.configure(text=lbl_cls_model_txt[lang_idx])
    update_dpd_options(dpd_cls_model, snd_step, var_cls_model, dpd_options_cls_model, model_cls_animal_options, row_cls_model, lbl_cls_model, from_lang_idx)
    cls_frame.configure(text=" ↳ " + cls_frame_txt[lang_idx] + " ")
    lbl_model_info.configure(text = "     " + lbl_model_info_txt[lang_idx])
    btn_model_info.configure(text=show_txt[lang_idx])
    lbl_choose_classes.configure(text = "     " + lbl_choose_classes_txt[lang_idx])
    btn_choose_classes.configure(text = select_txt[lang_idx])
    lbl_cls_detec_thresh.configure(text="     " + lbl_cls_detec_thresh_txt[lang_idx])
    lbl_cls_class_thresh.configure(text="     " + lbl_cls_class_thresh_txt[lang_idx])
    # lbl_smooth_cls_animal.configure(text="     " + lbl_smooth_cls_animal_txt[lang_idx])
    img_frame.configure(text=" ↳ " + img_frame_txt[lang_idx] + " ")
    lbl_use_checkpnts.configure(text="     " + lbl_use_checkpnts_txt[lang_idx])
    lbl_checkpoint_freq.configure(text="        ↳ " + lbl_checkpoint_freq_txt[lang_idx])
    update_ent_text(ent_checkpoint_freq, f"{eg_txt[lang_idx]}: 500")
    lbl_cont_checkpnt.configure(text="     " + lbl_cont_checkpnt_txt[lang_idx])
    lbl_process_vid.configure(text=lbl_process_vid_txt[lang_idx])
    vid_frame.configure(text=" ↳ " + vid_frame_txt[lang_idx] + " ")
    lbl_not_all_frames.configure(text="     " + lbl_not_all_frames_txt[lang_idx])
    lbl_nth_frame.configure(text="        ↳ " + lbl_nth_frame_txt[lang_idx])
    update_ent_text(ent_nth_frame, f"{eg_txt[lang_idx]}: 10")
    btn_start_deploy.configure(text=btn_start_deploy_txt[lang_idx])
    trd_step.configure(text=" " + trd_step_txt[lang_idx] + " ")
    lbl_hitl_main.configure(text=lbl_hitl_main_txt[lang_idx])
    btn_hitl_main.configure(text=["Start", "Iniciar"][lang_idx])
    fth_step.configure(text=" " + fth_step_txt[lang_idx] + " ")
    lbl_output_dir.configure(text=lbl_output_dir_txt[lang_idx])
    btn_output_dir.configure(text=browse_txt[lang_idx])
    lbl_separate_files.configure(text=lbl_separate_files_txt[lang_idx])
    sep_frame.configure(text=" ↳ " + sep_frame_txt[lang_idx] + " ")
    lbl_file_placement.configure(text="     " + lbl_file_placement_txt[lang_idx])
    rad_file_placement_move.configure(text=["Copy", "Copiar"][lang_idx])
    rad_file_placement_copy.configure(text=["Move", "Mover"][lang_idx])
    lbl_sep_conf.configure(text="     " + lbl_sep_conf_txt[lang_idx])
    lbl_vis_files.configure(text=lbl_vis_files_txt[lang_idx])
    lbl_crp_files.configure(text=lbl_crp_files_txt[lang_idx])
    lbl_exp.configure(text=lbl_exp_txt[lang_idx])
    exp_frame.configure(text=" ↳ " + exp_frame_txt[lang_idx] + " ")
    lbl_exp_format.configure(text=lbl_exp_format_txt[lang_idx])
    lbl_thresh.configure(text=lbl_thresh_txt[lang_idx])
    btn_start_postprocess.configure(text=btn_start_postprocess_txt[lang_idx])

    # update texts of help tab
    help_text.configure(state=NORMAL)
    help_text.delete('1.0', END)
    write_help_tab()

    # update texts of about tab
    about_text.configure(state=NORMAL)
    about_text.delete('1.0', END)
    write_about_tab()

    # top buttons
    adv_btn_switch_mode.configure(text = adv_btn_switch_mode_txt[lang_idx])
    sim_btn_switch_mode.configure(text = sim_btn_switch_mode_txt[lang_idx])
    sim_btn_switch_lang.configure(text = languages_available[next_lang_idx])
    adv_btn_switch_lang.configure(text = languages_available[next_lang_idx])
    adv_btn_sponsor.configure(text = adv_btn_sponsor_txt[lang_idx])
    sim_btn_sponsor.configure(text = adv_btn_sponsor_txt[lang_idx])
    adv_btn_reset_values.configure(text = adv_btn_reset_values_txt[lang_idx])
    sim_btn_reset_values.configure(text = adv_btn_reset_values_txt[lang_idx])

    # by addax text
    adv_abo_lbl.configure(text=adv_abo_lbl_txt[lang_idx])
    sim_abo_lbl.configure(text=adv_abo_lbl_txt[lang_idx])

    # simple mode
    sim_dir_lbl.configure(text = sim_dir_lbl_txt[lang_idx])
    sim_dir_pth.configure(text = sim_dir_pth_txt[lang_idx])
    sim_mdl_lbl.configure(text = sim_mdl_lbl_txt[lang_idx])
    update_sim_mdl_dpd()
    sim_spp_lbl.configure(text = sim_spp_lbl_txt[lang_idx])
    sim_run_btn.configure(text = sim_run_btn_txt[lang_idx])

# update frame states
def update_frame_states():
    # check dir validity
    if var_choose_folder.get() in ["", "/", "\\", ".", "~", ":"] or not os.path.isdir(var_choose_folder.get()):
        return
    if var_choose_folder.get() not in ["", "/", "\\", ".", "~", ":"] and os.path.isdir(var_choose_folder.get()):
        complete_frame(fst_step)
    else:
        enable_frame(fst_step)

    # check json files
    img_json = False
    path_to_image_json = os.path.join(var_choose_folder.get(), "image_recognition_file.json")
    if os.path.isfile(path_to_image_json):
        img_json = True
    vid_json = False
    if os.path.isfile(os.path.join(var_choose_folder.get(), "video_recognition_file.json")):
        vid_json = True
    
    # check if dir is already processed
    if img_json or vid_json:
        complete_frame(snd_step)
        enable_frame(fth_step)
    else:
        enable_frame(snd_step)
        disable_frame(fth_step)

    # check hitl status
    if img_json:
        status = get_hitl_var_in_json(path_to_image_json)
        if status == "never-started":
            enable_frame(trd_step)
            btn_hitl_main.configure(text = ["Start", "Iniciar"][lang_idx])
        elif status == "in-progress":
            enable_frame(trd_step)
            btn_hitl_main.configure(text = ["Continue", "Continuar"][lang_idx])
        elif status == "done":
            complete_frame(trd_step)
    else:
        disable_frame(trd_step)

# check if user entered text in entry widget
def no_user_input(var):
    if var.get() == "" or var.get().startswith("E.g.:") or var.get().startswith("Ejem.:"):
        return True
    else:
        return False

# show warning if not valid input
def invalid_value_warning(str, numeric = True):
    string = [f"You either entered an invalid value for the {str}, or none at all.", f"Ingresó un valor no válido para {str} o ninguno."][lang_idx] 
    if numeric:
        string += [" You can only enter numberic characters.", " Solo puede ingresar caracteres numéricos."][lang_idx]
    mb.showerror(invalid_value_txt[lang_idx], string)

# disable widgets based on row and col indeces
def disable_widgets_based_on_location(master, rows, cols):
    # list widgets to be removed
    widgets = []
    for row in rows:
        for col in cols:
            l = master.grid_slaves(row, col)
            for i in l:
                widgets.append(i)

    # remove widgets
    for widget in widgets:
        widget.configure(state=DISABLED)

# remove widgets based on row and col indexes
def remove_widgets_based_on_location(master, rows, cols):
    # list widgets to be removed
    widgets = []
    for row in rows:
        for col in cols:
            l = master.grid_slaves(row, col)
            for i in l:
                widgets.append(i)

    # remove widgets
    for widget in widgets:
        widget.grid_forget()

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
        self.text.configure(cursor="hand2")

    def _leave(self, event):
        self.text.configure(cursor="")

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
            child.configure(state=DISABLED)

# set all children of frame to normal state
def enable_widgets(frame):
    children = frame.winfo_children()
    for child in children:
        # labelframes have no state
        if child.winfo_class() != "Labelframe":
            child.configure(state=NORMAL)

# show warning for absolute paths option
shown_abs_paths_warning = True
def abs_paths_warning():
    global shown_abs_paths_warning
    if var_abs_paths.get() and shown_abs_paths_warning:
        mb.showinfo(warning_txt[lang_idx], ["It is not recommended to use absolute paths in the output file. Third party software (such "
                    "as Timelapse, Agouti etc.) will not be able to read the json file if the paths are absolute. Only enable"
                    " this option if you know what you are doing.",
                    "No se recomienda utilizar rutas absolutas en el archivo de salida. Software de terceros (como Timelapse, "
                    "Agouti etc.) no podrán leer el archivo json si las rutas son absolutas. Sólo active esta opción si sabe lo"
                    " que está haciendo."][lang_idx])
        shown_abs_paths_warning = False

# toggle image size entry box
def toggle_image_size_for_deploy():
    if var_use_custom_img_size_for_deploy.get():
        lbl_image_size_for_deploy.grid(row=row_image_size_for_deploy, sticky='nesw', pady=2)
        ent_image_size_for_deploy.grid(row=row_image_size_for_deploy, column=1, sticky='nesw', padx=5)
    else:
        lbl_image_size_for_deploy.grid_remove()
        ent_image_size_for_deploy.grid_remove()
    resize_canvas_to_content()

# toggle separation subframe
def toggle_sep_frame():
    if var_separate_files.get():
        sep_frame.grid(row=sep_frame_row, column=0, columnspan=2, sticky = 'ew')
        enable_widgets(sep_frame)
        sep_frame.configure(fg='black')
    else:
        disable_widgets(sep_frame)
        sep_frame.configure(fg='grey80')
        sep_frame.grid_forget()
    resize_canvas_to_content()

# toggle export subframe
def toggle_exp_frame():
    if var_exp.get():
        exp_frame.grid(row=exp_frame_row, column=0, columnspan=2, sticky = 'ew')
        enable_widgets(exp_frame)
        exp_frame.configure(fg='black')
    else:
        disable_widgets(exp_frame)
        exp_frame.configure(fg='grey80')
        exp_frame.grid_forget()
    resize_canvas_to_content()

# toggle classification subframe
def toggle_cls_frame(): 
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")

    # check the state of snd_step
    snd_step_enabled = False if snd_step.cget('fg') == 'grey80' else True

    # only enable cls_frame if snd_step is also enabled and user didn't choose None
    if var_cls_model.get() not in none_txt and snd_step_enabled:
        cls_frame.grid(row=cls_frame_row, column=0, columnspan=2, sticky = 'ew')
        enable_widgets(cls_frame)
        toggle_checkpoint_freq()
        cls_frame.configure(fg='black')
    else:
        disable_widgets(cls_frame)
        cls_frame.configure(fg='grey80')
        cls_frame.grid_forget()
    resize_canvas_to_content()

# toggle image subframe
def toggle_img_frame():
    if var_process_img.get():
        img_frame.grid(row=img_frame_row, column=0, columnspan=2, sticky = 'ew')
        enable_widgets(img_frame)
        toggle_checkpoint_freq()
        img_frame.configure(fg='black')
    else:
        disable_widgets(img_frame)
        img_frame.configure(fg='grey80')
        img_frame.grid_forget()
    resize_canvas_to_content()

# toggle video subframe
def toggle_vid_frame():
    if var_process_vid.get():
        vid_frame.grid(row=vid_frame_row, column=0, columnspan=2, sticky='ew')
        enable_widgets(vid_frame)
        toggle_nth_frame()
        vid_frame.configure(fg='black')
    else:
        disable_widgets(vid_frame)
        vid_frame.configure(fg='grey80')
        vid_frame.grid_forget()
    resize_canvas_to_content()

# convert frame to completed
def complete_frame(frame):
    global check_mark_one_row
    global check_mark_two_rows

    # check which frame 
    any_step = frame.cget('text').startswith(f' {step_txt[lang_idx]}')
    fst_step = frame.cget('text').startswith(f' {step_txt[lang_idx]} 1')
    snd_step = frame.cget('text').startswith(f' {step_txt[lang_idx]} 2')
    trd_step = frame.cget('text').startswith(f' {step_txt[lang_idx]} 3')
    fth_step = frame.cget('text').startswith(f' {step_txt[lang_idx]} 4')

    # adjust frames
    frame.configure(relief = 'groove')
    if any_step:
        frame.configure(fg='#579F2D')
    if snd_step:
        cls_frame.configure(relief = 'groove')
        img_frame.configure(relief = 'groove')
        vid_frame.configure(relief = 'groove')

    if trd_step or fst_step:
        # add check mark
        lbl_check_mark = Label(frame, image=check_mark_one_row)
        lbl_check_mark.image = check_mark_one_row
        lbl_check_mark.grid(row=0, column=0, rowspan=15, columnspan=2, sticky='nesw')
        if trd_step:
            btn_hitl_main.configure(text=["New session?", "¿Nueva sesión?"][lang_idx], state = NORMAL)
            btn_hitl_main.lift()
        if fst_step:
            btn_choose_folder.configure(text=f"{change_folder_txt[lang_idx]}?", state = NORMAL)
            btn_choose_folder.lift()
            dsp_choose_folder.lift()
    
    else:
        # the rest
        if not any_step:
            # sub frames of fth_step only
            frame.configure(fg='#579F2D')

        # add check mark
        lbl_check_mark = Label(frame, image=check_mark_two_rows)
        lbl_check_mark.image = check_mark_two_rows
        lbl_check_mark.grid(row=0, column=0, rowspan=15, columnspan=2, sticky='nesw')

        # add buttons
        btn_view_results = Button(master=frame, text=view_results_txt[lang_idx], width=1, command=lambda: view_results(frame))
        btn_view_results.grid(row=0, column=1, sticky='nesw', padx = 5)
        btn_uncomplete = Button(master=frame, text=again_txt[lang_idx], width=1, command=lambda: enable_frame(frame))
        btn_uncomplete.grid(row=1, column=1, sticky='nesw', padx = 5)

# enable a frame
def enable_frame(frame):
    uncomplete_frame(frame)
    enable_widgets(frame)

    # check which frame 
    any_step = frame.cget('text').startswith(f' {step_txt[lang_idx]}')
    fst_step = frame.cget('text').startswith(f' {step_txt[lang_idx]} 1')
    snd_step = frame.cget('text').startswith(f' {step_txt[lang_idx]} 2')
    trd_step = frame.cget('text').startswith(f' {step_txt[lang_idx]} 3')
    fth_step = frame.cget('text').startswith(f' {step_txt[lang_idx]} 4')

    # all frames
    frame.configure(relief = 'solid')
    if any_step:
        frame.configure(fg=EA_blue_color)
    if snd_step:
        toggle_cls_frame()
        cls_frame.configure(relief = 'solid')
        toggle_img_frame()
        img_frame.configure(relief = 'solid')
        toggle_vid_frame()
        vid_frame.configure(relief = 'solid')
        toggle_image_size_for_deploy()
    if fth_step:
        toggle_sep_frame()
        toggle_exp_frame()
        sep_frame.configure(relief = 'solid')

# remove checkmarks and complete buttons
def uncomplete_frame(frame):
    if not frame.cget('text').startswith(f' {step_txt[lang_idx]}'):
        # subframes in fth_step only
        frame.configure(fg='black')
    children = frame.winfo_children()
    for child in children:
        if child.winfo_class() == "Button" or child.winfo_class() == "Label":
            if child.cget('text') == again_txt[lang_idx] or child.cget('text') == view_results_txt[lang_idx] or child.cget('image') != "":
                child.grid_remove()

# disable a frame
def disable_frame(frame):
    uncomplete_frame(frame)
    disable_widgets(frame)
    # all frames
    frame.configure(fg='grey80')
    frame.configure(relief = 'flat')
    if frame.cget('text').startswith(f' {step_txt[lang_idx]} 2'):
        # snd_step only
        disable_widgets(cls_frame)
        cls_frame.configure(fg='grey80')
        cls_frame.configure(relief = 'flat')
        disable_widgets(img_frame)
        img_frame.configure(fg='grey80')
        img_frame.configure(relief = 'flat')
        disable_widgets(vid_frame)
        vid_frame.configure(fg='grey80')
        vid_frame.configure(relief = 'flat')
    if frame.cget('text').startswith(f' {step_txt[lang_idx]} 4'):
        # fth_step only
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
        lbl_checkpoint_freq.configure(state=NORMAL)
        ent_checkpoint_freq.configure(state=NORMAL)
    else:
        lbl_checkpoint_freq.configure(state=DISABLED)
        ent_checkpoint_freq.configure(state=DISABLED)

# toggle state of nth frame
def toggle_nth_frame():
    if var_not_all_frames.get():
        lbl_nth_frame.configure(state=NORMAL)
        ent_nth_frame.configure(state=NORMAL)
    else:
        lbl_nth_frame.configure(state=DISABLED)
        ent_nth_frame.configure(state=DISABLED)

# check required and maximum size of canvas and resize accordingly
def resize_canvas_to_content():
    root.update_idletasks()
    _, _, _, height_logo = advanc_main_frame.grid_bbox(0, 0)
    _, _, width_step1, height_step1 = deploy_scrollable_frame.grid_bbox(0, 1)
    _, _, _, height_step2 = deploy_scrollable_frame.grid_bbox(0, 2)
    _, _, width_step3, _ = deploy_scrollable_frame.grid_bbox(1, 1)
    canvas_required_height = height_step1 + height_step2
    canvas_required_width  = width_step1 + width_step3
    max_screen_height = root.winfo_screenheight()
    canvas_max_height = max_screen_height - height_logo - 300
    canvas_height = min(canvas_required_height, canvas_max_height, 800)
    deploy_canvas.configure(width = canvas_required_width, height = canvas_height)
    bg_height = canvas_height + height_logo + ADV_EXTRA_GRADIENT_HEIGHT
    new_advanc_bg_image = customtkinter.CTkImage(PIL_gradient, size=(ADV_WINDOW_WIDTH, bg_height))
    advanc_bg_image_label.configure(image=new_advanc_bg_image)

# functions to delete the grey text in the entry boxes for the...
# ... image size for deploy
image_size_for_deploy_init = True
def image_size_for_deploy_focus_in(_):
    global image_size_for_deploy_init
    if image_size_for_deploy_init and not var_image_size_for_deploy.get().isdigit():
        ent_image_size_for_deploy.delete(0, tk.END)
        ent_image_size_for_deploy.configure(fg='black')
    image_size_for_deploy_init = False

# ... checkpoint frequency
checkpoint_freq_init = True
def checkpoint_freq_focus_in(_):
    global checkpoint_freq_init
    if checkpoint_freq_init and not var_checkpoint_freq.get().isdigit():
        ent_checkpoint_freq.delete(0, tk.END)
        ent_checkpoint_freq.configure(fg='black')
    checkpoint_freq_init = False

# ... nth frame
nth_frame_init = True
def nth_frame_focus_in(_):
    global nth_frame_init
    if nth_frame_init and not var_nth_frame.get().isdigit():
        ent_nth_frame.delete(0, tk.END)
        ent_nth_frame.configure(fg='black')
    nth_frame_init = False

# check current status, switch to opposite and save
def switch_mode():

    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")

    # load
    advanced_mode = load_global_vars()["advanced_mode"]

    # switch
    if advanced_mode:
        advanc_mode.withdraw()
        simple_mode.deiconify()         
    else:
        advanc_mode.deiconify()
        simple_mode.withdraw()

    # save
    write_global_vars({
        "advanced_mode": not advanced_mode
    })

def sponsor_project():
    webbrowser.open("https://github.com/sponsors/PetervanLunteren")

class GreyTopButton(customtkinter.CTkButton):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color = ("#DBDBDB", "#333333"),
                       hover_color = ("#CFCFCF", "#2B2B2B"),
                       text_color = ("black", "white"),
                       height = 10,
                       width = 140,
                       border_width=GREY_BUTTON_BORDER_WIDTH)

def reset_values():

    # set vaules
    var_thresh.set(global_vars['var_thresh_default'])
    var_det_model_path.set("")
    var_det_model_short.set("")
    var_exclude_subs.set(False)
    var_use_custom_img_size_for_deploy.set(False)
    var_image_size_for_deploy.set("")
    var_abs_paths.set(False)
    var_disable_GPU.set(False)
    var_process_img.set(False)
    var_use_checkpnts.set(False)
    var_checkpoint_freq.set("")
    var_cont_checkpnt.set(False)
    var_process_vid.set(False)
    var_not_all_frames.set(False)
    var_nth_frame.set("")
    var_separate_files.set(False)
    var_file_placement.set(2)
    var_sep_conf.set(False)
    var_vis_files.set(False)
    var_crp_files.set(False)
    var_exp.set(False)
    var_exp_format.set(dpd_options_exp_format[lang_idx][global_vars['var_exp_format_idx']])
    write_global_vars({
        "var_det_model_idx": dpd_options_model[lang_idx].index(var_det_model.get()),
        "var_det_model_path": var_det_model_path.get(),
        "var_det_model_short": var_det_model_short.get(),
        "var_exclude_subs": var_exclude_subs.get(),
        "var_use_custom_img_size_for_deploy": var_use_custom_img_size_for_deploy.get(),
        "var_image_size_for_deploy": var_image_size_for_deploy.get() if var_image_size_for_deploy.get().isdigit() else "",
        "var_abs_paths": var_abs_paths.get(),
        "var_disable_GPU": var_disable_GPU.get(),
        "var_process_img": var_process_img.get(),
        "var_use_checkpnts": var_use_checkpnts.get(),
        "var_checkpoint_freq": var_checkpoint_freq.get() if var_checkpoint_freq.get().isdecimal() else "",
        "var_cont_checkpnt": var_cont_checkpnt.get(),
        "var_process_vid": var_process_vid.get(),
        "var_not_all_frames": var_not_all_frames.get(),
        "var_nth_frame": var_nth_frame.get() if var_nth_frame.get().isdecimal() else "",
        "var_separate_files": var_separate_files.get(),
        "var_file_placement": var_file_placement.get(),
        "var_sep_conf": var_sep_conf.get(),
        "var_vis_files": var_vis_files.get(),
        "var_crp_files": var_crp_files.get(),
        "var_exp": var_exp.get(),
        "var_exp_format_idx": dpd_options_exp_format[lang_idx].index(var_exp_format.get())
    })

    # reset model specific variables
    model_vars = load_model_vars()
    if model_vars != {}:

        # select all classes
        selected_classes = model_vars["all_classes"]
        write_model_vars(new_values = {"selected_classes": selected_classes})
        model_cls_animal_options(var_cls_model.get())

        # set model specific thresholds
        var_cls_detec_thresh.set(model_vars["var_cls_detec_thresh_default"])
        var_cls_class_thresh.set(model_vars["var_cls_class_thresh_default"])
        write_model_vars(new_values = {"var_cls_detec_thresh": var_cls_detec_thresh.get(),
                                    "var_cls_class_thresh": var_cls_class_thresh.get()})

    # update window
    toggle_cls_frame()
    toggle_img_frame()
    toggle_nth_frame()
    toggle_vid_frame()
    toggle_exp_frame()
    toggle_sep_frame()
    toggle_image_size_for_deploy()
    resize_canvas_to_content()

##########################################
############# TKINTER WINDOW #############
##########################################

# make it look similar on different systems
if os.name == "nt": # windows
    text_font = "TkDefaultFont"
    resize_img_factor = 0.95
    text_size_adjustment_factor = 0.83
    first_level_frame_font_size = 13
    second_level_frame_font_size = 10
    label_width = 320
    widget_width = 225
    frame_width = label_width + widget_width + 60
    subframe_correction_factor = 15
    minsize_rows = 28
    explanation_text_box_height_factor = 0.8
    PADY = 8
    PADX = 10
    ICON_SIZE = 35
    LOGO_SIZE = 50
    ADV_WINDOW_WIDTH = 1194
    SIM_WINDOW_WIDTH = 630
    SIM_WINDOW_HEIGHT = 699
    ADV_EXTRA_GRADIENT_HEIGHT = 78
    ADV_TOP_BANNER_WIDTH_FACTOR = 17.4
    SIM_TOP_BANNER_WIDTH_FACTOR = 6
    RESULTS_TABLE_WIDTH = 600
    RESULTS_WINDOW_WIDTH = 803
    RESULTS_WINDOW_HEIGHT = 700
    ADDAX_TXT_SIZE = 8
    GREY_BUTTON_BORDER_WIDTH = 0
elif sys.platform == "linux" or sys.platform == "linux2": # linux
    text_font = "Times"
    resize_img_factor = 1
    text_size_adjustment_factor = 0.7
    first_level_frame_font_size = 13
    second_level_frame_font_size = 10
    label_width = 320
    widget_width = 225
    frame_width = label_width + widget_width + 60
    subframe_correction_factor = 15
    minsize_rows = 28
    explanation_text_box_height_factor = 1
    PADY = 8
    PADX = 10
    ICON_SIZE = 35
    LOGO_SIZE = 50
    ADV_WINDOW_WIDTH = 1194
    SIM_WINDOW_WIDTH = 630
    SIM_WINDOW_HEIGHT = 683
    ADV_EXTRA_GRADIENT_HEIGHT = 70
    ADV_TOP_BANNER_WIDTH_FACTOR = 17.4
    SIM_TOP_BANNER_WIDTH_FACTOR = 6
    RESULTS_TABLE_WIDTH = 600
    RESULTS_WINDOW_WIDTH = 803
    RESULTS_WINDOW_HEIGHT = 700
    ADDAX_TXT_SIZE = 8
    GREY_BUTTON_BORDER_WIDTH = 1
else: # macOS
    text_font = "TkDefaultFont"
    resize_img_factor = 1
    text_size_adjustment_factor = 1
    first_level_frame_font_size = 15
    second_level_frame_font_size = 13
    label_width = 350
    widget_width = 170
    frame_width = label_width + widget_width + 50
    subframe_correction_factor = 15
    minsize_rows = 28
    explanation_text_box_height_factor = 1
    PADY = 8
    PADX = 10
    ICON_SIZE = 35
    LOGO_SIZE = 50
    ADV_WINDOW_WIDTH = 1194
    SIM_WINDOW_WIDTH = 630
    SIM_WINDOW_HEIGHT = 696
    ADV_EXTRA_GRADIENT_HEIGHT = 110
    ADV_TOP_BANNER_WIDTH_FACTOR = 17.4
    SIM_TOP_BANNER_WIDTH_FACTOR = 6
    RESULTS_TABLE_WIDTH = 600
    RESULTS_WINDOW_WIDTH = 803
    RESULTS_WINDOW_HEIGHT = 700
    ADDAX_TXT_SIZE = 9
    GREY_BUTTON_BORDER_WIDTH = 0

# TKINTER MAIN WINDOW 
root = Tk()
EcoAssist_icon_image = tk.PhotoImage(file=os.path.join(EcoAssist_files, "EcoAssist", "imgs", "logo_small_bg.png"))
root.iconphoto(True, EcoAssist_icon_image)
s = ttk.Style(root)
s.configure("TNotebook", tabposition='n')
root.withdraw()
main_label_font = customtkinter.CTkFont(family='CTkFont', size=14, weight = 'bold')

# ADVANCED MODE WINDOW 
advanc_mode = Toplevel(root)
advanc_mode.title(f"EcoAssist v{current_EA_version} - Advanced mode")
advanc_mode.geometry("+10+20")
advanc_mode.protocol("WM_DELETE_WINDOW", on_toplevel_close)
advanc_bg_image = customtkinter.CTkImage(PIL_gradient, size=(ADV_WINDOW_WIDTH, 10))
advanc_bg_image_label = customtkinter.CTkLabel(advanc_mode, image=advanc_bg_image)
advanc_bg_image_label.grid(row=0, column=0)
advanc_main_frame = customtkinter.CTkFrame(advanc_mode, corner_radius=0, fg_color = 'transparent')
advanc_main_frame.grid(row=0, column=0, sticky="ns")
tabControl = ttk.Notebook(advanc_main_frame)
advanc_mode.withdraw() # only show when all widgets are loaded

# logo
logoImage = customtkinter.CTkImage(PIL_logo, size=(LOGO_SIZE, LOGO_SIZE))
customtkinter.CTkLabel(advanc_main_frame, text="", image = logoImage).grid(column=0, row=0, columnspan=2, sticky='', pady=(PADY, 0), padx=0)
adv_top_banner = customtkinter.CTkImage(PIL_advanc_top_banner, size=(LOGO_SIZE * ADV_TOP_BANNER_WIDTH_FACTOR, LOGO_SIZE))
customtkinter.CTkLabel(advanc_main_frame, text="", image = adv_top_banner).grid(column=0, row=0, columnspan=2, sticky='ew', pady=(PADY, 0), padx=0)

# prepare check mark for later use
check_mark_one_row = PIL_checkmark.resize((20, 20), Image.Resampling.LANCZOS)
check_mark_one_row = ImageTk.PhotoImage(check_mark_one_row)
check_mark_two_rows = PIL_checkmark.resize((45, 45), Image.Resampling.LANCZOS)
check_mark_two_rows = ImageTk.PhotoImage(check_mark_two_rows)

# grey top buttons
adv_btn_switch_mode_txt = ["To simple mode", 'Al modo simple']
adv_btn_switch_mode = GreyTopButton(master = advanc_main_frame, text = adv_btn_switch_mode_txt[lang_idx], command = switch_mode)
adv_btn_switch_mode.grid(row=0, column=0, padx=PADX, pady=(PADY, 0), columnspan = 2, sticky="nw")
adv_btn_switch_lang = GreyTopButton(master = advanc_main_frame, text = "Switch language", command = set_language)
adv_btn_switch_lang.grid(row=0, column=0, padx=PADX, pady=(0, 0), columnspan = 2, sticky="sw")
adv_btn_sponsor_txt = ["Sponsor project", "Patrocine proyecto"]
adv_btn_sponsor = GreyTopButton(master = advanc_main_frame, text = adv_btn_sponsor_txt[lang_idx], command = sponsor_project)
adv_btn_sponsor.grid(row=0, column=0, padx=PADX, pady=(PADY, 0), columnspan = 2, sticky="ne")
adv_btn_reset_values_txt = ["Reset values", 'Restablecer valores']
adv_btn_reset_values = GreyTopButton(master = advanc_main_frame, text = adv_btn_reset_values_txt[lang_idx], command = reset_values)
adv_btn_reset_values.grid(row=0, column=0, padx=PADX, pady=(0, 0), columnspan = 2, sticky="se")

# about
adv_abo_lbl_txt = ["By Addax Data Science. More conservation technology? Visit", "Creado por Addax Data Science. ¿Más tecnología de conservación? Visite"]
adv_abo_lbl = tk.Label(advanc_main_frame, text=adv_abo_lbl_txt[lang_idx], font = Font(size = ADDAX_TXT_SIZE))
adv_abo_lbl.grid(row=6, column=0, columnspan = 2, sticky="")
adv_abo_lbl_link = tk.Label(advanc_main_frame, text="addaxdatascience.com", cursor="hand2", font = Font(size = ADDAX_TXT_SIZE, underline=1))
adv_abo_lbl_link.grid(row=7, column=0, columnspan = 2, sticky="", pady=(0, PADY))
adv_abo_lbl_link.bind("<Button-1>", lambda e: callback("http://addaxdatascience.com"))

# deploy tab
deploy_tab = ttk.Frame(tabControl)
deploy_tab.columnconfigure(0, weight=1, minsize=frame_width)
deploy_tab.columnconfigure(1, weight=1, minsize=frame_width)
deploy_tab_text = ['Deploy', 'Despliegue']
tabControl.add(deploy_tab, text=deploy_tab_text[lang_idx])
deploy_canvas = tk.Canvas(deploy_tab)
deploy_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
deploy_y_scrollbar = ttk.Scrollbar(deploy_tab, orient=tk.VERTICAL, command=deploy_canvas.yview)
deploy_y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
deploy_canvas.configure(yscrollcommand=deploy_y_scrollbar.set)
deploy_scrollable_frame = ttk.Frame(deploy_canvas)
deploy_canvas.create_window((0, 0), window=deploy_scrollable_frame, anchor="nw")
deploy_scrollable_frame.bind("<Configure>", lambda event: deploy_canvas.configure(scrollregion=deploy_canvas.bbox("all")))

# help tab
help_tab = ttk.Frame(tabControl)
help_tab_text = ['Help', 'Ayuda']
tabControl.add(help_tab, text=help_tab_text[lang_idx])

# about tab
about_tab = ttk.Frame(tabControl)
about_tab_text = ['About', 'Acerca de']
tabControl.add(about_tab, text=about_tab_text[lang_idx])

# grid
tabControl.grid(column=0, row=1, sticky="ns", pady = 0)

#### deploy tab
### first step
fst_step_txt = ['Step 1: Select folder', 'Paso 1: Seleccione carpeta']
row_fst_step = 1
fst_step = LabelFrame(deploy_scrollable_frame, text=" " + fst_step_txt[lang_idx] + " ", pady=2, padx=5, relief='solid', highlightthickness=5, font=100, fg=EA_blue_color, borderwidth=2)
fst_step.configure(font=(text_font, first_level_frame_font_size, "bold"))
fst_step.grid(column=0, row=row_fst_step, columnspan=1, sticky='ew')
fst_step.columnconfigure(0, weight=1, minsize=label_width)
fst_step.columnconfigure(1, weight=1, minsize=widget_width)

# choose folder
lbl_choose_folder_txt = ["Source folder", "Carpeta de origen"]
row_choose_folder = 0
lbl_choose_folder = Label(master=fst_step, text=lbl_choose_folder_txt[lang_idx], width=1, anchor="w")
lbl_choose_folder.grid(row=row_choose_folder, sticky='nesw', pady=2)
var_choose_folder = StringVar()
var_choose_folder.set("")
var_choose_folder_short = StringVar()
dsp_choose_folder = Label(master=fst_step, textvariable=var_choose_folder_short, fg='grey', padx = 5)
btn_choose_folder = Button(master=fst_step, text=browse_txt[lang_idx], width=1, command=lambda: [browse_dir(var_choose_folder, var_choose_folder_short, dsp_choose_folder, 25, row_choose_folder, 0, 'w', source_dir = True), update_frame_states()])
btn_choose_folder.grid(row=row_choose_folder, column=1, sticky='nesw', padx=5)

### second step
snd_step_txt = ['Step 2: Analysis', 'Paso 2: Análisis']
row_snd_step = 2
snd_step = LabelFrame(deploy_scrollable_frame, text=" " + snd_step_txt[lang_idx] + " ", pady=2, padx=5, relief='solid', highlightthickness=5, font=100, fg=EA_blue_color, borderwidth=2)
snd_step.configure(font=(text_font, first_level_frame_font_size, "bold"))
snd_step.grid(column=0, row=row_snd_step, sticky='nesw')
snd_step.columnconfigure(0, weight=1, minsize=label_width)
snd_step.columnconfigure(1, weight=1, minsize=widget_width)

# check which detectors are installed
det_models = fetch_known_models(DET_DIR)
dpd_options_model = [det_models + ["Custom model"], det_models + ["Otro modelo"]]

# choose detector
lbl_model_txt = ['Model to detect animals, vehicles, and persons', 'Modelo para detectar animales, vehículos y personas']
row_model = 0
lbl_model = Label(master=snd_step, text=lbl_model_txt[lang_idx], width=1, anchor="w")
lbl_model.grid(row=row_model, sticky='nesw', pady=2)
var_det_model = StringVar(snd_step)
var_det_model.set(dpd_options_model[lang_idx][global_vars["var_det_model_idx"]]) # take idx instead of string
var_det_model_short = StringVar()
var_det_model_short.set(global_vars["var_det_model_short"])
var_det_model_path = StringVar()
var_det_model_path.set(global_vars["var_det_model_path"])
dpd_model = OptionMenu(snd_step, var_det_model, *dpd_options_model[lang_idx], command=model_options)
dpd_model.configure(width=1)
dpd_model.grid(row=row_model, column=1, sticky='nesw', padx=5)
dsp_model = Label(master=snd_step, textvariable=var_det_model_short, fg=EA_blue_color)
if var_det_model_short.get() != "":
    dsp_model.grid(column=0, row=row_model, sticky='e')

# check if user has classifiers installed
cls_models = fetch_known_models(CLS_DIR)
dpd_options_cls_model = [["None"] + cls_models, ["Ninguno"] + cls_models]

# use classifier
lbl_cls_model_txt = ["Model to further identify animals", "Modelo para identificar mejor a los animales"]
row_cls_model = 1
lbl_cls_model = Label(snd_step, text=lbl_cls_model_txt[lang_idx], width=1, anchor="w")
lbl_cls_model.grid(row=row_cls_model, sticky='nesw', pady=2)
var_cls_model = StringVar(snd_step)
var_cls_model.set(dpd_options_cls_model[lang_idx][global_vars["var_cls_model_idx"]]) # take idx instead of string
dpd_cls_model = OptionMenu(snd_step, var_cls_model, *dpd_options_cls_model[lang_idx], command=model_cls_animal_options)
dpd_cls_model.configure(width=1, state=DISABLED)
dpd_cls_model.grid(row=row_cls_model, column=1, sticky='nesw', padx=5, pady=2)

# set global model vars for startup
model_vars = load_model_vars()

## classification option frame (hidden by default)
cls_frame_txt = ["Identification options", "Opciones de identificación"]
cls_frame_row = 2
cls_frame = LabelFrame(snd_step, text=" ↳ " + cls_frame_txt[lang_idx] + " ", pady=2, padx=5, relief='solid', highlightthickness=5, font=100, borderwidth=1, fg="black")
cls_frame.configure(font=(text_font, second_level_frame_font_size, "bold"))
cls_frame.grid(row=cls_frame_row, column=0, columnspan=2, sticky = 'ew')
cls_frame.columnconfigure(0, weight=1, minsize= label_width - subframe_correction_factor)
cls_frame.columnconfigure(1, weight=1, minsize= widget_width - subframe_correction_factor)
cls_frame.grid_forget()

# show model info
row_btn_model_info = 1
lbl_model_info_txt = ["Show model information", "Mostrar información del modelo (inglés)"]
row_model_info = 0
lbl_model_info = Label(master=cls_frame, text="     " + lbl_model_info_txt[lang_idx], width=1, anchor="w")
lbl_model_info.grid(row=row_model_info, sticky='nesw', pady=2)
btn_model_info = Button(master=cls_frame, text=show_txt[lang_idx], width=1, command=show_model_info)
btn_model_info.grid(row=row_model_info, column=1, sticky='nesw', padx=5)

# choose classes
lbl_choose_classes_txt = ["Select species", "Seleccionar especies"]
row_choose_classes = 1
lbl_choose_classes = Label(master=cls_frame, text="     " + lbl_choose_classes_txt[lang_idx], width=1, anchor="w")
lbl_choose_classes.grid(row=row_choose_classes, sticky='nesw', pady=2)
btn_choose_classes = Button(master=cls_frame, text=select_txt[lang_idx], width=1, command=open_species_selection)
btn_choose_classes.grid(row=row_choose_classes, column=1, sticky='nesw', padx=5)
if var_cls_model.get() not in none_txt:
    dsp_choose_classes = Label(cls_frame, text = f"{len(model_vars.get('selected_classes', []))} of {len(model_vars.get('all_classes', []))}")
else:
    dsp_choose_classes = Label(cls_frame, text= "")
dsp_choose_classes.grid(row=row_choose_classes, column=0, sticky='e', padx=0)
dsp_choose_classes.configure(fg=EA_blue_color)

# threshold to classify detections
lbl_cls_detec_thresh_txt = ["Detection confidence threshold", "Umbral de confianza de detección"]
row_cls_detec_thresh = 2
lbl_cls_detec_thresh = Label(cls_frame, text="     " + lbl_cls_detec_thresh_txt[lang_idx], width=1, anchor="w")
lbl_cls_detec_thresh.grid(row=row_cls_detec_thresh, sticky='nesw', pady=2)
var_cls_detec_thresh = DoubleVar()
var_cls_detec_thresh.set(model_vars.get('var_cls_detec_thresh', 0.6))
scl_cls_detec_thresh = Scale(cls_frame, from_=0.01, to=1, resolution=0.01, orient=HORIZONTAL,
                             variable=var_cls_detec_thresh, showvalue=0, width=10, length=1, state=DISABLED,
                             command=lambda value: write_model_vars(new_values = {"var_cls_detec_thresh": value}))
scl_cls_detec_thresh.grid(row=row_cls_detec_thresh, column=1, sticky='ew', padx=10)
dsp_cls_detec_thresh = Label(cls_frame, textvariable=var_cls_detec_thresh)
dsp_cls_detec_thresh.grid(row=row_cls_detec_thresh, column=0, sticky='e', padx=0)
dsp_cls_detec_thresh.configure(fg=EA_blue_color)

# threshold accept identifications
lbl_cls_class_thresh_txt = ["Classification confidence threshold", "Umbral de confianza de la clasificación"]
row_cls_class_thresh = 3
lbl_cls_class_thresh = Label(cls_frame, text="     " + lbl_cls_class_thresh_txt[lang_idx], width=1, anchor="w")
lbl_cls_class_thresh.grid(row=row_cls_class_thresh, sticky='nesw', pady=2)
var_cls_class_thresh = DoubleVar()
var_cls_class_thresh.set(model_vars.get('var_cls_class_thresh', 0.5))
scl_cls_class_thresh = Scale(cls_frame, from_=0.01, to=1, resolution=0.01, orient=HORIZONTAL,
                             variable=var_cls_class_thresh, showvalue=0, width=10, length=1, state=DISABLED,
                             command=lambda value: write_model_vars(new_values = {"var_cls_class_thresh": value}))
scl_cls_class_thresh.grid(row=row_cls_class_thresh, column=1, sticky='ew', padx=10)
dsp_cls_class_thresh = Label(cls_frame, textvariable=var_cls_class_thresh)
dsp_cls_class_thresh.grid(row=row_cls_class_thresh, column=0, sticky='e', padx=0)
dsp_cls_class_thresh.configure(fg=EA_blue_color)

# # Smoothen results
# lbl_smooth_cls_animal_txt = ["Smoothen results", "Suavizar resultados"]
# row_smooth_cls_animal = 4
# lbl_smooth_cls_animal = Label(cls_frame, text="     " + lbl_smooth_cls_animal_txt[lang_idx], width=1, anchor="w")
# lbl_smooth_cls_animal.grid(row=row_smooth_cls_animal, sticky='nesw', pady=2)
# var_smooth_cls_animal = BooleanVar()
# var_smooth_cls_animal.set(model_vars.get('var_smooth_cls_animal', False))
# chb_smooth_cls_animal = Checkbutton(cls_frame, variable=var_smooth_cls_animal, anchor="w",
#                                     command = lambda: write_model_vars(new_values = {"var_smooth_cls_animal": var_smooth_cls_animal.get()}))
# chb_smooth_cls_animal.grid(row=row_smooth_cls_animal, column=1, sticky='nesw', padx=5)

# include subdirectories
lbl_exclude_subs_txt = ["Don't process subdirectories", "No procesar subcarpetas"]
row_exclude_subs = 3
lbl_exclude_subs = Label(snd_step, text=lbl_exclude_subs_txt[lang_idx], width=1, anchor="w")
lbl_exclude_subs.grid(row=row_exclude_subs, sticky='nesw', pady=2)
var_exclude_subs = BooleanVar()
var_exclude_subs.set(global_vars['var_exclude_subs'])
chb_exclude_subs = Checkbutton(snd_step, variable=var_exclude_subs, anchor="w")
chb_exclude_subs.grid(row=row_exclude_subs, column=1, sticky='nesw', padx=5)

# use custom image size
lbl_use_custom_img_size_for_deploy_txt = ["Use custom image size", "Usar tamaño de imagen personalizado"]
row_use_custom_img_size_for_deploy = 4
lbl_use_custom_img_size_for_deploy = Label(snd_step, text=lbl_use_custom_img_size_for_deploy_txt[lang_idx], width=1, anchor="w")
lbl_use_custom_img_size_for_deploy.grid(row=row_use_custom_img_size_for_deploy, sticky='nesw', pady=2)
var_use_custom_img_size_for_deploy = BooleanVar()
var_use_custom_img_size_for_deploy.set(global_vars['var_use_custom_img_size_for_deploy'])
chb_use_custom_img_size_for_deploy = Checkbutton(snd_step, variable=var_use_custom_img_size_for_deploy, command=toggle_image_size_for_deploy, anchor="w")
chb_use_custom_img_size_for_deploy.grid(row=row_use_custom_img_size_for_deploy, column=1, sticky='nesw', padx=5)

# specify custom image size (not grid by default)
lbl_image_size_for_deploy_txt = ["Image size", "Tamaño imagen"]
row_image_size_for_deploy = 5
lbl_image_size_for_deploy = Label(snd_step, text=" ↳ " + lbl_image_size_for_deploy_txt[lang_idx], width=1, anchor="w")
var_image_size_for_deploy = StringVar()
var_image_size_for_deploy.set(global_vars['var_image_size_for_deploy'])
ent_image_size_for_deploy = tk.Entry(snd_step, textvariable=var_image_size_for_deploy, fg='grey', state=NORMAL, width=1)
if var_image_size_for_deploy.get() == "":
    ent_image_size_for_deploy.insert(0, f"{eg_txt[lang_idx]}: 640")
else:
    ent_image_size_for_deploy.configure(fg='black')
ent_image_size_for_deploy.bind("<FocusIn>", image_size_for_deploy_focus_in)
ent_image_size_for_deploy.configure(state=DISABLED)

# use absolute paths
lbl_abs_paths_txt = ["Use absolute paths in output file", "Usar rutas absolutas en archivo de salida"]
row_abs_path = 6
lbl_abs_paths = Label(snd_step, text=lbl_abs_paths_txt[lang_idx], width=1, anchor="w")
lbl_abs_paths.grid(row=row_abs_path, sticky='nesw', pady=2)
var_abs_paths = BooleanVar()
var_abs_paths.set(global_vars['var_abs_paths'])
chb_abs_paths = Checkbutton(snd_step, variable=var_abs_paths, command=abs_paths_warning, anchor="w")
chb_abs_paths.grid(row=row_abs_path, column=1, sticky='nesw', padx=5)

# use absolute paths
lbl_disable_GPU_txt = ["Disable GPU processing", "Desactivar el procesamiento en la GPU"]
row_disable_GPU = 7
lbl_disable_GPU = Label(snd_step, text=lbl_disable_GPU_txt[lang_idx], width=1, anchor="w")
lbl_disable_GPU.grid(row=row_disable_GPU, sticky='nesw', pady=2)
var_disable_GPU = BooleanVar()
var_disable_GPU.set(global_vars['var_disable_GPU'])
chb_disable_GPU = Checkbutton(snd_step, variable=var_disable_GPU, anchor="w")
chb_disable_GPU.grid(row=row_disable_GPU, column=1, sticky='nesw', padx=5)

# process images
lbl_process_img_txt = ["Process all images in the folder specified", "Procesar todas las imágenes en carpeta elegida"]
row_process_img = 8
lbl_process_img = Label(snd_step, text=lbl_process_img_txt[lang_idx], width=1, anchor="w")
lbl_process_img.grid(row=row_process_img, sticky='nesw', pady=2)
var_process_img = BooleanVar()
var_process_img.set(global_vars['var_process_img'])
chb_process_img = Checkbutton(snd_step, variable=var_process_img, command=toggle_img_frame, anchor="w")
chb_process_img.grid(row=row_process_img, column=1, sticky='nesw', padx=5)

## image option frame (hidden by default)
img_frame_txt = ["Image options", "Opciones de imagen"]
img_frame_row = 9
img_frame = LabelFrame(snd_step, text=" ↳ " + img_frame_txt[lang_idx] + " ", pady=2, padx=5, relief='solid', highlightthickness=5, font=100, borderwidth=1, fg="grey80")
img_frame.configure(font=(text_font, second_level_frame_font_size, "bold"))
img_frame.grid(row=img_frame_row, column=0, columnspan=2, sticky = 'ew')
img_frame.columnconfigure(0, weight=1, minsize=label_width - subframe_correction_factor)
img_frame.columnconfigure(1, weight=1, minsize=widget_width - subframe_correction_factor)
img_frame.grid_forget()

# use checkpoints
lbl_use_checkpnts_txt = ["Use checkpoints while running", "Usar puntos de control mientras se ejecuta"]
row_use_checkpnts = 0
lbl_use_checkpnts = Label(img_frame, text="     " + lbl_use_checkpnts_txt[lang_idx], pady=2, state=DISABLED, width=1, anchor="w")
lbl_use_checkpnts.grid(row=row_use_checkpnts, sticky='nesw')
var_use_checkpnts = BooleanVar()
var_use_checkpnts.set(global_vars['var_use_checkpnts'])
chb_use_checkpnts = Checkbutton(img_frame, variable=var_use_checkpnts, command=toggle_checkpoint_freq, state=DISABLED, anchor="w")
chb_use_checkpnts.grid(row=row_use_checkpnts, column=1, sticky='nesw', padx=5)

# checkpoint frequency
lbl_checkpoint_freq_txt = ["Checkpoint frequency", "Frecuencia puntos de control"]
row_checkpoint_freq = 1
lbl_checkpoint_freq = tk.Label(img_frame, text="        ↳ " + lbl_checkpoint_freq_txt[lang_idx], pady=2, state=DISABLED, width=1, anchor="w")
lbl_checkpoint_freq.grid(row=row_checkpoint_freq, sticky='nesw')
var_checkpoint_freq = StringVar()
var_checkpoint_freq.set(global_vars['var_checkpoint_freq'])
ent_checkpoint_freq = tk.Entry(img_frame, textvariable=var_checkpoint_freq, fg='grey', state=NORMAL, width=1)
ent_checkpoint_freq.grid(row=row_checkpoint_freq, column=1, sticky='nesw', padx=5)
if var_checkpoint_freq.get() == "":
    ent_checkpoint_freq.insert(0, f"{eg_txt[lang_idx]}: 10000")
else:
    ent_checkpoint_freq.configure(fg='black')
ent_checkpoint_freq.bind("<FocusIn>", checkpoint_freq_focus_in)
ent_checkpoint_freq.configure(state=DISABLED)

# continue from checkpoint file
lbl_cont_checkpnt_txt = ["Continue from last checkpoint file", "Continuar desde el último punto de control"]
row_cont_checkpnt = 2
lbl_cont_checkpnt = Label(img_frame, text="     " + lbl_cont_checkpnt_txt[lang_idx], pady=2, state=DISABLED, width=1, anchor="w")
lbl_cont_checkpnt.grid(row=row_cont_checkpnt, sticky='nesw')
var_cont_checkpnt = BooleanVar()
var_cont_checkpnt.set(global_vars['var_cont_checkpnt'])
chb_cont_checkpnt = Checkbutton(img_frame, variable=var_cont_checkpnt, state=DISABLED, command=disable_chb_cont_checkpnt, anchor="w")
chb_cont_checkpnt.grid(row=row_cont_checkpnt, column=1, sticky='nesw', padx=5)

# process videos
lbl_process_vid_txt = ["Process all videos in the folder specified", "Procesar todos los vídeos en la carpeta elegida"]
row_process_vid = 10
lbl_process_vid = Label(snd_step, text=lbl_process_vid_txt[lang_idx], width=1, anchor="w")
lbl_process_vid.grid(row=row_process_vid, sticky='nesw', pady=2)
var_process_vid = BooleanVar()
var_process_vid.set(global_vars['var_process_vid'])
chb_process_vid = Checkbutton(snd_step, variable=var_process_vid, command=toggle_vid_frame, anchor="w")
chb_process_vid.grid(row=row_process_vid, column=1, sticky='nesw', padx=5)

## video option frame (disabled by default)
vid_frame_txt = ["Video options", "Opciones de vídeo"]
vid_frame_row = 11
vid_frame = LabelFrame(snd_step, text=" ↳ " + vid_frame_txt[lang_idx] + " ", pady=2, padx=5, relief='solid', highlightthickness=5, font=100, borderwidth=1, fg="grey80")
vid_frame.configure(font=(text_font, second_level_frame_font_size, "bold"))
vid_frame.grid(row=vid_frame_row, column=0, columnspan=2, sticky='ew')
vid_frame.columnconfigure(0, weight=1, minsize=label_width - subframe_correction_factor)
vid_frame.columnconfigure(1, weight=1, minsize=widget_width - subframe_correction_factor)
vid_frame.grid_forget()

# dont process all frames
lbl_not_all_frames_txt = ["Don't process every frame", "No procesar cada fotograma"]
row_not_all_frames = 0
lbl_not_all_frames = Label(vid_frame, text="     " + lbl_not_all_frames_txt[lang_idx], pady=2, state=DISABLED, width=1, anchor="w")
lbl_not_all_frames.grid(row=row_not_all_frames, sticky='nesw')
var_not_all_frames = BooleanVar()
var_not_all_frames.set(global_vars['var_not_all_frames'])
chb_not_all_frames = Checkbutton(vid_frame, variable=var_not_all_frames, command=toggle_nth_frame, state=DISABLED, anchor="w")
chb_not_all_frames.grid(row=row_not_all_frames, column=1, sticky='nesw', padx=5)

# process every nth frame
lbl_nth_frame_txt = ["Analyse every Nth frame", "Analizar cada Nº fotograma"]
row_nth_frame = 1
lbl_nth_frame = tk.Label(vid_frame, text="        ↳ " + lbl_nth_frame_txt[lang_idx], pady=2, state=DISABLED, width=1, anchor="w")
lbl_nth_frame.grid(row=row_nth_frame, sticky='nesw')
var_nth_frame = StringVar()
var_nth_frame.set(global_vars['var_nth_frame'])
ent_nth_frame = tk.Entry(vid_frame, textvariable=var_nth_frame, fg='grey', state=NORMAL, width=1)
ent_nth_frame.grid(row=row_nth_frame, column=1, sticky='nesw', padx=5)
if var_nth_frame.get() == "":
    ent_nth_frame.insert(0, f"{eg_txt[lang_idx]}: 10")
else:
    ent_nth_frame.configure(fg='black')
ent_nth_frame.bind("<FocusIn>", nth_frame_focus_in)
ent_nth_frame.configure(state=DISABLED)

# button start deploy
btn_start_deploy_txt = ["Deploy model", "Desplegar modelo"]
row_btn_start_deploy = 12
btn_start_deploy = Button(snd_step, text=btn_start_deploy_txt[lang_idx], command=start_deploy)
btn_start_deploy.grid(row=row_btn_start_deploy, column=0, columnspan=2, sticky='ew')

### human-in-the-loop step
trd_step_txt = ["Step 3: Annotation (optional)", "Paso 3: Anotación (opcional)"]
trd_step_row = 1
trd_step = LabelFrame(deploy_scrollable_frame, text=" " + trd_step_txt[lang_idx] + " ", pady=2, padx=5, relief='solid', highlightthickness=5, font=100, fg=EA_blue_color, borderwidth=2)
trd_step.configure(font=(text_font, first_level_frame_font_size, "bold"))
trd_step.grid(column=1, row=trd_step_row, sticky='nesw')
trd_step.columnconfigure(0, weight=1, minsize=label_width)
trd_step.columnconfigure(1, weight=1, minsize=widget_width)

# human-in-the-loop 
lbl_hitl_main_txt = ["Manually verify results", "Verificar manualmente los resultados"]
row_hitl_main = 0
lbl_hitl_main = Label(master=trd_step, text=lbl_hitl_main_txt[lang_idx], width=1, anchor="w")
lbl_hitl_main.grid(row=row_hitl_main, sticky='nesw', pady=2)
btn_hitl_main = Button(master=trd_step, text=["Start", "Iniciar"][lang_idx], width=1, command = start_or_continue_hitl)
btn_hitl_main.grid(row=row_hitl_main, column=1, sticky='nesw', padx=5)

### fourth step
fth_step_txt = ["Step 4: Post-processing (optional)", "Paso 4: Post-Procesado (opcional)"]
fth_step_row = 2
fth_step = LabelFrame(deploy_scrollable_frame, text=" " + fth_step_txt[lang_idx] + " ", pady=2, padx=5, relief='solid', highlightthickness=5, font=100, fg=EA_blue_color, borderwidth=2)
fth_step.configure(font=(text_font, first_level_frame_font_size, "bold"))
fth_step.grid(column=1, row=fth_step_row, sticky='nesw')
fth_step.columnconfigure(0, weight=1, minsize=label_width)
fth_step.columnconfigure(1, weight=1, minsize=widget_width)

# folder for results
lbl_output_dir_txt = ["Destination folder", "Carpeta de destino"]
row_output_dir = 0
lbl_output_dir = Label(master=fth_step, text=lbl_output_dir_txt[lang_idx], width=1, anchor="w")
lbl_output_dir.grid(row=row_output_dir, sticky='nesw', pady=2)
var_output_dir = StringVar()
var_output_dir.set("")
var_output_dir_short = StringVar()
dsp_output_dir = Label(master=fth_step, textvariable=var_output_dir_short, fg=EA_blue_color)
btn_output_dir = Button(master=fth_step, text=browse_txt[lang_idx], width=1, command=lambda: browse_dir(var_output_dir, var_output_dir_short, dsp_output_dir, 25, row_output_dir, 0, 'e'))
btn_output_dir.grid(row=row_output_dir, column=1, sticky='nesw', padx=5)

# separate files
lbl_separate_files_txt = ["Separate files into subdirectories", "Separar archivos en subcarpetas"]
row_separate_files = 1
lbl_separate_files = Label(fth_step, text=lbl_separate_files_txt[lang_idx], width=1, anchor="w")
lbl_separate_files.grid(row=row_separate_files, sticky='nesw', pady=2)
var_separate_files = BooleanVar()
var_separate_files.set(global_vars['var_separate_files'])
chb_separate_files = Checkbutton(fth_step, variable=var_separate_files, command=toggle_sep_frame, anchor="w")
chb_separate_files.grid(row=row_separate_files, column=1, sticky='nesw', padx=5)

## separation frame
sep_frame_txt = ["Separation options", "Opciones de separación"]
sep_frame_row = 2
sep_frame = LabelFrame(fth_step, text=" ↳ " + sep_frame_txt[lang_idx] + " ", pady=2, padx=5, relief='solid', highlightthickness=5, font=100, borderwidth=1, fg="grey80")
sep_frame.configure(font=(text_font, second_level_frame_font_size, "bold"))
sep_frame.grid(row=sep_frame_row, column=0, columnspan=2, sticky = 'ew')
sep_frame.columnconfigure(0, weight=1, minsize=label_width - subframe_correction_factor)
sep_frame.columnconfigure(1, weight=1, minsize=widget_width - subframe_correction_factor)
sep_frame.grid_forget()

# method of file placement
lbl_file_placement_txt = ["Method of file placement", "Método de desplazamiento de archivo"]
row_file_placement = 0
lbl_file_placement = Label(sep_frame, text="     " + lbl_file_placement_txt[lang_idx], pady=2, width=1, anchor="w")
lbl_file_placement.grid(row=row_file_placement, sticky='nesw')
var_file_placement = IntVar()
var_file_placement.set(global_vars['var_file_placement'])
rad_file_placement_move = Radiobutton(sep_frame, text=["Copy", "Copiar"][lang_idx], variable=var_file_placement, value=2)
rad_file_placement_move.grid(row=row_file_placement, column=1, sticky='w', padx=5)
rad_file_placement_copy = Radiobutton(sep_frame, text=["Move", "Mover"][lang_idx], variable=var_file_placement, value=1)
rad_file_placement_copy.grid(row=row_file_placement, column=1, sticky='e', padx=5)

# separate per confidence
lbl_sep_conf_txt = ["Sort results based on confidence", "Clasificar resultados basados en confianza"]
row_sep_conf = 1
lbl_sep_conf = Label(sep_frame, text="     " + lbl_sep_conf_txt[lang_idx], width=1, anchor="w")
lbl_sep_conf.grid(row=row_sep_conf, sticky='nesw', pady=2)
var_sep_conf = BooleanVar()
var_sep_conf.set(global_vars['var_sep_conf'])
chb_sep_conf = Checkbutton(sep_frame, variable=var_sep_conf, anchor="w")
chb_sep_conf.grid(row=row_sep_conf, column=1, sticky='nesw', padx=5)

## visualize images
lbl_vis_files_txt = ["Draw bounding boxes and confidences", "Dibujar contornos y confianzas"]
row_vis_files = 3
lbl_vis_files = Label(fth_step, text=lbl_vis_files_txt[lang_idx], width=1, anchor="w")
lbl_vis_files.grid(row=row_vis_files, sticky='nesw', pady=2)
var_vis_files = BooleanVar()
var_vis_files.set(global_vars['var_vis_files'])
chb_vis_files = Checkbutton(fth_step, variable=var_vis_files, anchor="w")
chb_vis_files.grid(row=row_vis_files, column=1, sticky='nesw', padx=5)

## crop images
lbl_crp_files_txt = ["Crop detections", "Recortar detecciones"]
row_crp_files = 4
lbl_crp_files = Label(fth_step, text=lbl_crp_files_txt[lang_idx], width=1, anchor="w")
lbl_crp_files.grid(row=row_crp_files, sticky='nesw', pady=2)
var_crp_files = BooleanVar()
var_crp_files.set(global_vars['var_crp_files'])
chb_crp_files = Checkbutton(fth_step, variable=var_crp_files, anchor="w")
chb_crp_files.grid(row=row_crp_files, column=1, sticky='nesw', padx=5)

# export results
lbl_exp_txt = ["Export results and retrieve metadata", "Exportar resultados y recuperar metadatos"]
row_exp = 5
lbl_exp = Label(fth_step, text=lbl_exp_txt[lang_idx], width=1, anchor="w")
lbl_exp.grid(row=row_exp, sticky='nesw', pady=2)
var_exp = BooleanVar()
var_exp.set(global_vars['var_exp'])
chb_exp = Checkbutton(fth_step, variable=var_exp, anchor="w", command=toggle_exp_frame)
chb_exp.grid(row=row_exp, column=1, sticky='nesw', padx=5)

## exportation options
exp_frame_txt = ["Export options", "Opciones de exportación"]
exp_frame_row = 6
exp_frame = LabelFrame(fth_step, text=" ↳ " + exp_frame_txt[lang_idx] + " ", pady=2, padx=5, relief='solid', highlightthickness=5, font=100, borderwidth=1, fg="grey80")
exp_frame.configure(font=(text_font, second_level_frame_font_size, "bold"))
exp_frame.grid(row=exp_frame_row, column=0, columnspan=2, sticky = 'ew')
exp_frame.columnconfigure(0, weight=1, minsize=label_width - subframe_correction_factor)
exp_frame.columnconfigure(1, weight=1, minsize=widget_width - subframe_correction_factor)
exp_frame.grid_forget()

# export format
lbl_exp_format_txt = ["Output file format", "Formato del archivo de salida"]
row_exp_format = 0
lbl_exp_format = Label(exp_frame, text="     " + lbl_exp_format_txt[lang_idx], pady=2, width=1, anchor="w")
lbl_exp_format.grid(row=row_exp_format, sticky='nesw')
dpd_options_exp_format = [["XLSX", "CSV"], ["XLSX", "CSV"]]
var_exp_format = StringVar(exp_frame)
var_exp_format.set(dpd_options_exp_format[lang_idx][global_vars['var_exp_format_idx']])
dpd_exp_format = OptionMenu(exp_frame, var_exp_format, *dpd_options_exp_format[lang_idx])
dpd_exp_format.configure(width=1)
dpd_exp_format.grid(row=row_exp_format, column=1, sticky='nesw', padx=5)

# threshold
lbl_thresh_txt = ["Confidence threshold", "Umbral de confianza"]
row_lbl_thresh = 7
lbl_thresh = Label(fth_step, text=lbl_thresh_txt[lang_idx], width=1, anchor="w")
lbl_thresh.grid(row=row_lbl_thresh, sticky='nesw', pady=2)
var_thresh = DoubleVar()
var_thresh.set(global_vars['var_thresh'])
scl_thresh = Scale(fth_step, from_=0.01, to=1, resolution=0.01, orient=HORIZONTAL, variable=var_thresh, showvalue=0, width=10, length=1)
scl_thresh.grid(row=row_lbl_thresh, column=1, sticky='ew', padx=10)
dsp_thresh = Label(fth_step, textvariable=var_thresh)
dsp_thresh.configure(fg=EA_blue_color)
dsp_thresh.grid(row=row_lbl_thresh, column=0, sticky='e', padx=0)

# postprocessing button
btn_start_postprocess_txt = ["Post-process files", "Post-procesar archivos"]
row_start_postprocess = 8
btn_start_postprocess = Button(fth_step, text=btn_start_postprocess_txt[lang_idx], command=start_postprocess)
btn_start_postprocess.grid(row=row_start_postprocess, column=0, columnspan = 2, sticky='ew')

# set minsize for all rows inside labelframes...
for frame in [fst_step, snd_step, cls_frame, img_frame, vid_frame, fth_step, sep_frame]:
    set_minsize_rows(frame)

# ... but not for the hidden rows
snd_step.grid_rowconfigure(row_cls_detec_thresh, minsize=0) # model tresh
snd_step.grid_rowconfigure(row_image_size_for_deploy, minsize=0) # image size for deploy
snd_step.grid_rowconfigure(cls_frame_row, minsize=0) # cls options
snd_step.grid_rowconfigure(img_frame_row, minsize=0) # image options
snd_step.grid_rowconfigure(vid_frame_row, minsize=0) # video options
cls_frame.grid_rowconfigure(row_cls_detec_thresh, minsize=0) # cls animal thresh
# cls_frame.grid_rowconfigure(row_smooth_cls_animal, minsize=0) # cls animal smooth
fth_step.grid_rowconfigure(sep_frame_row, minsize=0) # sep options
fth_step.grid_rowconfigure(exp_frame_row, minsize=0) # exp options

# enable scroll on mousewheel
def deploy_canvas_mousewheel(event):
    if os.name == 'nt':
        deploy_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    else:
        deploy_canvas.yview_scroll(int(-1 * (event.delta / 2)), 'units')

# make deploy_tab scrollable
def bind_scroll_to_deploy_canvas():
    deploy_canvas.update_idletasks()
    deploy_canvas.configure(scrollregion=deploy_canvas.bbox("all"))
    deploy_canvas.bind_all("<MouseWheel>", deploy_canvas_mousewheel)
    deploy_canvas.bind_all("<Button-4>", deploy_canvas_mousewheel)
    deploy_canvas.bind_all("<Button-5>", deploy_canvas_mousewheel)
bind_scroll_to_deploy_canvas()

# resize deploy tab to content
resize_canvas_to_content()

# help tab
scroll = Scrollbar(help_tab)
help_text = Text(help_tab, width=1, height=1, wrap=WORD, yscrollcommand=scroll.set) 
help_text.configure(spacing1=2, spacing2=3, spacing3=2)
help_text.tag_config('intro', font=f'{text_font} {int(13 * text_size_adjustment_factor)} italic', foreground='black', lmargin1=10, lmargin2=10, underline = False) 
help_text.tag_config('tab', font=f'{text_font} {int(16 * text_size_adjustment_factor)} bold', foreground='black', lmargin1=10, lmargin2=10, underline = True) 
help_text.tag_config('frame', font=f'{text_font} {int(15 * text_size_adjustment_factor)} bold', foreground='darkblue', lmargin1=15, lmargin2=15) 
help_text.tag_config('feature', font=f'{text_font} {int(14 * text_size_adjustment_factor)} normal', foreground='black', lmargin1=20, lmargin2=20, underline = True) 
help_text.tag_config('explanation', font=f'{text_font} {int(13 * text_size_adjustment_factor)} normal', lmargin1=25, lmargin2=25)
hyperlink1 = HyperlinkManager(help_text)

# function to write text which can be called when user changes language settings
def write_help_tab():
    global help_text
    line_number = 1 

    # intro sentence
    help_text.insert(END, ["Below you can find detailed documentation for each setting. If you have any questions, feel free to contact me on ",
                           "A continuación encontrarás documentación detallada sobre cada ajuste. Si tienes alguna pregunta, no dudes en ponerte en contacto conmigo en "][lang_idx])
    help_text.insert(INSERT, "peter@addaxdatascience.com", hyperlink1.add(partial(webbrowser.open, "mailto:peter@addaxdatascience.com")))
    help_text.insert(END, [" or raise an issue on the ", " o plantear una incidencia en "][lang_idx])
    help_text.insert(INSERT, ["GitHub page", "la página de GitHub"][lang_idx], hyperlink1.add(partial(webbrowser.open, "https://github.com/PetervanLunteren/EcoAssist/issues")))
    help_text.insert(END, ".\n\n")
    help_text.tag_add('intro', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

    # first step
    help_text.insert(END, f"{fst_step_txt[lang_idx]}\n")
    help_text.tag_add('frame', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
    help_text.insert(END, f"{browse_txt[lang_idx]}\n")
    help_text.insert(END, ["Here you can browse for a folder which contains images and/or video\'s. The model will be deployed on this directory, as well as the post-processing analyses.\n\n",
                           "Aquí puede buscar una carpeta que contenga imágenes y/o vídeos. El modelo se desplegará en este directorio, así como los análisis de post-procesamiento.\n\n"][lang_idx])
    help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
    help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

    # second step
    help_text.insert(END, f"{snd_step_txt[lang_idx]}\n")
    help_text.tag_add('frame', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1

    # det model
    help_text.insert(END, f"{lbl_model_txt[lang_idx]}\n")
    help_text.insert(END, ["EcoAssist uses a combination of a detection model and a classification model to identify animals. The detection model will locate the animal, whereas the "
                           "classification model will identify which species the animal belongs to. Here, you can select the detection model that you want to use. If the dropdown "
                           "option 'Custom model' is selected, you will be prompted to select a custom YOLOv5 model file. The preloaded 'MegaDetector' models detect animals, people, "
                           "and vehicles in camera trap imagery. It does not identify the animals; it just finds them. Version A and B differ only in their training data. Each model "
                           "can outperform the other slightly, depending on your data. Try them both and see which one works best for you. If you really don't have a clue, just stick "
                           "with the default 'MegaDetector 5a'. More info about MegaDetector models ", "EcoAssist utiliza una combinación de un modelo de detección y un modelo de "
                           "clasificación para identificar animales. El modelo de detección localizará al animal, mientras que el modelo de clasificación identificará a qué especie "
                           "pertenece el animal. Aquí puede seleccionar el modelo de detección que desea utilizar. Si selecciona la opción desplegable 'Modelo personalizado', se le "
                           "pedirá que seleccione un archivo de modelo YOLOv5 personalizado. Los modelos 'MegaDetector' precargados detectan animales, personas y vehículos en imágenes"
                           " de cámaras trampa. No identifica a los animales, sólo los encuentra. Las versiones A y B sólo se diferencian en los datos de entrenamiento. Cada modelo "
                           "puede superar ligeramente al otro, dependiendo de sus datos. Pruebe los dos y vea cuál le funciona mejor. Si realmente no tienes ni idea, quédate con el "
                           "'MegaDetector 5a' por defecto. Más información sobre los modelos MegaDetector "][lang_idx])
    help_text.insert(INSERT, ["here", "aquí"][lang_idx], hyperlink1.add(partial(webbrowser.open, "https://github.com/ecologize/CameraTraps/blob/main/megadetector.md#megadetector-v50-20220615")))
    help_text.insert(END, ".\n\n")
    help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
    help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

    # cls model
    help_text.insert(END, f"{lbl_cls_model_txt[lang_idx]}\n")
    help_text.insert(END, ["EcoAssist uses a combination of a detection model and a classification model to identify animals. The detection model will locate the animal, whereas the "
                           "classification model will identify which species the animal belongs to. Here, you can select the classification model that you want to use. Each "
                           "classification model is developed for a specific area. Explore which model suits your data best, but please note that models developed for other biomes "
                           "or projects do not necessarily perform equally well in other ecosystems. Always investigate the model’s accuracy on your data before accepting any results.", 
                           "EcoAssist utiliza una combinación de un modelo de detección y un modelo de clasificación para identificar animales. El modelo de detección localizará al "
                           "animal, mientras que el modelo de clasificación identificará a qué especie pertenece el animal. Aquí puede seleccionar el modelo de clasificación que desea "
                           "utilizar. Cada modelo de clasificación se desarrolla para un área específica. Explore qué modelo se adapta mejor a sus datos, pero tenga en cuenta que los "
                           "modelos desarrollados para otros biomas o proyectos no funcionan necesariamente igual de bien en otros ecosistemas. Investiga siempre la precisión del modelo"
                           " en tus datos antes de aceptar cualquier resultado."][lang_idx])
    help_text.insert(END, "\n\n")
    help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
    help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

    # cls model info
    help_text.insert(END, f"{lbl_model_info_txt[lang_idx]}\n")
    help_text.insert(END, ["This will open a window with model information.", "Esto abrirá una ventana con información sobre el modelo."][lang_idx])
    help_text.insert(END, "\n\n")
    help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
    help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

    # cls spp selection
    help_text.insert(END, f"{lbl_choose_classes_txt[lang_idx]}\n")
    help_text.insert(END, ["Here, you can select and deselect the animals categories that are present in your project"
                          " area. If the animal category is not selected, it will be excluded from the results. The "
                          "category list will update according to the model selected.", "Aquí puede seleccionar y anular"
                          " la selección de las categorías de animales presentes en la zona de su proyecto. Si la "
                          "categoría de animales no está seleccionada, quedará excluida de los resultados. La lista de "
                          "categorías se actualizará según el modelo seleccionado."][lang_idx])
    help_text.insert(END, "\n\n")
    help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
    help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

    # threshold to classify detections
    help_text.insert(END, f"{lbl_cls_detec_thresh_txt[lang_idx]}\n")
    help_text.insert(END, ["EcoAssist uses a combination of a detection model and a classification model to identify animals. The detection model will locate "
                           "the animal, whereas the classification model will identify which species the animal belongs to. This confidence threshold defines "
                           "which animal detections will be passed on to the classification model for further identification.", "EcoAssist utiliza una "
                           "combinación de un modelo de detección y un modelo de clasificación para identificar a los animales. El modelo de detección "
                           "localizará al animal, mientras que el modelo de clasificación identificará a qué especie pertenece el animal. Este umbral de "
                           "confianza define qué animales detectados se pasarán al modelo de clasificación para su posterior identificación."][lang_idx])
    help_text.insert(END, "\n\n")
    help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
    help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

    # threshold to classify detections
    help_text.insert(END, f"{lbl_cls_class_thresh_txt[lang_idx]}\n")
    help_text.insert(END, ["EcoAssist uses a combination of a detection model and a classification model to identify animals. The detection model will locate "
                           "the animal, whereas the classification model will identify which species the animal belongs to. This confidence threshold defines "
                           "which animal identifications will be accepted.", "EcoAssist utiliza una combinación de un modelo de detección y un modelo de "
                           "clasificación para identificar a los animales. El modelo de detección localizará al animal, mientras que el modelo de clasificación"
                           " identificará a qué especie pertenece el animal. Este umbral de confianza define qué identificaciones de animales se aceptarán."][lang_idx])
    help_text.insert(END, "\n\n")
    help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
    help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

    # exclude subs
    help_text.insert(END, f"{lbl_exclude_subs_txt[lang_idx]}\n")
    help_text.insert(END, ["By default, EcoAssist will recurse into subdirectories. Select this option if you want to ignore the subdirectories and process only"
                           " the files directly in the chosen folder.\n\n", "Por defecto, EcoAssist buscará en los subdirectorios. Seleccione esta opción si "
                           "desea ignorar los subdirectorios y procesar sólo los archivos directamente en la carpeta elegida.\n\n"][lang_idx])
    help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
    help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

    # exclude detections
    help_text.insert(END, f"{lbl_use_custom_img_size_for_deploy_txt[lang_idx]} / {lbl_image_size_for_deploy_txt[lang_idx]}\n")
    help_text.insert(END, ["EcoAssist will resize the images before they get processed. EcoAssist will by default resize the images to 1280 pixels. "
                    "Deploying a model with a lower image size will reduce the processing time, but also the detection accuracy. Best results are obtained if you use the"
                    " same image size as the model was trained on. If you trained a model in EcoAssist using the default image size, you should set this value to 640 for "
                    "the YOLOv5 models. Use the default for the MegaDetector models.\n\n",
                    "EcoAssist redimensionará las imágenes antes de procesarlas. Por defecto, EcoAssist redimensionará las imágenes a 1280 píxeles. Desplegar un modelo "
                    "con un tamaño de imagen inferior reducirá el tiempo de procesamiento, pero también la precisión de la detección. Los mejores resultados se obtienen "
                    "si se utiliza el mismo tamaño de imagen con el que se entrenó el modelo. Si ha entrenado un modelo en EcoAssist utilizando el tamaño de imagen por "
                    "defecto, debe establecer este valor en 640 para los modelos YOLOv5. Utilice el valor por defecto para los modelos MegaDetector.\n\n"][lang_idx])
    help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
    help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

    # use absolute paths
    help_text.insert(END, f"{lbl_abs_paths_txt[lang_idx]}\n")
    help_text.insert(END, ["By default, the paths in the output file are relative (i.e. 'image.jpg') instead of absolute (i.e. '/path/to/some/folder/image.jpg'). This "
                    "option will make sure the output file contains absolute paths, but it is not recommended. Third party software (such as ",
                    "Por defecto, las rutas en el archivo de salida son relativas (es decir, 'imagen.jpg') en lugar de absolutas (es decir, '/ruta/a/alguna/carpeta/"
                    "imagen.jpg'). Esta opción se asegurará de que el archivo de salida contenga rutas absolutas, pero no se recomienda. Software de terceros (como "][lang_idx])
    help_text.insert(INSERT, "Timelapse", hyperlink1.add(partial(webbrowser.open, "https://saul.cpsc.ucalgary.ca/timelapse/")))
    help_text.insert(END, [") will not be able to read the output file if the paths are absolute. Only enable this option if you know what you are doing. More information"
                    " how to use Timelapse in conjunction with MegaDetector, see the ",
                    ") no serán capaces de leer el archivo de salida si las rutas son absolutas. Solo active esta opción si sabe lo que está haciendo. Para más información"
                    " sobre cómo utilizar Timelapse junto con MegaDetector, consulte "][lang_idx])
    help_text.insert(INSERT, ["Timelapse Image Recognition Guide", "la Guía de Reconocimiento de Imágenes de Timelapse"][lang_idx], hyperlink1.add(partial(webbrowser.open, "https://saul.cpsc.ucalgary.ca/timelapse/uploads/Guides/TimelapseImageRecognitionGuide.pdf")))
    help_text.insert(END, ".\n\n")
    help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
    help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

    # use checkpoints
    help_text.insert(END, f"{lbl_use_checkpnts_txt[lang_idx]}\n")
    help_text.insert(END, ["This is a functionality to save results to checkpoints intermittently, in case a technical hiccup arises. That way, you won't have to restart"
                    " the entire process again when the process is interrupted.\n\n",
                    "Se trata de una funcionalidad para guardar los resultados en puntos de control de forma intermitente, en caso de que surja un contratiempo técnico. "
                    "De esta forma, no tendrás que reiniciar todo el proceso de nuevo cuando éste se interrumpa.\n\n"][lang_idx])
    help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
    help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

    # checkpoint frequency
    help_text.insert(END, f"{lbl_checkpoint_freq_txt[lang_idx]}\n")
    help_text.insert(END, ["Fill in how often you want to save the results to checkpoints. The number indicates the number of images after which checkpoints will be saved."
                    " The entry must contain only numeric characters.\n\n",
                    "Introduzca la frecuencia con la que desea guardar los resultados en los puntos de control. El número indica el número de imágenes tras las cuales se "
                    "guardarán los puntos de control. La entrada debe contener sólo caracteres numéricos.\n\n"][lang_idx])
    help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
    help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

    # continue from checkpoint
    help_text.insert(END, f"{lbl_cont_checkpnt_txt[lang_idx]}\n")
    help_text.insert(END, ["Here you can choose to continue from the last saved checkpoint onwards so that the algorithm can continue where it left off. Checkpoints are"
                    " saved into the main folder and look like 'checkpoint_<timestamp>.json'. When choosing this option, it will search for a valid"
                    " checkpoint file and prompt you if it can't find it.\n\n",
                    "Aquí puede elegir continuar desde el último punto de control guardado para que el algoritmo pueda continuar donde lo dejó. Los puntos de control se "
                    "guardan en la carpeta principal y tienen el aspecto 'checkpoint_<fecha y hora>.json'. Al elegir esta opción, se buscará un archivo de punto de control "
                    "válido y se le preguntará si no puede encontrarlo.\n\n"][lang_idx])
    help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
    help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

    # don't process every frame
    help_text.insert(END, f"{lbl_not_all_frames_txt[lang_idx]}\n")
    help_text.insert(END,["When processing every frame of a video, it can take a long time to finish. Here, you can specify whether you want to analyse only a selection of frames."
                    f" At '{lbl_nth_frame_txt[lang_idx]}' you can specify how many frames you want to be analysed.\n\n",
                     "Procesar todos los fotogramas de un vídeo puede llevar mucho tiempo. Aquí puede especificar si desea analizar sólo una selección de fotogramas. "
                    f"En '{lbl_nth_frame_txt[lang_idx]}' puedes especificar cuántos fotogramas quieres que se analicen.\n\n"][lang_idx])
    help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
    help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

    # analyse every nth frame
    help_text.insert(END, f"{lbl_nth_frame_txt[lang_idx]}\n")
    help_text.insert(END, ["Specify how many frames you want to process. By entering 2, you will process every 2nd frame and thus cut process time by half. By entering 10, "
                    "you will shorten process time to 1/10, et cetera. However, keep in mind that the chance of detecting something is also cut to 1/10.\n\n",
                    "Especifique cuántos fotogramas desea procesar. Introduciendo 2, procesará cada 2 fotogramas y reducirá así el tiempo de proceso a la mitad. Introduciendo "
                    "10, reducirá el tiempo de proceso a 1/10, etcétera. Sin embargo, tenga en cuenta que la probabilidad de detectar algo también se reduce a 1/10.\n\n"][lang_idx])
    help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
    help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

    # third step
    help_text.insert(END, f"{trd_step_txt[lang_idx]}\n")
    help_text.tag_add('frame', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1

    # human verification
    help_text.insert(END, f"{lbl_hitl_main_txt[lang_idx]}\n")
    help_text.insert(END, ["This feature lets you verify the results of the model. You can use it to create training data or to double-check the results. When starting a new "
                           "session, you will first be directed to a window where you can select which images you would like to verify. For instance, someone might be only "
                           "interested in creating training data for 'class A' to unbalance his training dataset or only want to double-check detections with medium-sure "
                           "confidences. After you have selected the images, you will be able to verify them. After having verified all selected images, you will be prompted"
                           " if you want to create training data. If you do, the selected images and their associated annotation files will get a unique name and be either "
                           "moved or copied to a folder of your choice. This is particularly handy when you want to create training data since, for training, all files must "
                           "be in one folder. This way, the files will be unique, and you won't have replacement problems when adding the files to your existing training data. "
                           "You can also skip the training data and just continue to post-process the verified results. Not applicable to videos.\n\n",
                           "Esta característica le permite verificar los resultados del modelo. Puedes usarlo para crear datos de entrenamiento o para verificar los resultados. "
                           "Al iniciar una nueva sesión, primero se le dirigirá a una ventana donde podrá seleccionar qué imágenes desea verificar. Por ejemplo, alguien podría "
                           "estar interesado únicamente en crear datos de entrenamiento para la 'clase A' para desequilibrar su conjunto de datos de entrenamiento o simplemente "
                           "querer verificar las detecciones con confianzas medias-seguras. Una vez que hayas seleccionado las imágenes, podrás verificarlas. Después de haber "
                           "verificado todas las imágenes seleccionadas, se le preguntará si desea crear datos de entrenamiento. Si lo hace, las imágenes seleccionadas y sus "
                           "archivos de anotaciones asociados obtendrán un nombre único y se moverán o copiarán a una carpeta de su elección. Esto es particularmente útil cuando"
                           " desea crear datos de entrenamiento ya que, para el entrenamiento, todos los archivos deben estar en una carpeta. De esta manera, los archivos serán "
                           "únicos y no tendrás problemas de reemplazo al agregar los archivos a tus datos de entrenamiento existentes. También puedes omitir los datos de "
                           "entrenamiento y simplemente continuar con el posprocesamiento de los resultados verificados. No aplicable a vídeos.\n\n"][lang_idx])
    help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
    help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

    # forth step
    help_text.insert(END, f"{fth_step_txt[lang_idx]}\n")
    help_text.tag_add('frame', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1

    # destination folder
    help_text.insert(END, f"{lbl_output_dir_txt[lang_idx]}\n")
    help_text.insert(END, ["Here you can browse for a folder in which the results of the post-processing features will be placed. If nothing is selected, the folder "
                    "chosen at step one will be used as the destination folder.\n\n",
                    "Aquí puede buscar una carpeta en la que se colocarán los resultados de las funciones de postprocesamiento. Si no se selecciona nada, la carpeta "
                    "elegida en el primer paso se utilizará como carpeta de destino.\n\n"][lang_idx])
    help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
    help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

    # separate files
    help_text.insert(END, f"{lbl_separate_files_txt[lang_idx]}\n")
    help_text.insert(END, ["This function divides the files into subdirectories based on their detections. Please be warned that this will be done automatically. "
                    "There will not be an option to review and adjust the detections before the images will be moved. If you want that (a human in the loop), take a look at ",
                    "Esta función divide los archivos en subdirectorios en función de sus detecciones. Tenga en cuenta que esto se hará automáticamente. No habrá opción de "
                    "revisar y ajustar las detecciones antes de mover las imágenes. Si quieres eso (una humano en el bucle), echa un vistazo a "][lang_idx])
    help_text.insert(INSERT, "Timelapse", hyperlink1.add(partial(webbrowser.open, "https://saul.cpsc.ucalgary.ca/timelapse/")))
    help_text.insert(END, [", which offers such a feature. More information about that ",
                           ", que ofrece tal característica. Más información al respecto "][lang_idx])
    help_text.insert(INSERT, ["here", "aquí"][lang_idx], hyperlink1.add(partial(webbrowser.open, "https://saul.cpsc.ucalgary.ca/timelapse/uploads/Guides/TimelapseImageRecognitionGuide.pdf")))
    help_text.insert(END,[" (starting on page 9). The process of importing the output file produced by EcoAssist into Timelapse is described ",
                          " (a partir de la página 9). El proceso de importación del archivo de salida producido por EcoAssist en Timelapse se describe "][lang_idx])
    help_text.insert(INSERT, ["here", "aquí"][lang_idx], hyperlink1.add(partial(webbrowser.open, "https://saul.cpsc.ucalgary.ca/timelapse/pmwiki.php?n=Main.DownloadMegadetector")))
    help_text.insert(END,".\n\n")
    help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
    help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

    # method of file placement
    help_text.insert(END, f"{lbl_file_placement_txt[lang_idx]}\n")
    help_text.insert(END, ["Here you can choose whether to move the files into subdirectories, or copy them so that the originals remain untouched.\n\n",
                           "Aquí puedes elegir si quieres mover los archivos a subdirectorios o copiarlos de forma que los originales permanezcan intactos.\n\n"][lang_idx])
    help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
    help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

    # sort results based on confidence
    help_text.insert(END, f"{lbl_sep_conf_txt[lang_idx]}\n")
    help_text.insert(END, ["This feature will further separate the files based on its confidence value (in tenth decimal intervals). That means that each class will"
                        " have subdirectories like e.g. 'conf_0.6-0.7', 'conf_0.7-0.8', 'conf_0.8-0.9', etc.\n\n",
                        "Esta función separará aún más los archivos en función de su valor de confianza (en intervalos decimales). Esto significa que cada clase tendrá"
                        " subdirectorios como, por ejemplo, 'conf_0.6-0.7', 'conf_0.7-0.8', 'conf_0.8-0.9', etc.\n\n"][lang_idx])
    help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
    help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

    # visualize files
    help_text.insert(END, f"{lbl_vis_files_txt[lang_idx]}\n")
    help_text.insert(END, ["This functionality draws boxes around the detections and prints their confidence values. This can be useful to visually check the results."
                    " Videos can't be visualized using this tool. Please be aware that this action is permanent and cannot be undone. Be wary when using this on original images.\n\n",
                    "Esta funcionalidad dibuja recuadros alrededor de las detecciones e imprime sus valores de confianza. Esto puede ser útil para comprobar visualmente los "
                    "resultados. Los vídeos no pueden visualizarse con esta herramienta.\n\n"][lang_idx])
    help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
    help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

    # crop files
    help_text.insert(END, f"{lbl_crp_files_txt[lang_idx]}\n")
    help_text.insert(END, ["This feature will crop the detections and save them as separate images. Not applicable for videos.\n\n",
                           "Esta función recortará las detecciones y las guardará como imágenes separadas. No es aplicable a los vídeos.\n\n"][lang_idx])
    help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
    help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

    # export results
    help_text.insert(END, f"{lbl_exp_txt[lang_idx]}\n")
    help_text.insert(END, ["Here you can select whether you want to export the results to other file formats. It will additionally try to fetch image metadata, like "
                           "timestamps, locations, and more.\n\n", "Aquí puede seleccionar si desea exportar los resultados a otros formatos de archivo. Además, "
                           "intentará obtener metadatos de la imagen, como marcas de tiempo, ubicaciones, etc. \n\n"][lang_idx])
    help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
    help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

    # postprocess confidence threshold
    help_text.insert(END, f"{lbl_thresh_txt[lang_idx]}\n")
    help_text.insert(END, ["Detections below this value will not be post-processed. To adjust the threshold value, you can drag the slider or press either sides next to "
                    "the slider for a 0.01 reduction or increment. Confidence values are within the [0.01, 1] interval. If you set the confidence threshold too high, "
                    "you will miss some detections. On the other hand, if you set the threshold too low, you will get false positives. When choosing a threshold for your "
                    f"project, it is important to choose a threshold based on your own data. My advice is to first visualize your data ('{lbl_vis_files_txt[lang_idx]}') with a low "
                    "threshold to get a feeling of the confidence values in your data. This will show you how sure the model is about its detections and will give you an "
                    "insight into which threshold will work best for you. If you really don't know, 0.2 is probably a conservative threshold for most projects.\n\n",
                    "Las detecciones por debajo de este valor no se postprocesarán. Para ajustar el valor del umbral, puede arrastrar el control deslizante o pulsar "
                    "cualquiera de los lados junto al control deslizante para una reducción o incremento de 0,01. Los valores de confianza están dentro del intervalo "
                    "[0,01, 1]. Si ajusta el umbral de confianza demasiado alto, pasará por alto algunas detecciones. Por otro lado, si fija el umbral demasiado bajo, "
                    "obtendrá falsos positivos. Al elegir un umbral para su proyecto, es importante elegir un umbral basado en sus propios datos. Mi consejo es que primero"
                    f" visualice sus datos ('{lbl_vis_files_txt[lang_idx]}') con un umbral bajo para hacerse una idea de los valores de confianza de sus datos. Esto le mostrará lo "
                    "seguro que está el modelo sobre sus detecciones y le dará una idea de qué umbral funcionará mejor para usted. Si realmente no lo sabe, 0,2 es "
                    "probablemente un umbral conservador para la mayoría de los proyectos.\n\n"][lang_idx])
    help_text.tag_add('feature', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=1
    help_text.tag_add('explanation', f"{str(line_number)}.0", f"{str(line_number)}.end");line_number+=2

    # config help_text
    help_text.pack(fill="both", expand=True)
    help_text.configure(font=(text_font, 11, "bold"), state=DISABLED)
    scroll.configure(command=help_text.yview)
write_help_tab()

# about tab
about_scroll = Scrollbar(about_tab)
about_text = Text(about_tab, width=1, height=1, wrap=WORD, yscrollcommand=scroll.set)
about_text.configure(spacing1=2, spacing2=3, spacing3=2)
about_text.tag_config('title', font=f'{text_font} {int(15 * text_size_adjustment_factor)} bold', foreground='darkblue', lmargin1=10, lmargin2=10) 
about_text.tag_config('info', font=f'{text_font} {int(13 * text_size_adjustment_factor)} normal', lmargin1=20, lmargin2=20)
about_text.tag_config('citation', font=f'{text_font} {int(13 * text_size_adjustment_factor)} normal', lmargin1=30, lmargin2=50)
hyperlink = HyperlinkManager(about_text)

# function to write text which can be called when user changes language settings
def write_about_tab():
    global about_text
    text_line_number=1

    # contact
    about_text.insert(END, ["Contact\n", "Contacto\n"][lang_idx])
    about_text.insert(END, ["Please also help me to keep improving EcoAssist and let me know about any improvements, bugs, or new features so that I can keep it up-to-date. You can "
                           "contact me at ",
                           "Por favor, ayúdame también a seguir mejorando EcoAssist e infórmame de cualquier mejora, error o nueva función para que pueda mantenerlo actualizado. "
                           "Puedes ponerte en contacto conmigo en "][lang_idx])
    about_text.insert(INSERT, "peter@addaxdatascience.com", hyperlink.add(partial(webbrowser.open, "mailto:peter@addaxdatascience.com")))
    about_text.insert(END, [" or raise an issue on the ", " o plantear un problema en "][lang_idx])
    about_text.insert(INSERT, ["GitHub page", "la página de GitHub"][lang_idx], hyperlink.add(partial(webbrowser.open, "https://github.com/PetervanLunteren/EcoAssist/issues")))
    about_text.insert(END, ".\n\n")
    about_text.tag_add('title', str(text_line_number) + '.0', str(text_line_number) + '.end');text_line_number+=1
    about_text.tag_add('info', str(text_line_number) + '.0', str(text_line_number) + '.end');text_line_number+=2

    # ecoassist citation
    about_text.insert(END, ["EcoAssist citation\n", "Citar EcoAssist\n"][lang_idx])
    about_text.insert(END, ["If you used EcoAssist in your research, please use the following citations.\n",
                            "Si ha utilizado EcoAssist en su investigación, utilice la siguiente citas.\n"][lang_idx])
    about_text.insert(END, "- van Lunteren, P. (2023). EcoAssist: A no-code platform to train and deploy custom YOLOv5 object detection models. Journal of Open Source Software, 8(88), 5581. ")
    about_text.insert(INSERT, "https://doi.org/10.21105/joss.05581", hyperlink.add(partial(webbrowser.open, "https://doi.org/10.21105/joss.05581")))
    about_text.insert(END, ".\n")
    about_text.insert(END, "- Beery, S., Morris, D., & Yang, S. (2019). Efficient pipeline for camera trap image review. arXiv preprint arXiv:1907.06772. ")
    about_text.insert(INSERT, "https://doi.org/10.48550/arXiv.1907.06772", hyperlink.add(partial(webbrowser.open, "https://doi.org/10.48550/arXiv.1907.06772")))
    about_text.insert(END, ".\n\n")
    about_text.tag_add('title', str(text_line_number) + '.0', str(text_line_number) + '.end');text_line_number+=1
    about_text.tag_add('info', str(text_line_number) + '.0', str(text_line_number) + '.end');text_line_number+=1
    about_text.tag_add('citation', str(text_line_number) + '.0', str(text_line_number) + '.end');text_line_number+=1
    about_text.tag_add('citation', str(text_line_number) + '.0', str(text_line_number) + '.end');text_line_number+=2

    # image credits
    about_text.insert(END, ["Image credits\n", "Créditos de la imagen\n"][lang_idx])
    about_text.insert(END, ["The beautiful camera trap images of the fox and ocelot displayed at the top were taken from the ",
                            "Las bellas imágenes del zorro y el ocelote captadas por cámaras trampa que aparecen en la parte superior proceden del conjunto de "][lang_idx])
    about_text.insert(INSERT, ["WCS Camera Traps dataset", "datos WCS Camera Traps"][lang_idx], hyperlink.add(partial(webbrowser.open, "https://lila.science/datasets/wcscameratraps")))
    about_text.insert(END, [" provided by the ", " proporcionado por la "][lang_idx])
    about_text.insert(INSERT, "Wildlife Conservation Society", hyperlink.add(partial(webbrowser.open, "https://www.wcs.org/")))
    about_text.insert(END, ".\n\n")
    about_text.tag_add('title', str(text_line_number) + '.0', str(text_line_number) + '.end');text_line_number+=1
    about_text.tag_add('info', str(text_line_number) + '.0', str(text_line_number) + '.end');text_line_number+=2

    # development credits
    about_text.insert(END, ["Development\n", "Desarrollo\n"][lang_idx])
    about_text.insert(END, ["EcoAssist is developed by ",
                            "EcoAssist ha sido desarrollado por "][lang_idx])
    about_text.insert(INSERT, "Addax Data Science", hyperlink.add(partial(webbrowser.open, "https://addaxdatascience.com/")))
    about_text.insert(END, [" in collaboration with ",
                            " en colaboración con "][lang_idx])
    about_text.insert(INSERT, "Smart Parks", hyperlink.add(partial(webbrowser.open, "https://www.smartparks.org/")))
    about_text.insert(END, ".\n\n")
    about_text.tag_add('title', str(text_line_number) + '.0', str(text_line_number) + '.end');text_line_number+=1
    about_text.tag_add('info', str(text_line_number) + '.0', str(text_line_number) + '.end');text_line_number+=2

    # config about_text
    about_text.pack(fill="both", expand=True)
    about_text.configure(font=(text_font, 11, "bold"), state=DISABLED)
    scroll.configure(command=about_text.yview)
write_about_tab()

# SIMPLE MODE WINDOW 
dir_image = customtkinter.CTkImage(PIL_dir_image, size=(ICON_SIZE, ICON_SIZE))
mdl_image = customtkinter.CTkImage(PIL_mdl_image, size=(ICON_SIZE, ICON_SIZE))
spp_image = customtkinter.CTkImage(PIL_spp_image, size=(ICON_SIZE, ICON_SIZE))
run_image = customtkinter.CTkImage(PIL_run_image, size=(ICON_SIZE, ICON_SIZE))

# set up window
simple_mode = Toplevel(root)
simple_mode.title(f"EcoAssist v{current_EA_version} - Simple mode")
simple_mode.geometry("+10+20")
simple_mode.protocol("WM_DELETE_WINDOW", on_toplevel_close)
simple_mode.columnconfigure(0, weight=1, minsize=500)
main_label_font = customtkinter.CTkFont(family='CTkFont', size=14, weight = 'bold')
simple_bg_image = customtkinter.CTkImage(PIL_gradient, size=(SIM_WINDOW_WIDTH, SIM_WINDOW_HEIGHT))
simple_bg_image_label = customtkinter.CTkLabel(simple_mode, image=simple_bg_image)
simple_bg_image_label.grid(row=0, column=0)
simple_main_frame = customtkinter.CTkFrame(simple_mode, corner_radius=0, fg_color = 'transparent')
simple_main_frame.grid(row=0, column=0, sticky="ns")
simple_mode.withdraw() # only show when all widgets are loaded

# logo
sim_top_banner = customtkinter.CTkImage(PIL_simple_top_banner, size=(LOGO_SIZE * SIM_TOP_BANNER_WIDTH_FACTOR, LOGO_SIZE))
customtkinter.CTkLabel(simple_main_frame, text="", image = sim_top_banner).grid(column=0, row=0, columnspan=2, sticky='ew', pady=(PADY, 0), padx=0)

# top buttons
sim_btn_switch_mode_txt = ["To advanced mode", "Al modo avanzado"]
sim_btn_switch_mode = GreyTopButton(master = simple_main_frame, text = sim_btn_switch_mode_txt[lang_idx], command = switch_mode)
sim_btn_switch_mode.grid(row=0, column=0, padx=PADX, pady=(PADY, 0), columnspan = 2, sticky="nw")
sim_btn_switch_lang = GreyTopButton(master = simple_main_frame, text = "Switch language", command = set_language)
sim_btn_switch_lang.grid(row=0, column=0, padx=PADX, pady=(0, 0), columnspan = 2, sticky="sw")
sim_btn_sponsor = GreyTopButton(master = simple_main_frame, text = adv_btn_sponsor_txt[lang_idx], command = sponsor_project)
sim_btn_sponsor.grid(row=0, column=0, padx=PADX, pady=(PADY, 0), columnspan = 2, sticky="ne")
sim_btn_reset_values = GreyTopButton(master = simple_main_frame, text = adv_btn_reset_values_txt[lang_idx], command = reset_values)
sim_btn_reset_values.grid(row=0, column=0, padx=PADX, pady=(0, 0), columnspan = 2, sticky="se")

# choose folder
sim_dir_frm_1 = MyMainFrame(master=simple_main_frame)
sim_dir_frm_1.grid(row=1, column=0, padx=PADX, pady=PADY, sticky="nswe")
sim_dir_img_widget = customtkinter.CTkLabel(sim_dir_frm_1, text="", image = dir_image, compound = 'left')
sim_dir_img_widget.grid(row=0, column=0, padx=PADX, pady=PADY, sticky="nswe")
sim_dir_frm = MySubFrame(master=sim_dir_frm_1)
sim_dir_frm.grid(row=0, column=1, padx=(0, PADX), pady=PADY, sticky="nswe")
sim_dir_lbl_txt = ["Which folder do you want to analyse?", "¿Qué carpeta quieres analizar?"]
sim_dir_lbl = customtkinter.CTkLabel(sim_dir_frm, text=sim_dir_lbl_txt[lang_idx], font = main_label_font)
sim_dir_lbl.grid(row=0, column=0, padx=PADX, pady=(0, PADY/4), columnspan = 2, sticky="nsw")
sim_dir_inf = InfoButton(master = sim_dir_frm, text = "?", command = sim_dir_show_info)
sim_dir_inf.grid(row=0, column=0, padx=PADX, pady=PADY, sticky="e", columnspan = 2)
sim_dir_btn = customtkinter.CTkButton(sim_dir_frm, text=browse_txt[lang_idx], width = 1, command = lambda: [browse_dir(var_choose_folder, var_choose_folder_short, dsp_choose_folder, 25, row_choose_folder, 0, 'w', source_dir = True), update_frame_states()])
sim_dir_btn.grid(row=1, column=0, padx=(PADX, PADX/2), pady=(0, PADY), sticky="nswe")
sim_dir_pth_frm = MySubSubFrame(master=sim_dir_frm)
sim_dir_pth_frm.grid(row=1, column=1, padx=(PADX/2, PADX), pady=(0, PADY), sticky="nesw")
sim_dir_pth_txt = ["no folder selected", "no hay carpeta seleccionada"]
sim_dir_pth = customtkinter.CTkLabel(sim_dir_pth_frm, text=sim_dir_pth_txt[lang_idx], text_color = "grey")
sim_dir_pth.pack()

# choose model
sim_mdl_frm_1 = MyMainFrame(master=simple_main_frame)
sim_mdl_frm_1.grid(row=2, column=0, padx=PADX, pady=(0, PADY), sticky="nswe")
sim_mdl_img_widget = customtkinter.CTkLabel(sim_mdl_frm_1, text="", image = mdl_image, compound = 'left')
sim_mdl_img_widget.grid(row=1, column=0, padx=PADX, pady=PADY, sticky="nswe")
sim_mdl_frm = MySubFrame(master=sim_mdl_frm_1)
sim_mdl_frm.grid(row=1, column=1, padx=(0, PADX), pady=PADY, sticky="nswe")
sim_mdl_lbl_txt = ["Which species identification model do you want to use?", "¿Qué modelo de identificación de especies quiere utilizar?"]
sim_mdl_lbl = customtkinter.CTkLabel(sim_mdl_frm, text=sim_mdl_lbl_txt[lang_idx], font = main_label_font)
sim_mdl_lbl.grid(row=0, column=0, padx=PADX, pady=(0, PADY/4), columnspan = 2, sticky="nsw")
sim_mdl_inf = InfoButton(master = sim_mdl_frm, text = "?", command = sim_mdl_show_info)
sim_mdl_inf.grid(row=0, column=0, padx=PADX, pady=PADY, sticky="e", columnspan = 2)
# convert to more elaborate dpd value for the 'None' simple mode option
sim_dpd_options_cls_model = [[item[0] + suffixes_for_sim_none[i], *item[1:]] for i, item in enumerate(dpd_options_cls_model)]
sim_mdl_dpd = customtkinter.CTkOptionMenu(sim_mdl_frm, values=sim_dpd_options_cls_model[lang_idx], command=sim_mdl_dpd_callback, width = 1)
sim_mdl_dpd.set(sim_dpd_options_cls_model[lang_idx][global_vars["var_cls_model_idx"]]) # take idx instead of string
sim_mdl_dpd.grid(row=1, column=0, padx=PADX, pady=(PADY/4, PADY), sticky="nswe", columnspan = 2)

# select animals
sim_spp_frm_1 = MyMainFrame(master=simple_main_frame)
sim_spp_frm_1.grid(row=3, column=0, padx=PADX, pady=(0, PADY), sticky="nswe")
sim_spp_img_widget = customtkinter.CTkLabel(sim_spp_frm_1, text="", image = spp_image, compound = 'left')
sim_spp_img_widget.grid(row=2, column=0, padx=PADX, pady=PADY, sticky="nswe")
sim_spp_frm = MySubFrame(master=sim_spp_frm_1, width=1000)
sim_spp_frm.grid(row=2, column=1, padx=(0, PADX), pady=PADY, sticky="nswe")
sim_spp_lbl_txt = ["Which species are present in your project area?", "¿Qué especies están presentes en la zona de su proyecto?"]
sim_spp_lbl = customtkinter.CTkLabel(sim_spp_frm, text=sim_spp_lbl_txt[lang_idx], font = main_label_font, text_color = 'grey')
sim_spp_lbl.grid(row=0, column=0, padx=PADX, pady=(0, PADY/4), columnspan = 2, sticky="nsw")
sim_spp_inf = InfoButton(master = sim_spp_frm, text = "?", command = sim_spp_show_info)
sim_spp_inf.grid(row=0, column=0, padx=PADX, pady=PADY, sticky="e", columnspan = 2)
sim_spp_scr_height = 238
sim_spp_scr = SpeciesSelectionFrame(master=sim_spp_frm, height=sim_spp_scr_height, dummy_spp = True)
sim_spp_scr._scrollbar.configure(height=0)
sim_spp_scr.grid(row=1, column=0, padx=PADX, pady=(PADY/4, PADY), sticky="ew", columnspan = 2)

# deploy button
sim_run_frm_1 = MyMainFrame(master=simple_main_frame)
sim_run_frm_1.grid(row=4, column=0, padx=PADX, pady=(0, PADY), sticky="nswe")
sim_run_img_widget = customtkinter.CTkLabel(sim_run_frm_1, text="", image = run_image, compound = 'left')
sim_run_img_widget.grid(row=3, column=0, padx=PADX, pady=PADY, sticky="nswe")
sim_run_frm = MySubFrame(master=sim_run_frm_1, width=1000)
sim_run_frm.grid(row=3, column=1, padx=(0, PADX), pady=PADY, sticky="nswe")
sim_run_btn_txt = ["Start processing", "Empezar a procesar"]
sim_run_btn = customtkinter.CTkButton(sim_run_frm, text=sim_run_btn_txt[lang_idx], command=lambda: start_deploy(simple_mode = True), fg_color = ('#579F2D', 'green'), hover_color = 'darkgreen')
sim_run_btn.grid(row=0, column=0, padx=PADX, pady=PADY, sticky="nswe", columnspan = 2)

# about
sim_abo_lbl = tk.Label(simple_main_frame, text=adv_abo_lbl_txt[lang_idx], font = Font(size = ADDAX_TXT_SIZE))
sim_abo_lbl.grid(row=5, column=0, columnspan = 2, sticky="")
sim_abo_lbl_link = tk.Label(simple_main_frame, text="addaxdatascience.com", cursor="hand2", font = Font(size = ADDAX_TXT_SIZE, underline=1))
sim_abo_lbl_link.grid(row=6, column=0, columnspan = 2, sticky="", pady=(0, PADY))
sim_abo_lbl_link.bind("<Button-1>", lambda e: callback("http://addaxdatascience.com"))

# main function
def main():

    # try to download the model info json to check if there are new models
    fetch_latest_model_info()

    # initialise start screen
    enable_frame(fst_step)
    disable_frame(snd_step)
    disable_frame(trd_step)
    disable_frame(fth_step)
    set_lang_buttons(lang_idx)

    # super weird but apparently neccesary, otherwise script halts at first root.update()
    switch_mode()
    switch_mode()

    # run
    root.mainloop()

# executable as script
if __name__ == "__main__":
    main()
