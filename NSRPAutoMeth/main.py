from PIL import ImageGrab
from paddleocr import PaddleOCR
import re
from pydirectinput import press 
import logging
from win32gui import FindWindow, GetWindowRect
from configparser import ConfigParser
from time import sleep, time
import logging 
from pyautogui import getAllTitles
from os.path import exists
from warnings import filterwarnings
import cv2
import numpy as np
from PIL import Image
if __name__ != "__main__":
    from NSRPAutoMeth.constants import QUESTION_ANSWERS, LITHIUM_IMG, METH_IMG, ACETONE_IMG, CENTER_INVENTORY_IMG
    from NSRPAutoMeth.game_controller import GameController
    from NSRPAutoMeth.inventory_controller import find_matches, draw_rectangles, draw_point
    


class NSRPAutoMeth:
    """
    Class contains the main bot loop and manages the bots state.

    Methods
    -------
    start() 
        Starts the main loop of the bot
    __setup()
        Sets up the bot
    __tick()
        Manages the bot state, called every set interval
    __getText()
        Takes screenshot of screen and returns text detected
    __getProductionPercent(imageText: str)
        Returns production time found in given text
    __getQuestion(imageText: str)
        Returns question found in given text
    """
    __consecutiveFailedTicks = 0
    __cooking = False

    def __imageToText(self, imgPath: str) -> str:
        return " ".join(re.findall(r"'(.*?)'", str(self.__ocr.ocr(imgPath, cls=True))))

    def __getText(self) -> str:
        
        """Finds text within left half of screen

        Returns
        -------
        str
            The text found within left half of window
        """
        imgPath = "images/log/last-ss.jpg"
        if self.use_game_window[0] == "t": # if using game window to take screenshot
            # get window size
            window_handle = FindWindow(None, self.window_name)
            window_rect   = GetWindowRect(window_handle)
            # screenshot left half of screen
            logging.debug("Window rect: " + str(window_rect))
            img = ImageGrab.grab(bbox=(window_rect[0], window_rect[1], window_rect[2] / 3, window_rect[3]))
        else: # screenshot and crop to left half
            img = ImageGrab.grab(bbox=(0, self.resolution_y/5, self.resolution_x / 3, self.resolution_y))
        # save image
        img.save(imgPath)
        return self.__imageToText(imgPath)

    def __getProductionPercent(self, text: str) -> str:
        """Returns production time of found in given text 

        Parameters
        ----------
        text : str
            The text to find production percentage in

        Returns
        -------
        str
            The production percentage found within given text
        """
        productionPercent = re.search(r"\d+(?=%)", text)
        if productionPercent is None:
            return None
        return productionPercent.group(0)

    def __getQuestion(self, text: str) -> str:
        """Finds question in given text

        Parameters
        ----------
        text : str
            The text to find question in

        Returns
        -------
        str
            The key to  a question found within text, if one is found
        """
        for question in QUESTION_ANSWERS:
            if question in text:
                return question

    def __answerQuestion(self, question: str, text: str) -> None:
        """Finds question's answer, then presses corresponding number

        Parameters
        ----------
        text : str
            The text to find answer in
        question : str
            The question to answer
        """
        answer = QUESTION_ANSWERS[question]
        try:
            answerIndex = text.index(answer)
        except ValueError:
            logging.warning(
                "Answer not found in text after question was found")
            return
        number = text[answerIndex - 3]
        press(number)*3
        logging.info(f'Answered Question: "{question}"')

    def __count_items(self, imgPath: str, template):
        """Counts the number of items a given template has in image"""
        rectangles = find_matches(imgPath, template)
        tempImgPath = "images/log/last-temp.jpg"
        count = 0
        img = cv2.imread(imgPath)
        for (x, y, w, h) in rectangles:
            tempRectImg = img[y:y+h, x:x+w]
            # make white color more visible
            tempRectImg = cv2.cvtColor(tempRectImg, cv2.COLOR_BGR2GRAY)
            tempRectImg = cv2.cvtColor(tempRectImg, cv2.COLOR_GRAY2BGR)
            tempRectImg = cv2.resize(tempRectImg, (tempRectImg.shape[1] * 2, tempRectImg.shape[0] * 2), interpolation=cv2.INTER_CUBIC)
            cv2.imwrite(tempImgPath, tempRectImg)
            tempText = self.__imageToText(tempImgPath)
            # get number after g and before x
            tempText = re.search(r"(?<=g)\d+(?=x)", tempText)
            if tempText is None:
                logging.warning("Failed to find count")
                continue
            count += int(tempText.group(0))
        return count

    def __move_meth(self, leftImgPath: str):
        """Move meth from inventory to glove box"""
        meth_rectangles = find_matches(leftImgPath, METH_IMG)
        self.game_controller.holdInventoryQuickMove()
        sleep(0.1)
        if len(meth_rectangles) == 0:
            logging.info("No meth found in inventory")
        if len(meth_rectangles) > 0:
            logging.info(f"Moved x{len(meth_rectangles)} meth to glove box")
            for rectangle in meth_rectangles:
                # click center of rectangle
                self.game_controller.click(rectangle[0] + rectangle[2] / 2, rectangle[1] + rectangle[3] / 2)
                sleep(0.1)
        self.game_controller.releaseInventoryQuickMove()

    def __check_supplies(self) -> None:
        """Checks for low supplies and refills if necessary. 
        This includes food, water, lithium, acetone, and meth"""
        logging.info("Checking supplies")
        imgPath = "images/log/last-inventory-ss.jpg"
        leftImgPath = "images/log/left-half.jpg"
        rightImgPath = "images/log/right-half.jpg"
        centerImgPath = "images/log/center-half.jpg"
        img = ImageGrab.grab()
        img.save(imgPath)
        # leftImg = img.crop((img.width / 2, 0, img.width, img.height)) # right side for debug
        leftImg = img.crop((0, 0, img.width / 2, img.height)) # left side
        leftImg.save(leftImgPath)
        rightImg = img.crop((img.width / 2, 0, img.width, img.height)) # right side
        rightImg.save(rightImgPath)

        # move meth in player inventory to glove box
        self.__move_meth(leftImgPath)

        ACETONE_PER_COOK = 5
        LITHIUM_PER_COOK = 2
        required_lithium, required_acetone = 0, 0
        # check if supplies are low
        if (required_lithium := LITHIUM_PER_COOK - self.__count_items(leftImgPath, LITHIUM_IMG)) > 0:
            logging.info("Lithium low, refilling")
            if self.__count_items(rightImgPath, LITHIUM_IMG) >= required_lithium:
                logging.info("Found enough lithium in right half of screen")
        if (required_acetone := ACETONE_PER_COOK - self.__count_items( leftImgPath, ACETONE_IMG)) > 0:
            logging.info("Acetone low, refilling")
            if self.__count_items(rightImgPath, ACETONE_IMG) >= required_acetone:
                logging.info("Found enough acetone in right half of screen")
        # check if food and water are low

        # refill supplies
        # find acetone and lithium in inventory

        # draw rectangles
        lithium_rectangles = find_matches(imgPath, LITHIUM_IMG)
        draw_rectangles(imgPath, lithium_rectangles, "Lithium")

        acetone_rectangles = find_matches(imgPath, ACETONE_IMG, 0.6)
        draw_rectangles(imgPath, acetone_rectangles, "ACETONE")

        # get center 22th of screenCENTER_INVENTORY
        CENTER_RATIO = 50
        centerImg = img.crop((img.width / 2 - img.width / CENTER_RATIO, 0, img.width / 2 + img.width / CENTER_RATIO, img.height))
        # make white text easier to read
        centerImg = cv2.cvtColor(np.array(centerImg), cv2.COLOR_BGR2GRAY)
        centerImg = cv2.cvtColor(centerImg, cv2.COLOR_GRAY2BGR)
        # save image
        centerImg = Image.fromarray(centerImg)
        centerImg.save(centerImgPath)
        center_rectangles = find_matches(centerImgPath, CENTER_INVENTORY_IMG, 0.4, 1)
        draw_rectangles(centerImgPath, center_rectangles, "Center")
        # draw circle on imgPath with center of center rectangle, add orignal pixels to get accurate center
        if len(center_rectangles) > 0:
            center_rectangle = center_rectangles[0]
            center_x = (center_rectangle[0] + center_rectangle[2] / 2) + img.width / 2 - img.width / CENTER_RATIO
            center_y = center_rectangle[1] + center_rectangle[3] / 2
            draw_point(imgPath, (int(center_x), int(center_y)), "Center")
        
    

    def __check_for_information(self, text) -> bool:
        """Checks for question or production percentage within left half of screen"""
        flag = False
        question = self.__getQuestion(text)
        if question is not None:
            self.__answerQuestion(question, text)
            flag = True
        if "production:" in text: # production percent 
            productionPercent = self.__getProductionPercent(text)
            if productionPercent == None:
                logging.warning("Production percent failed, 'production:' found but no percent")
            else:
                logging.info(f"Production: {productionPercent}%")
                flag = True
        return flag

    def __tick(self) -> None:
        """ Runs every tick managing the bots state"""
        if not self.__cooking:
            self.__check_supplies()
            self.game_controller.startCook()
            self.__cooking = True
            logging.info("Started cook")
            return
        text = self.__getText()
        found_info = self.__check_for_information(text)
        # log if tick found info question or production percentage
        if found_info:
            self.__consecutiveFailedTicks = 0
        else:
            logging.warning("No question or production percent detected")
            logging.debug("Detected Text: " + text)
            self.__consecutiveFailedTicks += 1
        # if over five failed ticks then restart
        if self.__consecutiveFailedTicks > 5:
            logging.warning("Restarting cook, 5 failed ticks")
            self.__cooking = False
            self.__consecutiveFailedTicks = 0
            self.game_controller.moveBackToFront()


    def __setup(self):
        """ Sets up the bots logging and loads the settings config file """
        # clear current log setup
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        logging.basicConfig(
            filename="log.txt", 
            level=logging.NOTSET,
            format="%(asctime)s:%(levelname)s:%(message)s")
        logging.getLogger().addHandler(logging.StreamHandler()) # print log to console
        parser = ConfigParser()
        if not exists("settings.ini"):
            logging.error("settings.ini not found")
            exit()
        parser.read('settings.ini')
        self.tick_interval: int = int(parser.get('Basic', 'tick_interval'))
        self.countdown = int(parser.get('Basic', 'countdown'))
        self.window_name = parser.get('Setup', 'window_name')
        self.game_controller = GameController(parser)
        self.window_exist_check = parser.get('Debug', 'window_exist_check')
        self.use_game_window = parser.get('Debug', 'use_game_window')
        self.resolution_x, self.resolution_y = parser.get('Debug', 'resolution').split("x")
        self.resolution_y = int(self.resolution_y.split(" ")[0])
        self.resolution_x = int(self.resolution_x)
        clear_log = parser.get('Debug', 'clear_log')
        if clear_log[0] == "t":
            open("log.txt", "w").close() # clear log.txt
        logging.root.setLevel(
            getattr(logging, parser.get('Debug', 'log_level').split(" ")[0].upper(), None))
        filterwarnings(action='ignore', category=DeprecationWarning, message='`np.bool8` is a deprecated alias for `np.bool_')
        logging.debug("Setup complete")


    def start(self):
        """ 
            Starts the bot 
        """
        self.__ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
        self.__setup()
        # check if game window is open
        if self.window_exist_check[0] == "t"  and self.window_name not in getAllTitles():
            logging.error("Game window not found, check settings.ini or disable check")
            exit()
        # countdown to start from 10
        for i in range(self.countdown, 0, -1):
            logging.info("Starting in: " + str(i))
            sleep(1)
        # main loop
        while True:
            self.__tick()
            curr_time = time()
            sleep(self.tick_interval - (time() - curr_time))
