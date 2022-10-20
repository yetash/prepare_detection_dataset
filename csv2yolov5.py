import os
import numpy as np
import codecs
import pandas as pd
import json
from glob import glob
import cv2
import shutil
from sklearn.model_selection import train_test_split
from IPython import embed
from dsconfig import basedir, classname_to_id

# 1.initialize path
datasetname = "train2017"  # test or trainval
csv_file = os.path.join(basedir, "labels.csv")
image_raw_parh = os.path.join(basedir, "images/")

# 2.create folder
label_save_path = os.path.join("yolov5/labels", datasetname)
image_save_path = os.path.join("yolov5/images", datasetname)
if not os.path.exists(label_save_path):
    os.makedirs(label_save_path)
if not os.path.exists(image_save_path):
    os.makedirs(image_save_path)

# 3.preprocessing: achieve file name and bbox
total_csv_annotations = {}
annotations = pd.read_csv(csv_file, header=None).values
for annotation in annotations:
    key = annotation[0].split(os.sep)[-1]
    value = np.array([annotation[1:]])
    if key in total_csv_annotations.keys():
        total_csv_annotations[key] = np.concatenate(
            (total_csv_annotations[key], value), axis=0)
    else:
        total_csv_annotations[key] = value

# create label
for filename, labels in total_csv_annotations.items():
    fn = filename.split('.')[0]
    f = open(os.path.join(label_save_path, fn+".txt"), "w")
    shutil.copy(os.path.join(image_raw_parh, filename),
                os.path.join(image_save_path))
    im = cv2.imread(os.path.join(image_raw_parh, filename))
    im_height = im.shape[0]
    im_width = im.shape[1]
    for l in labels:
        xmin = float(l[0])
        ymin = float(l[1])
        xmax = float(l[2])
        ymax = float(l[3])
        class_id = classname_to_id[l[-1]]
        box_center_x = (xmin + xmax)/(2 * im_width)
        box_center_y = (ymin + ymax)/(2 * im_height)
        box_width = (xmax - xmin)/im_width
        box_height = (ymax - ymin)/im_height
        f.write(
            f'{class_id:d} {box_center_x:.6f} {box_center_y:.6f} {box_width:.6f} {box_height:.6f}\n')
    f.close()
