import requests
import json
from datetime import datetime
from fake_useragent import UserAgent
import os
import sys
import logging


keys_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "keys.json")
feeds_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "feeds")
log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "run.log")

logger = logging.getLogger(__name__)
formatter = logging.basicConfig(filename=log_path, level=logging.INFO, format="%(asctime)s [%(levelname)s]  [%(filename)s] %(funcName)s: %(message)s")
feed_url = "https://www.metadefender.com/feeds/json"


def read_json(file):
    with open(file, "r") as json_file:
        data = json.load(json_file)
    return data


def write_json(json_obj, file):
    with open(file, "w") as json_file:
        json.dump(json_obj, json_file)
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
        if r.status_code == 200:
            try:
                data = r.json()
                feed_file = os.path.join(feeds_dir, "intel_metadefender_{}.json".format(
                    datetime.now().isoformat().split(".")[0].replace(":", "_")))
                if len(data) > 0:
                    write_json(file=feed_file, json_obj=data)
                    logger.info("Successfully saved in %s" % feed_file)
                else:
                    logger.warning("Empty feed, no data saved")
            except json.decoder.JSONDecodeError:
                logger.error("Empty feed file or bad json")
        else:
            logger.error("Bad HTTP response, got %d" % r.status_code)
    except requests.RequestException:
        logger.error("Information grabbing failed")


def metadefender_run():
    try:
        logger.info("Started")
        metadefender_grab(url=feed_url)
    except Exception:
        logger.error("Information gathering interrupted", exc_info=True)
        sys.exit(1)
