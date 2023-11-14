from pycocotools import coco
import json
import subprocess
import os
import argparse
import sys
import shutil
from tqdm import tqdm

parser = argparse.ArgumentParser(
    description="merge different coco dataset and clean label")
parser.add_argument('datasets', type=str, nargs='+',
                    help="list of dataset need to merge")
parser.add_argument('--file', '-f', type=str, default='',
                    help="list of dataset need to merge")
parser.add_argument('--output', '-o', type=str, default='debug',
                    help="output path merged dataset")
args = parser.parse_args()

if args.file:
    with open(args.file, 'r') as f:
        args.datasets = json.load(f)
print('Merge datasets:', args.datasets)
print('To:', args.output)

WANTED_ITEMS = [
    "wire",  # 1
    "pet feces",  # 2
    "shoe",  # 3
    "bar stool a",  # 4 closed
    "fan",  # 5 closed
    "power strip",  # 6
    "dock(ruby)_ir",  # 7 closed
    "dock(rubys+tanosv)_ir",  # 8
    "bar stool b",  # 9
    "scale",  # 10
    "clothing item",  # 11 closed
    "cleaning robot",  # 12
    "fan b",  # 13 closed
    "door mark a",  # 14
    "door mark b",  # 15 closed
    "wheel",  # 16
    "door mark c",  # 17 closed
    "flat base",  # 18 closed
    "whole fan",  # 19
    "whole fan b",  # 20 closed
    "whole bar stool a",  # 21
    "whole bar stool b",  # 22
    "fake poop a",  # 23
    "dust pan",  # 24
    "folding chair",  # 25
    "laundry basket",  # 26
    "handheld cleaner",  # 27
    "sock",  # 28
    "fake poop b",  # 29
    "fan c",  # 30 closed
    "whole fan c",  # 31
    "rocking chair",  # 32
    "floor lamp",  # 33 closed
    "coat rack",  # 34 closed
    "tv cabinet",  # 35 closed
    "flush toilet",  # 36 closed
    "bed",  # 37 closed
    "rectangular sofa",  # 38 closed
    "dining table cluster",  # 39 closed
    "loose wire",  # 40 closed
    "cat",  # 41
    "dog",  # 42
    "curled fabric"  # 43
]
categories = [{"id": WANTED_ITEMS.index(
    i) + 1, "name": i, "supercategory": ""} for i in WANTED_ITEMS]

loose_wire = ['curled wire', 'straight wire']
flat_base = ['bar stool a', 'fan', 'flat base', 'floor lamp', 'coat rack']
erase_difficult = {'fake poop a':None, 'fake poop b':None, 'power strip':None, 'curled fabric':None, 'shoe':None}
# category_map = {
#     37:1,     #wire
#     19:2,     #pet feces
#     14:3,     #shoe
#     22:6,     #power strip
#     8:8,      #dock(rubys+tanosv)_ir
#     34:9,     #bar stool b
#     10:10,     #scale
#     9:12,     #cleaning robot
#     31:14,    #door mark a
#     33:16,    #wheel
#     36:19,    #whole fan
#     13:21,    #whole bar stool a
#     11:22,    #whole bar stool b
#     27:23,    #fake poop a
#     12:24,    #dust pan
#     7:25,     #folding chair
#     6:26,     #laundry basket
#     21:27,    #handheld cleaner
#     20:28,    #sock
#     5:29,     #fake poop b
#     32:31,    #whole fan c
#     23:32,    #rocking chair
#     45:41,    #cat
#     46:42,    #dog
#     53:43,    #curled fabric

#     54:40,    #straight wire
#     55:40,    #curled wire

#     24:18,    #bar stool a
#     25:18,    #fan
#     16:18,    #flat base
#     17:18,    #floor lamp
#     18:18     #coat rack
# }

if not args.output == 'debug':
    os.makedirs(os.path.join(args.output, "images"), exist_ok=True)

output_annotations = {
    'licenses': [{'name': '', 'id': 0, 'url': ''}],
    'info': {'contributor': '', 'date_created': '', 'description': '', 'url': '', 'version': '', 'year': ''},
    'categories': categories,
    'images': [],
    'annotations': []}

for i in tqdm(args.datasets):
    shutil.copytree(os.path.join(i, "images"), os.path.join(args.output, "images"), dirs_exist_ok= True)
    erase_review = None
    if 'erase.json' in os.listdir(i):
        if args.output == 'debug':
            print(os.path.join(i, 'erase.json'))
        
        with open(os.path.join(i, 'erase.json'), 'r') as f:
            erase_review = json.load(f)

    image_dir = os.path.join(i, 'images')
    if 'instances_merged.json' in os.listdir(os.path.join(i, 'annotations')):
        ann_file = os.path.join(i, 'annotations', 'instances_merged.json')
    else:
        ann_file = os.path.join(i, 'annotations', 'instances_default.json')

    if args.output == 'debug':
        print(image_dir)
        print(ann_file)
    
    if not args.output == 'debug':
        command_line = 'cp -r %s %s' % (image_dir, args.output)
        subprocess.Popen(command_line, shell=True, stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT).wait()

    with open(ann_file, 'r') as f:
        ann_content = json.load(f)

    category_map = {}
    for i in WANTED_ITEMS:
        for j in ann_content['categories']:
            if j['name'] in loose_wire:
                category_map[j['id']] = WANTED_ITEMS.index('loose wire') + 1
            elif j['name'] in flat_base:
                category_map[j['id']] = WANTED_ITEMS.index('flat base') + 1
            elif j['name'] == i:
                category_map[j['id']] = WANTED_ITEMS.index(i) + 1

            if j['name'] in erase_difficult:
                erase_difficult[j['name']] = j['id']

    if args.output == 'debug':
        print(category_map)

    image_id_map = {}
    for image in ann_content['images']:
        if erase_review is not None and image['id'] in erase_review:
            continue
        image_id_map[image['id']] = len(output_annotations['images']) + 1
        image['id'] = len(output_annotations['images']) + 1
        output_annotations['images'].append(image)
        
    for annotation in ann_content['annotations']:
        if erase_review is not None and annotation['image_id'] in erase_review:
            continue
        if not 'difficult' in annotation['attributes']:
            pass
        elif annotation['category_id'] in erase_difficult.values() and annotation['attributes']['difficult'] and 'train' in args.output:
            continue
        try:
            annotation['image_id'] = image_id_map[annotation['image_id']]
            annotation['category_id'] = category_map[annotation['category_id']]
            annotation['id'] = len(output_annotations['annotations']) + 1
            output_annotations['annotations'].append(annotation)
        except:
            if args.output == 'debug':
                print(annotation)
            else:
                continue

if not args.output == 'debug':
    os.makedirs(os.path.join(args.output, 'annotations'), exist_ok=True)
    with open(os.path.join(args.output, 'annotations', 'instances_merged.json'), 'w') as f:
        json.dump(output_annotations, f)
    with open(os.path.join(args.output, 'merged_log'), 'w') as f:
        json.dump(sys.argv, f)

    coco.COCO(os.path.join(args.output, 'annotations', 'instances_merged.json'))

else:
    print(json.dumps(sys.argv, indent=4))

