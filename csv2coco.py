# -*- coding: utf-8 -*-

import os
import json
import numpy as np
import cv2
import os
from tqdm import tqdm
from dsconfig import parse_args, copy_image
from utils.extract_csv_label import parse_csv
from sklearn.model_selection import train_test_split

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
        for key in tqdm(keys, desc="create coco annot"):
            self.images.append(self._image(key))
            shapes = self.total_annos[key]
            if not np.isnan(shapes[:,:4].astype(np.float32)).any():# keep empty image as negative sample
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
        instance['info']        = 'coco'
        instance['license']     = ['license']
        instance['images']      = self.images
        instance['annotations'] = self.annotations
        instance['categories']  = self.categories
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
    args = parse_args()
    ds_type = args.type
    trainval_split_ratio = args.ratio
    
    print("start converting csv into COCO Dataset")
    print(f"dataset path: {args.basedir}")
    print(f"dataset type: {args.type}")

    csv_file = os.path.join(args.basedir, "labels.csv")
    image_dir = os.path.join(args.basedir, "images")

    total_csv_annotations, classname_to_id = parse_csv(csv_file, args.class_id)
    total_keys = list(total_csv_annotations.keys())
    # create folders
    saved_coco_path = args.basedir
    if not os.path.exists(os.path.join(saved_coco_path, 'coco', 'annotations')):
        os.makedirs(os.path.join(saved_coco_path, 'coco', 'annotations'))
    if not os.path.exists(os.path.join(saved_coco_path, 'coco', 'images')):
        os.makedirs(os.path.join(saved_coco_path,'coco', 'images'))
        
    if ds_type == "train" or ds_type == "test" or ds_type == "val":
        # copy images
        if not args.annot_only:
            for file in tqdm(total_keys, desc="copy images"):
                copy_image(image_dir, os.path.join(saved_coco_path, 'coco', 'images'), file)
        CsvCoCo = Csv2CoCo(image_dir=image_dir, total_annos=total_csv_annotations, classname_to_id = classname_to_id)
        total_instance = CsvCoCo.to_coco(total_keys)
        CsvCoCo.save_coco_json(total_instance, os.path.join(saved_coco_path, 'coco', 'annotations', 'instances_' + ds_type + '2017.json'))
    elif ds_type == "trainval":
        # divide by keys
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
        if not args.annot_only:
            for file in tqdm(train_keys, desc="copy images"):
                copy_image(image_dir, os.path.join(saved_coco_path, 'coco', 'images'), file)
            for file in tqdm(val_keys, desc="copy images"):
                copy_image(image_dir, os.path.join(saved_coco_path, 'coco', 'images'), file)
        
        # convert train set to coco json format
        CsvCoCo = Csv2CoCo(image_dir=image_dir,total_annos=total_csv_annotations, classname_to_id = classname_to_id)
        train_instance = CsvCoCo.to_coco(train_keys)
        CsvCoCo.save_coco_json(train_instance, os.path.join(saved_coco_path, 'coco', 'annotations', 'instances_train2017.json'))
        
        # convert validation set to coco json format
        CsvCoCo = Csv2CoCo(image_dir=image_dir, total_annos=total_csv_annotations, classname_to_id = classname_to_id)
        val_instance = CsvCoCo.to_coco(val_keys)
        CsvCoCo.save_coco_json(val_instance, os.path.join(saved_coco_path, 'coco', 'annotations', 'instances_val2017.json'))
