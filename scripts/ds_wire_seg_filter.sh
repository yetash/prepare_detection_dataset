#!/bin/bash

DATASET=dataset
MERGED_DATASET=merged_dataset
VOC_DATASET_PATH=$1
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
        file_name="$(basename "$file")"
        task_file=$(echo "$file_name" | cut -f 1 -d  '-' )
        task_id=$(echo "$task_file" | cut -f 1 -d '_')
        task_id=$(echo "$task_id" | cut -f 2 -d '#')
        if [ ! -d ${DATASET}/${task_file} ]; then
            echo extracting $task_file
            unzip -q "$file" -d  ${DATASET}/${task_file} 
        else
            echo $task_file exists
        fi
        python ${SCRIPT_PATH}/../voc2csv.py ${DATASET}/${task_file} --image_type png --filter_class "wire" "curled wire" "straight wire"
        CSV_LIST=${CSV_LIST}" "${DATASET}/${task_file}/labels.csv
        IMG_LIST=${IMG_LIST}" "/home/cary/ws/data/cleaner_od/wire_seg/wire_patch6/0816-tasks-data/${task_id}/raw        
	fi
done
python ${SCRIPT_PATH}/../merge_csv.py -c $CSV_LIST -i $IMG_LIST -o $MERGED_DATASET
python ${SCRIPT_PATH}/../csv2voc.py  -t train -p ${MERGED_DATASET}

zip -rq VOCdevkit.zip ${MERGED_DATASET}/VOCdevkit