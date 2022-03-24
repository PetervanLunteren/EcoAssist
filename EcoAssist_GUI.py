import json
from pathlib import Path
import cv2
from bounding_box import bounding_box as bb
import webbrowser
from tkHyperlinkManager import *
from tkinter import filedialog
from tkinter import ttk
import tkinter as tk
import os
import re
from subprocess import Popen, PIPE
import time
import datetime
from tkinter import messagebox as mb
import platform
import subprocess
import traceback
from PIL import ImageTk, Image, ImageFilter
from functools import partial
import numpy as np
import xml.etree.cElementTree as ET


# function to start the MegaDetector process for images
def produce_json(path_to_image_folder, additional_json_cmds):
    print(f"Processing images with MegaDetector model...\n")
    mega_stats['text'] = update_progress_label_short(command="load")
    path_to_git = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    loc_detector_batch = os.path.join(path_to_git, "cameratraps", "detection", "run_tf_detector_batch.py")
    loc_pb = os.path.join(path_to_git, "md_v4.1.0.pb")
    Path(os.path.join(path_to_image_folder, "json_file")).mkdir(parents=True, exist_ok=True)
    loc_json_file = os.path.join(path_to_image_folder, "json_file", "output.json")
    batch_command = f"python3 '{loc_detector_batch}' '{loc_pb}'{additional_json_cmds}'{path_to_image_folder}' '{loc_json_file}'"
    print(f"batch_command: {batch_command}")
    with Popen([batch_command],
               stderr=PIPE, bufsize=1, shell=True,
               universal_newlines=True) as p:
        for line in p.stderr:
            print(line, end='')
            if '%' in line[0:4]:
                times = re.search("(\[.*?\])", line)[1]
                progress_bar = re.search("^[^\/]*[^[^ ]*", line.replace(times, ""))[0]
                percentage, current_im, total_im = [int(x) for x in re.findall('[0-9]+', progress_bar)]
                elapsed_time = re.search("(?<=\[)(.*)(?=<)", times)[1]
                time_left = re.search("(?<=<)(.*)(?=,)", times)[1]
                mega_progbar['value'] = percentage
                mega_stats['text'] = update_progress_label_short(elapsed_time, time_left, command="running")
            window.update()
        mega_stats['text'] = update_progress_label_short(elapsed_time, time_left, command="done")
        window.update()


# function to start the MegaDetector process for video's
def produce_json_video(path_to_video_folder, additional_json_cmds):
    print(f"Processing videos with MegaDetector model...\n")
    v_mega_stats['text'] = update_progress_label_short(command="load")
    path_to_git = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    loc_process_video_py = os.path.join(path_to_git, "cameratraps", "detection", "process_video.py")
    loc_pb = os.path.join(path_to_git, "md_v4.1.0.pb")
    Path(os.path.join(path_to_video_folder, "json_files")).mkdir(parents=True, exist_ok=True)
    loc_json_file = os.path.join(path_to_video_folder, "json_files", "output.json")
    video_command = f"python3 '{loc_process_video_py}'{additional_json_cmds} --output_json_file '{loc_json_file}' '{loc_pb}' '{path_to_video_folder}'"
    print(f"video_command: {video_command}")
    with Popen([video_command],
               stderr=PIPE, bufsize=1, shell=True,
               universal_newlines=True) as p:
        for line in p.stderr:
            print(line, end='')
            if '%' in line[0:4]:
                times = re.search("(\[.*?\])", line)[1]
                progress_bar = re.search("^[^\/]*[^[^ ]*", line.replace(times, ""))[0]
                percentage, current_im, total_im = [int(x) for x in re.findall('[0-9]+', progress_bar)]
                elapsed_time = re.search("(?<=\[)(.*)(?=<)", times)[1]
                time_left = re.search("(?<=<)(.*)(?=,)", times)[1]
                v_mega_progbar['value'] = percentage
                v_mega_stats['text'] = update_progress_label_short(elapsed_time, time_left, command="running")
            window.update()
        v_mega_stats['text'] = update_progress_label_short(elapsed_time, time_left, command="done")
        window.update()


# function to crop detections based on json file (for images)
def crop(path_to_image_folder, del_originals, separated_files):
    print(f"Cropping images...\n")
    global elapsed_time_crop
    global time_left_crop
    path_to_json = os.path.join(path_to_image_folder, "json_file", "output.json")
    start_time = time.time()
    nloop = 1
    with open(path_to_json) as json_file:
        data = json.load(json_file)
    n_images = len(data['images'])
    for image in data['images']:
        crop_progbar['value'] += 100 / n_images
        counter = 1
        n_detections = len(image['detections'])
        detections_list = image['detections']
        if not n_detections == 0:
            for detection in image['detections']:
                if separated_files:
                    animal_detecs = 0
                    person_detecs = 0
                    vehicle_detecs = 0
                    for i in range(n_detections):
                        if detections_list[i]["category"] == "1":
                            animal_detecs += 1
                        if detections_list[i]["category"] == "2":
                            person_detecs += 1
                        if detections_list[i]["category"] == "3":
                            vehicle_detecs += 1
                    if animal_detecs != 0 and person_detecs == 0 and vehicle_detecs == 0:
                        file = os.path.join(os.path.split(image['file'])[0], 'images', 'animals',
                                            os.path.split(image['file'])[1])
                    elif animal_detecs == 0 and person_detecs != 0 and vehicle_detecs == 0:
                        file = os.path.join(os.path.split(image['file'])[0], 'images', 'persons',
                                            os.path.split(image['file'])[1])
                    elif animal_detecs == 0 and person_detecs == 0 and vehicle_detecs != 0:
                        file = os.path.join(os.path.split(image['file'])[0], 'images', 'vehicles',
                                            os.path.split(image['file'])[1])
                    else:
                        file = os.path.join(os.path.split(image['file'])[0], 'images', 'multiple_categories',
                                            os.path.split(image['file'])[1])
                else:
                    file = image['file']
                category = detection['category']
                im = Image.open(file)
                width, height = im.size
                left = int(round(detection['bbox'][0] * width))
                top = int(round(detection['bbox'][1] * height))
                right = int(round(detection['bbox'][2] * width)) + left
                bottom = int(round(detection['bbox'][3] * height)) + top
                cropped_im = im.crop((left, top, right, bottom))
                if category == '1':
                    path, file_ext = os.path.split(
                        os.path.splitext(file)[0] + '_crop' + str(counter) + '_animal' + '.jpg')
                elif category == '2':
                    path, file_ext = os.path.split(
                        os.path.splitext(file)[0] + '_crop' + str(counter) + '_person' + '.jpg')
                else:
                    path, file_ext = os.path.split(
                        os.path.splitext(file)[0] + '_crop' + str(counter) + '_vehicle' + '.jpg')
                Path(os.path.join(path, '_cropped_images')).mkdir(parents=True, exist_ok=True)
                cropped_im.save(os.path.join(path, '_cropped_images', file_ext))
                counter += 1
            if del_originals and os.path.exists(file):
                os.remove(file)
        elapsed_time_crop = str(datetime.timedelta(seconds=round(time.time() - start_time)))
        time_left_crop = str(
            datetime.timedelta(
                seconds=round(((time.time() - start_time) * n_images / nloop) - (time.time() - start_time))))
        crop_stats['text'] = update_progress_label_short(elapsed_time_crop, time_left_crop, command="running")
        nloop += 1
        window.update()
    crop_stats['text'] = update_progress_label_short(elapsed_time_crop, time_left_crop, command="done")
    window.update()


# function to draw boxes around the detections based on json file (for images)
def visualise_bbox(path_to_image_folder, del_originals, separated_files):
    print(f"Visualising images...\n")
    global elapsed_time_bbox
    global time_left_bbox
    start_time = time.time()
    nloop = 1
    path_to_json = os.path.join(path_to_image_folder, "json_file", "output.json")
    with open(path_to_json) as json_file:
        data = json.load(json_file)
    n_images = len(data['images'])
    for image in data['images']:
        n_detections = len(image['detections'])
        detections_list = image['detections']
        bbox_progbar['value'] += 100 / n_images
        if not n_detections == 0:
            if separated_files:
                animal_detecs = 0
                person_detecs = 0
                vehicle_detecs = 0
                for i in range(n_detections):
                    if detections_list[i]["category"] == "1":
                        animal_detecs += 1
                    if detections_list[i]["category"] == "2":
                        person_detecs += 1
                    if detections_list[i]["category"] == "3":
                        vehicle_detecs += 1
                if animal_detecs != 0 and person_detecs == 0 and vehicle_detecs == 0:
                    file = os.path.join(os.path.split(image['file'])[0], 'images', 'animals',
                                        os.path.split(image['file'])[1])
                elif animal_detecs == 0 and person_detecs != 0 and vehicle_detecs == 0:
                    file = os.path.join(os.path.split(image['file'])[0], 'images', 'persons',
                                        os.path.split(image['file'])[1])
                elif animal_detecs == 0 and person_detecs == 0 and vehicle_detecs != 0:
                    file = os.path.join(os.path.split(image['file'])[0], 'images', 'vehicles',
                                        os.path.split(image['file'])[1])
                else:
                    file = os.path.join(os.path.split(image['file'])[0], 'images', 'multiple_categories',
                                        os.path.split(image['file'])[1])
            else:
                file = image['file']
            im = cv2.imread(file)
            if del_originals == True and os.path.exists(file):
                os.remove(file)
            for detection in image['detections']:
                category = detection['category']
                conf = str(round(detection['conf'] * 100, 2))
                height, width = im.shape[:2]
                left = int(round(detection['bbox'][0] * width))
                top = int(round(detection['bbox'][1] * height))
                right = int(round(detection['bbox'][2] * width)) + left
                bottom = int(round(detection['bbox'][3] * height)) + top
                if category == '1':
                    label = 'animal ' + conf + '%'
                    colour = 'fuchsia'
                elif category == '2':
                    label = 'person ' + conf + '%'
                    colour = 'red'
                else:
                    label = 'vehicle ' + conf + '%'
                    colour = 'orange'
                bb.add(im, left, top, right, bottom, label, colour)
            path, file = os.path.split(os.path.splitext(file)[0] + '_detections' + '.jpg')
            Path(os.path.join(path, '_visualised_images')).mkdir(parents=True, exist_ok=True)
            cv2.imwrite(os.path.join(path, '_visualised_images', file), im)
        elapsed_time_bbox = str(datetime.timedelta(seconds=round(time.time() - start_time)))
        time_left_bbox = str(
            datetime.timedelta(
                seconds=round(((time.time() - start_time) * n_images / nloop) - (time.time() - start_time))))
        bbox_stats['text'] = update_progress_label_short(elapsed_time_bbox, time_left_bbox, command="running")
        nloop += 1
        window.update()
    bbox_stats['text'] = update_progress_label_short(elapsed_time_bbox, time_left_bbox, command="done")
    window.update()


