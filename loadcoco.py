import os
import cv2
import random
import numpy as np
from pycocotools.coco import COCO
from tqdm import tqdm

def load_coco(coco_res, im_base_dir):
    max_box_per_im = 0
    total_box_sum = 0
    id2im={}
    id2cat={}
    for _,v in coco_res.imgs.items():
        id2im[v['id']] = v['file_name']
    for _,v in coco_res.cats.items():
        id2cat[v['id']] = v['name']
    colorlist = []
    for i in range(len(id2cat) + 1):
        colorlist.append([random.randint(0,255),random.randint(0,255),random.randint(0,255)])
    for _,v in tqdm(coco_res.imgToAnns.items()):
        total_box_sum += len(v)
        max_box_per_im = len(v) if len(v) > max_box_per_im else max_box_per_im
        im_name = id2im[v[0]['image_id']]
        im = cv2.imread(os.path.join(im_base_dir, im_name))
        for i in range(len(v)):
            if 'score' not in v[i].keys():
                v[i]['score'] = 1 
            if v[i]['score'] > 0.3:
                x1 = int(v[i]['bbox'][0])
                y1 = int(v[i]['bbox'][1])
                x2 = int(v[i]['bbox'][2]) + x1
                y2 = int(v[i]['bbox'][3]) + y1
                c_id = v[i]['category_id']
                cv2.rectangle(im, (x1,y1), (x2, y2),colorlist[c_id], 1)
                cv2.putText(im, f"{id2cat[c_id]} {v[i]['score']:.2f}", (x1,y1+15), cv2.FONT_HERSHEY_COMPLEX_SMALL,1,colorlist[c_id])
        cv2.imshow("", im)
        cv2.waitKey()
    print(f"max box num in one image: {max_box_per_im}")
    print(f"avg box num in one image: {float(total_box_sum)/float(len(coco_res.imgToAnns.items())):.2f}")

annFile =     "/home/cary/git/data/cleaner_od/coco/annotations/instances_train2017.json"
im_base_dir = "/home/cary/git/data/cleaner_od/coco/images/train2017"
cocoGt = COCO(annFile)
load_coco(cocoGt, im_base_dir)