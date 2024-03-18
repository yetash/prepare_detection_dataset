import os
import cv2
import random
import numpy as np
import argparse
from tqdm import tqdm
from xml.etree import ElementTree as ET

room2index = []
colorlist  = []

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", type=str, default="example", help="voc path includes Annotations and JPEGImages")
    parser.add_argument("-s", "--show", action="store_true", default=False, help="show image")
    parser.add_argument("-c", "--show_class", type=str, help="only show specific class")
    parser.add_argument("-b", "--black_box", action="store_true", default=False, help = "draw black box")
    args = parser.parse_args()
    return args

class SceneBox:
    def __init__(self, roomindex, box):
        self.roomindex = roomindex
        self.x1 = box[0]
        self.y1 = box[1]
        self.x2 = box[2]
        self.y2 = box[3]
        if (len(box) == 4):
            self.score = 1.
        else:
            self.score = box[4]
        self.room = room2index[self.roomindex]
        self.color = colorlist[self.roomindex]


def show_box_in_image(im, box: SceneBox):
    font = cv2.FONT_HERSHEY_COMPLEX_SMALL
    fontScale = 0.5
    if (box.score > 0):
        text = "{:.2f} {}".format(box.score, box.room)
        cv2.putText(im, text, (int(float(box.x1)),
                    int(float(box.y1)+10)), font, fontScale, box.color, 1)
        cv2.rectangle(im, (int(float(box.x1)), int(float(box.y1))),
                      (int(float(box.x2)), int(float(box.y2))), box.color, 1)


if __name__ == "__main__":
    args = parse_args()
    show = args.show
    cnt = {}
    anno_cnt = 0

    basepath = args.path
    annopath = os.path.join(basepath, "Annotations")
    jpegpath = os.path.join(basepath, "JPEGImages")
    annofile = os.listdir(annopath)
    #random.shuffle(annofile)
    for i in tqdm(range(len(annofile))):
        anno_cnt+=1
        fpath = os.path.join(annopath, annofile[i])
        tree = ET.parse(fpath)
        root = tree.getroot()
        imgname = str()
        boxlist = list()
        black_box_list = list()
        for child in root:
            if child.tag == 'filename':
                imgname = child.text
            elif child.tag == 'object':
                objname = str()
                rectloc = list()
                for c in child:
                    if c.tag == 'name':
                        objname = c.text
                        find_black_box= True if objname == "black-box" else False
                        # find a new class
                        if objname not in room2index:
                            room2index.append(objname)
                            room2index.sort()
                            cnt[objname] = 0
                            colorlist.append([random.randint(0,255),random.randint(0,255),random.randint(0,255)])
                    elif c.tag == 'bndbox':
                        for xy in c:
                            rectloc.append(xy.text)
                if find_black_box:
                    black_box_list.append(rectloc)
                    find_black_box = False
                box = SceneBox(room2index.index(objname), rectloc)
                boxlist.append(box)
                cnt[box.room] +=1
        if args.black_box and len(black_box_list) > 0:
            immat = cv2.imread(os.path.join(jpegpath, imgname))
            for box in black_box_list:
                x1,y1,x2,y2 = round(float(box[0])),round(float(box[1])),round(float(box[2])),round(float(box[3]))
                area = np.array([[x1,y1],[x2,y1],[x2,y2],[x1,y2]])
                cv2.fillPoly(immat,[area],color=(0,0,0))
            cv2.imwrite(os.path.join(jpegpath,imgname),immat)
        if show:    
            immat = cv2.imread(os.path.join(jpegpath, imgname))
            for b in boxlist:
                show_box_in_image(immat, b)
            cv2.imshow(" ", immat)
            cv2.waitKey()
    print(f"----total-image----: {anno_cnt:>5d}")
    for i,n in cnt.items():
        print(f"{i:-^19s}: {n:>5d}")