# function to move the images and their xmls (if present) to their associated directories
def separate_images(path_to_image_folder):
    print(f"Separating images...\n")
    global elapsed_time_sep
    global time_left_sep
    path_to_json = os.path.join(path_to_image_folder, "json_file", "output.json")
    start_time = time.time()
    nloop = 1
    with open(path_to_json) as json_file:
        data = json.load(json_file)
    n_images = len(data['images'])
    for image in data['images']:  # mkdir for all dirs containing images
        file = os.path.splitext(image['file'])  # list: ext in [1] and the rest in [0]
        file_path = os.path.dirname(os.path.normpath(file[0] + file[1]))
        file_name = os.path.splitext(
            os.path.basename(os.path.normpath(file[0] + file[1])))  # list: ext in [1] and the rest in [0]
        detections_list = image['detections']
        n_detections = len(detections_list)
        sep_progbar['value'] += 100 / n_images
        Path(os.path.join(file_path, "images")).mkdir(parents=True, exist_ok=True)
        if n_detections == 0:  # move images based based on detections
            Path(os.path.join(file_path, "images", "empties")).mkdir(parents=True, exist_ok=True)
            os.replace(os.path.join(file[0] + file[1]),
                       os.path.join(file_path, "images", "empties", file_name[0] + file_name[1]))
        else:
            animal_detecs = 0
            person_detecs = 0
            vehicle_detecs = 0
            for i in range(n_detections):
                if detections_list[i]["category"] == "1":
                    animal_detecs += 1
                if detections_list[i]["category"] == "2":
                    person_detecs += 1
                if detections_list[i]["category"] == "3":
                    vehicle_detecs += 1
            if animal_detecs != 0 and person_detecs == 0 and vehicle_detecs == 0:
                Path(os.path.join(file_path, "images", "animals")).mkdir(parents=True, exist_ok=True)
                os.replace(os.path.join(file[0] + file[1]),
                           os.path.join(file_path, "images", "animals", file_name[0] + file_name[1]))
                if os.path.isfile(os.path.join(file[0] + ".xml")):
                    os.replace(os.path.join(file[0] + ".xml"),
                               os.path.join(file_path, "images", "animals", file_name[0] + ".xml"))
            elif animal_detecs == 0 and person_detecs != 0 and vehicle_detecs == 0:
                Path(os.path.join(file_path, "images", "persons")).mkdir(parents=True, exist_ok=True)
                os.replace(os.path.join(file[0] + file[1]),
                           os.path.join(file_path, "images", "persons", file_name[0] + file_name[1]))
                if os.path.isfile(os.path.join(file[0] + ".xml")):
                    os.replace(os.path.join(file[0] + ".xml"),
                               os.path.join(file_path, "images", "persons", file_name[0] + ".xml"))
            elif animal_detecs == 0 and person_detecs == 0 and vehicle_detecs != 0:
                Path(os.path.join(file_path, "images", "vehicles")).mkdir(parents=True, exist_ok=True)
                os.replace(os.path.join(file[0] + file[1]),
                           os.path.join(file_path, "images", "vehicles", file_name[0] + file_name[1]))
                if os.path.isfile(os.path.join(file[0] + ".xml")):
                    os.replace(os.path.join(file[0] + ".xml"),
                               os.path.join(file_path, "images", "vehicles", file_name[0] + ".xml"))
            else:
                Path(os.path.join(file_path, "images", "multiple_categories")).mkdir(parents=True, exist_ok=True)
                os.replace(os.path.join(file[0] + file[1]),
                           os.path.join(file_path, "images", "multiple_categories", file_name[0] + file_name[1]))
                if os.path.isfile(os.path.join(file[0] + ".xml")):
                    os.replace(os.path.join(file[0] + ".xml"),
                               os.path.join(file_path, "images", "multiple_categories", file_name[0] + ".xml"))
        elapsed_time_sep = str(datetime.timedelta(seconds=round(time.time() - start_time)))
        time_left_sep = str(
            datetime.timedelta(
                seconds=round(((time.time() - start_time) * n_images / nloop) - (time.time() - start_time))))
        sep_stats['text'] = update_progress_label_short(elapsed_time_sep, time_left_sep, command="running")
        nloop += 1
        window.update()
    sep_stats['text'] = update_progress_label_short(elapsed_time_sep, time_left_sep, command="done")
    window.update()


# function to move the video's to their associated directories
def separate_videos(path_to_video_folder):
    print(f"Separating video's...\n")
    global elapsed_time_sep
    global time_left_sep
    path_to_json = os.path.join(path_to_video_folder, "json_files", "output.frames.json")
    start_time = time.time()
    nloop = 1
    with open(path_to_json) as json_file:
        data = json.load(json_file)
    detections_dict = {}
    for image in data['images']:
        video = os.path.dirname(image['file'])
        detections_list = image['detections']
        n_detections = len(detections_list)
        Path(os.path.join(path_to_video_folder, "videos")).mkdir(parents=True, exist_ok=True)
        animal_detecs = 0
        person_detecs = 0
        vehicle_detecs = 0
        for i in range(n_detections):
            if detections_list[i]["category"] == "1":
                animal_detecs += 1
            if detections_list[i]["category"] == "2":
                person_detecs += 1
            if detections_list[i]["category"] == "3":
                vehicle_detecs += 1
        if video in detections_dict:
            detections_dict[video][0] += animal_detecs
            detections_dict[video][1] += person_detecs
            detections_dict[video][2] += vehicle_detecs
        else:
            detections_dict[video] = [animal_detecs, person_detecs, vehicle_detecs]
    n_videos = len(detections_dict.keys())
    for video in detections_dict:
        print(
            f"\n{video} has {detections_dict[video][0]} animals, {detections_dict[video][1]} persons, {detections_dict[video][2]} vehicles")
        if detections_dict[video][0] != 0 and detections_dict[video][1] == 0 and detections_dict[video][2] == 0:
            if len(os.path.normpath(video).split(os.sep)) > 1:
                video_path_excl_video = os.path.normpath(video).split(os.sep)[:-1]
                file = os.path.normpath(video).split(os.sep)[-1]
                Path(os.path.join(path_to_video_folder, *video_path_excl_video, "videos", "animals")).mkdir(
                    parents=True,
                    exist_ok=True)
                os.replace(os.path.join(path_to_video_folder, *video_path_excl_video, file),
                           os.path.join(path_to_video_folder, *video_path_excl_video, "videos", "animals", file))
            else:
                Path(os.path.join(path_to_video_folder, "videos", "animals")).mkdir(parents=True, exist_ok=True)
                os.replace(os.path.join(path_to_video_folder, video),
                           os.path.join(path_to_video_folder, "videos", "animals", video))
        elif detections_dict[video][0] == 0 and detections_dict[video][1] != 0 and detections_dict[video][2] == 0:
            if len(os.path.normpath(video).split(os.sep)) > 1:
                video_path_excl_video = os.path.normpath(video).split(os.sep)[:-1]
                file = os.path.normpath(video).split(os.sep)[-1]
                Path(os.path.join(path_to_video_folder, *video_path_excl_video, "videos", "persons")).mkdir(
                    parents=True,
                    exist_ok=True)
                os.replace(os.path.join(path_to_video_folder, *video_path_excl_video, file),
                           os.path.join(path_to_video_folder, *video_path_excl_video, "videos", "persons", file))
            else:
                Path(os.path.join(path_to_video_folder, "videos", "persons")).mkdir(parents=True, exist_ok=True)
                os.replace(os.path.join(path_to_video_folder, video),
                           os.path.join(path_to_video_folder, "videos", "persons", video))
        elif detections_dict[video][0] == 0 and detections_dict[video][1] == 0 and detections_dict[video][2] != 0:
            if len(os.path.normpath(video).split(os.sep)) > 1:
                video_path_excl_video = os.path.normpath(video).split(os.sep)[:-1]
                file = os.path.normpath(video).split(os.sep)[-1]
                Path(os.path.join(path_to_video_folder, *video_path_excl_video, "videos", "vehicles")).mkdir(
                    parents=True,
                    exist_ok=True)
                os.replace(os.path.join(path_to_video_folder, *video_path_excl_video, file),
                           os.path.join(path_to_video_folder, *video_path_excl_video, "videos", "vehicles", file))
            else:
                Path(os.path.join(path_to_video_folder, "videos", "vehicles")).mkdir(parents=True, exist_ok=True)
                os.replace(os.path.join(path_to_video_folder, video),
                           os.path.join(path_to_video_folder, "videos", "vehicles", video))
        elif detections_dict[video][0] == 0 and detections_dict[video][1] == 0 and detections_dict[video][2] == 0:
            if len(os.path.normpath(video).split(os.sep)) > 1:
                video_path_excl_video = os.path.normpath(video).split(os.sep)[:-1]
                file = os.path.normpath(video).split(os.sep)[-1]
                Path(os.path.join(path_to_video_folder, *video_path_excl_video, "videos", "empties")).mkdir(
                    parents=True,
                    exist_ok=True)
                os.replace(os.path.join(path_to_video_folder, *video_path_excl_video, file),
                           os.path.join(path_to_video_folder, *video_path_excl_video, "videos", "empties", file))
            else:
                Path(os.path.join(path_to_video_folder, "videos", "empties")).mkdir(parents=True, exist_ok=True)
                os.replace(os.path.join(path_to_video_folder, video),
                           os.path.join(path_to_video_folder, "videos", "empties", video))
        else:
            if len(os.path.normpath(video).split(os.sep)) > 1:
                video_path_excl_video = os.path.normpath(video).split(os.sep)[:-1]
                file = os.path.normpath(video).split(os.sep)[-1]
                Path(os.path.join(path_to_video_folder, *video_path_excl_video, "videos", "multiple_categories")).mkdir(
                    parents=True,
                    exist_ok=True)
                os.replace(os.path.join(path_to_video_folder, *video_path_excl_video, file),
                           os.path.join(path_to_video_folder, *video_path_excl_video, "videos", "multiple_categories",
                                        file))
            else:
                Path(os.path.join(path_to_video_folder, "videos", "multiple_categories")).mkdir(parents=True,
                                                                                                exist_ok=True)
                os.replace(os.path.join(path_to_video_folder, video),
                           os.path.join(path_to_video_folder, "videos", "multiple_categories", video))
        v_sep_progbar['value'] += 100 / n_videos
        elapsed_time_sep = str(datetime.timedelta(seconds=round(time.time() - start_time)))
        time_left_sep = str(
            datetime.timedelta(
                seconds=round(((time.time() - start_time) * n_videos / nloop) - (time.time() - start_time))))
        v_sep_stats['text'] = update_progress_label_short(elapsed_time_sep, time_left_sep, command="running")
        nloop += 1
        window.update()
    v_sep_stats['text'] = update_progress_label_short(elapsed_time_sep, time_left_sep, command="done")
    window.update()


