import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--type", default="train", choices=[ "train", "test", "trainval" ], help="dataset type: train, test or trainval")
    parser.add_argument("-d", "--basedir", default="example", help="base directory which includes images and labels.csv")
    parser.add_argument("-r", "--ratio", type=float, default=0.2, help="trainval split ratio [0,1]")
    args = parser.parse_args()
    return args