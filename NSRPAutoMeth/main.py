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
if __name__ != "__main__":
    from NSRPAutoMeth.constants import QUESTION_ANSWERS
    from NSRPAutoMeth.game_controller import GameController


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

    def __getText(self) -> str:
        
        """Finds text within left half of screen

        Returns
        -------
        str
            The text found within left half of window
        """
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
        img.save("last-screenshot.png")
        return " ".join(re.findall(r"'(.*?)'", str(self.__ocr.ocr('last-screenshot.png', cls=True))))

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
        logging.debug("Setup complete")


    def start(self):
        """ 
            Starts the bot 
        """
        print("Setting up...")
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