# function to indent xml files so it is human readable. With thanks to ade (Stack Overflow)
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


# function to create xml label files in Pascal VOC format. With thanks to Uzzal Podder (Stack Overflow).
def create_labimg_xml(image_path, annotation_list):
    # expected input:
    # anotation_list = ['left1,bottom1,X,X,right1,top1,X,X,label1',
    #                   'left2,bottom2,X,X,right2,top2,X,X,label2',
    #                   'left3,bottom3,X,X,right3,top3,X,X,label3']
    # (X = doesn't matter...)
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


# function to create XML files based on MegaDetector output json (for images)
def create_xml(path_to_json):
    print(f"Creating .xml label files for the images...\n")
    global elapsed_time_xml
    global time_left_xml
    start_time = time.time()
    nloop = 1
    with open(path_to_json) as json_file:
        data = json.load(json_file)
    n_images = len(data['images'])
    for image in data['images']:
        xml_progbar['value'] += 100 / n_images
        file = str(image['file'])
        n_detections = len(image['detections'])
        annotation_list = []
        if not n_detections == 0:
            for detection in image['detections']:
                category = detection['category']
                if category == '1':
                    label = 'animal'
                elif category == '2':
                    label = 'person'
                else:
                    label = 'vehicle'
                    label = 'vehicle'
                im = Image.open(file)
                width, height = im.size
                left = int(round(detection['bbox'][0] * width))
                top = int(round(detection['bbox'][1] * height))
                right = int(round(detection['bbox'][2] * width)) + left
                bottom = int(round(detection['bbox'][3] * height)) + top
                list_of_coords = [left, bottom, left, left, right, top, left, label]
                # No clue why create_labimg_xml() expects so many values in annotation_list...
                # As far as I can see the function only uses [0, 1, 4, 5, -1].
                # Just filled the rest up with xmin and it seems to work...
                string = ','.join(map(str, list_of_coords))
                annotation_list.append(string)
            create_labimg_xml(file, annotation_list)
        elapsed_time_xml = str(datetime.timedelta(seconds=round(time.time() - start_time)))
        time_left_xml = str(
            datetime.timedelta(
                seconds=round(((time.time() - start_time) * n_images / nloop) - (time.time() - start_time))))
        xml_stats['text'] = update_progress_label_short(elapsed_time_xml, time_left_xml, command="running")
        nloop += 1
        window.update()
    xml_stats['text'] = update_progress_label_short(elapsed_time_xml, time_left_xml, command="done")
    window.update()


# function to check if the checkpoint file is present
def check_if_checkpointfile_is_present(directory):
    global loc_chkpnt_file
    checkpoint_name_re = 'checkpoint_\d+\.json'
    checkpoint_counter = 0
    output_counter = 0
    if os.path.isdir(os.path.join(directory, "json_file")):
        for filename in os.listdir(os.path.join(directory, "json_file")):
            if re.search(checkpoint_name_re, filename):
                checkpoint_counter += 1
                loc_chkpnt_file = os.path.join(directory, "json_file", filename)
            if re.search('output.json', filename):
                output_counter += 1
        if output_counter > 0 and checkpoint_counter > 0:
            if mb.askquestion("Completed output file found",
                              "There is a completed output file present in\n'" + os.path.join(
                                  directory) + "'. Are you sure the process for this folder is not already finished? Do you still wish to continue from checkpoint file?") == 'no':
                return False
        if output_counter > 0 and checkpoint_counter == 0:
            if mb.askquestion("Completed output file found",
                              "There is a completed output file present in\n'" + os.path.join(
                                  directory) + "', but no checkpoint file. Are you sure the process for this folder is not already finished?") == 'no':
                return False
        if checkpoint_counter == 0:
            mb.showerror("No checkpoint file found", "There is no checkpoint file present in\n'" + os.path.join(
                directory) + "'. Are you sure you enabled 'Use checkpoints while running' last time and specified a number of images as frequency which has been processed?")
            return False
        elif checkpoint_counter > 1:
            mb.showerror("Multiple checkpoint files found",
                         "There are multiple checkpoint files present in\n'" + os.path.join(
                             directory) + "'. Please delete the wrong checkpoint file(s) and keep only the relevant file.")
            return False
        else:
            return True
    else:
        mb.showerror("No 'json_file' directory found",
                     "There is no 'json_file' directory present in\n'" + os.path.join(
                         directory) + ".")
        return False


# function to print the progress when loading
def update_progress_label_short(value1="", value2="", command=""):
    if command == "":
        return f"In queue"
    if command == "load":
        return f"Algorithm is starting up..."
    if command == "running":
        return f"Elapsed time:\t\t{value1}\n" \
               f"Time left:\t\t\t{value2}\n"
    if command == "done":
        return f"Elapsed time:\t\t{value1}\n" \
               f"Time left:\t\t\t{value2}\n" \
               f"                                Done!"


# function to open the folder after finishing
def open_file(path):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


# function to browse dirs
def browse_dir_button():
    filename = filedialog.askdirectory()
    loc_input_image_folder.set(filename)
    loc_input_image_folder_short.set((os.path.basename(os.path.normpath(filename))[:16] + '...') if len(
        os.path.basename(os.path.normpath(filename))) > 19 else os.path.basename(os.path.normpath(filename)))
    if loc_input_image_folder.get() != '':
        dir1.grid(column=0, row=0, sticky='e')


# functions for the tkinter GUI
def togglecf():
    if check_use_checkpoints.get():
        lbl4.config(state=NORMAL)
        ent1.config(state=NORMAL)
    else:
        lbl4.config(state="disabled")
        ent1.config(state="disabled")


def v_togglecf():
    if v_check_dont_process_every_frame.get():
        v_lbl4.config(state=NORMAL)
        v_ent1.config(state=NORMAL)
    else:
        v_lbl4.config(state="disabled")
        v_ent1.config(state="disabled")


del_already_shown = 0


def toggle_del():
    global del_already_shown
    if not del_already_shown:
        del_already_shown += 1
        if not mb.askyesno("Warning",
                           "Are you sure you want to delete the original images?"
                           "\n\n"
                           "This action can not be undone."):
            check_del.set(False)


def toggle_data_type(self):
    if data_type.get() == "Images":
        # remove video labelframes
        v_meg_frame.grid_remove()
        v_sep_frame.grid_remove()
        # add image labelframes
        meg_frame.grid(column=0, row=2, columnspan=2, sticky='ew')
        vis_frame.grid(column=0, row=3, columnspan=2, sticky='ew')
        sep_frame.grid(column=0, row=4, columnspan=2, sticky='ew')
        xml_frame.grid(column=0, row=5, columnspan=2, sticky='ew')
    else:
        # remove image labelframes
        meg_frame.grid_remove()
        vis_frame.grid_remove()
        sep_frame.grid_remove()
        xml_frame.grid_remove()
        # add video labelframes
        v_meg_frame.grid(column=0, row=2, columnspan=2, sticky='ew')
        v_sep_frame.grid(column=0, row=3, columnspan=2, sticky='ew')


