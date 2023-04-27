import numpy as np
from pycocotools.coco import COCO
from pycocotools.cocoeval import COCOeval

# Load gt
annFile = '/home/cary/git/data/yolov_test/VOCdevkit/VOC2007/coco/annotations/voc_2007_trainval.json'
cocoGt = COCO(annFile)
resFile = "output.json"
cocoDt = cocoGt.loadRes(resFile)
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