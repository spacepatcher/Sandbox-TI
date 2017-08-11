import sys
import os
from datetime import datetime
import json
import time
from sdk.blueliv_api import BluelivAPI


keys_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "keys.json")


def read_config(file):
    with open(file, "r") as json_data_file:
        data = json.load(json_data_file)
    return data


def blueliv_grab():
    keys = read_config(keys_file)
    api = BluelivAPI(base_url='https://freeapi.blueliv.com', token=keys["keys"].get("blueliv"))
    try:
        i = 0
        while True:
            i += 1
            response = api.crime_servers.last()
            if response.items:
                current_time = datetime.now().isoformat().split(".")[0].replace(":", "_")
                with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "indices",
                                       "intel_blueliv_{}.json".format(current_time)), "w") as f:
                    json.dump(response.items, f)
                    f.write("\n")
                break
            else:
                time.sleep(60)
            if i > 10:
                break
    except Exception as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    blueliv_grab()