already_shown = 0


def disable_meg():
    lbl1.config(state=DISABLED)
    scl1.config(state=DISABLED)
    lbl2.config(state=DISABLED)
    chb1.config(state=DISABLED)
    lbl3.config(state=DISABLED)
    chb2.config(state=DISABLED)
    lbl5.config(state=DISABLED)
    chb3.config(state=DISABLED)
    lbl4.config(state=DISABLED)
    ent1.config(state=DISABLED)

    v_lbl1.config(state=DISABLED)
    v_scl1.config(state=DISABLED)
    v_leftLabel.config(state=DISABLED)
    v_lbl2.config(state=DISABLED)
    v_chb1.config(state=DISABLED)
    v_lbl5.config(state=DISABLED)
    v_chb3.config(state=DISABLED)
    v_lbl4.config(state=DISABLED)
    v_ent1.config(state=DISABLED)
    global already_shown
    if not already_shown:
        mb.showwarning('Warning',
                       'If you have already run MegaDetector on the this folder, make sure that you still have those same images or video\'s in the directory.\n\nImages/video\'s added afterwards will not be processed.\n\nAny image/video removed from the folder will cause an error.')
        already_shown = 1


def enable_meg():
    lbl1.config(state=NORMAL)
    scl1.config(state=NORMAL)
    lbl2.config(state=NORMAL)
    chb1.config(state=NORMAL)
    lbl3.config(state=NORMAL)
    chb2.config(state=NORMAL)
    lbl5.config(state=NORMAL)
    chb3.config(state=NORMAL)
    lbl4.config(state=NORMAL)
    ent1.config(state=NORMAL)

    v_lbl1.config(state=NORMAL)
    v_scl1.config(state=NORMAL)
    v_leftLabel.config(state=NORMAL)
    v_lbl2.config(state=NORMAL)
    v_chb1.config(state=NORMAL)
    v_lbl5.config(state=NORMAL)
    v_chb3.config(state=NORMAL)
    v_lbl4.config(state=NORMAL)
    v_ent1.config(state=NORMAL)


def handle_focus_in(_):
    ent1.delete(0, tk.END)
    ent1.config(fg='black')


def handle_focus_out(_):
    ent1.delete(0, tk.END)
    ent1.config(fg='grey')
    ent1.insert(0, "E.g.: 100")


def handle_enter(txt):
    handle_focus_out('dummy')


def v_handle_focus_in(_):
    v_ent1.delete(0, tk.END)
    v_ent1.config(fg='black')


def v_handle_focus_out(_):
    v_ent1.delete(0, tk.END)
    v_ent1.config(fg='grey')
    v_ent1.insert(0, "E.g.: 100")


def v_handle_enter(txt):
    v_handle_focus_out('dummy')


def open_labelImg():
    global previous_dir_processed
    global previous_sep_setting
    try:
        previous_dir_processed
    except NameError:
        previous_dir_processed = loc_input_image_folder.get()
    try:
        previous_sep_setting
    except NameError:
        previous_sep_setting = False
    if previous_sep_setting:
        previous_dir_processed = os.path.join(previous_dir_processed, "images", "animals")
    path_to_labelImg = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "labelImg")
    path_to_labelImg_install = os.path.join(os.path.dirname(os.path.realpath(__file__)), "open_labelImg.command")
    path_to_classes_txt = os.path.join(path_to_labelImg, "data", "predefined_classes.txt")
    print(f"path_to_labelImg: {path_to_labelImg}")
    print(f"path_to_labelImg_install: {path_to_labelImg_install}")
    print(f"path_to_classes_txt: {path_to_classes_txt}")
    if not os.path.isdir(path_to_labelImg):
        if mb.askyesno("labelImg not found",
                       "labelImg is not found. Do you want to download it?\n\n"
                       "It will open as soon as it is downloaded. This usually takes about a minute "
                       "depending on your internet connection."):
            os.system(f"sh '{path_to_labelImg_install}' '{previous_dir_processed}' '{path_to_classes_txt}'")
    else:
        os.system(f"sh '{path_to_labelImg_install}' '{previous_dir_processed}' '{path_to_classes_txt}'")


