DATASET_TYPE = "VOCSample"
# DATASET_TYPE="Scene"
if DATASET_TYPE == "VOCSample":
    classname_to_id = {"dog": 0,
                       "person": 1,
                       "train": 2}
    basedir = "example"
elif DATASET_TYPE == "Scene":
    classname_to_id = {"bedRoom": 0,
                       "diningRoom": 1,
                       "kitchen": 2,
                       "livingRoom": 3,
                       "restroom": 4}
    basedir = "data/scene_val"
