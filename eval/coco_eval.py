import os.path as osp
import random
import cv2
import numpy as np
from pycocotools.coco import COCO
from pycocotools.cocoeval import COCOeval
from coco2sr_eval import sr_eval

def load_coco(coco_res,im_base_dir):    
    id2im={}
    id2cat={}
    for _,v in coco_res.imgs.items():
        id2im[v['id']] = v['file_name']
    for _,v in coco_res.cats.items():
        id2cat[v['id']] = v['name']
    colorlist = []
    for i in range(len(id2cat) + 1):
        colorlist.append([random.randint(0,255),random.randint(0,255),random.randint(0,255)])
    for _,v in coco_res.imgToAnns.items():
        im_name = id2im[v[0]['image_id']]
        im = cv2.imread(osp.join(im_base_dir,im_name))
        for i in range(len(v)):
            if v[i]['score'] > 0.2:
                x1 = int(v[i]['bbox'][0])
                y1 = int(v[i]['bbox'][1])
                x2 = int(v[i]['bbox'][2]) + x1
                y2 = int(v[i]['bbox'][3]) + y1
                c_id = v[i]['category_id']
                cv2.rectangle(im, (x1,y1), (x2, y2),colorlist[c_id], 1)
                cv2.putText(im, f"{id2cat[c_id]} {v[i]['score']:.2f}", (x1,y1+15), cv2.FONT_HERSHEY_COMPLEX_SMALL,1,colorlist[c_id])
        cv2.imshow("", im)
        cv2.waitKey()

def cocoAP_eval(cocoGt, cocoDt):
    cocoEval = COCOeval(cocoGt, cocoDt, 'bbox')
    
    cocoEval.evaluate()
    cocoEval.accumulate()
    cocoEval.summarize()
    
    # print per class AP
    headers = ["class", "AP50", "mAP"]
    colums = 6
    per_class_ap50s = []
    per_class_maps = []
    precisions = cocoEval.eval["precision"]
    
    class_names = []
    for k,v in cocoDt.cats.items():
        class_names.append(v['name'])
    AP50 = []
    for k in range(len(class_names)):
        precision_50 = precisions[0,:, k, 0, -1]
        precision_50 = precision_50[precision_50 > -1]
        if not precision_50.size:
            print("no precision", class_names[k])
            continue
        ap50 = np.mean(precision_50) if precision_50.size else float("nan")
        per_class_ap50s.append(float(ap50 * 100))
        AP50.append((class_names[k],ap50))
        
        per_class_ap50s.append(float(ap50 * 100))
        precision = precisions[:, :, k, 0, -1]
        precision = precision[precision > -1]
        ap = np.mean(precision) if precision.size else float("nan")
        per_class_maps.append(float(ap * 100))
    
    AP50 = sorted(AP50, key=lambda name_prec: name_prec[1], reverse=True)
    for a5 in AP50:
        print(f"{a5[0]: ^19s}: {a5[1]*100:.2f}")

if __name__ == "__main__":
    #Load gt
    im_base_dir = "/home/cary/git/data/scene_job/coco/val2017"
    annFile     = "/home/cary/git/data/scene_job/coco/annotations/instance_val2017.json"
    resFile = "/home/cary/rr/prepare_detection_dataset/data/scene_res/wetectron_bbox.json"
    # resFile = "/home/cary/rr/prepare_detection_dataset/data/scene_res/eval/model_0140000/inference/coco_2017_val/bbox.json"

    # im_base_dir = "/home/cary/git/data/indoor_segmentation/coco_indoor/val2017/"
    # annFile     = '/home/cary/git/data/indoor_segmentation/coco_indoor/annotations/instances_val2017.json'
    # resFile = "/home/cary/rr/prepare_detection_dataset/data/indoor_res/eval/model_0140000/inference/coco_2017_val/bbox.json"

    # im_base_dir = "/home/cary/git/data/cleaner_od/coco/images/val2017"
    # annFile     = '/home/cary/git/data/cleaner_od/coco/annotations/instances_val2017.json'
    # resFile = "/home/cary/rr/prepare_detection_dataset/data/robo_res/eval/model_0140000/inference/coco_2017_val/bbox.json"

    cocoGt = COCO(annFile)
    cocoDt = cocoGt.loadRes(resFile)
    load_coco(cocoDt,im_base_dir)
    #sr_eval(cocoGt, cocoDt)
    #cocoAP_eval(cocoGt, cocoDt)