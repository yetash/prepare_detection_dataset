#!/bin/bash

DATASET=dataset
MERGED_DATASET=merged_dataset
DATASET_PATH=$1
SCRIPT_PATH=$(cd $(dirname $0);pwd)


cd $DATASET_PATH
#rm ${DATASET} -rf
rm ${MERGED_DATASET} -rf
mkdir ${DATASET}

DATASET_LIST=""

for file in ${DATASET_PATH}/*
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
        DATASET_LIST=${DATASET_LIST}" "${DATASET}/${task_file}
	fi
done
echo ${DATASET_LIST}
python ${SCRIPT_PATH}/../merge_coco_annot.py ${DATASET_LIST} -o ${MERGED_DATASET}

tar -czf ir_dataset.tar.gz ${MERGED_DATASET}