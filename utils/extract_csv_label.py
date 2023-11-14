import pandas as pd
import numpy as np
import os

def class_id(csv_file):
    class2id = {}
    annotations = pd.read_csv(csv_file, header=None).values
    class_names = list(set(annotations[:,-1]))
    class_names = pd.Series(class_names).dropna().tolist()
    class_names.sort()
    for i in range(len(class_names)):
        class2id[class_names[i]] = i
    return class2id

def parse_class_id(file_path):
    f = open(file_path, "r")
    classname_to_id = dict()
    count = 1
    for line in f.readlines():
        classname_to_id[line.strip()] = count
        count += 1
    return classname_to_id


def parse_csv(csv_file, class_id_file):
    if class_id_file:
        classname_to_id = parse_class_id(class_id_file)
    else:       
        classname_to_id = class_id(csv_file)
        for k in classname_to_id.keys():
            classname_to_id[k] += 1
    # parse csv
    classname_cnt = {}
    for k,v in classname_to_id.items():
        classname_cnt[k] = 0
    total_csv_annotations = {}
    annotations = pd.read_csv(csv_file, header=None).values
    for annotation in annotations:
        key = annotation[0].split(os.sep)[-1]
        value = np.array([annotation[1:]])
        class_label = value[0,-1]
        # exclude undesigned labels and keep negative samples
        if class_label not in classname_to_id.keys() and isinstance(class_label,str):
            continue
        
        # count class label number
        if class_label not in classname_cnt.keys():
            classname_cnt[class_label] = 0
        classname_cnt[class_label]+=1
        
        if key in total_csv_annotations.keys():
            total_csv_annotations[key] = np.concatenate(
                (total_csv_annotations[key], value), axis=0)
        else:
            total_csv_annotations[key] = value
    print("-------class label count---------")
    for k,v in classname_cnt.items():
        print(f"{str(k): ^25s} : {v}")
    return total_csv_annotations, classname_to_id


if __name__=="__main__":
    csv_file = "example/labels.csv"
    class_dict = class_id(csv_file)
    text_prompt = ""
    for k,v in class_dict.items():
        text_prompt+=k +"."
    print(text_prompt)