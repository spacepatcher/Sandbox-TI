import requests
import json
from datetime import datetime
from fake_useragent import UserAgent
import os
import sys


keys_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "keys.json")
feeds_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "feeds")



def read_json(file):
    with open(file, "r") as json_file:
        data = json.load(json_file)
    return data


def write_json(json_obj, file):
    with open(file, "w") as json_file:
        json.dump(json_obj, json_file, indent=2, sort_keys=True)
        json_file.write("\n")
    return


def metadefender_grab(url=None):
    keys = read_json(keys_file)
    ua = UserAgent()
    payload = {
        "apikey": keys.get("keys").get("metadefender")
    }
    headers = {
        'User-Agent': ua.random,
    }
    try:
        r = requests.get(url, params=payload, headers=headers)
    except requests.RequestException as e:
        print("Information grabbing failed")
        print(e)
        sys.exit(1)
    if r.status_code == 200:
        data = r.json()
        feed_file = os.path.join(feeds_path, "intel_metadefender_{}.json".format(datetime.now().isoformat().split(".")[0].replace(":", "_")))
        write_json(file=feed_file, json_obj=data)
    else:
        print("Bad HTTP response, got %d" % r.status_code)
        sys.exit(1)


if __name__ == "__main__":
    feed_url = "https://www.metadefender.com/feeds/json"
    try:
        metadefender_grab(url=feed_url)
    except Exception as e:
        print("Information gathering interrupted")
        print(e)
        sys.exit(1)
