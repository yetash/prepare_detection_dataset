#!/bin/bash

DATASET=dataset
MERGED_DATASET=default_black
DATASET_PATH=$1
SCRIPT_PATH=$(cd $(dirname $0);pwd)


cd $DATASET_PATH
rm ${DATASET} -rf
rm ${MERGED_DATASET} -rf
mkdir ${DATASET}

DATASET_LIST=""

for file in ${DATASET_PATH}/*
do 
	is_zip=$(echo $file | grep ".zip")
	if [ -n "$is_zip" ]; then
        file_name="$(basename "$file")"
        task_name=$(echo "$file_name" | cut -f 1 -d  '-' )
        task_type=$(echo "$file_name" | cut -f 3 -d '-' | cut -f 1 -d " ")
        task_file=${task_name}_${task_type} 
        if [ ! -d ${DATASET}/${task_file} ]; then
            echo extracting $task_file
            unzip -q "$file" -d  ${DATASET}/${task_file}
        else
            echo $task_file exists
        fi
	fi
done
python ${SCRIPT_PATH}/../loadvoc.py -p ${DATASET_PATH}/${DATASET}/${task_name}_pascal -b
cp -r ${DATASET_PATH}/${DATASET}/${task_name}_pascal/JPEGImages/* ${DATASET_PATH}/${DATASET}/${task_name}_labelme/default
cd ${DATASET}/${task_name}_labelme
tar -czf ${task_name}_labelme.tar.gz default
mv ${task_name}_labelme.tar.gz ../../..
