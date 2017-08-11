import requests
import json
from datetime import datetime
import os
import sys


keys_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "keys.json")


def read_config(file):
    with open(file, "r") as json_data_file:
        data = json.load(json_data_file)
    return data


def vt_grab():
    keys = read_config(keys_file)
    payload = {"key": keys["keys"].get("virus-total")}
    r = requests.get("https://www.virustotal.com/intelligence/hunting/notifications-feed/", params=payload)
    if r.status_code == 200:
        data = r.json()
        if data.get("result") == 1:
            grabbed_docs = []
            everything = []
            current_time = datetime.now().isoformat().split(".")[0].replace(":", "_")
            for i in data.get("notifications"):
                grabbed_docs.append(i.get("id"))
                everything.append(i)
            with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "indices", "intel_virus-total_{}.json".format(current_time)), "w") as f:
                json.dump(everything, f)
                f.write("\n")
            # delete grabbed docs from notifications
            requests.post("https://www.virustotal.com/intelligence/hunting/delete-notifications/programmatic/", params=payload, json=grabbed_docs)
    else:
        return


if __name__ == "__main__":
    try:
        vt_grab()
    except Exception as e:
        print("Information gathering interrupted")
        print(e)
        sys.exit(1)
