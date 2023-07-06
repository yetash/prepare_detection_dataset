import json
import pickle
import cv2
import random
from tqdm import tqdm
from pycocotools.coco import COCO
from utils.class_map_parser import get_class_dict
showim = True
im_base_dir = "/home/cary/git/data/yolov_test/VOCdevkit/VOC2007/images/"
annFile = '/home/cary/git/data/yolov_test/VOCdevkit/VOC2007/coco/annotations/voc_2007_trainval.json'
cocoGt = COCO(annFile)

im2id = {}
cat2id = {}
for k,v in cocoGt.imgs.items():
    im2id[v['file_name']] = v['id']
for k,v in cocoGt.cats.items():
    cat2id[v['name']] = v['id']

colorlist = []
for i in range(len(cat2id)):
    colorlist.append([random.randint(0,255),random.randint(0,255),random.randint(0,255)])

f = open("data/tmp_result.pickle","rb")
res = pickle.load(f)
annotations = []
for k,v in tqdm(res.items()):
    if k not in im2id.keys():
        continue
    im_id = im2id[k]
    boxes = v[0]
    confi = v[1]
    label = v[2]
    im = cv2.imread(im_base_dir+k)
    for i in range(len(label)):
        class_dict = get_class_dict()
        if label[i] not in class_dict.keys():
            label[i] = label[i].split(" ")[0]
        if label[i] not in class_dict.keys():
            for k,v in class_dict.items():
                if k.find(label[i])!=-1:
                    label[i] = k
                    break
        label[i] = class_dict[label[i]]
        
        label_id = -1
        if label[i] in cat2id.keys():
            label_id = cat2id[label[i]]
        else:
            print(label[i])
            continue
        annotations.append({'image_id': im_id, 'category_id': label_id, 'bbox': [boxes[i][0], boxes[i][1], boxes[i][2]- boxes[i][0], boxes[i][3] - boxes[i][1]], 'score': confi[i].item()})
        x1 = int(boxes[i][0])
        y1 = int(boxes[i][1])
        x2 = int(boxes[i][2])
        y2 = int(boxes[i][3])
        cv2.rectangle(im, (x1,y1), (x2, y2),colorlist[label_id-1], 1)
        cv2.putText(im, label[i], (x1,y1+15), cv2.FONT_HERSHEY_COMPLEX_SMALL,1,colorlist[label_id-1])
    if showim:
        cv2.imshow("", im)
        cv2.waitKey()
with open("data/output.json", "w") as f:
    json.dump(annotations,f)