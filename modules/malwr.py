import requests
import sys
import os
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import time
from datetime import datetime
import json


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
    config = read_json(file=config_path)
    last_added_timestamp = datetime(*time.strptime(config.get("malwr").get("last_added"), "%Y-%m-%d %H:%M:%S")[:6])
    last_added_hash = config.get("malwr").get("last_added_hash")
    for data_item in reversed(raw_data):
        analysis_timestamp_raw = data_item["date"].replace(".", "").replace("am", "AM").replace("pm", "PM").replace("midnight", "12 AM")
        while True:
            try:
                analysis_timestamp = datetime.strptime(analysis_timestamp_raw, "%b %d, %Y, %I:%M %p")
                break
            except ValueError:
                pass
            try:
                analysis_timestamp = datetime.strptime(analysis_timestamp_raw, "%b %d, %Y, %I %p")
                break
            except ValueError:
                pass
            try:
                analysis_timestamp = datetime.strptime(analysis_timestamp_raw, "%B %d, %Y, %I:%M %p")
                break
            except ValueError:
                pass
            try:
                analysis_timestamp = datetime.strptime(analysis_timestamp_raw, "%B %d, %Y, %I %p")
                break
            except ValueError:
                pass
            finally:
                break
        added_hash = data_item.get("md5")
        if analysis_timestamp >= last_added_timestamp and added_hash != last_added_hash:
            filtered.append(data_item)
    config["malwr"]["last_added"] = analysis_timestamp.strftime("%Y-%m-%d %H:%M:%S")
    config["malwr"]["last_added_hash"] = added_hash
    write_json(json_obj=config, file=config_path)
    return filtered


def m_grab(url=None):
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
        data = parse_page(r.text)
        if data:
            data_filtered = filter_old(raw_data=data)
            feed_file = os.path.join(feeds_path, "intel_malwr_{}.json".format(datetime.now().isoformat().split(".")[0].replace(":", "_")))
            write_json(file=feed_file, json_obj=data_filtered)
        else:
            print("Empty HTTP response")
    else:
        print("Bad HTTP response, got %d" % r.status_code)
        sys.exit(1)


if __name__ == "__main__":
    feed_url = "https://malwr.com/analysis/?page=1"
    try:
        m_grab(url=feed_url)
    except Exception as e:
        print("Information gathering interrupted")
        print(e)
        sys.exit(1)
