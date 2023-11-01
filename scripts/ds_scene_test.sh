#!/bin/bash

DATASET=dataset
MERGED_DATASET=merged_dataset
VOC_DATASET_PATH=$1
SCRIPT_PATH=$(cd $(dirname $0);pwd)


cd $VOC_DATASET_PATH
#rm ${DATASET} -rf
mkdir ${DATASET}
rm ${MERGED_DATASET} -rf
mkdir ${MERGED_DATASET}

CSV_LIST=""
IMG_LIST=""

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
        python ${SCRIPT_PATH}/../voc2csv.py ${DATASET}/${task_file}
        CSV_LIST=${CSV_LIST}" "${DATASET}/${task_file}/labels.csv
        IMG_LIST=${IMG_LIST}" "${DATASET}/${task_file}/JPEGImages
	fi
done
python ${SCRIPT_PATH}/../merge_csv.py -c $CSV_LIST -i $IMG_LIST -o $MERGED_DATASET
python ${SCRIPT_PATH}/../csv2voc.py  -t test -d ${MERGED_DATASET}
python ${SCRIPT_PATH}/../csv2coco.py -t test -d ${MERGED_DATASET}
mv ${MERGED_DATASET}/coco/annotations/instances_test2017.json ${MERGED_DATASET}/coco/annotations/voc_2007_test.json
rm -rf ${MERGED_DATASET}/VOCdevkit/VOC2007/annotations
mv -f ${MERGED_DATASET}/coco/annotations ${MERGED_DATASET}/VOCdevkit/VOC2007

tar -czf sr_test.tar.gz ${MERGED_DATASET}/VOCdevkit
