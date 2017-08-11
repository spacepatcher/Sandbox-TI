import requests
import sys
import os
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import time
from datetime import datetime
import json


config = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")


def read_config(file):
    with open(file, "r") as json_data_file:
        data = json.load(json_data_file)
    return data


def write_config(json_obj, file):
    with open(file, "w") as json_data_file:
        json.dump(json_obj, json_data_file, indent=2, sort_keys=True)
    return


def parse_page(page):
    data = []
    soup = BeautifulSoup(page, "html.parser")
    table = soup.find("table")
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols_list = [item.text.strip() for item in cols]
        data.append(
            {
                "date": cols_list[0],
                "md5": cols_list[1],
                "file_name": cols_list[2],
                "file_type": cols_list[3],
                "antivirus": cols_list[4],
            }
        )
    return data


def filter_old(raw_data):
    filtered = []
    analysis_timestamp = None
    added_hash = None
    config_json = read_config(file=config)
    for data_item in reversed(raw_data):
        if data_item.get("date"):
            analysis_timestamp_raw = data_item["date"].replace("a.m.", "AM").replace("p.m.", "PM").replace("midnight", "12 AM")
            try:
                analysis_timestamp = datetime.strptime(analysis_timestamp_raw, "%B %d, %Y, %I:%M %p")
            except ValueError:
                analysis_timestamp = datetime.strptime(analysis_timestamp_raw, "%B %d, %Y, %I %p")
            added_hash = data_item.get("md5")
            last_added_timestamp = datetime(*time.strptime(config_json.get("malwr").get("last_added"), "%Y-%m-%d %H:%M:%S")[:5])
            last_added_hash = config_json.get("malwr").get("last_added_hash")
            if analysis_timestamp >= last_added_timestamp and added_hash != last_added_hash:
                filtered.append(data_item)
    config_json["malwr"]["last_added"] = analysis_timestamp.strftime("%Y-%m-%d %H:%M:%S")
    config_json["malwr"]["last_added_hash"] = added_hash
    write_config(json_obj=config_json, file=config)
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


def m_grab():
    url = "https://malwr.com/analysis/?page=1"
    ua = UserAgent()
    headers = {
        'User-Agent': ua.random,
    }
    try:
        r = requests.get(url, headers=headers)
    except requests.RequestException as e1:
        print(e1)
        sys.exit(1)
    if r.status_code == 200:
        data = parse_page(r.text)
        if data:
            everything = []
            data_filtered = filter_old(raw_data=data)
            current_time_formatted = datetime.now().isoformat().split(".")[0].replace(":", "_")
            result_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "indices",
                                       "intel_malwr_{}.json".format(current_time_formatted))
            for item in data_filtered:
                everything.append(item)
            everything_filtered = filter_json_arrays(raw_json=everything)
            if everything_filtered:
                with open(result_file, "w") as f:
                    json.dump(everything_filtered, f)
                    f.write("\n")
        else:
            print("Empty HTTP response")
    else:
        print("Bad HTTP response")
        sys.exit(1)


if __name__ == "__main__":
    try:
        m_grab()
    except Exception as e:
        print("Information gathering interrupted")
        print(e)
        sys.exit(1)
