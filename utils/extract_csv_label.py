import pandas as pd

def class_id(csv_file):
    class2id = {}
    annotations = pd.read_csv(csv_file, header=None).values
    class_names = list(set(annotations[:,-1]))
    class_names = pd.Series(class_names).dropna().tolist()
    class_names.sort()
    for i in range(len(class_names)):
        class2id[class_names[i]] = i
    return class2id
    
if __name__=="__main__":
    csv_file = "/home/cary/git/data/yolov_test/VOCdevkit/VOC2007/labels.csv"
    class_dict = class_id(csv_file)
    text_prompt = ""
    for k,v in class_dict.items():
        text_prompt+=k +"."
    print(text_prompt)