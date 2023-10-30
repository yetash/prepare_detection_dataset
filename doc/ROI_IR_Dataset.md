# Infrared Object Detection

### 1. Dataset
CVAT [project 44](http://192.168.50.120:8080/projects/44) contains all infrared images data so far.

Training dataset includes tasks: [958](http://192.168.50.120:8080/tasks/958), [968](http://192.168.50.120:8080/tasks/968), [971](http://192.168.50.120:8080/tasks/971),  [1001](http://192.168.50.120:8080/tasks/1001), [1144](http://192.168.50.120:8080/tasks/1144), [1149](http://192.168.50.120:8080/tasks/1149)  
Test dataset includes tasks: [969](http://192.168.50.120:8080/tasks/969), [1145](http://192.168.50.120:8080/tasks/1145)

Download above tasks in COCO format and using `tools/merge_dataset.py` to merge them.

```shell
/home/roborock/Projects/nanodet/tools/merge_dataset.py None -f riod.lambda.8.train.json -o riod.lambda.8.post_train
``` 
or
```shell
/home/roborock/Projects/nanodet/tools/merge_dataset.py /home/roborock/Datasets/task971 /home/roborock/Datasets/task958 /home/roborock/Datasets/task968 /home/roborock/Datasets/task1001 /home/roborock/Datasets/task1144 /home/roborock/Datasets/task1149 -o riod.lambda.8.post_train
```