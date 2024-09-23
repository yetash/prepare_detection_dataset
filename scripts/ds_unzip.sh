#!/bin/bash

VOC_DATASET_PATH=$1


DATASET=dataset
MERGED_DATASET=merged_dataset
SCRIPT_PATH=$(cd $(dirname $0);pwd)


cd $VOC_DATASET_PATH
rm ${DATASET} -rf
mkdir ${DATASET}
rm ${MERGED_DATASET} -rf
mkdir ${MERGED_DATASET}

CSV_LIST=""
IMG_LIST=""

for file in ${VOC_DATASET_PATH}/*
do 
	is_zip=$(echo $file | grep ".zip")
	if [ -n "$is_zip" ]; then
        task_file="$(basename "$file")"
        if [ ! -d ${DATASET}/${task_file} ]; then
            echo extracting $task_file
            unzip -q "$file" -d  ${DATASET}/${task_file}
        else
            echo $task_file exists
        fi      
	fi
done