import os
import cv2
import argparse
import os.path as osp
from tqdm import tqdm
import xml.etree.ElementTree as ET


def voc_xml2csv(args):
    voc_path=args.path
    print(f"parsing voc dataset: {voc_path}")
    label_path = osp.join(voc_path, "labels.csv")
    Annot_path = osp.join(voc_path, "Annotations")
    Image_path = osp.join(voc_path, "JPEGImages")
    annots = []
    if len(args.set_file) == 0:    
        annots = os.listdir(Annot_path)
    else:
        sef_f = open(args.set_file, "r")
        for l in sef_f.readlines():
            annots.append(l.replace("\n","") + ".xml")
    

    label_f = open(label_path, "w")
    empty_xml_cnt = 0
    for an in tqdm(annots):
        tree = ET.parse(osp.join(Annot_path, an))
        root = tree.getroot()
        obj_list = list()
        image_name = str()
        for child in root:
            if child.tag == "filename":
                image_name = child.text
                if image_name.split(".")[-1] != args.image_type:
                    immat=cv2.imread(osp.join(Image_path, image_name))
                    image_name = osp.splitext(image_name)[0] + "." + args.image_type
                    cv2.imwrite(osp.join(Image_path, image_name),immat)
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
                            if tmp_dict[0] != args.exclude_class:
                                obj_list.append(tmp_dict)
                            tmp_dict = [0]
        if(len(obj_list)==0):
            obj_list=[["","","","",""]]
            empty_xml_cnt+=1
        
        skip_annot = False
        if(len(args.filter_class)>0):
            skip_annot = True
            for fc in args.filter_class:                
                for ob in obj_list:
                    if fc == ob[0]:
                        skip_annot = False
                        break
                if skip_annot == False:
                    break
        if skip_annot:
            continue
        
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
    parser.add_argument("-p", "--path", type=str, nargs='?', help="VOC path like */VOCdevkit/VOC2007")
    parser.add_argument("--image_type", type=str, default="jpeg", choices=[ "png", "jpeg", "bmp" ], help="format image type")
    parser.add_argument("--filter_class", default="", type=str, nargs='*', help= "only save in filter_class")
    parser.add_argument("--exclude_class", default="", type=str, help= "exclude the class")
    parser.add_argument("--set_file", default="", type=str, help="convert csv file only in set file")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    voc_xml2csv(args)
