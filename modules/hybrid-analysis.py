import requests
import sys
import os
from fake_useragent import UserAgent
import time
from datetime import datetime
import json


config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")
feeds_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "feeds")


def read_config(file):
    with open(file, "r") as json_file:
        data = json.load(json_file)
    return data


def write_json(json_obj, file):
    with open(file, "w") as json_file:
        json.dump(json_obj, json_file, indent=2, sort_keys=True)
        json_file.write("\n")
    return


def filter_old(raw_data):
    filtered = []
    analysis_timestamp = None
    added_hash = None
    config = read_config(file=config_path)
    last_added_timestamp = datetime(*time.strptime(config.get("hybrid-analysis").get("last_added"), "%Y-%m-%d %H:%M:%S")[:6])
    last_added_hash = config.get("hybrid-analysis").get("last_added_hash")
    for data_item in reversed(raw_data.get("data")):
        try:
            analysis_timestamp = datetime(*time.strptime(data_item.get("analysis_start_time"), "%Y-%m-%d %H:%M:%S")[:6])
            added_hash = data_item["md5"]
        except ValueError as e:
            print("Bad feed: bad analysis_start_time")
            print(e)
            continue
        except KeyError as e:
            print("Bad feed: no md5")
            print(e)
            continue
        if analysis_timestamp >= last_added_timestamp and added_hash != last_added_hash:
            filtered.append(data_item)
    config["hybrid-analysis"]["last_added"] = analysis_timestamp.strftime("%Y-%m-%d %H:%M:%S")
    config["hybrid-analysis"]["last_added_hash"] = added_hash
    write_json(json_obj=config, file=config_path)
    return filtered


def filter_json_arrays(raw_json):
    filtered = []
    for dict_item in raw_json:
        i = 0
        for key, value in dict_item.copy().items():
            if type(value) == list:
                if type(value[0]) == dict:
                    for internal_dict in value:
                        new_key = key + str(i)
                        i += 1
                        dict_item.update(
                            {
                                new_key: internal_dict
                            }
                        )
                        dict_item.pop(key, None)
        filtered.append(dict_item)
    return filtered


def ha_grab(url=None):
    ua = UserAgent()
    headers = {
        'User-Agent': ua.random,
    }
    try:
        r = requests.get(url, headers=headers)
    except requests.RequestException as e:
        print("Information grabbing failed")
        print(e)
        sys.exit(1)
    if r.status_code == 200:
        data = r.json()
        if data.get("count") > 0:
            data_filtered = filter_old(raw_data=data)
            data_filtered = filter_json_arrays(raw_json=data_filtered)
            feed_file = os.path.join(feeds_path, "intel_hybrid-analysis_{}.json".format(datetime.now().isoformat().split(".")[0].replace(":", "_")))
            write_json(file=feed_file, json_obj=data_filtered)
        else:
            print("Empty HTTP response")
    else:
        print("Bad HTTP response, got %d" % r.status_code)
        sys.exit(1)


if __name__ == "__main__":
    feed_url = "https://www.hybrid-analysis.com/feed?json"
    try:
        ha_grab(url=feed_url)
    except Exception as e:
        print("Information gathering interrupted")
        print(e)
        sys.exit(1)
