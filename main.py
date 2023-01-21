from pytesseract import pytesseract
from concurrent.futures import ThreadPoolExecutor
from time import sleep, time
from NSRPAutoMeth import GameInformation, PATH_TO_TESSERACT


if __name__ == "__main__":
    pytesseract.tesseract_cmd = PATH_TO_TESSERACT
    GameInfo = GameInformation()
    with ThreadPoolExecutor(max_workers=3) as executor:
        while True:
            executor.submit(GameInfo.tick)
            curr_time = time()
            sleep(1 - (time() - curr_time))


