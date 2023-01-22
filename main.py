from pytesseract import pytesseract
from time import sleep, time
from NSRPAutoMeth import GameInformation
import logging 
from configparser import ConfigParser

parser = ConfigParser()
parser.read('settings.ini')
tick_interval: int = int(parser.get('Basic', 'tick_interval'))

open("log.txt", "w").close() # clear log.txt
logging.basicConfig(
    filename="log.txt", 
    level=logging.INFO, 
    format="%(asctime)s:%(levelname)s:%(message)s")
logging.getLogger().addHandler(logging.StreamHandler()) # print log to console

if __name__ == "__main__":
    pytesseract.tesseract_cmd = parser.get('Basic', 'path_to_tesseract')
    GameInfo = GameInformation()
    # countdown to start from 10
    for i in range(10, 0, -1):
        logging.info("Starting in: " + str(i))
        sleep(1)
    # main loop
    while True:
        GameInfo.tick()
        curr_time = time()
        sleep(tick_interval - (time() - curr_time))

