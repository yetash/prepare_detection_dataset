import argparse
import os.path as osp


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--basedir", type=str, default="example", help="base directory path which includes labels.csv")
    parser.add_argument("-f", "--filter_file", type=str, default="none", help="files list to be filtered")
    parser.add_argument("--class_file", type=str, default="none", help="file that include all class")
    parser.add_argument("--rm_noobj", action="store_true", default=False, help="filter images without any object")
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

def remove_file(args):
    filter_file = open(args.filter_file, "r")
    files_list=[]
    for l in filter_file.readlines():
        files_list.append(l.split(",")[0])
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
    if (len(files_list) > len(files_filtered)):
        unfiltered_files= set(files_list) - set(files_filtered)
        for unf in unfiltered_files:
            print(unf)
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

if __name__=="__main__":
    args = parse_args()
    if args.rm_noobj:
        filter_noobj(args)
    elif args.filter_file !="none":
        remove_file(args)
    elif args.class_file !="none":
        collect_class_labels(args)
    else:
        print("nothing to do")