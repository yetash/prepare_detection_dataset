#!/bin/bash

VOC_DATASET_PATH=$1
DATSET_FILE_PATH=$2

if [ ! -d "$VOC_DATASET_PATH" ]; then
    echo "work directory $VOC_DATASET_PATH does not exist"
    exit 1
elif [ ! -f "$DATSET_FILE_PATH" ]; then
    echo "dataset file $DATSET_FILE_PATH does not exist"
    exit 1
fi

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

python ${SCRIPT_PATH}/../utils/download.py \
--download_dir ${VOC_DATASET_PATH} \
--dataset_list ${DATSET_FILE_PATH} \
--new_cvat

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
        python ${SCRIPT_PATH}/../loadvoc.py -p ${DATASET}/${task_file} -b
        python ${SCRIPT_PATH}/../voc2csv.py ${DATASET}/${task_file} --image_type png --exclude_class black-box
        CSV_LIST=${CSV_LIST}" "${DATASET}/${task_file}/labels.csv
        IMG_LIST=${IMG_LIST}" "${DATASET}/${task_file}/JPEGImages        
	fi
done

python ${SCRIPT_PATH}/../merge_csv.py -c $CSV_LIST -i $IMG_LIST -o $MERGED_DATASET
python ${SCRIPT_PATH}/../tools/csv_filter.py  -p ${MERGED_DATASET} --replace_label "stairway" "upward stairway"
mv ${MERGED_DATASET}/labels_filtered.csv ${MERGED_DATASET}/labels.csv
python ${SCRIPT_PATH}/../csv2voc.py  -t train -p ${MERGED_DATASET}
python ${SCRIPT_PATH}/../csv2coco.py -t train -p ${MERGED_DATASET} -a -c /home/cary/ws/rr/prepare_detection_dataset/doc/Scene_Dataset_ID.txt
mv ${MERGED_DATASET}/coco/annotations/instances_train2017.json ${MERGED_DATASET}/coco/annotations/voc_2007_trainval.json
rm -rf ${MERGED_DATASET}/VOCdevkit/VOC2007/annotations
mv -f ${MERGED_DATASET}/coco/annotations ${MERGED_DATASET}/VOCdevkit/VOC2007

tar -czf sr_train.tar.gz ${MERGED_DATASET}
rm ${DATASET} -rf
rm ${MERGED_DATASET} -rf