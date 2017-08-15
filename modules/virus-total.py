import requests
import json
from datetime import datetime
import os
import sys
import logging


keys_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "keys.json")
feeds_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docker-persistance/logstash/feeds")
log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "run.log")


def read_json(file):
    with open(file, "r") as json_file:
        data = json.load(json_file)
    return data


def write_json(json_obj, file):
    with open(file, "w") as json_file:
        json.dump(json_obj, json_file)
        json_file.write("\n")
    return


def vt_grab(url=None):
    keys = read_json(keys_file)
    payload = {
        "key": keys["keys"].get("virus-total")
    }
    try:
        r = requests.get(url, params=payload)
    except requests.RequestException:
        logger.error("Information grabbing failed")
        sys.exit(1)
    if r.status_code == 200:
        try:
            data = r.json()
            if data.get("result") == 1:
                grabbed_docs = []
                everything = []
                for i in data.get("notifications"):
                    grabbed_docs.append(i.get("id"))
                    everything.append(i)
                feed_file = os.path.join(feeds_path, "intel_virus-total_{}.json".format(datetime.now().isoformat().split(".")[0].replace(":", "_")))
                if len(everything) > 0:
                    write_json(file=feed_file, json_obj=everything)
                    logger.info("Successfully saved in %s" % feed_file)
                else:
                    logger.warning("Empty feed, no data saved")
                # delete grabbed docs from notifications
                requests.post("https://www.virustotal.com/intelligence/hunting/delete-notifications/programmatic/", params=payload, json=grabbed_docs)
        except json.decoder.JSONDecodeError:
            logger.error("Empty feed file or bad json")
            sys.exit(1)
    else:
        logger.error("Bad HTTP response, got %d" % r.status_code)
        sys.exit(1)


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    formatter = logging.basicConfig(filename=log_path, level=logging.INFO, format="%(asctime)s [%(levelname)s]  [%(filename)s] %(funcName)s: %(message)s")
    feed_url = "https://www.virustotal.com/intelligence/hunting/notifications-feed/"
    try:
        logger.info("Started")
        vt_grab(url=feed_url)
    except Exception:
        logger.error("Information gathering interrupted", exc_info=True)
        sys.exit(1)
