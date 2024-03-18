import os
from tqdm import tqdm
import shutil
import numpy as np
import os.path as osp

path = "/home/cary/git/data/cleaner_od/train_data/JPEGImages"
files = os.listdir(path)
split_num = 4
str_split_idx = path.rfind("/")
base_dir = path[:str_split_idx]
folder_name = path[str_split_idx+1:]
file_split_nums = np.linspace(0, len(files), num=split_num+1)

for i in tqdm(range(split_num)):
    new_folder_path = osp.join(base_dir, folder_name + "_" + str(i))
    if not os.path.exists(new_folder_path):
        os.mkdir(new_folder_path)
    for j in range(int(file_split_nums[i]), int(file_split_nums[i+1])):
        if not osp.exists(osp.join(new_folder_path, files[j])):
            shutil.copy(osp.join(path,files[j]),new_folder_path)