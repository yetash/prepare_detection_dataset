import os
import shutil
import argparse
from glob import glob
import os.path as osp



def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", type=str, default="example", help="image path to be filtered")
    parser.add_argument("-k", "--keyword", type=str, default="", help="filter image with keyword")
    args = parser.parse_args()
    return args

if __name__=="__main__":
    args = parse_args()
    im_path = args.path
    new_im_path = im_path + "_filtered"
    if not osp.exists(new_im_path):
       os.mkdir(new_im_path)
    imgs = glob(osp.join(im_path, "**", "*"), recursive=True)
    for im in imgs:
        if "IRN" in im or "Carpet" in im or "floor" in im or "other" in im or "IRAction" in im or ".fs" in im:
            continue
        if os.path.isdir(im):
            continue
        if len(args.keyword) > 0:
            if args.keyword not in im:
                continue
        ext = im.split(".")[-1]
        if ext not in ["jpeg", "png", "jpg"]:
            print(im)
            continue
        shutil.copy(im,new_im_path)
        #print(im)