# tkinter window to show progress and perform the commands
def openProgressWindow():
    global loc_input_image_folder
    global check_prod_JSON
    if selected_rbtn.get() == 'N':
        check_prod_JSON = True
    else:
        check_prod_JSON = False
    global conf_thresh
    global check_recurse
    global check_use_checkpoints
    global int_checkpoint_n
    global check_cont_from_checkpoint
    global loc_chkpnt_file
    global check_sep
    global check_vis_detec
    global check_crop
    global check_del
    global check_xml
    global previous_dir_processed
    global previous_sep_setting
    global data_type
    global v_check_prod_JSON
    if v_selected_rbtn.get() == 'N':
        v_check_prod_JSON = True
    else:
        v_check_prod_JSON = False
    global v_check_recurse
    global v_conf_thresh
    global v_check_dont_process_every_frame
    global v_int_analyse_every_nth
    global v_check_sep

    if data_type.get() == "Images":
        if check_use_checkpoints.get() and not int_checkpoint_n.get().isdecimal():
            if mb.askyesno("Invalid value",
                           "You either entered an invalid value for the checkpoint frequency, or none at all. You can only enter numberic characters.\n\nDo you want to proceed with the default value 100?"):
                int_checkpoint_n.set("100")
                ent1.config(fg='black')
        if loc_input_image_folder.get() == "":
            mb.showerror("Error", message="Please specify a directory with images to be processed.")
        check_recurse_ui = check_recurse.get()
        if check_recurse_ui:  # if recurse is checked and no subdirs are present -> uncheck
            for subdir in os.listdir(loc_input_image_folder.get()):
                if os.path.isdir(os.path.join(loc_input_image_folder.get(), subdir)):
                    check_recurse_ui = True
                    break
                else:
                    check_recurse_ui = False
        if check_cont_from_checkpoint.get() and check_if_checkpointfile_is_present(
                loc_input_image_folder.get()) or not check_cont_from_checkpoint.get():
            newWindow = Toplevel(window)
            newWindow.title("Progress")
            newWindow.geometry()

            # logo
            panel = tk.Label(newWindow, image=grey_bg_logo)
            panel.grid(column=0, row=0, columnspan=2, sticky='ew', pady=(5, 0))

            # Megadetector status
            if check_prod_JSON:
                mega_frame = LabelFrame(newWindow, text="Algorithm", pady=2, padx=5, relief='solid',
                                        highlightthickness=5,
                                        font=100, fg='darkblue')
                mega_frame.configure(font=("TkDefaultFont", 15, "bold"))
                mega_frame.grid(column=0, row=1, columnspan=2, sticky='ew')
                mega_frame.columnconfigure(0, weight=3, minsize=115)
                mega_frame.columnconfigure(1, weight=1, minsize=115)
                mega_frame.rowconfigure(1, weight=0, minsize=60)
                global mega_progbar
                mega_progbar = ttk.Progressbar(master=mega_frame, orient='horizontal', mode='determinate', length=280)
                mega_progbar.grid(column=0, row=0, columnspan=2, padx=10, pady=2)
                global mega_stats
                mega_stats = ttk.Label(master=mega_frame, text=update_progress_label_short())
                mega_stats.grid(column=0, row=1, columnspan=2)

            # xml label status
            if check_xml.get():
                xml_frame = LabelFrame(newWindow, text="Create label files", pady=2, padx=5, relief='solid',
                                       highlightthickness=5, font=100, fg='darkblue', width=300, height=200)
                xml_frame.configure(font=("TkDefaultFont", 15, "bold"))
                xml_frame.grid(column=0, row=2, columnspan=2, sticky='ew')
                xml_frame.columnconfigure(0, weight=3, minsize=115)
                xml_frame.columnconfigure(1, weight=1, minsize=115)
                xml_frame.rowconfigure(1, weight=0, minsize=60)
                global xml_progbar
                xml_progbar = ttk.Progressbar(master=xml_frame, orient='horizontal', mode='determinate', length=280)
                xml_progbar.grid(column=0, row=0, columnspan=2, padx=10, pady=2)
                global xml_stats
                xml_stats = ttk.Label(master=xml_frame, text=update_progress_label_short())
                xml_stats.grid(column=0, row=1, columnspan=2)

            # separate ims status
            if check_sep.get():
                sep_frame = LabelFrame(newWindow, text="Separate images", pady=2, padx=5, relief='solid',
                                       highlightthickness=5, font=100, fg='darkblue', width=300, height=200)
                sep_frame.configure(font=("TkDefaultFont", 15, "bold"))
                sep_frame.grid(column=0, row=3, columnspan=2, sticky='ew')
                sep_frame.columnconfigure(0, weight=3, minsize=115)
                sep_frame.columnconfigure(1, weight=1, minsize=115)
                sep_frame.rowconfigure(1, weight=0, minsize=60)
                global sep_progbar
                sep_progbar = ttk.Progressbar(master=sep_frame, orient='horizontal', mode='determinate', length=280)
                sep_progbar.grid(column=0, row=0, columnspan=2, padx=10, pady=2)
                global sep_stats
                sep_stats = ttk.Label(master=sep_frame, text=update_progress_label_short())
                sep_stats.grid(column=0, row=1, columnspan=2)

            # draw boxes status
            if check_vis_detec.get():
                bbox_frame = LabelFrame(newWindow, text="Draw bounding boxes", pady=2, padx=5, relief='solid',
                                        highlightthickness=5, font=100, fg='darkblue')
                bbox_frame.configure(font=("TkDefaultFont", 15, "bold"))
                bbox_frame.grid(column=0, row=4, columnspan=2, sticky='ew')
                bbox_frame.columnconfigure(0, weight=3, minsize=115)
                bbox_frame.columnconfigure(1, weight=1, minsize=115)
                bbox_frame.rowconfigure(1, weight=0, minsize=60)
                global bbox_progbar
                bbox_progbar = ttk.Progressbar(master=bbox_frame, orient='horizontal', mode='determinate', length=280)
                bbox_progbar.grid(column=0, row=0, columnspan=2, padx=10, pady=2)
                global bbox_stats
                bbox_stats = ttk.Label(master=bbox_frame, text=update_progress_label_short())
                bbox_stats.grid(column=0, row=1, columnspan=2)

            # crop status
            if check_crop.get():
                crop_frame = LabelFrame(newWindow, text="Crop images", pady=2, padx=5, relief='solid',
                                        highlightthickness=5,
                                        font=100, fg='darkblue', width=300, height=200)
                crop_frame.configure(font=("TkDefaultFont", 15, "bold"))
                crop_frame.grid(column=0, row=5, columnspan=2, sticky='ew')
                crop_frame.columnconfigure(0, weight=3, minsize=115)
                crop_frame.columnconfigure(1, weight=1, minsize=115)
                crop_frame.rowconfigure(1, weight=0, minsize=60)
                global crop_progbar
                crop_progbar = ttk.Progressbar(master=crop_frame, orient='horizontal', mode='determinate', length=280)
                crop_progbar.grid(column=0, row=0, columnspan=2, padx=10, pady=2)
                global crop_stats
                crop_stats = ttk.Label(master=crop_frame, text=update_progress_label_short())
                crop_stats.grid(column=0, row=1, columnspan=2)

            try:
                cmd_thres = "--threshold " + str(
                    round(conf_thresh.get()) / 100) + " "  # create string with additional arguments for the json cmd
                if check_recurse_ui:
                    cmd_check_recurse = "--recursive "
                else:
                    cmd_check_recurse = ""
                if check_use_checkpoints.get() and int_checkpoint_n.get() != "":
                    cmd_check_use_chkpnts = "--checkpoint_frequency " + int_checkpoint_n.get() + " "
                else:
                    cmd_check_use_chkpnts = ""
                if check_cont_from_checkpoint.get() and loc_chkpnt_file != "":
                    cmd_loc_chkpnt_file = "--resume_from_checkpoint '" + loc_chkpnt_file + "' "
                else:
                    cmd_loc_chkpnt_file = ""
                additional_batch_cmds = " " + cmd_thres + cmd_check_recurse + cmd_check_use_chkpnts + cmd_loc_chkpnt_file

                if check_prod_JSON:  # run cmds
                    produce_json(loc_input_image_folder.get(), additional_batch_cmds)
                if check_xml.get():
                    path_to_json = os.path.join(loc_input_image_folder.get(), "json_file", "output.json")
                    create_xml(path_to_json)
                if check_sep.get():
                    separate_images(loc_input_image_folder.get())
                if check_vis_detec.get() and check_crop.get() and check_del.get():
                    visualise_bbox(path_to_image_folder=loc_input_image_folder.get(),
                                   del_originals=False,
                                   separated_files=check_sep.get())
                    crop(path_to_image_folder=loc_input_image_folder.get(),
                         del_originals=True,
                         separated_files=check_sep.get())
                elif check_vis_detec.get() and check_crop.get() and not check_del.get():
                    visualise_bbox(path_to_image_folder=loc_input_image_folder.get(),
                                   del_originals=False,
                                   separated_files=check_sep.get())
                    crop(path_to_image_folder=loc_input_image_folder.get(),
                         del_originals=False,
                         separated_files=check_sep.get())
                elif check_vis_detec.get():
                    visualise_bbox(path_to_image_folder=loc_input_image_folder.get(),
                                   del_originals=check_del.get(),
                                   separated_files=check_sep.get())
                elif check_crop.get():
                    crop(path_to_image_folder=loc_input_image_folder.get(),
                         del_originals=check_del.get(),
                         separated_files=check_sep.get())
                print('Succesfully finished - all processes done!')
                mb.showinfo('Succesfully finished', "All processes done!")
                newWindow.destroy()
                open_file(loc_input_image_folder.get())
                previous_dir_processed = loc_input_image_folder.get()
                previous_sep_setting = check_sep.get()
            except Exception as error:
                mb.showerror(title="Error",
                             message="An error has occurred: '" + str(error) + "'.",
                             detail=traceback.format_exc())
                newWindow.destroy()
    else:
        if v_check_dont_process_every_frame.get() and not v_int_analyse_every_nth.get().isdecimal():
            if mb.askyesno("Invalid value",
                           "You either entered an invalid value for 'Analyse every Nth frame', or none at all. You can only enter numberic characters.\n\nDo you want to proceed with the default value 10?\n\n"
                           "That means you process only 1 out of 10 frames, making the process time 10 times faster."):
                v_int_analyse_every_nth.set("10")
                v_ent1.config(fg='black')
        if loc_input_image_folder.get() == "":
            mb.showerror("Error", message="Please specify a directory with videos to be processed.")
        v_check_recurse_ui = v_check_recurse.get()
        if v_check_recurse_ui:  # if recurse is checked and no subdirs are present -> uncheck
            for subdir in os.listdir(loc_input_image_folder.get()):
                if os.path.isdir(os.path.join(loc_input_image_folder.get(), subdir)):
                    v_check_recurse_ui = True
                    break
                else:
                    v_check_recurse_ui = False

        newWindow = Toplevel(window)
        newWindow.title("Progress")
        newWindow.geometry()

        # logo
        panel = tk.Label(newWindow, image=grey_bg_logo)
        panel.grid(column=0, row=0, columnspan=2, sticky='ew', pady=(5, 0))

        # Megadetector status
        if v_check_prod_JSON:
            v_mega_frame = LabelFrame(newWindow, text="Algorithm", pady=2, padx=5, relief='solid', highlightthickness=5,
                                      font=100, fg='darkblue')
            v_mega_frame.configure(font=("TkDefaultFont", 15, "bold"))
            v_mega_frame.grid(column=0, row=1, columnspan=2, sticky='ew')
            v_mega_frame.columnconfigure(0, weight=3, minsize=115)
            v_mega_frame.columnconfigure(1, weight=1, minsize=115)
            v_mega_frame.rowconfigure(1, weight=0, minsize=60)
            global v_mega_progbar
            v_mega_progbar = ttk.Progressbar(master=v_mega_frame, orient='horizontal', mode='determinate', length=280)
            v_mega_progbar.grid(column=0, row=0, columnspan=2, padx=10, pady=2)
            global v_mega_stats
            v_mega_stats = ttk.Label(master=v_mega_frame, text=update_progress_label_short())
            v_mega_stats.grid(column=0, row=1, columnspan=2)

        # separate status
        if v_check_sep.get():
            v_sep_frame = LabelFrame(newWindow, text="Separate movies", pady=2, padx=5, relief='solid',
                                     highlightthickness=5, font=100, fg='darkblue', width=300, height=200)
            v_sep_frame.configure(font=("TkDefaultFont", 15, "bold"))
            v_sep_frame.grid(column=0, row=3, columnspan=2, sticky='ew')
            v_sep_frame.columnconfigure(0, weight=3, minsize=115)
            v_sep_frame.columnconfigure(1, weight=1, minsize=115)
            v_sep_frame.rowconfigure(1, weight=0, minsize=60)
            global v_sep_progbar
            v_sep_progbar = ttk.Progressbar(master=v_sep_frame, orient='horizontal', mode='determinate', length=280)
            v_sep_progbar.grid(column=0, row=0, columnspan=2, padx=10, pady=2)
            global v_sep_stats
            v_sep_stats = ttk.Label(master=v_sep_frame, text=update_progress_label_short())
            v_sep_stats.grid(column=0, row=1, columnspan=2)

        try:
            if v_check_recurse_ui:
                v_cmd_check_recurse = "--recursive "
            else:
                v_cmd_check_recurse = ""
            v_conf_thresh_str = str(round(v_conf_thresh.get()) / 100)
            v_cmd_thres = f"--rendering_confidence_threshold {v_conf_thresh_str} --json_confidence_threshold {v_conf_thresh_str} "
            if v_check_dont_process_every_frame.get():
                c_cmd_every_nth_frame = f"--frame_sample {v_int_analyse_every_nth.get()} "
            else:
                c_cmd_every_nth_frame = ""
            additional_videos_cmds = " " + v_cmd_check_recurse + v_cmd_thres + c_cmd_every_nth_frame
            if v_check_prod_JSON:
                produce_json_video(loc_input_image_folder.get(), additional_videos_cmds)
            if v_check_sep.get():
                separate_videos(loc_input_image_folder.get())
            print('Succesfully finished - all processes done!')
            mb.showinfo('Succesfully finished', "All processes done!")
            newWindow.destroy()
            open_file(loc_input_image_folder.get())
            previous_dir_processed = loc_input_image_folder.get()
            previous_sep_setting = check_sep.get()
        except Exception as error:
            mb.showerror(title="Error",
                         message="An error has occurred: '" + str(error) + "'.",
                         detail=traceback.format_exc())
            newWindow.destroy()


