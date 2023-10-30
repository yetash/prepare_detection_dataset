import os
import sys
import shutil
import os.path as osp

if __name__=="__main__":
    ds = []
    base_dir = "/home/cary/git/data/scene_job/scene_training/dataset"
    files = os.listdir(base_dir)
    for f in files:
        if osp.isdir(osp.join(base_dir,f)):
            ds.append(f)
    ds_num = len(ds)
    total_images = []
    total_without_task = []
    for i in range(ds_num):
        imgs = os.listdir(osp.join(base_dir, ds[i], "JPEGImages"))
        total_images.extend(imgs)
        for im in imgs:
            #remove taks prefix
            if "__" in im:
                total_without_task.append(im.split("__")[1])
            else:
                total_without_task.append(im)

    dup_file = set([n for n in total_without_task if total_without_task.count(n) > 1])

    ori_file = []
    for df in dup_file:
        for im in total_images:
            if df in im:
                ori_file.append(im)
    if (len(ori_file)==0):
        print("no duplicate file")
        sys.exit()
    if not os.path.exists("dup_files"):
        os.mkdir("dup_files")
    for i in range(ds_num):
        imgs = os.listdir(osp.join(base_dir, ds[i], "JPEGImages"))
        imgs = sorted(imgs)
        for of in ori_file:
            if of in imgs:
                shutil.copy(osp.join(base_dir, ds[i], "JPEGImages",of), "dup_files")
                print(ds[i], of, imgs.index(of))

