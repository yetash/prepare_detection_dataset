import argparse
import random
import os.path as osp


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--basedir", type=str, default="example", help="base directory path which includes labels.csv")
    parser.add_argument("-f", "--filter_file", type=str, default="none", help="files list to be filtered")
    parser.add_argument("--balanced_class_num", type=int, default=0, help="select num for each class")
    parser.add_argument("--class_file", type=str, default="none", help="file that include all class")
    parser.add_argument("--rm_noobj", action="store_true", default=False, help="filter images without any object")
    parser.add_argument("--rm_blackbox", action="store_true", default=False, help="remove black box annotations")
    parser.add_argument("--replace_label", type=str, default="", nargs="+", help="replace label origin1 new1 origin2 new2 ...")
    args = parser.parse_args()
    return args

def filter_noobj(args):
    origin_f = open(osp.join(args.basedir, "labels.csv"),"r")
    filter_f = open(osp.join(args.basedir, "labels_filtered.csv"),"w")
    count=0
    for l in origin_f.readlines():
        if ",,,," in l:
            count+=1
            continue
        filter_f.write(l)
    print(f"filter {count} files without obj")
    origin_f.close()
    filter_f.close()

def remove_blackbox(args):
    origin_f = open(osp.join(args.basedir, "labels.csv"),"r")
    filter_f = open(osp.join(args.basedir, "labels_filtered.csv"),"w")
    count=0
    for l in origin_f.readlines():
        if "black-box" in l.split(",")[-1]:
            count+=1
            continue
        filter_f.write(l)
    print(f"filter {count} lines with black-box")
    origin_f.close()
    filter_f.close()

def remove_file(args):
    filter_file = open(args.filter_file, "r")
    files_list=[]
    for l in filter_file.readlines():
        files_list.append(l.strip('\n'))
    filter_file.close()
    files_list=list(set(files_list))
    
    files_filtered=set()
    origin_f = open(osp.join(args.basedir, "labels.csv"),"r")
    filter_f = open(osp.join(args.basedir, "labels_filtered.csv"),"w")
    for l in origin_f.readlines():
        skip=False
        for file in files_list:
            if file in l:
                files_filtered.add(file)
                skip=True
                break
        if skip:
            continue
        filter_f.write(l)
    print(f"remove files {len(files_filtered)}/{len(files_list)}")
    unf_cnt=0
    if (len(files_list) > len(files_filtered)):
        unfiltered_files= set(files_list) - set(files_filtered)
        for unf in unfiltered_files:
            unf_cnt+=1
    print(f"cannot find {unf_cnt} files")
    origin_f.close()
    filter_f.close()

def collect_class_labels(args):
    class_file = open(args.class_file, "r")
    class_cnt={}
    total_cnt=0
    for l in class_file.readlines():
        class_name = l.strip("\n")
        if len(class_name) > 0:
            class_cnt[class_name] = 0
    class_file.close()
    
    origin_f = open(osp.join(args.basedir, "labels.csv"),"r")
    filter_f = open(osp.join(args.basedir, "labels_filtered.csv"),"w")
    for l in origin_f.readlines():
        line_label = l.split(",")[-1].strip("\n")
        skip=True
        for k,_ in class_cnt.items():
            if k == line_label:
                skip=False
                class_cnt[k] += 1
                total_cnt += 1
                break
        # print (l, skip)
        if skip:
            continue
        filter_f.write(l)
    for k,v in class_cnt.items():
        print(f"{k:-^19s}: {v:>5d}")
    origin_f.close()
    filter_f.close()
    print(f"----total-labels----: {total_cnt:>5d}")

def balanced_class(args):
    origin_f = open(osp.join(args.basedir, "labels.csv"),"r")
    filter_f = open(osp.join(args.basedir, "labels_filtered.csv"),"w")
    count={}
    lines=origin_f.readlines()
    random.shuffle(lines)
    for l in lines:
        class_name = l.split(",")[-1]
        if class_name not in count.keys():
            count[class_name]=1
        elif count[class_name] < args.balanced_class_num:
            count[class_name]+=1
            filter_f.write(l)
        else:
            continue
        
    print(f"filter csv count: {count}")
    origin_f.close()
    filter_f.close()

def replace_class(args):
    labels = args.replace_label
    origin_labels = labels[::2]
    new_labels = labels[1::2]

    origin_f = open(osp.join(args.basedir, "labels.csv"),"r")
    filter_f = open(osp.join(args.basedir, "labels_filtered.csv"),"w")
    lines=origin_f.readlines()
    for l in lines:
        line_splits = l.split(",")
        class_name = line_splits[-1]
        replace = False
        for i in range(len(origin_labels)):
            if origin_labels[i] == class_name.strip("\n"):
                class_name = new_labels[i] + "\n"
                replace = True
                break
        if replace:
            line_splits[-1] = class_name
            new_line = line_splits[0]
            for j in range(1,len(line_splits)):
                new_line +="," + line_splits[j]
            filter_f.write(new_line)
        else:
            filter_f.write(l)
    

if __name__=="__main__":
    args = parse_args()
    if args.rm_noobj:
        filter_noobj(args)
    elif args.rm_blackbox:
        remove_blackbox(args)
    elif args.filter_file !="none":
        remove_file(args)
    elif args.class_file !="none":
        collect_class_labels(args)
    elif args.balanced_class_num > 0:
        balanced_class(args)
    elif len(args.replace_label) > 0:
        replace_class(args)
    else:
        print("nothing to do")