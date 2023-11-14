# Infrared Object Detection

### 1. Dataset
CVAT [project 44](http://192.168.50.120:8080/projects/44) contains all infrared images data so far.

### **Training Dataset**
| 数据集 | 图片数量 |
| :-----| :-----|
|[train_lambda_5](http://192.168.50.120:8080/tasks/971) |43604|
|[train_lambda_6](http://192.168.50.120:8080/tasks/958) |1098|
|[train_lambda_7](http://192.168.50.120:8080/tasks/1001)|573|
|[train_lambda_8](http://192.168.50.120:8080/tasks/1149)|335|
|[反光白色\浅色柱状物体（训练）](http://192.168.50.120:8080/tasks/968)|354|
|[耷拉线-黑白数据-训练总](http://192.168.50.120:8080/tasks/1144)|312|
|总计|46276|


### **Training Dataset**
| 数据集 | 图片数量 |
| :-----| :-----|
| [Test(total) lambda.5](http://192.168.50.120:8080/tasks/969)|6027|
| [耷拉线-黑白数据-测试总](http://192.168.50.120:8080/tasks/1145)|48|
|总计|6075|

Download above tasks in COCO format and using `tools/merge_dataset.py` to merge them.

```shell
/home/roborock/Projects/nanodet/tools/merge_dataset.py None -f riod.lambda.8.train.json -o riod.lambda.8.post_train
``` 
or
```shell
/home/roborock/Projects/nanodet/tools/merge_dataset.py /home/roborock/Datasets/task971 /home/roborock/Datasets/task958 /home/roborock/Datasets/task968 /home/roborock/Datasets/task1001 /home/roborock/Datasets/task1144 /home/roborock/Datasets/task1149 -o riod.lambda.8.post_train
```