# tkinter main window
window = Tk()
window.title("EcoAssist 1.0")
window.geometry()
window.configure(background="white")
tabControl = ttk.Notebook(window)

# logo
logo_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'imgs', 'logo.png')
logo = Image.open(logo_path)
logo = logo.resize((int(logo.size[0] / 3), int(logo.size[1] / 3)), Image.ANTIALIAS)
white_bg_logo = Image.new("RGBA", logo.size, "WHITE")
white_bg_logo.paste(logo, (0, 0), logo)
white_bg_logo.convert('RGB')
white_bg_logo = ImageTk.PhotoImage(white_bg_logo)
grey_bg_logo = ImageTk.PhotoImage(logo)

# fox image
fox_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'imgs', 'fox.jpg')
fox = Image.open(fox_path)
left = 100
top = 150
right = left + 211 * 2
bottom = top + 81 * 2
fox = fox.crop((left, top, right, bottom))
fox = fox.resize((211, 81), Image.ANTIALIAS)
rad = 10
back = Image.new('RGB', (fox.size[0], fox.size[1]), (255, 255, 255))
back.paste(fox, (rad, 0))
mask = Image.new('L', (fox.size[0], fox.size[1]), 255)
blck = Image.new('L', (fox.size[0], fox.size[1]), 0)
mask.paste(blck, (2 * rad, 0))
blur = back.filter(ImageFilter.GaussianBlur(rad / 2))
back.paste(blur, mask=mask)
fox = ImageTk.PhotoImage(back)

# camera image
cam_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'imgs', 'cam.jpg')
cam = Image.open(cam_path)
c_left = 322
c_top = 190
c_right = c_left + 211 * 1.5
c_bottom = c_top + 81 * 1.5
cam = cam.crop((c_left, c_top, c_right, c_bottom))
cam = cam.resize((200, 81), Image.ANTIALIAS)
back = Image.new('RGB', (cam.size[0] + rad, cam.size[1]), (255, 255, 255))
back.paste(cam, (0, 0))
mask = Image.new('L', (cam.size[0] + rad, cam.size[1]), 255)
blck = Image.new('L', (cam.size[0] - rad, cam.size[1]), 0)
mask.paste(blck, (0, 0))
blur = back.filter(ImageFilter.GaussianBlur(rad / 2))
back.paste(blur, mask=mask)
cam = ImageTk.PhotoImage(back)

# imgs
tk.Label(window, image=white_bg_logo, bg="white", highlightthickness=0, highlightbackground="white").grid(column=0,
                                                                                                          row=0,
                                                                                                          sticky='ns',
                                                                                                          pady=(3, 3),
                                                                                                          padx=(0, 0))
tk.Label(window, image=cam, bg="white", highlightthickness=0, highlightbackground="white").grid(column=0, row=0,
                                                                                                sticky='wns',
                                                                                                pady=(3, 3),
                                                                                                padx=(3, 0))
tk.Label(window, image=fox, bg="white", highlightthickness=0, highlightbackground="white").grid(column=0, row=0,
                                                                                                sticky='ens',
                                                                                                pady=(3, 3),
                                                                                                padx=(0, 3))

# tabs
param_tab = ttk.Frame(tabControl)
help_tab = ttk.Frame(tabControl)
about_tab = ttk.Frame(tabControl)
tabControl.add(param_tab, text='Parameters')
tabControl.add(help_tab, text='Help')
tabControl.add(about_tab, text='About')
tabControl.grid()

# Folder frame
dir_frame = LabelFrame(param_tab, text="Folder choice", pady=2, padx=5, relief='solid', highlightthickness=5, font=100,
                       fg='darkblue')
dir_frame.configure(font=("TkDefaultFont", 15, "bold"))
dir_frame.grid(column=0, row=1, columnspan=2, sticky='ew')
dir_frame.columnconfigure(0, weight=1, minsize=430)
dir_frame.columnconfigure(1, weight=1, minsize=115)

Label(master=dir_frame, text="Folder containing camera trap data").grid(row=0, column=0, sticky='w', pady=5)
loc_input_image_folder = StringVar()
loc_input_image_folder_short = StringVar()
dir1 = Label(master=dir_frame, textvariable=loc_input_image_folder_short, fg='darkred')
Button(master=dir_frame, text="Browse", command=browse_dir_button).grid(row=0, column=1, sticky='e', padx=5)

Label(master=dir_frame, text="Type of data").grid(row=1, column=0, sticky='w', pady=5)
OPTIONS = ["Images", "Video's"]
data_type = StringVar(dir_frame)
data_type.set(OPTIONS[0])
dropdown = OptionMenu(dir_frame, data_type, *OPTIONS, command=toggle_data_type)
dropdown.config(width=6)
dropdown.grid(row=1, column=1, sticky='e', padx=5)

# Megadetector frame for images
meg_frame = LabelFrame(param_tab, text="Algorithm settings", pady=2, padx=5, relief='solid', highlightthickness=5,
                       fg='darkblue')
meg_frame.configure(font=("TkDefaultFont", 15, "bold"))
meg_frame.grid(column=0, row=2, columnspan=2, sticky='ew')
meg_frame.columnconfigure(0, weight=1, minsize=430)
meg_frame.columnconfigure(1, weight=1, minsize=115)

Label(meg_frame, text="Has the MegaDetector algorithm already been run over these images?").grid(column=0, row=0,
                                                                                                 sticky='w', pady=5)
selected_rbtn = StringVar()
selected_rbtn.set("N")
Radiobutton(meg_frame, text='No', value='N', variable=selected_rbtn, command=enable_meg).grid(column=1, row=0,
                                                                                              sticky='w', padx=5)
Radiobutton(meg_frame, text='Yes', value='Y', variable=selected_rbtn, command=disable_meg).grid(column=1, row=0,
                                                                                                sticky='e', padx=5)

lbl1 = Label(meg_frame, text="Confidence threshold (%)")
lbl1.grid(row=1, sticky='w', pady=5)
conf_thresh = DoubleVar()
conf_thresh.set(80)
scl1 = Scale(meg_frame, from_=10, to=100, orient=HORIZONTAL, length=100, variable=conf_thresh, showvalue=0)
scl1.grid(column=1, row=1, sticky='e', padx=5)
leftLabel = Label(meg_frame, textvariable=conf_thresh)
leftLabel.config(fg="darkred")
leftLabel.grid(column=0, row=1, sticky='e', padx=5)

lbl2 = Label(meg_frame, text="Include subdirectories", pady=5)
lbl2.grid(row=2, sticky='w')
check_recurse = BooleanVar()
check_recurse.set(True)
chb1 = Checkbutton(meg_frame, variable=check_recurse)
chb1.grid(row=2, column=1, sticky='e', padx=5)

lbl3 = Label(meg_frame, text="Use checkpoints while running", pady=5)
lbl3.grid(row=3, sticky='w')
check_use_checkpoints = BooleanVar()
check_use_checkpoints.set(False)
chb2 = Checkbutton(meg_frame, variable=check_use_checkpoints, command=togglecf)
chb2.grid(row=3, column=1, sticky='e', padx=5)

lbl4 = tk.Label(meg_frame, text='Checkpoint frequency', state=DISABLED, pady=5)
lbl4.grid(row=4, sticky='w')
int_checkpoint_n = StringVar()
ent1 = tk.Entry(meg_frame, width=10, textvariable=int_checkpoint_n, fg='grey', state=NORMAL)
ent1.grid(row=4, column=1, sticky='e', padx=5)
ent1.insert(0, "E.g.: 100")
ent1.bind("<FocusIn>", handle_focus_in)
ent1.bind("<FocusOut>", handle_focus_out)
ent1.bind("<Return>", handle_enter)
ent1.config(state=DISABLED)

lbl5 = Label(meg_frame, text="Continue from last checkpoint file onwards", pady=5)
lbl5.grid(row=5, sticky='w')
check_cont_from_checkpoint = BooleanVar()
check_cont_from_checkpoint.set(False)
chb3 = Checkbutton(meg_frame, variable=check_cont_from_checkpoint)
chb3.grid(row=5, column=1, sticky='e', padx=5)

# Visualisation frame for images
vis_frame = LabelFrame(param_tab, text="Visualisation settings", pady=2, padx=5, relief='solid', highlightthickness=5,
                       fg='darkblue')
vis_frame.configure(font=("TkDefaultFont", 15, "bold"))
vis_frame.grid(column=0, row=3, columnspan=2, sticky='ew')
vis_frame.columnconfigure(0, weight=3, minsize=430)
vis_frame.columnconfigure(1, weight=1, minsize=115)

lbl9 = Label(vis_frame, text="Draw boxes around the detections and show confidences", state=NORMAL, pady=5)
lbl9.grid(row=0, sticky='w')
check_vis_detec = BooleanVar()
chb5 = Checkbutton(vis_frame, variable=check_vis_detec, state=NORMAL)
chb5.grid(row=0, column=1, sticky='e', padx=5)

lbl10 = Label(vis_frame, text="Crop detections", pady=5)
lbl10.grid(row=1, sticky='w')
check_crop = BooleanVar()
chb6 = Checkbutton(vis_frame, variable=check_crop)
chb6.grid(row=1, column=1, sticky='e', padx=5)

lbl11 = Label(vis_frame, text="Delete original images", pady=5)
lbl11.grid(row=2, sticky='w')
check_del = BooleanVar()
check_del.set(False)
chb7 = Checkbutton(vis_frame, variable=check_del, command=toggle_del)
chb7.grid(row=2, column=1, sticky='e', padx=5)

