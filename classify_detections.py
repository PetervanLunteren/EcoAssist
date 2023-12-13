# Script to add species specific classifications to animal detections
# Written by Peter van Lunteren
# Latest edit by Peter van Lunteren on 17 Oct 2023

# import packages
from ultralytics import YOLO
import json
import os
import sys
import torch
import stat
import time
import pickle
import humanfriendly
from tqdm import tqdm
from PIL import Image, ImageOps
from collections import defaultdict 
import shutil

# init vars
animal_model_fpath = str(sys.argv[1]) if sys.argv[1] != 'None' else None
animal_thresh = float(sys.argv[2]) if sys.argv[2] != 'None' else None
smooth_bool = True if sys.argv[3] == 'True' else False
vehicle_model_fpath = str(sys.argv[4]) if sys.argv[4] != 'None' else None
vehicle_thresh = float(sys.argv[5]) if sys.argv[5] != 'None' else None
person_model_fpath = str(sys.argv[6]) if sys.argv[6] != 'None' else None
person_thresh = float(sys.argv[7]) if sys.argv[7] != 'None' else None
json_path = str(sys.argv[8])
temp_frame_folder = str(sys.argv[9])
EcoAssist_files = str(sys.argv[10])

# load models
animal_model = YOLO(animal_model_fpath) if animal_model_fpath != None else None
vehicle_model = YOLO(vehicle_model_fpath) if vehicle_model_fpath != None else None
person_model = YOLO(person_model_fpath) if person_model_fpath != None else None

# get external code in here
sys.path.insert(0, EcoAssist_files)
sys.path.insert(0, os.path.join(EcoAssist_files, "cameratraps"))
from detection.video_utils import frame_results_to_video_results
from md_utils.ct_utils import is_list_sorted
from EcoAssist.smooth_params import *

# fetch classifications for single crop
def get_classification(img_fpath, detection_type):
    if detection_type == 'animal':
        results = animal_model(img_fpath, verbose=False)
    elif detection_type == 'vehicle':
        results = vehicle_model(img_fpath, verbose=False)
    elif detection_type == 'person':
        results = person_model(img_fpath, verbose=False)
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

# crop detection with equal sides (Thanks Dan Morris)
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

    # count the number of crops to classify
    n_crops_to_classify = 0
    with open(json_path) as image_recognition_file_content:
        data = json.load(image_recognition_file_content)
        label_map = fetch_label_map_from_json(json_path)
        for image in data['images']:
            if 'detections' in image:
                for detection in image['detections']:
                    conf = detection["conf"]
                    category_id = detection['category']
                    category = label_map[category_id]
                    if animal_model_fpath != None:
                        if conf >= animal_thresh and category == 'animal':
                            n_crops_to_classify += 1
                    if vehicle_model_fpath != None:
                        if conf >= vehicle_thresh and category == 'vehicle':
                            n_crops_to_classify += 1
                    if person_model_fpath != None:
                        if conf >= person_thresh and category == 'person':
                            n_crops_to_classify += 1

    # crop and classify
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
        with tqdm(total=n_crops_to_classify) as pbar:
            for image in data['images']:

                # loop
                fname = image['file']
                if 'detections' in image:
                    for detection in image['detections']:
                        conf = detection["conf"]
                        category_id = detection['category']
                        category = label_map[category_id]
                        if animal_model_fpath == None and category == 'animal':
                            continue
                        if vehicle_model_fpath == None and category == 'vehicle':
                            continue
                        if person_model_fpath == None and category == 'person':
                            continue
                        if category == 'animal' and conf >= animal_thresh or \
                            category == 'vehicle' and conf >= vehicle_thresh or \
                            category == 'person' and conf >= person_thresh:
                            img_fpath = os.path.join(img_dir, fname)
                            bbox = detection['bbox']
                            crop = remove_background(Image.open(img_fpath), bbox)
                            name_classifications = get_classification(crop, category)

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

                            # update prgressbar
                            pbar.update(1)

    # # write unaltered json for timelapse
    json_path_unaltered = os.path.splitext(json_path)[0] + "_original" + os.path.splitext(json_path)[1]
    data['classification_categories'] = {v: k for k, v in inverted_cls_label_map.items()}
    with open(json_path_unaltered, "w") as json_file:
        json.dump(data, json_file, indent=1)

    # smooth results if user specified
    json_to_rewrite = json_path_unaltered
    if smooth_bool and json_path.endswith("image_recognition_file.json"):
        json_path_smooth = os.path.splitext(json_path)[0] + "_smooth" + os.path.splitext(json_path)[1]
        smooth_json(json_path_unaltered, json_path_smooth)
        json_to_rewrite = json_path_smooth

    # rewrite json to be used by EcoAssist
    with open(json_to_rewrite) as image_recognition_file_content:
        data = json.load(image_recognition_file_content)

        # fetch label maps
        cls_label_map = data['classification_categories']
        det_label_map = data['detection_categories']
        inverted_cls_label_map = {v: k for k, v in cls_label_map.items()}
        inverted_det_label_map = {v: k for k, v in det_label_map.items()}

        # add cls classes to det label map
        for k, v in inverted_cls_label_map.items():
            inverted_det_label_map[k] = str(len(inverted_det_label_map) + 1)

        # loop and adjust
        for image in data['images']:
            if 'detections' in image:
                for detection in image['detections']:
                    category_id = detection['category']
                    category = det_label_map[category_id]
                    if 'classifications' in detection:
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

