import os
import cv2
from tqdm import tqdm
from xml.etree import ElementTree as ET

#room2index = ['background', 'dog', 'person', 'train']
room2index = ['background', 'bedRoom', 'diningRoom', 'kitchen', 'livingRoom','restroom']


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
    cnt = {
        "bedRoom": 0,
        "diningRoom": 0,
        "kitchen": 0,
        "livingRoom": 0,
        "restroom": 0        
    }
    anno_cnt = 0
    set_path = "/home/ly/ws/data/robot_scene_recognition/scene_detection_job/test_set/fill_light_test"
    basepath = os.path.join(set_path, "VOCdevkit", "VOC2007")
    annopath = os.path.join(basepath, "Annotations")
    jpegpath = os.path.join(basepath, "JPEGImages")
    annofile = os.listdir(annopath)
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
                        if objname not in room2index:
                            room2index.append(objname)
                    elif c.tag == 'bndbox':
                        for xy in c:
                            rectloc.append(xy.text)
                box = SceneBox(room2index.index(objname), rectloc)
                boxlist.append(box)
        immat = cv2.imread(os.path.join(jpegpath, imgname))
        show = False
        for b in boxlist:
            show_box_in_image(immat, b)
            cnt[b.room] +=1
            if show:
                if(b.room == "diningRoom"):
                    print(b.x1,b.y1,b.x2,b.y2)
                    cv2.imshow(" ", immat)
                    cv2.waitKey()
    print(f"----total-image----: {anno_cnt:0>5d}")
    for i,n in cnt.items():
        print(f"{i:-^19s}: {n:0>5d}")
