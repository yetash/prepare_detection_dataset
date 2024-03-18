def get_class_dict():
    f = open("data/class_map.txt","r")
    lines = f.readlines()
    class_dict={}
    for l in lines:
        l = l[:-1]
        delimiter_idx = l.find(":") 
        if delimiter_idx!= -1:
            class_dict[l[delimiter_idx+1:]] = l[:delimiter_idx]
        else:
            class_dict[l] = l
    return class_dict

if __name__=="__main__":
    class_dict = get_class_dict()
    text_prompt=""
    for k,v in class_dict.items():
        text_prompt+=k+"."
    print(text_prompt)