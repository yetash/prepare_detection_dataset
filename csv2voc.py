import os
import numpy as np
import codecs
import pandas as pd
import json
from glob import glob
import cv2
import shutil
from sklearn.model_selection import train_test_split
from IPython import embed
from dsconfig import basedir,classname_to_id
#1.标签路径
datasettype = "trainval"#test or trainval
csv_file = os.path.join(basedir,"labels.csv")
image_raw_parh = os.path.join(basedir,"images")

#2.创建要求文件夹
saved_path = os.path.join("VOCdevkit","VOC2007")
image_save_path = os.path.join(saved_path,"JPEGImages")
if not os.path.exists(os.path.join(saved_path,"Annotations")):
    os.makedirs(os.path.join(saved_path,"Annotations"))
if not os.path.exists(image_save_path):
    os.makedirs(image_save_path)
if not os.path.exists(os.path.join(saved_path, "ImageSets","Main")):
    os.makedirs(os.path.join(saved_path, "ImageSets","Main"))
    
#3.获取待处理文件
total_csv_annotations = {}
annotations = pd.read_csv(csv_file,header=None).values
for annotation in annotations:
    key = annotation[0].split(os.sep)[-1]
    value = np.array([annotation[1:]])
    if key in total_csv_annotations.keys():
        total_csv_annotations[key] = np.concatenate((total_csv_annotations[key],value),axis=0)
    else:
        total_csv_annotations[key] = value

label_set = set()
total_files = list()
#4.读取标注信息并写入 xml
for filename,label in total_csv_annotations.items():
    fn = filename.split('.')[0]
    if fn not in total_files:
        total_files.append(fn)
    # move images to voc JPEGImages folder
    shutil.copy(os.path.join(image_raw_parh,filename),image_save_path)
    #embed()
    #print(image_raw_parh)
    height, width, channels = cv2.imread(os.path.join(image_raw_parh,filename)).shape
    #embed()
    with codecs.open(os.path.join(saved_path,"Annotations",filename.split('.')[0] + ".xml"),"w","utf-8") as xml:
        xml.write('<annotation>\n')
        xml.write('\t<folder>' + 'VOC2007' + '</folder>\n')
        xml.write('\t<filename>' + filename + '</filename>\n')
        xml.write('\t<source>\n')
        xml.write('\t\t<database>The VOC2007 Database</database>\n')
        xml.write('\t\t<annotation>PASCAL VOC2007</annotation>\n')
        xml.write('\t\t<image>flickr</image>\n')
        xml.write('\t\t<flickrid>NULL</flickrid>\n')
        xml.write('\t</source>\n')
        xml.write('\t<owner>\n')
        xml.write('\t\t<flickrid>NULL</flickrid>\n')
        xml.write('\t\t<name>Lance</name>\n')
        xml.write('\t</owner>\n')
        xml.write('\t<size>\n')
        xml.write('\t\t<width>'+ str(width) + '</width>\n')
        xml.write('\t\t<height>'+ str(height) + '</height>\n')
        xml.write('\t\t<depth>' + str(channels) + '</depth>\n')
        xml.write('\t</size>\n')
        xml.write('\t\t<segmented>0</segmented>\n')
        if isinstance(label,float):
            ## 空白
            xml.write('</annotation>')
            continue
        for label_detail in label:
            labels = label_detail
            #embed()
            xmin = int(labels[0])
            ymin = int(labels[1])
            xmax = int(labels[2])
            ymax = int(labels[3])
            label_ = labels[-1]
            label_set.add(label_)
            if xmax <= xmin:
                pass
            elif ymax <= ymin:
                pass
            else:
                xml.write('\t<object>\n')
                xml.write('\t\t<name>'+label_+'</name>\n')
                xml.write('\t\t<pose>Unspecified</pose>\n')
                xml.write('\t\t<truncated>1</truncated>\n')
                xml.write('\t\t<difficult>0</difficult>\n')
                xml.write('\t\t<bndbox>\n')
                xml.write('\t\t\t<xmin>' + str(xmin) + '</xmin>\n')
                xml.write('\t\t\t<ymin>' + str(ymin) + '</ymin>\n')
                xml.write('\t\t\t<xmax>' + str(xmax) + '</xmax>\n')
                xml.write('\t\t\t<ymax>' + str(ymax) + '</ymax>\n')
                xml.write('\t\t</bndbox>\n')
                xml.write('\t</object>\n')
                #print(filename,xmin,ymin,xmax,ymax,labels)
        xml.write('</annotation>')

#6.save files in Main
# load total files
txtsavepath = os.path.join(saved_path,"ImageSets","Main")

# split into test train and val
test_files  = list()
train_files = list()
val_files   = list()
trainval_files = list()
if datasettype == "test":
    test_files = total_files
else:
    train_files,val_files = train_test_split(total_files,test_size=0.15,random_state=42)
    trainval_files = train_files + val_files

# write test.txt train.txt val.txt trainval.txt
dataset =[test_files,train_files,val_files,trainval_files]
setname =["test","train","val","trainval"]
assert len(dataset) == len(setname)
for i in range(len(dataset)):
    if(len(dataset[i]) > 0):
        f = open(os.path.join(txtsavepath,setname[i] + ".txt"),'w')
        dataset[i] = (dataset[i])
        for fn in dataset[i]:
            f.write(fn + "\n")
        f.close()

# write class_*.txt
for lb in label_set:
    for  i in range(len(dataset)):
        if(len(dataset[i]) > 0):
            label_file =  open(os.path.join(txtsavepath,lb+"_" + setname[i] + ".txt"),'w')
        for filename,labels in total_csv_annotations.items():
            filename = filename.split('.')[0]
            if filename in dataset[i]:
                find = False
                for l in labels:
                    if(l[-1] == lb):
                        find = True
                        break
                if find:
                    label_file.write(filename+"  1\n")
                else:
                    label_file.write(filename+" -1\n")
            