import os
import cv2
from xml.etree import ElementTree as ET

room2index = ['background', 'dog', 'person', 'train']


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
        colorlist = [(255, 255, 255), (255, 0, 0), (0, 255, 0),
                     (0, 0, 255), (130, 130, 0), (130, 0, 130)]
        self.room = room2index[self.roomindex]
        self.color = colorlist[self.roomindex % 6]


def show_box_in_image(im, box: SceneBox):
    font = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = 0.5
    if (box.score > 0):
        text = "{:.2f} {}".format(box.score, box.room)
        cv2.putText(im, text, (int(float(box.x2) - 200),
                    int(float(box.y2))), font, fontScale, box.color, 2)
        cv2.rectangle(im, (int(float(box.x1)), int(float(box.y1))),
                      (int(float(box.x2)), int(float(box.y2))), box.color, 1)


if __name__ == "__main__":
    basepath = os.path.join("VOCdevkit", "VOC2007")
    annopath = os.path.join(basepath, "Annotations")
    jpegpath = os.path.join(basepath, "JPEGImages")
    annofile = os.listdir(annopath)
    for i in range(len(annofile)):
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
                        if objname not in room2index:
                            room2index.append(objname)
                    elif c.tag == 'bndbox':
                        for xy in c:
                            rectloc.append(xy.text)
                box = SceneBox(room2index.index(objname), rectloc)
                boxlist.append(box)
        immat = cv2.imread(os.path.join(jpegpath, imgname))
        for b in boxlist:
            show_box_in_image(immat, b)
        cv2.imshow(" ", immat)
        cv2.waitKey()
