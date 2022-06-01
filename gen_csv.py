import os

cwd_path     = os.path.dirname(os.path.realpath(__file__))
example_path = os.path.join(cwd_path,"example")
img_dir      = os.path.join(example_path,"images")
filename1 = os.path.join(img_dir,"000001.jpg")
filename2 = os.path.join(img_dir,"000002.jpg")

info = [[filename1,"48 240 195 371 dog"],
        [filename1,"8 12 352 498 person"],
        [filename2,"139 200 207 301 train"]
        ]
csv_labels = open(os.path.join(example_path,"labels.csv"),"w")
for filename,bboxes in info:
    bbox = bboxes.split(" ")
    label = bbox[-1]
    csv_labels.write(filename+","+bbox[0]+","+bbox[1]+","+bbox[2]+","+bbox[3]+","+label+"\n")
csv_labels.close()