# Seperator frame for images
sep_frame = LabelFrame(param_tab, text="Separate images", pady=2, padx=5, relief='solid', highlightthickness=5,
                       fg='darkblue')
sep_frame.configure(font=("TkDefaultFont", 15, "bold"))
sep_frame.grid(column=0, row=4, columnspan=2, sticky='ew')
sep_frame.columnconfigure(0, weight=3, minsize=430)
sep_frame.columnconfigure(1, weight=1, minsize=115)

lbl8 = Label(sep_frame, text="Separate images into subdirectories based on their detections", pady=5)
lbl8.grid(row=0, sticky='w')
check_sep = BooleanVar()
check_sep.set(True)
chb4 = Checkbutton(sep_frame, variable=check_sep)
chb4.grid(row=0, column=1, sticky='e', padx=5)

# XML frame for images
xml_frame = LabelFrame(param_tab, text="Create label files", pady=2, padx=5, relief='solid', highlightthickness=5,
                       fg='darkblue')
xml_frame.configure(font=("TkDefaultFont", 15, "bold"))
xml_frame.grid(column=0, row=5, columnspan=2, sticky='ew')
xml_frame.columnconfigure(0, weight=3, minsize=430)
xml_frame.columnconfigure(1, weight=1, minsize=115)

lbl9 = Label(xml_frame, text="Create .xml label files for all detections in Pascal VOC format", pady=5)
lbl9.grid(row=0, sticky='w')
check_xml = BooleanVar()
check_xml.set(False)
chb5 = Checkbutton(xml_frame, variable=check_xml)
chb5.grid(row=0, column=1, sticky='e', padx=5)

lbl10 = Label(xml_frame, text="Open labelImg to review and adjust these label files", pady=5)
lbl10.grid(row=1, sticky='w')
Button(master=xml_frame, text="Open", command=open_labelImg).grid(row=1, column=1, sticky='e', padx=5)

# Megadetector frame for videos
v_meg_frame = LabelFrame(param_tab, text="Algorithm settings", pady=2, padx=5, relief='solid', highlightthickness=5,
                         fg='darkblue')
v_meg_frame.configure(font=("TkDefaultFont", 15, "bold"))
v_meg_frame.columnconfigure(0, weight=1, minsize=430)
v_meg_frame.columnconfigure(1, weight=1, minsize=115)

Label(v_meg_frame, text="Has the MegaDetector algorithm already been run over these video's?").grid(column=0, row=0,
                                                                                                    sticky='w', pady=5)
v_selected_rbtn = StringVar()
v_selected_rbtn.set("N")
Radiobutton(v_meg_frame, text='No', value='N', variable=v_selected_rbtn, command=enable_meg).grid(column=1, row=0,
                                                                                                  sticky='w', padx=5)
Radiobutton(v_meg_frame, text='Yes', value='Y', variable=v_selected_rbtn, command=disable_meg).grid(column=1, row=0,
                                                                                                    sticky='e', padx=5)
v_lbl1 = Label(v_meg_frame, text="Confidence threshold (%)")
v_lbl1.grid(row=1, sticky='w', pady=5)
v_conf_thresh = DoubleVar()
v_conf_thresh.set(95)
v_scl1 = Scale(v_meg_frame, from_=10, to=100, orient=HORIZONTAL, length=100, variable=v_conf_thresh, showvalue=0)
v_scl1.grid(column=1, row=1, sticky='e', padx=5)
v_leftLabel = Label(v_meg_frame, textvariable=v_conf_thresh)
v_leftLabel.config(fg="darkred")
v_leftLabel.grid(column=0, row=1, sticky='e', padx=5)

# v_lbl2 = Label(v_meg_frame, text="Include subdirectories", pady=5)
# v_lbl2.grid(row=2, sticky='w')
v_check_recurse = BooleanVar()
v_check_recurse.set(True)
# v_chb1 = Checkbutton(v_meg_frame, variable=v_check_recurse)
# v_chb1.grid(row=2, column=1, sticky='e', padx=5)

v_lbl5 = Label(v_meg_frame, text="Don't process every frame", pady=5)
v_lbl5.grid(row=4, sticky='w')
v_check_dont_process_every_frame = BooleanVar()
v_check_dont_process_every_frame.set(False)
v_chb3 = Checkbutton(v_meg_frame, variable=v_check_dont_process_every_frame, command=v_togglecf)
v_chb3.grid(row=4, column=1, sticky='e', padx=5)

v_lbl4 = tk.Label(v_meg_frame, text='Analyse every Nth frame', state=DISABLED, pady=5)
v_lbl4.grid(row=5, sticky='w')
v_int_analyse_every_nth = StringVar()
v_ent1 = tk.Entry(v_meg_frame, width=10, textvariable=v_int_analyse_every_nth, fg='grey', state=NORMAL)
v_ent1.grid(row=5, column=1, sticky='e', padx=5)
v_ent1.insert(0, "E.g.: 10")
v_ent1.bind("<FocusIn>", v_handle_focus_in)
v_ent1.bind("<FocusOut>", v_handle_focus_out)
v_ent1.bind("<Return>", v_handle_enter)
v_ent1.config(state=DISABLED)

# Seperator frame for videos
v_sep_frame = LabelFrame(param_tab, text="Separate videos", pady=2, padx=5, relief='solid', highlightthickness=5,
                         fg='darkblue')
v_sep_frame.configure(font=("TkDefaultFont", 15, "bold"))
v_sep_frame.columnconfigure(0, weight=3, minsize=430)
v_sep_frame.columnconfigure(1, weight=1, minsize=115)

v_lbl8 = Label(v_sep_frame, text="Separate videos into subdirectories based on their detections", pady=5)
v_lbl8.grid(row=0, sticky='w')
v_check_sep = BooleanVar()
v_check_sep.set(True)
v_chb4 = Checkbutton(v_sep_frame, variable=v_check_sep)
v_chb4.grid(row=0, column=1, sticky='e', padx=5)

# run button
button = Button(
    param_tab,
    text="Process files",
    command=openProgressWindow)
button.grid(column=0, row=7, columnspan=2, padx=5, pady=0, sticky='ew')

# help tab
scroll = Scrollbar(help_tab)
scroll.grid(row=0, column=1, sticky='ns')
t = Text(help_tab, width=70, height=43, wrap=WORD,
         yscrollcommand=scroll.set)
t.tag_config('title', font='TkDefaultFont 13 bold', foreground='darkblue')
t.tag_config('mark', font='TkDefaultFont 13 italic', foreground='darkred', justify='center')
t.tag_config('info', font='TkDefaultFont 13 normal')

t.insert(END, "Please find below a list of parameters with an explanation on how to interpret them.\n\n")
t.tag_add('info', '1.0', '1.end')

t.insert(END, "--------------------------------------------------------------------------------------------\n")
t.insert(END, "General options\n")
t.insert(END, "--------------------------------------------------------------------------------------------\n")
t.insert(END, "Folder containing camera trap data\n")
t.insert(END,
         "Here you can browse for a folder which contains camera trap images or video\'s. All further specified settings will be performed on this directory.\n\n")
t.tag_add('mark', '3.0', '3.end')
t.tag_add('mark', '4.0', '4.end')
t.tag_add('mark', '5.0', '5.end')
t.tag_add('title', '6.0', '6.end')
t.tag_add('info', '7.0', '7.end')

t.insert(END, "Type of data\n")
t.insert(END, "Indicate whether you want to process images or video\'s. The options for analysis differ.\n\n")
t.tag_add('title', '9.0', '9.end')
t.tag_add('info', '10.0', '10.end')

t.insert(END, "--------------------------------------------------------------------------------------------\n")
t.insert(END, "Options available when analysing images\n")
t.insert(END, "--------------------------------------------------------------------------------------------\n")
t.insert(END, "Has the MegaDetector algorithm already been run over these images?\n")
t.insert(END,
         "Here you can indicate if you have already run the algorithm over the images using EcoAssist. If so, EcoAssist will use the existing output. Please note that the folder must contain the same images (and filenames). Any new images added afterwards will not be handled and any images removed from the folder will cause an error.\n\n")
t.tag_add('mark', '12.0', '12.end')
t.tag_add('mark', '13.0', '13.end')
t.tag_add('mark', '14.0', '14.end')
t.tag_add('title', '15.0', '15.end')
t.tag_add('info', '16.0', '16.end')

t.insert(END, "Confidence threshold (%)\n")
t.insert(END,
         "The confidence threshold after which MegaDetector will return a detection. If you set a high confidence threshold, you will only get the animals of which MegaDetector is certain (but will probably miss a few less certain animals). If you set the threshold low, you will get false positives. In my experience a threshold of 80% generally works well, but this might be different with specific ecosystems. My advice is to first run the model on a directory with 100 representative images with the option 'Draw boxes around the detections and show confidences' and then manually check the detections. This will show you how sure the model is about its detections and will give you an insight into which threshold will yield the least false positives and false negatives.\n\n")
t.tag_add('title', '18.0', '18.end')
t.tag_add('info', '19.0', '19.end')

t.insert(END, "Include subdirectories\n")
t.insert(END, "Select if your folder contains other directories which should also be handled.\n\n")
t.tag_add('title', '21.0', '21.end')
t.tag_add('info', '22.0', '22.end')

t.insert(END, "Use checkpoints while running\n")
t.insert(END,
         "This is a functionality to save results to checkpoints intermittently, in case technical hiccup arises. That way you won't have to restart the entire process again when the process is interrupted.\n\n")
