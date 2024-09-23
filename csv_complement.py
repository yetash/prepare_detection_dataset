import os
import shutil
from tqdm import tqdm
import os.path as osp
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--csv", nargs=2, type=str, help="csv path (A - B)")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    csv_lines=[]

    complement_csv_path = args.csv[0] + ".complement"
    
    file_name_set_list=[]
    for csv in tqdm(args.csv):
        file_name_set = set()
        csv_f = open(csv,"r")
        lines = csv_f.readlines()
        for line in lines:
            file_name = line.split(",")[0]
            file_name_set.add(file_name)
        file_name_set_list.append(file_name_set)
        csv_f.close()
    file_name_complement_set = file_name_set_list[0] - file_name_set_list[1]
    print("setA file num: ", len(file_name_set_list[0]))
    print("setB file num: ", len(file_name_set_list[1]))
    print("A-B  file num: ", len(file_name_complement_set))
    
    complement_csv_f = open(complement_csv_path, "w")
    csv_f = open(args.csv[0],"r")
    lines = csv_f.readlines()
    for line in lines:
        file_name = line.split(",")[0]
        if file_name not in file_name_complement_set:
            continue
        complement_csv_f.write(line)
    complement_csv_f.close()
    
    
