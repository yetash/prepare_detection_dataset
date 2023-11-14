import os
import cv2
import shutil
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--type", default="train", choices=[ "train", "test", "trainval" ], help="dataset type: train, test or trainval")
    parser.add_argument("-d", "--basedir", default="example", help="base directory which includes images and labels.csv")
    parser.add_argument("-r", "--ratio", type=float, default=0.2, help="trainval split ratio [0,1]")
    parser.add_argument("-c", "--class_id", type=str, default="", help="fixed mapping between class id and names")
    parser.add_argument("-a", "--annot_only", action="store_true", default=False, help="create annotation only")
    args = parser.parse_args()
    return args

#copy images and change suffix into jpeg
def copy_image(image_src_path, image_dst_path, filename, file_format = ""):
    suffix = os.path.splitext(filename)[1][1:]
    new_suffix = file_format if len(file_format) > 0 else suffix
    
    image_new_path = os.path.join(image_dst_path, os.path.splitext(filename)[0] + "." + new_suffix)
    if os.path.exists(image_new_path):
        return
    
    if suffix==new_suffix:
        shutil.copy(os.path.join(image_src_path, filename), image_dst_path)
    else:
        im_mat = cv2.imread(os.path.join(image_src_path, filename))        
        cv2.imwrite(image_new_path, im_mat)