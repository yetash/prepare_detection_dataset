import os
import argparse
import os.path as osp
import xml.etree.ElementTree as ET


def voc_xml2csv(voc_path):
    print(f"parsing voc dataset: {voc_path}")
    label_path = osp.join(voc_path, "labels.csv")
    Annot_path = osp.join(voc_path, "Annotations")
    annots = os.listdir(Annot_path)

    label_f = open(label_path, "w")
    empty_xml_cnt = 0
    for an in annots:
        tree = ET.parse(osp.join(Annot_path, an))
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
                        if (len(tmp_dict) == 5):
                            obj_list.append(tmp_dict)
                            tmp_dict = [0]
        if(len(obj_list)==0):
            obj_list=[["","","","",""]]
            empty_xml_cnt+=1
        for ob in obj_list:
            line = image_name
            for i in range(1, len(ob)):
                line += "," + ob[i]
            line += "," + ob[0]
            line += "\n"
            label_f.write(line)
    label_f.close()
    print("total xml:",len(annots), "\nempty xml:", empty_xml_cnt, "\nvalid xml:", len(annots) - empty_xml_cnt)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=str, nargs='?', help="VOC path like */VOCdevkit/VOC2007")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    voc_xml2csv(args.path)
