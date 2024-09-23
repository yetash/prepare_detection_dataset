#!/bin/bash

DATASET_PATH=$1
DATSET_FILE_PATH=$2

if [ ! -d "$DATASET_PATH" ]; then
    echo "work directory $DATASET_PATH does not exist"
    exit 1
elif [ ! -f "$DATSET_FILE_PATH" ]; then
    echo "dataset file $DATSET_FILE_PATH does not exist"
    exit 1
fi

DATASET=dataset
MERGED_DATASET=default_black
SCRIPT_PATH=$(cd $(dirname $0);pwd)


cd $DATASET_PATH
rm ${DATASET} -rf
rm ${MERGED_DATASET} -rf
mkdir ${DATASET}
mkdir ${MERGED_DATASET}

python ${SCRIPT_PATH}/../utils/download.py \
--download_dir ${DATASET_PATH} \
--dataset_list ${DATSET_FILE_PATH} \
--new_cvat

python ${SCRIPT_PATH}/../utils/download.py \
--download_dir ${DATASET_PATH} \
--dataset_list ${DATSET_FILE_PATH} \
--new_cvat \
--dataset_type labelme --annot_only

for file in ${DATASET_PATH}/*
do 
	is_zip=$(echo $file | grep ".zip")
	if [ -n "$is_zip" ]; then
        file_name="$(basename "$file")"
        # task_name=$(echo "$file_name" | cut -f 1 -d  '-' )
        # task_type=$(echo "$file_name" | cut -f 3 -d '-' | cut -f 1 -d " ")
        task_file=$(echo "$file_name" | cut -f 1 -d  '.' )
        if [ ! -d ${DATASET}/${task_file} ]; then
            echo extracting $task_file
            unzip -q "$file" -d  ${DATASET}/${task_file}
        else
            echo $task_file exists
        fi
	fi
done

for file in ${DATASET}/*
do
    if [ -d "$file" ]; then
        file_name="$(basename "$file")"
        task_id=$(echo "$file_name" | cut -f 2 -d '_')
        task_type=$(echo "$file_name" | cut -f 3 -d '_')
        if  [ $task_type = "labelme" ]; then
            python ${SCRIPT_PATH}/../loadvoc.py -p ${DATASET_PATH}/${DATASET}/task_${task_id}_voc -b
            cp -r ${DATASET_PATH}/${DATASET}/task_${task_id}_voc/JPEGImages/* ${DATASET_PATH}/${DATASET}/${file_name}/default
            pushd ${DATASET}/${file_name}
            tar -czf ${file_name}.tar.gz default
            mv ${file_name}.tar.gz ../../${MERGED_DATASET}
            popd
        fi
    fi
done
