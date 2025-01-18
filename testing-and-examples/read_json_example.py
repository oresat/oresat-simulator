

import json



if __name__ == "__main__":

    with open("my_file.json", "r") as config_file:
        my_config = json.load(config_file)


    for key,value in my_config.items():
        print(key, ": ", value)
