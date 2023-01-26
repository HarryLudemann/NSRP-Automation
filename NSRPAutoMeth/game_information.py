from PIL import ImageGrab
from pytesseract.pytesseract import image_to_string
from pydirectinput import press 
from NSRPAutoMeth.questions import QUESTION_ANSWERS
from NSRPAutoMeth.game_controls import startCook, moveBackToFront
import logging
from pyautogui import size


class GameInformation:
    _consecutiveFailedTicks = 0
    _cooking = False
    def _getText(self) -> str:
        """ Takes screenshot of screen and returns text detected."""
        img = ImageGrab.grab()
        img.save("last-screenshot.png")
        text = image_to_string(img)
        # if a line contains certain symbols the then remove
        newLines = []
        for line in text.splitlines():
            if any(char in line for char in ["[", "]", "|"]):
                continue
            if line == "":
                continue
            newLines.append(line)
        return "\n".join(newLines).strip()

    def _getProductionPercent(self, imageText: str) -> str:
        """ Returns production time of given images text. """
        if "production:" in imageText:
            productionTime = imageText.split("production:")[1].split("%")[0]
            return productionTime.strip()

    def _getQuestion(self, imageText: str) -> str:
        """ Returns question of given images text. """
        if "?" in imageText:
            for question in QUESTION_ANSWERS:
                if question in imageText:
                    return question

    def _answerQuestion(self, question: str, imageText: str) -> None:
        """ Answers question. """
        # check question is in the dict
        if question not in QUESTION_ANSWERS:
            logging.info(f'Question: "{question}" not in dict.')
            return
        answer = QUESTION_ANSWERS[question]
        if answer in imageText:
            # get the number at the start of the line of where answer is
            answerIndex = imageText.index(answer)
            # get just the third character before the answer
            number = imageText[answerIndex - 3]
            press(number)
            press(number)
            press(number)
            logging.info(f'Answered Question: "{question}"')

    def tick(self) -> None:
        """ Runs every tick. """
        if not self._cooking:
            startCook()
            logging.info("Started cook")
            self._cooking = True
            return
        imageText = self._getText()
        # check if image contains question or production percent
        flag = False
        if "?" in imageText: # if question 2
            question = self._getQuestion(imageText)
            self._answerQuestion(question, imageText)
            flag = True
        elif "production:" in imageText: # if production percent is showing
            productionPercent = self._getProductionPercent(imageText)
            logging.info(f"Production: {productionPercent}%")
            flag = True
        else:
            logging.warning("No question or production percent detected: " + imageText)
        # count tick and/or failed tick
        if flag:
            self._consecutiveFailedTicks = 0
        else:
            self._consecutiveFailedTicks += 1
        # if over five failed ticks then restart
        if self._consecutiveFailedTicks > 5:
            logging.info("Cooking Completed or Failed.")
            logging.info("Restarting cooking process...")
            self._cooking = False
            self._consecutiveFailedTicks = 0
            moveBackToFront()
