import os
import cv2
import random
from tqdm import tqdm
from xml.etree import ElementTree as ET

room2index = []
colorlist  = []

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
    show = False
    cnt = {}
    anno_cnt = 0
    set_path = "example"
    basepath = os.path.join(set_path, "VOCdevkit", "VOC2007")
    annopath = os.path.join(basepath, "Annotations")
    jpegpath = os.path.join(basepath, "JPEGImages")
    annofile = os.listdir(annopath)
    random.shuffle(annofile)
    for i in tqdm(range(len(annofile))):
        anno_cnt+=1
        fpath = os.path.join(annopath, annofile[i])
        tree = ET.parse(fpath)
        root = tree.getroot()
        imgname = str()
        boxlist = list()
        for child in root:
            if child.tag == 'filename':
                imgname = child.text
            elif child.tag == 'object':
                objname = str()
                rectloc = list()
                for c in child:
                    if c.tag == 'name':
                        objname = c.text
                        # find a new class
                        if objname not in room2index:
                            room2index.append(objname)
                            room2index.sort()
                            cnt[objname] = 0
                            colorlist.append([random.randint(0,255),random.randint(0,255),random.randint(0,255)])
                    elif c.tag == 'bndbox':
                        for xy in c:
                            rectloc.append(xy.text)
                box = SceneBox(room2index.index(objname), rectloc)
                boxlist.append(box)
        immat = cv2.imread(os.path.join(jpegpath, imgname))
        for b in boxlist:
            show_box_in_image(immat, b)
            cnt[b.room] +=1
            if show:
                    cv2.imshow(" ", immat)
                    cv2.waitKey()
    print(f"----total-image----: {anno_cnt:>5d}")
    for i,n in cnt.items():
        print(f"{i:-^19s}: {n:>5d}")
