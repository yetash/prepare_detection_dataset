#!/bin/bash

DATASET=dataset
MERGED_DATASET=merged_dataset
VOC_DATASET_PATH=$1
SCRIPT_PATH=$(cd $(dirname $0);pwd)


cd $VOC_DATASET_PATH
#rm ${DATASET} -rf
rm ${MERGED_DATASET} -rf
mkdir ${DATASET}

for file in ${VOC_DATASET_PATH}/*
do 
	is_zip=$(echo $file | grep ".zip")
	if [ -n "$is_zip" ]; then
        task_id=$(echo "$file" | cut -f 2 -d '#' | cut -f 1 -d "_")
        task_file=task_${task_id} 
        if [ ! -d ${DATASET}/${task_file} ]; then
            echo extracting $task_file
            unzip -q "$file" -d  ${DATASET}/${task_file}
        else
            echo $task_file exists
        fi
	fi
done

python ${SCRIPT_PATH}/../merge_voc_label2csv.py ${DATASET} -o ${MERGED_DATASET}
python ${SCRIPT_PATH}/../csv2voc.py  -t train -d ${MERGED_DATASET}
python ${SCRIPT_PATH}/../csv2coco.py -t train -d ${MERGED_DATASET}
mv ${MERGED_DATASET}/coco/annotations/instances_train2017.json ${MERGED_DATASET}/coco/annotations/voc_2007_trainval.json
rm -rf ${MERGED_DATASET}/VOCdevkit/VOC2007/annotations
mv -f ${MERGED_DATASET}/coco/annotations ${MERGED_DATASET}/VOCdevkit/VOC2007

tar -czf sr_train.tar.gz ${MERGED_DATASET}/VOCdevkit