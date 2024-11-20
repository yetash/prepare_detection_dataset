import os
import cv2
import random
import argparse
import numpy as np
from pycocotools.coco import COCO
from tqdm import tqdm


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", type=str, default="example", help="coco path includes annotations and images")
    parser.add_argument("-s", "--show", action="store_true", default=False, help="show image")
    parser.add_argument("-c", "--show_class", type=str, help="only show specific class")
    args = parser.parse_args()
    return args

def load_coco(coco_res, im_base_dir, show_im=False, show_class=None):
    annot_ims = []
    max_box_per_im = 0
    total_box_sum = 0
    id2im={}
    id2cat={}
    id2sum={}
    for _,v in coco_res.imgs.items():
        id2im[v['id']] = v['file_name']
    for _,v in coco_res.cats.items():
        id2cat[v['id']] = v['name']
        id2sum[v['id']] = 0
    colorlist = []
    for i in range(len(id2cat) + 1):
        colorlist.append([random.randint(0,255),random.randint(0,255),random.randint(0,255)])
    for _,v in tqdm(coco_res.imgToAnns.items()):
        total_box_sum += len(v)
        max_box_per_im = len(v) if len(v) > max_box_per_im else max_box_per_im
        im_name = id2im[v[0]['image_id']]
        annot_ims.append(im_name)
        for i in range(len(v)):
            id2sum[v[i]['category_id']] += 1
        if show_class != None:
            show_im = False
            for i in range(len(v)):
                if show_class == id2cat[v[i]['category_id']]:
                    show_im = True
                    break
        if show_im:
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
    print(f"total image number: {len(id2im)}")
    print(f"max box num in one image: {max_box_per_im}")
    print(f"avg box num in one image: {float(total_box_sum)/float(len(coco_res.imgToAnns.items())):.2f}")
    for _,v in coco_res.cats.items():
        print(f"{id2cat[v['id']]: ^25s} : {id2sum[v['id']]}")
    
    json_f = open("rio_coral_coco_class_texts.json","w")
    json_line = "["
    coral_class_line = "("
    coral_palette_line = "["
    count=1
    for _,v in coco_res.cats.items():
        if count%5 == 0:
            coral_class_line += "\n"
            coral_palette_line += "\n"
        count+=1
        coral_class_line +="\"" + id2cat[v['id']] + "\","
        json_line += "[\"" + id2cat[v['id']] + "\"],"
        coral_palette_line += "(" + str(random.randint(0,255)) +"," + str(random.randint(0,255)) +","+ str(random.randint(0,255))+"),"
    coral_class_line = coral_class_line[:-1] + "),"
    coral_palette_line = coral_palette_line[:-1] + "]"
    json_line = json_line[:-1] + "]\n"
    json_f.write(json_line)
    json_f.close()
    print(coral_class_line)
    print(coral_palette_line)
    
    if show_class == "neg":
        total_im = os.listdir(im_base_dir)
        empty_annot_ims = set(total_im) - set(annot_ims)
        print(empty_annot_ims)
        for e_im in tqdm(empty_annot_ims):
            im = cv2.imread(os.path.join(im_base_dir, e_im))
            cv2.imshow("", im)
            cv2.waitKey()

if __name__ == "__main__":
    args = parse_args()
    annFiles = os.listdir(os.path.join(args.path, "annotations"))
    for annFile in annFiles:
        im_base_dir = os.path.join(args.path, "images")
        cocoGt = COCO(os.path.join(args.path, "annotations", annFile))
        load_coco(cocoGt, im_base_dir, show_im = args.show, show_class = args.show_class)