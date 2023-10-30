import os
import cv2
import shutil
import argparse
import os.path as osp
from tqdm import tqdm

def voc_main2csv(voc_path):
    img_path = osp.join(voc_path, "JPEGImages")
    voc_path = osp.join(voc_path, "ImageSets", "Main")
    class_files = os.listdir(voc_path)
    
    #
    
    
    if "default.txt" in class_files:
        class_files.remove("default.txt")
    image_files = os.listdir(img_path)
    image_suffix = image_files[0].split(".")[-1]

    image_names = list()
    result_dict = dict()
    img_class_list = list()
    
    #negative sample
    if len(class_files) == 0:
        for n in os.listdir(img_path):
            image_names.append(n)
            img_class_list.append([n[:n.rfind(".")] + ".jpeg", -1])
        return image_names,img_class_list

    for class_f in class_files:
        class_name = class_f.split("_")[0]
        f = open(osp.join(voc_path, class_f))
        tmp_res = list()
        lines = f.readlines()
        for l in lines:
            if (len(image_names) < len(lines)):
                image_names.append(l[:l.rfind(" ")].strip() + "." + image_suffix)
            image_label = int(l.split(" ")[-1])
            assert (image_label == 1 or image_label == -1)
            tmp_res.append(image_label)
        result_dict[class_name] = tmp_res


    for i, n in enumerate(image_names):
        neg_sample = True
        for class_name, res_list in result_dict.items():
            if (res_list[i] == 1):
                neg_sample = False
                img_class_list.append([n[:n.rfind(".")] + ".jpeg", class_name])
        if neg_sample:
            img_class_list.append([n[:n.rfind(".")] + ".jpeg", -1])
    return image_names, img_class_list

def merge_fake_box_set(merge_path, out_path):
    if out_path:
        new_set_path = out_path
    else:
        new_set_path = osp.join(osp.dirname(merge_path), "merged_dataset")
    new_set_img_path = osp.join(new_set_path, "images")
    for p in [new_set_path, new_set_img_path]:
        if not osp.exists(p):
            os.makedirs(p)

    csv_f = open(osp.join(new_set_path, "labels.csv"), "w")

    total_img_class_list = list()
    total_img_count = 0

    for im_set in os.listdir(merge_path):
        img_names, img_class_list = voc_main2csv(osp.join(merge_path, im_set),)
        total_img_class_list.extend(img_class_list)
        total_img_count += len(img_names)
        for n in tqdm(img_names):
            #assert(len(n.split("."))==2)
            im_suffix = n.split(".")[-1]
            if im_suffix == "jpeg":
                if not osp.exists(osp.join(new_set_img_path, n)):
                    shutil.copy(osp.join(merge_path, im_set,"JPEGImages", n), new_set_img_path)
            elif im_suffix == "png" or im_suffix == "jpg":
                new_im_name = n[:n.rfind(".")] + ".jpeg"
                if not osp.exists(osp.join(new_set_img_path, new_im_name)):
                    im_mat = cv2.imread(osp.join(merge_path, im_set,"JPEGImages", n))
                    cv2.imwrite(osp.join(new_set_img_path,new_im_name), im_mat)
            

    print(f"total image number: {total_img_count}, total label number: {len(total_img_class_list)}")
    assert (total_img_count == len(os.listdir(new_set_img_path)))

    for l in total_img_class_list:
        if l[1] != -1:
            line = l[0] + ",0,0,50,50," + l[1] + "\n"
        else:
            line = l[0] + ",,,,,\n"
        csv_f.write(line)
    csv_f.close()

    room_count = dict()
    for l in total_img_class_list:
        if l[1] in room_count.keys():
            room_count[l[1]] += 1
        else:
            room_count[l[1]] = 1
    print(room_count)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=str, nargs='?', help="path that includes several VOC datasets")
    parser.add_argument("-o", "--out", type=str, help="output directory path")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    merge_fake_box_set(args.path, args.out)