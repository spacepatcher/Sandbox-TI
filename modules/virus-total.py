import requests
import json
from datetime import datetime
import os
import sys
import traceback


keys_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "keys.json")
config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")
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


def vt_grab(url=None):
    keys = read_json(keys_file)
    payload = {
        "key": keys["keys"].get("virus-total")
    }
    try:
        r = requests.get(url, params=payload)
    except requests.RequestException as e:
        print("Information grabbing failed")
        print(e)
        sys.exit(1)
    if r.status_code == 200:
        data = r.json()
        if data.get("result") == 1:
            grabbed_docs = []
            everything = []
            for i in data.get("notifications"):
                grabbed_docs.append(i.get("id"))
                everything.append(i)
            feed_file = os.path.join(feeds_path, "intel_virus-total_{}.json".format(datetime.now().isoformat().split(".")[0].replace(":", "_")))
            write_json(file=feed_file, json_obj=everything)
            # delete grabbed docs from notifications
            requests.post("https://www.virustotal.com/intelligence/hunting/delete-notifications/programmatic/", params=payload, json=grabbed_docs)
    else:
        print("Bad HTTP response, got %d" % r.status_code)
        sys.exit(1)


if __name__ == "__main__":
    feed_url = "https://www.virustotal.com/intelligence/hunting/notifications-feed/"
    try:
        vt_grab(url=feed_url)
    except Exception:
        print("Information gathering interrupted")
        traceback.print_exc()
        sys.exit(1)
