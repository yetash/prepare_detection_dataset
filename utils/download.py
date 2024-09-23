import os
import requests
import argparse
import pandas as pd
#from read_excel import get_task_list

new_cvat_url="http://192.168.51.40:2024"
cvat_url="http://192.168.51.120:8080"
# proxies = {'http': 'socks5://192.168.53.217:1103'}

cvat_user_data = {
    "username": "yuanjiabo",   # change to your username
    "password": "roborock2022" # change to your password
}

new_cvat_user_data = {
    "username": "yuanjiabo",   # change to your username
    "password": "rr123456789"  # change to your password
}

new_cvat_dataset_type = {
    "voc"     : "PASCAL+VOC+1.1",
    "labelme" : "LabelMe+3.0",
    "coco"    : "COCO+1.0"
}

def download(dataset_dir, dataset_list, download_type='dataset', dataset_type="voc", download_new_cvat=False):
    if download_new_cvat:
        dataset_url_format = new_cvat_dataset_type[dataset_type]
    os.makedirs(dataset_dir, exist_ok=True)
    for task_info in dataset_list:
        task_id, new_task_id = task_info
        task_id = new_task_id if download_new_cvat else task_id
        task_id = int(task_id)
        task_file_name= f"task_{task_id}_{dataset_type}.zip"
        if os.path.exists(f'{dataset_dir}/{task_file_name}'):
            print('existing task ', task_id)
            continue
        print('downloading ', task_file_name)
        if download_new_cvat:
            download_url = f'{new_cvat_url}/api/tasks/{task_id}/{download_type}?org=&use_default_location=true&filename={task_file_name}.zip&format={dataset_url_format}&action=download'
        else:
            download_url = f"{cvat_url}/api/v1/tasks/{task_id}/{download_type}?format=PASCAL%20VOC%201.1&action=download"
        ret = session.get(download_url, stream=True)  # , proxies=proxies, verify=False)
        while 1:
            ret = session.get(download_url, stream=True)  # , proxies=proxies, verify=False)
            if ret.status_code == 200:
                print(f"Task {task_id} Got!")
                with open(f'{dataset_dir}/{task_file_name}', 'wb') as output_file:
                    for chunk in ret.iter_content(chunk_size=1024*1024*2):
                        if chunk:
                            output_file.write(chunk)
                break
            if ret.status_code == 404:
                print(f"Task {task_id} Not Found!")
                break
            elif ret.status_code == 500:
                print(f"Task {task_id} Server Error!")
                break

if __name__ == '__main__':
    parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS,
                                     description='download dataset')
    parser.add_argument('--download_dir', type=str, required=True, default=None,
                        help='save dir')
    parser.add_argument('--dataset_list', type=str, required=True, default=None,
                        help="dataset list")
    parser.add_argument("--new_cvat", action="store_true", default=False,
                        help="download from new cvat")
    parser.add_argument("--annot_only", action="store_true", default=False, 
                        help="do not save image")
    parser.add_argument("--dataset_type", type=str, choices=["coco", "voc", "labelme"], default="voc", 
                        help="dataset type")
    args = parser.parse_args()

    user_data = new_cvat_user_data if args.new_cvat else cvat_user_data 

    session = requests.session()
    
    if args.new_cvat:
        page = session.post(f"{new_cvat_url}/api/auth/login?org=", json=user_data)#, proxies=proxies, verify=False)
    else:
        page = session.post(f"{cvat_url}/api/v1/auth/login", user_data)
    assert page.status_code == 200
    
    download_type="annotations"if args.annot_only else "dataset"       

    dataset_info = pd.read_csv(args.dataset_list, header=None).values
    tasks_ids = dataset_info[:,-2:][1:].tolist()
    
    download(args.download_dir, tasks_ids, download_type, args.dataset_type, args.new_cvat)