t.tag_add('title', '24.0', '24.end')
t.tag_add('info', '25.0', '25.end')

t.insert(END, "Checkpoint frequency\n")
t.insert(END,
         "Fill in how often you want to save the results to checkpoints. The number indicates the number of images after which checkpoints will be saved. The entry must contain only numeric characters.\n\n")
t.tag_add('title', '27.0', '27.end')
t.tag_add('info', '28.0', '28.end')

t.insert(END, "Continue from last checkpoint file onwards\n")
t.insert(END,
         "Here you can choose to continue from the last saved checkpoint onwards so that the algorithm can continue where it left off. Checkpoints are saved into the 'json' subdirectory within the main folder.\n\n")
t.tag_add('title', '30.0', '30.end')
t.tag_add('info', '31.0', '31.end')

t.insert(END, "Draw boxes around the detections and show confidences\n")
t.insert(END,
         "This functionality draws boxes around the detections and saves them in the subdirectory '_visualised_images'. Animals, persons and vehicles are visualised using different colours. The confidence with which the model has appointed this detection is also shown.\n\n")
t.tag_add('title', '33.0', '33.end')
t.tag_add('info', '34.0', '34.end')

t.insert(END, "Crop detections\n")
t.insert(END, "Specify if you want the detections to be cropped and saved into a subdirectory '_cropped_images'.\n\n")
t.tag_add('title', '36.0', '36.end')
t.tag_add('info', '37.0', '37.end')

t.insert(END, "Delete original images\n")
t.insert(END,
         "The crop and draw bounding box functions alter the images. Specify if you want to delete the unaltered orignal images.\n\n")
t.tag_add('title', '39.0', '39.end')
t.tag_add('info', '40.0', '40.end')

t.insert(END, "Separate images into subdirectories based on their detections\n")
t.insert(END,
         "This function divides the images in the subdirectories 'empties', 'animals', 'persons', 'vehicles', and 'multiple_categories'.\n\n")
t.tag_add('title', '42.0', '42.end')
t.tag_add('info', '43.0', '43.end')

t.insert(END, "Create .xml label files for all detections in Pascal VOC format\n")
t.insert(END,
         "When training your own model using machine learning the images generally need to be labelled in Pascal VOC format. When this option is enabled it will annotate the images. You only have to assign the appropriate species using the option 'Open labelImg to review and adjust these labels'. The animals are already located.\n\n")
t.tag_add('title', '45.0', '45.end')
t.tag_add('info', '46.0', '46.end')

t.insert(END, "Open labelImg to review and adjust these labels\n")
hyperlink1 = HyperlinkManager(t)
t.insert(INSERT, "LabelImg",
         hyperlink1.add(
             partial(webbrowser.open, "https://github.com/tzutalin/labelImg")))
t.insert(END,
         " is a open source application which makes it easy to annotate images for object detection machine learning. Here you can easily open the application. The first time it will download the application into the 'EcoAssist_files' folder. It defaults to opening the previously processed folder containing cameratrap imagery. When nothing has been processed it will open with the folder specified at 'folder choice'. When annotating, you can change the defeault labels to your own by changing the predefined_classes.txt file in EcoAssist_files/labelImg/data.\n\n")
t.tag_add('title', '48.0', '48.end')
t.tag_add('info', '49.0', '49.end')

t.insert(END, "--------------------------------------------------------------------------------------------\n")
t.insert(END, "Options available when analysing video\'s\n")
t.insert(END, "--------------------------------------------------------------------------------------------\n")
t.insert(END, "Has the MegaDetector algorithm already been run over these video\'s?\n")
t.insert(END,
         "Here you can indicate if you have already run the algorithm over the images using EcoAssist. If so, EcoAssist will use the existing output. Please note that the folder must contain the same files (and filenames). Any new video's added afterwards will not be handled and any video's removed from the folder will cause an error.\n\n")
t.tag_add('mark', '51.0', '51.end')
t.tag_add('mark', '52.0', '52.end')
t.tag_add('mark', '53.0', '53.end')
t.tag_add('title', '54.0', '54.end')
t.tag_add('info', '55.0', '55.end')

t.insert(END, "Confidence threshold (%)\n")
t.insert(END,
         "The confidence threshold after which MegaDetector will return a detection. If you set a high confidence threshold, you will only get the animals of which MegaDetector is certain (but will probably miss a few less certain animals). If you set the threshold low, you will get false positives. When analysing video's, the model first splits it into frames and then analyses the frames as images. This means that for one video, many frames are processed, so the chance of getting a false positive is higher than for just one image. With one false positive the video could be placed into the wrong subdirectory. That is why it generally is good practise to set the threshold for video's relatively high. If an animal is present in the video, it will most likely be in many frames and thus will still be detected. In my experience a threshold of 95% generally works well, but this might be different with specific ecosystems.\n\n")
t.tag_add('title', '57.0', '57.end')
t.tag_add('info', '58.0', '58.end')

# t.insert(END, "Include subdirectories\n")
# t.insert(END, "Select if your folder contains other directories which should also be handled.\n\n")
# t.tag_add('title', '60.0', '60.end')
# t.tag_add('info', '61.0', '61.end')

t.insert(END, "Don't process every frame\n")
t.insert(END,
         "When processing every frame of a video, it can take a long, long time to finish. Here you can specify whether you want to analyse only a selection of frames. At 'analyse every Nth frame' you can specify how many frames you want to be analysed.\n\n")
t.tag_add('title', '60.0', '60.end')
t.tag_add('info', '61.0', '61.end')

t.insert(END, "Analyse every Nth frame\n")
t.insert(END,
         "Specify how many frames you want to process. By entering 2, you will process every 2nd frame and thus cut process time by half. By entering 50, you will shorten process time to 1/50, et cetera.\n\n")
t.tag_add('title', '63.0', '63.end')
t.tag_add('info', '64.0', '64.end')

t.insert(END, "Separate videos into subdirectories based on their detections\n")
t.insert(END,
         "This function divides the videos in the subdirectories 'empties', 'animals', 'persons', 'vehicles', and 'multiple_categories'.")
t.tag_add('title', '66.0', '66.end')
t.tag_add('info', '67.0', '67.end')

t.grid(row=0, column=0, sticky="nesw")
t.configure(font=("TkDefaultFont", 11, "bold"), state=DISABLED)
scroll.config(command=t.yview)

# about tab
text = Text(about_tab, width=70, height=43, wrap=WORD,
            yscrollcommand=scroll.set)
text.tag_config('title', font='TkDefaultFont 13 bold', foreground='darkblue')
text.tag_config('info', font='TkDefaultFont 13 normal')
text.tag_config('italic', font='TkDefaultFont 13 italic')

text.insert(END, "The application\n")
text.insert(END,
            "EcoAssist is a freely available and open-source application with the aim of helping ecologists all over the world with their camera trap imagery. It uses a deep learning algorithm trained to detect the presence of animals, people and vehicles in camera trap data. You can let the algorithm process images or videos and filter out the empties, annotate for further processing (such as training your own algorithm) and visualise or crop the detections.\n\n")
text.tag_add('title', '1.0', '1.end')
text.tag_add('info', '2.0', '2.end')

text.insert(END, "The model\n")
text.insert(END, "For this application, I used ")
hyperlink = HyperlinkManager(text)
text.insert(INSERT, "MegaDetector",
            hyperlink.add(
                partial(webbrowser.open, "https://github.com/microsoft/CameraTraps/blob/master/megadetector.md")))
text.insert(END,
            " to detect animals, people, and vehicles. It does not identify animals, it just finds them. The model is created by Beery, Morris, and Yang (2019) and is based on Faster-RCNN with an InceptionResNetv2 base network. The model was trained with the TensorFlow Object Detection API, using several hundred thousand bounding boxes from a variety of ecosystems. MegaDetector has a precision of 89%–99% at detecting animals and on a typical laptop (bought in 2021) it takes somewhere between 8 and 20 seconds per image. This works out to being able to process approximately between 4.000 and 10.000 images per day. The model is free, and it makes the creators super-happy when people use it, so I put their emailadress here for your convenience: ")
text.insert(INSERT, "cameratraps@microsoft.com",
            hyperlink.add(partial(webbrowser.open, "mailto:cameratraps@microsoft.com")))
text.insert(END, ".\n\n")
text.tag_add('title', '4.0', '4.end')
text.tag_add('info', '5.0', '5.end')

text.insert(END, "   Beery, S., Morris, D., & Yang, S. (2019). Efficient pipeline for camera trap image review.\n"
                 "      ArXiv preprint arXiv:1907.06772.\n\n")
text.tag_add('italic', '7.0', '8.end')

text.insert(END, "The author\n")
text.insert(END,
            "This program is written by Peter van Lunteren. I am a wildlife ecologist with a special interest in artificial intelligence, and how it can be applied to improve ecological research. EcoAssist is written to assist camera trap ecologists in their day-to-day activities without needing to have any programming skills. Help me to keep improving EcoAssist and let me know about any improvements, bugs, or new features so that I can continue to keep it up-to-date. Also, I would also very much like to know who uses the tool and for what reason. Please send me an email on ")
text.insert(INSERT, "contact@pvanlunteren.com",
            hyperlink.add(partial(webbrowser.open, "mailto:contact@pvanlunteren.com")))
text.insert(END, ".")
text.tag_add('title', '10.0', '10.end')
text.tag_add('info', '11.0', '11.end')
text.grid(row=0, column=0, sticky="nesw")
text.configure(font=("TkDefaultFont", 11, "bold"), state=DISABLED)

window.mainloop()
