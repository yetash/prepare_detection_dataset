import cv2
import numpy as np
import os.path as osp

pd_exterio_ratio = 0.3
showim = False
showclass = "diningRoom"
base_path = "/home/cary/git/data/scene_job/coco/val2017"

class SceneBox:
    def __init__(self, room, roomid, box):
        self.room = room
        self.roomid = roomid
        self.x1 = box[0]
        self.y1 = box[1]
        self.x2 = box[2]
        self.y2 = box[3]
        self.score = box[4]
        colorlist = [(255, 255, 255), (255, 0, 0), (0, 255, 0),
                     (0, 0, 255), (130, 130, 0), (130, 0, 130)]
        self.color = colorlist[self.roomid % 6]


def show_box_in_image(im, box: SceneBox):
    font = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = 0.5
    if (box.score > 0.1):
        text = "{:.2f} {}".format(box.score, box.room)
        cv2.putText(im, text, (int(box.x2) - 200, int(box.y2)),
                    font, fontScale, box.color, 2)
        cv2.rectangle(im, (int(box.x1), int(box.y1)),
                      (int(box.x2), int(box.y2)), box.color, 1)

def voc_ap(rec, prec, use_07_metric=False):
    """Compute VOC AP given precision and recall. If use_07_metric is true, uses
    the VOC 07 11-point method (default:False).
    """
    if use_07_metric:
        # 11 point metric
        ap = 0.
        for t in np.arange(0., 1.1, 0.1):
            if np.sum(rec >= t) == 0:
                p = 0
            else:
                p = np.max(prec[rec >= t])
            ap = ap + p / 11.
    else:
        # correct AP calculation
        # first append sentinel values at the end
        mrec = np.concatenate(([0.], rec, [1.]))
        mpre = np.concatenate(([0.], prec, [0.]))

        # compute the precision envelope
        for i in range(mpre.size - 1, 0, -1):
            mpre[i - 1] = np.maximum(mpre[i - 1], mpre[i])

        # to calculate area under PR curve, look for points
        # where X axis (recall) changes value
        i = np.where(mrec[1:] != mrec[:-1])[0]

        # and sum (\Delta recall) * prec
        ap = np.sum((mrec[i + 1] - mrec[i]) * mpre[i + 1])
    return ap

def voc_eval(gt_res, pd_res, class_name, t_cnt, ovthresh=0.5, img_names=dict()):
  class_recs = gt_res
  npos       = t_cnt
  image_ids  = pd_res["image_ids"]
  confidence = np.array(pd_res["confidence"])  
  BB = np.array(pd_res["BB"])
  # sort by confidence
  sorted_ind = np.argsort(-confidence)
  BB = BB[sorted_ind, :]
  image_ids = [image_ids[x] for x in sorted_ind]
  # go down dets and mark TPs and FPs
  nd = len(image_ids)
  tp = np.zeros(nd)
  fp = np.zeros(nd)
  for d in range(nd):
    R = class_recs[image_ids[d]]
    bb = BB[d, :].astype(float)
    ovmax = -np.inf
    BBGT = np.array(R['bbox']).astype(float)
    if (showim and showclass == class_name) and len(img_names) > 0:
      im_mat = cv2.imread(osp.join(base_path,img_names[image_ids[d]]['file_name']))
      if BBGT.size > 0:
        #convert [x,y,w,h] to [x0,y0,x1,y1]
        BBGT[:,2] += BBGT[:,0]
        BBGT[:,3] += BBGT[:,1]
        show_box = BBGT[0].tolist()
        show_box.append(1)
        show_box_in_image(im_mat, SceneBox("gt",0, show_box))
        #print(f"gt box {show_box}")
      show_box = BB[d].tolist()
      show_box.append(confidence[sorted_ind[d]])
      show_box_in_image(im_mat, SceneBox(class_name,1,show_box))
      if(BBGT.size > 0 or len(show_box)==4):
          cv2.imshow("",im_mat)
          cv2.waitKey()
    if BBGT.size > 0:
      #convert [x,y,w,h] to [x0,y0,x1,y1]
      BBGT[:,2] += BBGT[:,0]
      BBGT[:,3] += BBGT[:,1]
      # compute overlaps
      # intersection
      ixmin = np.maximum(BBGT[:, 0], bb[0])
      iymin = np.maximum(BBGT[:, 1], bb[1])
      ixmax = np.minimum(BBGT[:, 2], bb[2])
      iymax = np.minimum(BBGT[:, 3], bb[3])
      iw = np.maximum(ixmax - ixmin + 1., 0.)
      ih = np.maximum(iymax - iymin + 1., 0.)
      inters = iw * ih
      # union
      uni = (((bb[2] - bb[0] + 1.) * (bb[3] - bb[1] + 1.) - inters) * pd_exterio_ratio +
             (BBGT[:, 2] - BBGT[:, 0] + 1.) * (BBGT[:, 3] - BBGT[:, 1] + 1.))
      overlaps = inters / uni
      ovmax = np.max(overlaps)
    if ovmax > ovthresh:
      if not R['det']:
          R['det'] = True
          tp[d] = 1.
      else:
          fp[d] = 1.
    else:
      fp[d] = 1.
  # compute precision recall
  fp = np.cumsum(fp)
  tp = np.cumsum(tp)
  rec = tp / float(npos)
  # avoid divide by zero in case the first detection matches a difficult
  # ground truth
  prec = tp / np.maximum(tp + fp, np.finfo(np.float64).eps)
  ap = voc_ap(rec, prec, False)
  return rec, prec, ap

def sr_eval(cocoGt, cocoDt):
    #evaluate scene recognition result
    if (cocoGt.cats != cocoDt.cats):
      return
    cats = cocoGt.cats
    ap = dict()
    prec = dict()
    rec = dict()
    gt_res = dict()
    pd_res = dict()
    #sort by category
    for _,cats_v in cats.items():
      cat_na = cats_v['name']
      cat_id = cats_v['id']
      t_cnt  = 0
      gt_res[cat_na] = dict()
      # achieve gt boxes 
      for _,gt_v in cocoGt.anns.items():
        im_name = gt_v['image_id']
        #for coco classification  only
        if im_name not in gt_res[cat_na]:
          gt_res[cat_na][im_name] = {
            'bbox':[],
            'det':False
          }
        if(gt_v["category_id"] == cat_id):
          t_cnt += 1
          gt_res[cat_na][im_name]['bbox'].append(gt_v['bbox'])
      # achieve pd boxes
      pd_res[cat_na] = {"image_ids" : [],
                        "confidence" : [],
                        "BB" : []}
      for _,pd_v in cocoDt.anns.items():
        if (pd_v["category_id"] == cat_id):
          pd_res[cat_na]["image_ids"].append(pd_v['image_id'])
          pd_res[cat_na]["confidence"].append(pd_v['score'])
          pd_res[cat_na]["BB"].append(pd_v['bbox'])
      class_rec, class_prec, class_ap = voc_eval(gt_res[cat_na], pd_res[cat_na], cat_na, t_cnt, 0.5, cocoGt.imgs)
      ap[cat_na] = class_ap
      prec[cat_na] = class_prec
      rec[cat_na] = class_rec
    print("AP50")
    mAP50 = []
    for k,v in ap.items():
      mAP50.append(v)
      print(f"{k:<10} : {v*100 :.1f}")
    print(f'mAP50 {sum(mAP50)/len(mAP50)*100:.1f}')