# Script to further identify MD animal detections using a mewc classification model
# It constsist of code that is specific for this kind of model architechture, and 
# code that is generic for all model architectures that will be run via EcoAssist.
# Written by Peter van Lunteren
# Latest edit by Peter van Lunteren on 22 Jan 2024

#############################################
############### MODEL GENERIC ###############
#############################################
# catch shell arguments
import sys
EcoAssist_files = str(sys.argv[1])
cls_model_fpath = str(sys.argv[2])
cls_detec_thresh = float(sys.argv[3])
cls_class_thresh = float(sys.argv[4])
smooth_bool = True if sys.argv[5] == 'True' else False
json_path = str(sys.argv[6])
temp_frame_folder =  None if str(sys.argv[7]) == 'None' else str(sys.argv[7])

##############################################
############### MODEL SPECIFIC ###############
##############################################
# imports
import os
import cv2
import yaml
import numpy as np
import tensorflow as tf
import tensorflow_addons as tfa
from tensorflow.keras.models import load_model

# load model
animal_model = load_model(cls_model_fpath, custom_objects={'loss': tfa.losses.SigmoidFocalCrossEntropy()})
img_size = animal_model.get_config()["layers"][0]["config"]["batch_input_shape"][1]

# check GPU availability
GPU_availability = True if len(tf.config.list_logical_devices('GPU')) > 0 else False

# read label map
def read_yaml(file_path):
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)
class_map = read_yaml(os.path.join(os.path.dirname(cls_model_fpath), "class_list.yaml"))
inv_class = {v: k for k, v in class_map.items()}

# predict from cropped image
# input: cropped PIL image
# output: unsorted classifications formatted as [['aardwolf', 2.3025326090220233e-09], ['african wild cat', 5.658252888451898e-08], ... ]
# no need to remove forbidden classes from the predictions, that will happen in infrence_lib.py
def get_classification(PIL_crop):
    img = np.array(PIL_crop)
    img = cv2.resize(img, (img_size, img_size))
    img = np.expand_dims(img, axis=0)
    pred = animal_model.predict(img, verbose=0)[0]
    class_ids = sorted(inv_class.values())
    classifications = []
    for i in range(len(pred)):
        classifications.append([class_ids[i], float(pred[i])])
    return classifications

#############################################
############### MODEL GENERIC ###############
#############################################
# run main function
import EcoAssist.classification_utils.inference_lib as ea
ea.classify_MD_json(json_path = json_path,
                    GPU_availability = GPU_availability,
                    cls_detec_thresh = cls_detec_thresh,
                    cls_class_thresh = cls_class_thresh,
                    smooth_bool = smooth_bool,
                    inference_function = get_classification,
                    temp_frame_folder = temp_frame_folder,
                    cls_model_fpath = cls_model_fpath)