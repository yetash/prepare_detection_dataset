def copy_file(src, dst):
    lines = src.readlines()
    for line in lines:
        dst.write(line)

if __name__ == "__main__":
    base_dir = "/home/ly/ws/data/robot_scene_recognition/scene_detection_job/test_set/RGB_test/csv_format/"
    csv1_path = base_dir + "labels1.csv"
    csv2_path = base_dir + "labels.csv"
    new_csv_path = base_dir + "new_labels.csv"
    new_csv_f = open(new_csv_path, "w")
    csv1_f = open(csv1_path, "r")
    csv2_f = open(csv2_path, "r")
    copy_file(csv1_f, new_csv_f)
    copy_file(csv2_f, new_csv_f)
    new_csv_f.close()
    csv1_f.close()
    csv2_f.close()