import os
from tqdm import tqdm
import shutil
import os.path as osp
import xml.etree.ElementTree as ET

def voc_xml2csv(voc_path):
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

def voc_main2csv(voc_path):
    voc_path = osp.join(voc_path, "ImageSets", "Main")
    class_files = os.listdir(voc_path)
    class_files.remove("default.txt")
    
    image_names = list()
    result_dict = dict()
    
    for class_f in class_files:
        class_name = class_f.split("_")[0]
        f = open(osp.join(voc_path, class_f))
        tmp_res = list()
        lines = f.readlines()
        for l in lines:
            l_split = l.split(" ")
            if(len(image_names) < len(lines)):
                image_names.append(l_split[0] + ".jpeg") 
            image_label = int(l_split[-1])
            assert(image_label==1 or image_label==-1)
            tmp_res.append(image_label)
        result_dict[class_name] = tmp_res

    img_class_list = list()
    for i, n in enumerate(image_names):
        for class_name, res_list in result_dict.items():
            if(res_list[i] == 1):
                img_class_list.append([n,class_name])
    return image_names, img_class_list
    
if __name__ == "__main__":
    merge_path = "/home/ly/ws/data/robot_scene_recognition/scene_detection_job/merge"
    new_set_path = osp.join(osp.dirname(merge_path), "merge_data_set")
    new_set_img_path = osp.join(new_set_path,"images")
    csv_f = open(osp.join(new_set_path,"labels.csv"),"w")
    
    for p in [new_set_path, new_set_img_path]:
        if not osp.exists(p):
            os.makedirs(p)
    total_img_class_list = list()
    total_img_count = 0
    
    for im_set in os.listdir(merge_path):
        img_names, img_class_list = voc_main2csv(osp.join(merge_path,im_set))
        total_img_class_list.extend(img_class_list)
        total_img_count += len(img_names)
        for n in tqdm(img_names):
            if not osp.exists(osp.join(new_set_img_path,n)):
                n_path = osp.join(merge_path,im_set,"JPEGImages",n)
                shutil.copy(n_path,new_set_img_path)
    
    print(f"total image number: {total_img_count}, total label number: {len(total_img_class_list)}")
    assert(total_img_count == len(os.listdir(new_set_img_path)))
    
    for l in total_img_class_list:
        line = l[0] + ",0,0,50,50," + l[1] +"\n"
        csv_f.write(line)
    csv_f.close()
    
    room_count = dict()
    for l in total_img_class_list:
        if l[1] in room_count.keys():
            room_count[l[1]] += 1
        else:
            room_count[l[1]] = 1
    print(room_count)    