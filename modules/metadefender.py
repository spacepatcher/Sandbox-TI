import requests
import json
from datetime import datetime
from fake_useragent import UserAgent
import os
import sys


config = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")
keys_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "keys.json")


def read_config(file):
    with open(file, "r") as json_data_file:
        data = json.load(json_data_file)
    return data


def metadefender_grab():
    keys = read_config(keys_file)
    payload = {"key": keys["keys"].get("metadefender")}
    url = "https://www.metadefender.com/feeds/json"
    ua = UserAgent()
    headers = {
        'User-Agent': ua.random,
    }
    try:
        r = requests.get(url, params=payload, headers=headers)
    except requests.RequestException as e:
        print(e)
        sys.exit(1)
    if r.status_code == 200:
        data = r.json()
        current_time_formatted = datetime.now().isoformat().split(".")[0].replace(":", "_")
        result_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "indices",
                                   "intel_metadefender_{}.json".format(current_time_formatted))
        try:
            if data.get("status") == "error":
                with open(result_file, "w") as f:
                    json.dump(data, f)
                    f.write("\n")
        except AttributeError:
            with open(result_file, "w") as f:
                json.dump(data, f)
                f.write("\n")
        return
    else:
        print(r.status_code)
        return

if __name__ == "__main__":
    try:
        metadefender_grab()
    except Exception as e:
        print("Information gathering interrupted")
        print(e)
        sys.exit(1)
