# Based on classification_utils/model_types/sdwa-pt/ script


#############################################
############### MODEL GENERIC ###############
#############################################
import sys
import logging
import torch
import pandas as pd
import torch.nn.functional as F
from pathlib import Path
from torchvision import transforms


EcoAssist_files = str(sys.argv[1])
cls_model_fpath = str(sys.argv[2])
cls_detec_thresh = float(sys.argv[3])
cls_class_thresh = float(sys.argv[4])
smooth_bool = True if sys.argv[5] == 'True' else False
json_path = str(sys.argv[6])
temp_frame_folder = None if str(sys.argv[7]) == 'None' else str(sys.argv[7])


log_file = f"{EcoAssist_files}/EcoAssist/logfiles/sochi_classification_model.log"
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s', 
                    handlers=[logging.FileHandler(log_file, mode='w'), logging.StreamHandler()])


logging.info("Starting script with the following arguments:")
logging.info(f"EcoAssist_files: {EcoAssist_files}")
logging.info(f"cls_model_fpath: {cls_model_fpath}")
logging.info(f"cls_detec_thresh: {cls_detec_thresh}")
logging.info(f"cls_class_thresh: {cls_class_thresh}")
logging.info(f"smooth_bool: {smooth_bool}")
logging.info(f"json_path: {json_path}")
logging.info(f"temp_frame_folder: {temp_frame_folder}")


##############################################
############### MODEL SPECIFIC ###############
##############################################
# set paths
chkpt_path = Path(cls_model_fpath).parent / "classificator_sochi_v2.pt"
class_csv_path = Path(cls_model_fpath).parent / "classes.csv"
logging.info(f"Checkpoint path: {chkpt_path}")
logging.info(f"Class CSV path: {class_csv_path}")


GPU_availability = False
device_str = 'cpu'
try:
    if torch.backends.mps.is_built() and torch.backends.mps.is_available():
        GPU_availability = True
        device_str = 'mps'
except Exception as e:
    logging.warning(f"MPS backend not available: {e}")

if not GPU_availability:
    if torch.cuda.is_available():
        GPU_availability = True
        device_str = 'cuda'

device = torch.device(device_str)

logging.info(f"Device selected: {device_str}")
logging.info(f"GPU availability: {GPU_availability}")


logging.info("Loading model and class data...")
classes = pd.read_csv(class_csv_path)
model = torch.jit.load(chkpt_path)
model.to(torch.device(device_str))
model.eval()

# image preprocessing 
preprocess = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])


def get_classification(PIL_crop):
    input_tensor = preprocess(PIL_crop)
    input_batch = input_tensor.unsqueeze(0)
    input_batch = input_batch.to(device)
    output = model(input_batch)
    probabilities = F.softmax(output, dim=1)
    probabilities_np = probabilities.cpu().detach().numpy()
    classifications = [[classes.iloc[i].values[1], prob] for i, prob in enumerate(probabilities_np[0])]
    return classifications

# Функция кропа
def get_crop(img, bbox_norm):
    buffer = 0 
    width, height = img.size
    bbox1, bbox2, bbox3, bbox4 = bbox_norm
    left = width * bbox1
    top = height * bbox2
    right = width * (bbox1 + bbox3)
    bottom = height * (bbox2 + bbox4)
    left = max(0, int(left) - buffer)
    top = max(0, int(top) - buffer)
    right = min(width, int(right) + buffer)
    bottom = min(height, int(bottom) + buffer)
    image_cropped = img.crop((left, top, right, bottom))
    return image_cropped

#############################################
############### MODEL GENERIC ###############
#############################################
import EcoAssist.classification_utils.inference_lib as ea
logging.info("Starting main classification...")
ea.classify_MD_json(json_path=json_path,
                    GPU_availability=GPU_availability,
                    cls_detec_thresh=cls_detec_thresh,
                    cls_class_thresh=cls_class_thresh,
                    smooth_bool=smooth_bool,
                    crop_function=get_crop,
                    inference_function=get_classification,
                    temp_frame_folder=temp_frame_folder,
                    cls_model_fpath=cls_model_fpath)
logging.info("Classification completed.")# catch shell arguments

