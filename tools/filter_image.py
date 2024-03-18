import os
import shutil
from glob import glob
import os.path as osp




if __name__=="__main__":
    im_path = "/home/cary/ws/buzz/mlengine/debug/scene/211821_Coral-开发测试-刘岩-地图问题-B1.2-01222200-快速建图3-房间识别问题/211821筛选/玄关"
    new_im_path = im_path + "_filtered"
    if not osp.exists(new_im_path):
       os.mkdir(new_im_path)
    imgs = glob(im_path + "/*/*",recursive=True)
    filtered_imgs=[]
    for im in imgs:
        if "IRN" in im or "Carpet" in im or "floor" in im or "other" in im or "IRAction" in im:
            continue
        shutil.copy(im,new_im_path)
        print(im)