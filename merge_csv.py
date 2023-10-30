import os
import shutil
from tqdm import tqdm
import os.path as osp
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--csv", nargs="+", type=str, help="csv path to be merged")
    parser.add_argument("-i", "--image", nargs="+", type=str, help="img path to be merged")
    parser.add_argument("-o", "--out", type=str, help="merged output path")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    assert(len(args.csv) == len(args.image))
    csv_lines=[]
    merged_csv_path = osp.join(args.out, "labels.csv")
    merged_img_path = osp.join(args.out, "images")
    merged_csv_f = open(merged_csv_path, "w")
    for csv in tqdm(args.csv):
        csv_f = open(csv,"r")
        lines = csv_f.readlines()
        for line in lines:
            merged_csv_f.write(line)
    merged_csv_f.close()
    
    if not osp.exists(merged_img_path):
        os.makedirs(merged_img_path)
    for impath in tqdm(args.image):
        for im in os.listdir(impath):
            shutil.copy(osp.join(impath,im), osp.join(merged_img_path,im))