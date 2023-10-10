# Script to add species specific classifications to animal detections
# Written by Peter van Lunteren
# Latest edit by Peter van Lunteren on 9 Oct 2023

# import packages
from ultralytics import YOLO
import json
import os
import sys
import torch
from tqdm import tqdm
from PIL import Image, ImageOps
import shutil

# init vars
model_path = sys.argv[1]
json_path = sys.argv[2]
cls_thresh = float(sys.argv[3])
EcoAssist_files = sys.argv[4]
temp_frame_folder = sys.argv[5]
model = YOLO(model_path)

# get exisiting code in here
sys.path.insert(0, os.path.join(EcoAssist_files, "cameratraps"))
from detection.video_utils import frame_results_to_video_results

# fetch classifications for single crop
def get_classification(img_fpath):
    results = model(img_fpath, verbose=False)
    names_dict = results[0].names
    probs = results[0].probs.data.tolist()
    classifications = []
    for idx, v in names_dict.items():
        classifications.append([v, probs[idx]])
    return classifications

# fetch label map from json
def fetch_label_map_from_json(path_to_json):
    with open(path_to_json, "r") as json_file:
        data = json.load(json_file)
    label_map = data['detection_categories']
    return label_map

# crop detection with equal sides
def remove_background(img, bbox_norm):
    img_w, img_h = img.size
    xmin = int(bbox_norm[0] * img_w)
    ymin = int(bbox_norm[1] * img_h)
    box_w = int(bbox_norm[2] * img_w)
    box_h = int(bbox_norm[3] * img_h)
    box_size = max(box_w, box_h)
    xmin = max(0, min(
        xmin - int((box_size - box_w) / 2),
        img_w - box_w))
    ymin = max(0, min(
        ymin - int((box_size - box_h) / 2),
        img_h - box_h))
    box_w = min(img_w, box_size)
    box_h = min(img_h, box_size)
    if box_w == 0 or box_h == 0:
        return
    crop = img.crop(box=[xmin, ymin, xmin + box_w, ymin + box_h])
    crop = ImageOps.pad(crop, size=(box_size, box_size), color=0)
    return crop

# run through json and convert detections to classficiations
def convert_detections_to_classification(json_path, img_dir):

    # check if mps or cuda is available
    GPU_availability = False
    try:
        if torch.backends.mps.is_built() and torch.backends.mps.is_available():
            GPU_availability = True
    except:
        pass
    if not GPU_availability:
        GPU_availability = torch.cuda.is_available()

    # start running
    print(f"GPU available: {GPU_availability}")
    initial_it = True
    with open(json_path) as image_recognition_file_content:
        data = json.load(image_recognition_file_content)
        label_map = fetch_label_map_from_json(json_path)
        if 'classification_categories' not in data:
            data['classification_categories'] = {}
        inverted_cls_label_map = {v: k for k, v in data['classification_categories'].items()}
        inverted_det_label_map = {v: k for k, v in data['detection_categories'].items()}
        n_tot_img = len(data['images'])
        for image in tqdm(data['images']):

            # loop
            fname = image['file']
            for detection in image['detections']:
                conf = detection["conf"]
                category_id = detection['category']
                category = label_map[category_id]
                if conf >= cls_thresh and category == 'animal':
                    img_fpath = os.path.join(img_dir, fname)
                    bbox = detection['bbox']
                    crop = remove_background(Image.open(img_fpath), bbox)
                    name_classifications = get_classification(crop)

                    # check if name already in classification_categories
                    idx_classifications = []
                    for elem in name_classifications:
                        name = elem[0]
                        if initial_it:
                            if name not in inverted_cls_label_map:
                                highest_index = 0
                                for key, value in inverted_cls_label_map.items():
                                    value = int(value)
                                    if value > highest_index:
                                        highest_index = value
                                inverted_cls_label_map[name] = str(highest_index + 1)
                        idx_classifications.append([inverted_cls_label_map[name], round(elem[1], 5)])
                    initial_it = False

                    # sort
                    idx_classifications = sorted(idx_classifications, key=lambda x:x[1], reverse=True)
                    detection['classifications'] = idx_classifications

    # write unaltered json for timelapse
    json_path_unaltered = os.path.splitext(json_path)[0] + "_original" + os.path.splitext(json_path)[1]
    data['classification_categories'] = {v: k for k, v in inverted_cls_label_map.items()}
    with open(json_path_unaltered, "w") as json_file:
        json.dump(data, json_file, indent=1)

    # rewrite json to be used by EcoAssist
    with open(json_path_unaltered) as image_recognition_file_content:
        data = json.load(image_recognition_file_content)

        # fetch label maps
        cls_label_map = data['classification_categories']
        det_label_map = data['detection_categories']
        inverted_cls_label_map = {v: k for k, v in cls_label_map.items()}
        inverted_det_label_map = {v: k for k, v in det_label_map.items()}

        # add cls classes to det label map
        inverted_det_label_map['Unclassified animal'] = inverted_det_label_map.pop('animal')
        for k, v in inverted_cls_label_map.items():
            inverted_det_label_map[k] = str(len(inverted_det_label_map) + 1)

        # loop and adjust
        for image in data['images']:
            for detection in image['detections']:
                category_id = detection['category']
                category = det_label_map[category_id]
                if category == 'animal' and 'classifications' in detection:
                    highest_classification = detection['classifications'][0]
                    class_idx = highest_classification[0]
                    class_name = cls_label_map[class_idx]
                    detec_idx = inverted_det_label_map[class_name]
                    detection['prev_conf'] = detection["conf"]
                    detection['prev_category'] = detection['category']
                    detection["conf"] = highest_classification[1]
                    detection['category'] = str(detec_idx)

    # write json to be used by EcoAssist
    data['detection_categories'] = {v: k for k, v in inverted_det_label_map.items()}
    with open(json_path, "w") as json_file:
        json.dump(data, json_file, indent=1)

# different workflow for videos than for images
if json_path.endswith('video_recognition_file.json'):

    # init vars
    json_path_head = os.path.splitext(json_path)[0]
    json_path_tail = os.path.splitext(json_path)[1]
    video_level_json = json_path
    video_level_json_original = json_path_head + '_original' + json_path_tail
    frame_level_json = json_path_head + '.frames' + json_path_tail
    frame_level_json_original = json_path_head + '.frames_original' + json_path_tail

    # for video's we need to classify the frames json instead of the normal json
    convert_detections_to_classification(json_path = frame_level_json,
                                         img_dir = temp_frame_folder)
    
    # convert frame results to video results
    frame_results_to_video_results(input_file = frame_level_json,
                                   output_file = video_level_json)
    frame_results_to_video_results(input_file = frame_level_json_original,
                                   output_file = video_level_json_original)

    # remove unnecessary jsons
    if os.path.isfile(frame_level_json_original):
        os.remove(frame_level_json_original)
    if os.path.isfile(frame_level_json):
        os.remove(frame_level_json)

# for images it's much more straight forward
else:
    convert_detections_to_classification(json_path = json_path,
                                         img_dir = os.path.dirname(json_path))