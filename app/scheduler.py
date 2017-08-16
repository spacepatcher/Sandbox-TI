import schedule
import time
from modules.hybrid_analysis import ha_run
from modules.malwr import malwr_run
from modules.metadefender import metadefender_run
# from modules.virus_total import vt_run


schedule.every(90).minutes.do(ha_run)
schedule.every(60).minutes.do(malwr_run)
schedule.every(24).hours.do(metadefender_run)
# schedule.every(10).minutes.do(vt_run)


while True:
    schedule.run_pending()
    time.sleep(1)
