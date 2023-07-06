# -*- coding: utf-8 -*-
'''
@time: 2019/01/11 11:28
spytensor
'''

import os
import json
import numpy as np
import pandas as pd
import glob
import cv2
import os
import shutil
from IPython import embed
from sklearn.model_selection import train_test_split
from dsconfig import basedir,trainval_split_ratio
from utils.extract_csv_label import class_id
np.random.seed(41)


class Csv2CoCo:

    def __init__(self, image_dir, total_annos, classname_to_id):
        self.images = []
        self.annotations = []
        self.categories = []
        self.img_id = 0
        self.ann_id = 0
        self.image_dir = image_dir
        self.total_annos = total_annos
        self.classname_to_id_ = classname_to_id
        self._init_categories()

    def save_coco_json(self, instance, save_path):
        json.dump(instance, open(save_path, 'w'),
                  ensure_ascii=False, indent=2)

    # create COCO annotation json
    def to_coco(self, keys):
        for key in keys:
            self.images.append(self._image(key))
            shapes = self.total_annos[key]
            for shape in shapes:
                bboxi = []
                for cor in shape[:-1]:
                    bboxi.append(int(cor))
                label = shape[-1]
                annotation = self._annotation(bboxi, label)
                self.annotations.append(annotation)
                self.ann_id += 1
            self.img_id += 1
        instance = {}
        instance['info'] = 'spytensor created'
        instance['license'] = ['license']
        instance['images'] = self.images
        instance['annotations'] = self.annotations
        instance['categories'] = self.categories
        return instance

    # create COCO class
    def _init_categories(self):
        for k, v in self.classname_to_id_.items():
            category = {}
            category['id'] = v
            category['name'] = k
            self.categories.append(category)

    # create COCO image
    def _image(self, path):
        image = {}
        img = cv2.imread(os.path.join(self.image_dir, path))
        image['height'] = img.shape[0]
        image['width'] = img.shape[1]
        image['id'] = self.img_id
        image['file_name'] = path
        return image

    # create COCO annotation
    def _annotation(self, shape, label):
        # label = shape[-1]
        points = shape[:4]
        annotation = {}
        annotation['id'] = self.ann_id
        annotation['image_id'] = self.img_id
        annotation['category_id'] = int(self.classname_to_id_[label])
        annotation['segmentation'] = self._get_seg(points)
        annotation['bbox'] = self._get_box(points)
        annotation['iscrowd'] = 0
        annotation['area'] = self._get_area(points)
        return annotation

    # conver xyxy to xywh
    def _get_box(self, points):
        min_x = points[0]
        min_y = points[1]
        max_x = points[2]
        max_y = points[3]
        return [min_x, min_y, max_x - min_x, max_y - min_y]
    
    # calculate area
    def _get_area(self, points):
        min_x = points[0]
        min_y = points[1]
        max_x = points[2]
        max_y = points[3]
        return (max_x - min_x+1) * (max_y - min_y+1)
    # segmentation

    def _get_seg(self, points):
        min_x = points[0]
        min_y = points[1]
        max_x = points[2]
        max_y = points[3]
        h = max_y - min_y
        w = max_x - min_x
        a = []
        a.append([min_x, min_y, min_x, min_y+0.5*h, min_x, max_y, min_x+0.5*w, max_y,
                 max_x, max_y, max_x, max_y-0.5*h, max_x, min_y, max_x-0.5*w, min_y])
        return a


if __name__ == '__main__':
    csv_file = os.path.join(basedir, "labels.csv")
    image_dir = os.path.join(basedir, "images")
    classname_to_id = class_id(csv_file)
    for k in classname_to_id.keys():
        classname_to_id[k] += 1
    saved_coco_path = basedir
    # parse csv
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
    # divide by keys
    total_keys = list(total_csv_annotations.keys())
    train_keys, val_keys = train_test_split(total_keys, test_size=trainval_split_ratio)
    print("train_n:", len(train_keys), 'val_n:', len(val_keys))
    # create folders
    if not os.path.exists(os.path.join(saved_coco_path, 'coco', 'annotations')):
        os.makedirs(os.path.join(saved_coco_path, 'coco', 'annotations'))
    if not os.path.exists(os.path.join(saved_coco_path, 'coco', 'images', 'train2017')):
        os.makedirs(os.path.join(saved_coco_path,'coco', 'images', 'train2017'))
    if not os.path.exists(os.path.join(saved_coco_path, 'coco', 'images', 'val2017')):
        os.makedirs(os.path.join(saved_coco_path, 'coco', 'images', 'val2017'))
    # copy images
    for file in train_keys:
        shutil.copy(os.path.join(image_dir, file), os.path.join(
            saved_coco_path, 'coco', 'images', 'train2017'))
    for file in val_keys:
        shutil.copy(os.path.join(image_dir, file), os.path.join(
            saved_coco_path, 'coco', 'images', 'val2017'))
    # convert train set to coco json format
    CsvCoCo = Csv2CoCo(image_dir=image_dir,
                         total_annos=total_csv_annotations, classname_to_id = classname_to_id)
    train_instance = CsvCoCo.to_coco(train_keys)
    CsvCoCo.save_coco_json(train_instance, os.path.join(
        saved_coco_path, 'coco', 'annotations', 'instances_train2017.json'))
    # convert validation set to coco json format
    val_instance = CsvCoCo.to_coco(val_keys)
    CsvCoCo.save_coco_json(val_instance, os.path.join(
        saved_coco_path, 'coco', 'annotations', 'instances_val2017.json'))
    # convert train and validation set to coco json format
    trainval_instance = CsvCoCo.to_coco(total_keys)
    CsvCoCo.save_coco_json(trainval_instance, os.path.join(
        saved_coco_path, 'coco', 'annotations', 'voc_2007_trainval.json'))
    # convert test set to coco json format
    shutil.copy(os.path.join(saved_coco_path, 'coco', 'annotations', 'voc_2007_trainval.json'), 
                os.path.join(saved_coco_path, 'coco', 'annotations', 'voc_2007_test.json'))
