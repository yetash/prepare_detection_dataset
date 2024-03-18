import os
import cv2
import shutil
import os.path as osp
import pandas as pd
from tqdm import tqdm


def find_key_word(path):
    index = path.find("SL_")
    if index != -1:
        return index
    index = path.find("StereoVision_")
    if index != -1:
        return index
    return index
    
def compare_im(im1_path, im2_path):
    index1 = find_key_word(im1_path)
    index2 = find_key_word(im2_path)
    if(index1 == -1 or index2 == -1):
        if im1_path in im2_path or im2_path in im1_path:
            return True
        return False
    if(osp.splitext(im1_path[index1:])[0] != osp.splitext(im2_path[index2:])[0]):
        return False    
    return True

def img_filter(dir,out_f):
    of = open(out_f,"w")
    files = os.listdir(dir)
    files_num = len(files)
    for i in tqdm(range(0,files_num)):
        for j in (range(i+1,files_num)):
            if compare_im(files[i],files[j]):
                of.write(files[i]+","+files[j]+"\n")
    return

def img_compare_filter(dir1,dir2,out_f):
    of = open(out_f,"w")
    files1 = os.listdir(dir1)
    files2 = os.listdir(dir2)
    for f1 in tqdm(files1):
        for f2 in (files2):
            if compare_im(f1,f2):   
                of.write(f1+","+f2+"\n")
                # im1_mat = cv2.imread(im1_path)
                # im2_mat = cv2.imread(im2_path)
                # cv2.imshow(im1_path, im1_mat)
                # cv2.imshow(im2_path, im2_mat)
                # cv2.waitKey()
    of.close()
    
def get_cvat_task_name(path):
    index = path.find("task#")
    return (path[index:].split("_")[0])
    
if __name__=="__main__":
    # dir1="/home/cary/ws/data/cleaner_od/wire_seg/patch4/merged_dataset/VOCdevkit/VOC2007/JPEGImages"
    # dir2="/home/cary/ws/data/cleaner_od/wire_seg/test_patch1/merged_dataset/VOCdevkit/VOC2007/JPEGImages"
    # dir3="/home/cary/Downloads/task#1433_wire task-2024_01_23_05_43_16-coco 1.0/images/val"
    # #img_filter(dir2, get_cvat_task_name(dir2)+"_duplicate.txt")
    # img_compare_filter(dir2,dir3, get_cvat_task_name(dir1) + "_" +get_cvat_task_name(dir3) + "_compare.txt")
    
    coco_dir = "/home/cary/Downloads/task_wire_patch4-2024_02_23_02_06_36-cvat for images 1.1"
    origin_img_dir = "/home/cary/share/copy_by_task"
    table = pd.ExcelFile("/home/cary/ws/data/cleaner_od/wire_seg/附件4_CVAT需维护数据.xlsx")
    sheet0 = table.parse(sheet_name=0)
    # selected_wire_patch = ["patch0","patch1","patch2","patch3"]
    # task_list=[]
    # for i in range(len(sheet0["wire_patch"])):
    #     for swp in selected_wire_patch:
    #         if sheet0["wire_patch"][i]==swp:
    #             task_list.append(sheet0["task_id"][i][4:])
    task_list=os.listdir(origin_img_dir)
    images_no_black_path= osp.join(coco_dir,"img_no_black")
    if not osp.exists(images_no_black_path):
        os.mkdir(images_no_black_path)
    for im_name in tqdm(os.listdir(osp.join(coco_dir,"images"))):
        im_name_tmp = im_name
        # im_name = im_name[(im_name.find("__")+2):]
        find_image=False
        for task_id in task_list:
            origin_im_dir_path = osp.join(origin_img_dir, task_id)
            for origin_im_name in os.listdir(origin_im_dir_path):
                if origin_im_name==im_name:
                    find_image=True
                    shutil.copy(osp.join(origin_im_dir_path, origin_im_name), osp.join(images_no_black_path, im_name_tmp))
                    break
            if find_image:
                break
        assert(find_image==True)
    