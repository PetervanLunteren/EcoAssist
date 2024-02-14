# Script to further identify MD animal detections using a yolov8 classification model
# It constsist of code that is specific for this kind of model architechture, and 
# code that is generic for all model architectures that will be run via EcoAssist.
# Written by Peter van Lunteren
# Latest edit by Peter van Lunteren on 23 Jan 2024

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
from ultralytics import YOLO
import torch

# load model
animal_model = YOLO(cls_model_fpath)

# check GPU availability
GPU_availability = False
try:
    if torch.backends.mps.is_built() and torch.backends.mps.is_available():
        GPU_availability = True
except:
    pass
if not GPU_availability:
    GPU_availability = torch.cuda.is_available()

# read label map
# # not neccesary for yolov8 models to retreive label map exernally, as it is incorporated into the model itself

# predict from cropped image
# input: cropped PIL image
# output: unsorted classifications formatted as [['aardwolf', 2.3025326090220233e-09], ['african wild cat', 5.658252888451898e-08], ... ]
# no need to remove forbidden classes from the predictions, that will happen in infrence_lib.py
def get_classification(PIL_crop):
    results = animal_model(PIL_crop, verbose=False)
    names_dict = results[0].names
    probs = results[0].probs.data.tolist()
    classifications = []
    for idx, v in names_dict.items():
        classifications.append([v, probs[idx]])
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
