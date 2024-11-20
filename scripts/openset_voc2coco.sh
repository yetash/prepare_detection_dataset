TYPE=train
BASEPATH=/roborock/data/datasets/ncy_dataset
VOC2007PATH=${BASEPATH}/${TYPE}/VOCdevkit/VOC2007
CLASSFILE=/roborock/data/datasets/ncy_dataset/dataset_tools/voc_classes60.txt
OUTPATH=/roborock/data/datasets/yjb_dataset/rio60
SETNAME=${TYPE}_rio59.txt

#convert voc to csv
python voc2csv.py -p ${VOC2007PATH} \
--set_file ${VOC2007PATH}/ImageSets/Main/${SETNAME} \
--out_dir ${OUTPATH}

#filter csv class
python tools/csv_filter.py  -p ${OUTPATH} --class_file ${CLASSFILE}
mv ${OUTPATH}/labels_filtered.csv ${OUTPATH}/labels.csv

#convert csv to coco
python csv2coco.py -t ${TYPE} -p ${OUTPATH} \
-c ${CLASSFILE} -a

pushd $OUTPATH
mv images coco/${TYPE}2017
rmdir coco/images
rm labels.csv
popd