# check other predictions whitin an image or sequence and smooth results to minimise prediction errors
# Thanks Dan Morris (https://github.com/agentmorris/MegaDetector/blob/main/api/batch_processing/data_preparation/manage_local_batch.py)
def smooth_json(json_input_fpath, json_output_fpath):
    # init vars
    filename_base = os.path.normpath(os.path.dirname(json_input_fpath))
    classification_detection_files = [json_input_fpath]
    overflow_folder_handling_enabled = False

    # check if user assigned other and non-other categories
    global other_category_names
    global non_other_category_names
    other_category_names_assigned = False
    non_other_category_names_assigned = False
    if 'other_category_names' in vars() or 'other_category_names' in globals():
        other_category_names_assigned = True
    if 'non_other_category_names' in vars() or 'non_other_category_names' in globals():
        non_other_category_names_assigned = True

    # if user has not assigned values to other_category_names and non_other_category_names themselves, we'll try to
    # automatically distille the other category
    if other_category_names_assigned == False or non_other_category_names_assigned == False:
        with open(json_input_fpath,'r') as f:
            d = json.load(f)
            categories = list(d['classification_categories'].values())
            if 'other' not in categories:
                other_category_names = []
                non_other_category_names = categories
                print(f"<EA>Warning: category 'other' not present in json file. The variables other_category_names"
                    " and non_other_category_names also not assigned in EcoAssist\smooth_params.py. Will not"
                    " perform 'other'-smoothing, but will proceed with classification and sequence smoothing"
                    " as usual.<EA>")
            else:
                other_category_names = ['other']
                categories.remove('other')
                non_other_category_names = categories

    smoothed_classification_files = []
    for final_output_path in classification_detection_files:
        classifier_output_path = final_output_path
        classifier_output_path_within_image_smoothing = classifier_output_path.replace(
            '.json','_within_image_smoothing.json')
        with open(classifier_output_path,'r') as f:
            d = json.load(f)
        category_name_to_id = {d['classification_categories'][k]:k for k in d['classification_categories']}
        other_category_ids = []
        for s in other_category_names:
            if s in category_name_to_id:
                other_category_ids.append(category_name_to_id[s])
            else:
                print('<EA>Warning: "other" category {} not present in file {}<EA>'.format(
                    s,classifier_output_path))
        n_other_classifications_changed = 0
        n_other_images_changed = 0
        n_detections_flipped = 0
        n_images_changed = 0
        
        # Before we do anything else, get rid of everything but the top classification for each detection.
        for im in d['images']:
            if 'detections' not in im or im['detections'] is None or len(im['detections']) == 0:
                continue
            detections = im['detections']
            for det in detections:
                if 'classifications' not in det or len(det['classifications']) == 0:
                    continue
                classification_confidence_values = [c[1] for c in det['classifications']]
                assert is_list_sorted(classification_confidence_values,reverse=True)
                det['classifications'] = [det['classifications'][0]]
            # ...for each detection in this image
        # ...for each image
        
        for im in tqdm(d['images']):
            if 'detections' not in im or im['detections'] is None or len(im['detections']) == 0:
                continue
            detections = im['detections']
            category_to_count = defaultdict(int)
            for det in detections:
                if ('classifications' in det) and (det['conf'] >= detection_confidence_threshold):
                    for c in det['classifications']:
                        if c[1] >= classification_confidence_threshold:
                            category_to_count[c[0]] += 1
                    # ...for each classification
                # ...if there are classifications for this detection
            # ...for each detection
                            
            if len(category_to_count) <= 1:
                continue
            category_to_count = {k: v for k, v in sorted(category_to_count.items(),
                                                        key=lambda item: item[1], 
                                                        reverse=True)}
            keys = list(category_to_count.keys())
            
            # Handle a quirky special case: if the most common category is "other" and 
            # it's "tied" with the second-most-common category, swap them
            if (len(keys) > 1) and \
                (keys[0] in other_category_ids) and \
                (keys[1] not in other_category_ids) and \
                (category_to_count[keys[0]] == category_to_count[keys[1]]):
                    keys[1], keys[0] = keys[0], keys[1]
            
            max_count = category_to_count[keys[0]]
            # secondary_count = category_to_count[keys[1]]
            # The 'secondary count' is the most common non-other class
            secondary_count = 0
            for i_key in range(1,len(keys)):
                if keys[i_key] not in other_category_ids:
                    secondary_count = category_to_count[keys[i_key]]
                    break
            most_common_category = keys[0]
            assert max_count >= secondary_count
            
            # If we have at least *min_detections_to_overwrite_other* in a category that isn't
            # "other", change all "other" classifications to that category
            if max_count >= min_detections_to_overwrite_other and \
                most_common_category not in other_category_ids:
                other_change_made = False
                for det in detections:
                    if ('classifications' in det) and (det['conf'] >= detection_overwrite_threshold): 
                        for c in det['classifications']:                
                            if c[1] >= classification_overwrite_threshold and \
                                c[0] in other_category_ids:
                                n_other_classifications_changed += 1
                                other_change_made = True
                                c[0] = most_common_category
                        # ...for each classification
                    # ...if there are classifications for this detection
                # ...for each detection
                
                if other_change_made:
                    n_other_images_changed += 1
            # ...if we should overwrite all "other" classifications
        
            if max_count < min_detections_above_threshold:
                continue
            if secondary_count >= max_detections_secondary_class:
                continue
            
            # At this point, we know we have a dominant category; change all other above-threshold
            # classifications to that category.  That category may have been "other", in which
            # case we may have already made the relevant changes.
            n_detections_flipped_this_image = 0
            for det in detections:
                if ('classifications' in det) and (det['conf'] >= detection_overwrite_threshold):
                    for c in det['classifications']:
                        if c[1] >= classification_overwrite_threshold and \
                            c[0] != most_common_category:
                            c[0] = most_common_category
                            n_detections_flipped += 1
                            n_detections_flipped_this_image += 1
                    # ...for each classification
                # ...if there are classifications for this detection
            # ...for each detection
            
            if n_detections_flipped_this_image > 0:
                n_images_changed += 1
        # ...for each image    
        
        print('<EA>Classification smoothing: changed {} detections on {} images<EA>'.format(
            n_detections_flipped,n_images_changed))
        print('<EA>"Other" smoothing: changed {} detections on {} images<EA>'.format(
            n_other_classifications_changed,n_other_images_changed))
        with open(classifier_output_path_within_image_smoothing,'w') as f:
            json.dump(d,f,indent=1)
        print('Wrote results to:\n{}'.format(classifier_output_path_within_image_smoothing))
        smoothed_classification_files.append(classifier_output_path_within_image_smoothing)
    # ...for each file we want to smooth

    #% Read EXIF data from all images
    from data_management import read_exif
    exif_options = read_exif.ReadExifOptions()
    exif_options.verbose = False
    # exif_options.n_workers = default_workers_for_parallel_tasks
    # exif_options.use_threads = parallelization_defaults_to_threads
    exif_options.processing_library = 'pil'
    exif_options.byte_handling = 'delete'
    exif_results_file = os.path.join(filename_base,'exif_data.json')
    if os.path.isfile(exif_results_file):
        print('Reading EXIF results from {}'.format(exif_results_file))
        with open(exif_results_file,'r') as f:
            exif_results = json.load(f)
    else:        
        exif_results = read_exif.read_exif_from_folder(filename_base,
                                                    output_file=exif_results_file,
                                                    options=exif_options)

    #% Prepare COCO-camera-traps-compatible image objects for EXIF results
    import datetime    
    from data_management.read_exif import parse_exif_datetime_string
    min_valid_timestamp_year = 2000
    now = datetime.datetime.now()
    image_info = []
    images_without_datetime = []
    images_with_invalid_datetime = []
    exif_datetime_tag = 'DateTimeOriginal'
    for exif_result in tqdm(exif_results):
        im = {}

        # By default we assume that each leaf-node folder is a location
        if overflow_folder_handling_enabled:
            im['location'] = relative_path_to_location(os.path.dirname(exif_result['file_name']))
        else:
            im['location'] = os.path.dirname(exif_result['file_name'])

        im['file_name'] = exif_result['file_name']
        im['id'] = im['file_name']
        if ('exif_tags' not in exif_result) or (exif_result['exif_tags'] is None) or \
            (exif_datetime_tag not in exif_result['exif_tags']): 
            exif_dt = None
        else:
            exif_dt = exif_result['exif_tags'][exif_datetime_tag]
            exif_dt = parse_exif_datetime_string(exif_dt)
        if exif_dt is None:
            im['datetime'] = None
            images_without_datetime.append(im['file_name'])
        else:
            dt = exif_dt
            
            # An image from the future (or within the last hour) is invalid
            if (now - dt).total_seconds() <= 1*60*60:
                print('<EA>Warning: datetime for {} is {}<EA>'.format(
                    im['file_name'],dt))
                im['datetime'] = None            
                images_with_invalid_datetime.append(im['file_name'])
            
            # An image from before the dawn of time is also invalid
            elif dt.year < min_valid_timestamp_year:
                print('<EA>Warning: datetime for {} is {}<EA>'.format(
                    im['file_name'],dt))
                im['datetime'] = None
                images_with_invalid_datetime.append(im['file_name'])
            
            else:
                im['datetime'] = dt
        image_info.append(im)
    # ...for each exif image result

    print('<EA>Parsed EXIF datetime information, unable to parse EXIF data from {} of {} images<EA>'.format(
        len(images_without_datetime),len(exif_results)))

    #% Assemble into sequences
    from data_management import cct_json_utils
    print('Assembling images into sequences')
    cct_json_utils.create_sequences(image_info)

    # Make a list of images appearing at each location
    sequence_to_images = defaultdict(list)
    for im in tqdm(image_info):
        sequence_to_images[im['seq_id']].append(im)
    all_sequences = list(sorted(sequence_to_images.keys()))

    #% Load classification results
    sequence_level_smoothing_input_file = smoothed_classification_files[0]
    with open(sequence_level_smoothing_input_file,'r') as f:
        d = json.load(f)

    # Map each filename to classification results for that file
    filename_to_results = {}
    for im in tqdm(d['images']):
        filename_to_results[im['file'].replace('\\','/')] = im

    #% Smooth classification results over sequences (prep)
    classification_category_id_to_name = d['classification_categories']
    classification_category_name_to_id = {v: k for k, v in classification_category_id_to_name.items()}
    class_names = list(classification_category_id_to_name.values())
    animal_detection_category = '1'
    assert(d['detection_categories'][animal_detection_category] == 'animal')
    other_category_ids = set([classification_category_name_to_id[s] for s in other_category_names])

    # These are the only classes to which we're going to switch other classifications
    category_names_to_smooth_to = set(non_other_category_names)
    category_ids_to_smooth_to = set([classification_category_name_to_id[s] for s in category_names_to_smooth_to])
    assert all([s in class_names for s in category_names_to_smooth_to])    
    
    #% Smooth classification results over sequences (supporting functions)
    def results_for_sequence(images_this_sequence):
        """
        Fetch MD results for every image in this sequence, based on the 'file_name' field
        """
        results_this_sequence = []
        for im in images_this_sequence:
            fn = im['file_name']
            results_this_image = filename_to_results[fn]
            assert isinstance(results_this_image,dict)
            results_this_sequence.append(results_this_image)
        return results_this_sequence

    def top_classifications_for_sequence(images_this_sequence):
        """
        Return all top-1 animal classifications for every detection in this 
        sequence, regardless of  confidence

        May modify [images_this_sequence] (removing non-top-1 classifications)
        """
        classifications_this_sequence = []
        for im in images_this_sequence:
            fn = im['file_name']
            results_this_image = filename_to_results[fn]
            if 'detections' in results_this_image:
                if results_this_image['detections'] is None:
                    continue
            else:
                continue
            for det in results_this_image['detections']:
                
                # Only process animal detections
                if det['category'] != animal_detection_category:
                    continue
                
                # Only process detections with classification information
                if 'classifications' not in det:
                    continue
                
                # We only care about top-1 classifications, remove everything else
                if len(det['classifications']) > 1:
                    
                    # Make sure the list of classifications is already sorted by confidence
                    classification_confidence_values = [c[1] for c in det['classifications']]
                    assert is_list_sorted(classification_confidence_values,reverse=True)
                    
                    # ...and just keep the first one
                    det['classifications'] = [det['classifications'][0]]
                    
                # Confidence values should be sorted within a detection; verify this, and ignore 
                top_classification = det['classifications'][0]
                classifications_this_sequence.append(top_classification)
            # ...for each detection in this image
        # ...for each image in this sequence
        return classifications_this_sequence
    # ...top_classifications_for_sequence()


    def count_above_threshold_classifications(classifications_this_sequence):    
        """
        Given a list of classification objects (tuples), return a dict mapping
        category IDs to the count of above-threshold classifications.
        
        This dict's keys will be sorted in descending order by frequency.
        """
        
        # Count above-threshold classifications in this sequence
        category_to_count = defaultdict(int)
        for c in classifications_this_sequence:
            if c[1] >= classification_confidence_threshold:
                category_to_count[c[0]] += 1
        
        # Sort the dictionary in descending order by count
        category_to_count = {k: v for k, v in sorted(category_to_count.items(),
                                                    key=lambda item: item[1], 
                                                    reverse=True)}
        
        keys_sorted_by_frequency = list(category_to_count.keys())
            
        # Handle a quirky special case: if the most common category is "other" and 
        # it's "tied" with the second-most-common category, swap them.
        if len(other_category_names) > 0:
            if (len(keys_sorted_by_frequency) > 1) and \
                (keys_sorted_by_frequency[0] in other_category_names) and \
                (keys_sorted_by_frequency[1] not in other_category_names) and \
                (category_to_count[keys_sorted_by_frequency[0]] == \
                category_to_count[keys_sorted_by_frequency[1]]):
                    keys_sorted_by_frequency[1], keys_sorted_by_frequency[0] = \
                        keys_sorted_by_frequency[0], keys_sorted_by_frequency[1]
        sorted_category_to_count = {}    
        for k in keys_sorted_by_frequency:
            sorted_category_to_count[k] = category_to_count[k]
        return sorted_category_to_count
    # ...def count_above_threshold_classifications()
        
    def sort_images_by_time(images):
        """
        Returns a copy of [images], sorted by the 'datetime' field (ascending).
        """
        return sorted(images, key = lambda im: im['datetime'])        

    def get_first_key_from_sorted_dictionary(di):
        if len(di) == 0:
            return None
        return next(iter(di.items()))[0]

    def get_first_value_from_sorted_dictionary(di):
        if len(di) == 0:
            return None
        return next(iter(di.items()))[1]

    #% Smooth classifications at the sequence level (main loop)
    n_other_flips = 0
    n_classification_flips = 0
    n_unclassified_flips = 0

    # Break if this token is contained in a filename (set to None for normal operation)
    debug_fn = None
    for i_sequence,seq_id in tqdm(enumerate(all_sequences),total=len(all_sequences)):
        images_this_sequence = sequence_to_images[seq_id]
        
        # Count top-1 classifications in this sequence (regardless of confidence)
        classifications_this_sequence = top_classifications_for_sequence(images_this_sequence)
        
        # Handy debugging code for looking at the numbers for a particular sequence
        for im in images_this_sequence:
            if debug_fn is not None and debug_fn in im['file_name']:
                raise ValueError('')
        if len(classifications_this_sequence) == 0:
            continue
        
        # Count above-threshold classifications for each category
        sorted_category_to_count = count_above_threshold_classifications(classifications_this_sequence)
        if len(sorted_category_to_count) == 0:
            continue
        
        max_count = get_first_value_from_sorted_dictionary(sorted_category_to_count)    
        dominant_category_id = get_first_key_from_sorted_dictionary(sorted_category_to_count)
        
        # If our dominant category ID isn't something we want to smooth to, don't mess around with this sequence
        if dominant_category_id not in category_ids_to_smooth_to:
            continue
        
        ## Smooth "other" classifications ##
        if max_count >= min_dominant_class_classifications_above_threshold_for_other_smoothing:        
            for c in classifications_this_sequence:           
                if c[0] in other_category_ids:
                    n_other_flips += 1
                    c[0] = dominant_category_id
                    c[1] = flipped_other_confidence_value

        # By not re-computing "max_count" here, we are making a decision that the count used
        # to decide whether a class should overwrite another class does not include any "other"
        # classifications we changed to be the dominant class.  If we wanted to include those...
        # 
        # sorted_category_to_count = count_above_threshold_classifications(classifications_this_sequence)
        # max_count = get_first_value_from_sorted_dictionary(sorted_category_to_count)    
        # assert dominant_category_id == get_first_key_from_sorted_dictionary(sorted_category_to_count)
        
        ## Smooth non-dominant classes ##
        if max_count >= min_dominant_class_classifications_above_threshold_for_class_smoothing:
            
            # Don't flip classes to the dominant class if they have a large number of classifications
            category_ids_not_to_flip = set()
            for category_id in sorted_category_to_count.keys():
                secondary_class_count = sorted_category_to_count[category_id]
                dominant_to_secondary_ratio = max_count / secondary_class_count
                
                # Don't smooth over this class if there are a bunch of them, and the ratio
                # if primary to secondary class count isn't too large
                
                # Default ratio
                ratio_for_override = min_dominant_class_ratio_for_secondary_override_table[None]
                
                # Does this dominant class have a custom ratio?
                if dominant_category_id in min_dominant_class_ratio_for_secondary_override_table:
                    ratio_for_override = \
                        min_dominant_class_ratio_for_secondary_override_table[dominant_category_id]
                if (dominant_to_secondary_ratio < ratio_for_override) and \
                    (secondary_class_count > \
                    max_secondary_class_classifications_above_threshold_for_class_smoothing):
                    category_ids_not_to_flip.add(category_id)
            for c in classifications_this_sequence:
                if c[0] not in category_ids_not_to_flip and c[0] != dominant_category_id:
                    c[0] = dominant_category_id
                    c[1] = flipped_class_confidence_value
                    n_classification_flips += 1
            
        ## Smooth unclassified detections ##
        if max_count >= min_dominant_class_classifications_above_threshold_for_unclassified_smoothing:
            results_this_sequence = results_for_sequence(images_this_sequence)
            detections_this_sequence = []
            for r in results_this_sequence:
                if r['detections'] is not None:
                    detections_this_sequence.extend(r['detections'])
            for det in detections_this_sequence:
                if 'classifications' in det and len(det['classifications']) > 0:
                    continue
                if det['category'] != animal_detection_category:
                    continue
                if det['conf'] < min_detection_confidence_for_unclassified_flipping:
                    continue
                det['classifications'] = [[dominant_category_id,flipped_unclassified_confidence_value]]
                n_unclassified_flips += 1
                                
    # ...for each sequence    
    print('\nFinished sequence smoothing\n')
    print('<EA>Flipped {} "other" classifications<EA>'.format(n_other_flips))
    print('<EA>Flipped {} species classifications<EA>'.format(n_classification_flips))
    print('<EA>Flipped {} unclassified detections<EA>'.format(n_unclassified_flips))
    
    #% Write smoothed classification results
    with open(os.path.join(filename_base, json_output_fpath),'w') as f:
        json.dump(d,f,indent=1)
    
    #% remove temporary jsons
    if os.path.isfile(classifier_output_path_within_image_smoothing):
        os.remove(classifier_output_path_within_image_smoothing)

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
