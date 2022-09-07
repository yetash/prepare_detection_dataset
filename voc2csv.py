import os
import os.path as osp
import xml.etree.ElementTree as ET

def voc2csv(voc_path):
    label_path = osp.join(voc_path,"labels.csv")
    Annot_path = osp.join(voc_path,"Annotations")
    annots = os.listdir(Annot_path)
       
    label_f = open(label_path, "w")
    for an in annots:
        tree = ET.parse(osp.join(Annot_path,an))
        root = tree.getroot() 
        obj_list = list()
        image_name = str()
        for child in root:
            if child.tag == "filename":
                image_name = child.text
            if child.tag == 'object':
                tmp_dict = [0]
                for obj in child:
                    if obj.tag == 'name':
                        tmp_dict[0] = obj.text
                    if obj.tag == 'bndbox':
                        if tmp_dict[0] == 0:
                            print("error: box without type")
                        for xy in obj:
                            tmp_dict.append(xy.text)
                        if(len(tmp_dict) == 5):
                            obj_list.append(tmp_dict)
                            tmp_dict = [0]
        for ob in obj_list:
            line = image_name
            for i in range(1,len(ob)):
                line += ","+ ob[i]
            line += "," + ob[0]
            line += "\n"
            label_f.write(line)
    label_f.close()
    
if __name__ == "__main__":
    voc_path = "/home/ly/ws/rr/rpha/data/dataset/scene_recognition/daylight_test/VOCdevkit/VOC2007"
    voc2csv(voc_path)