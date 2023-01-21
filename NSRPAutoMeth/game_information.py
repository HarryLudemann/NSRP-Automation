from PIL import ImageGrab
from pytesseract.pytesseract import image_to_string
from pyautogui import press 
from NSRPAutoMeth.constants import QUESTION_ANSWERS
from NSRPAutoMeth.game_controls import startCook, moveBackToFront

class GameInformation:
    consecutiveFailedTicks = 0
    cooking = False
    def _getText(self) -> str:
        """ Takes screenshot of screen and returns text detected."""
        # img = Image.open("images/Question.png")
        # img = Image.open("images/ProductionPercent.png")
        img = ImageGrab.grab()
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
        if "Meth production:" in imageText:
            productionTime = imageText.split("Meth production:")[1].split("%")[0]
            return productionTime.strip()

    def _getQuestion(self, imageText: str) -> str:
        """ Returns question of given images text. """
        if "?" in imageText:
            for question in QUESTION_ANSWERS:
                if question in imageText:
                    return question

    def _answerQuestion(self, question: str, imageText: str) -> None:
        """ Answers question. """
        answer = QUESTION_ANSWERS[question]
        if answer in imageText:
            # get the number at the start of the line of where answer is
            answerIndex = imageText.index(answer)
            # get just the third character before the answer
            number = imageText[answerIndex - 3]
            press(number)

    def tick(self) -> None:
        """ Runs every tick. """
        if not self.cooking:
            startCook()
            self.cooking = True
            return
        imageText = self._getText()
        # check if image contains question or production percent
        flag = False
        if "Meth production:" in imageText: # if production percent is showing
            productionPercent = self._getProductionPercent(imageText)
            print(f"Production: {productionPercent}%")
            flag = True
        if "?" in imageText: # if question 2
            question = self._getQuestion(imageText)
            self._answerQuestion(question, imageText)
            print(f'Answered Question: "{question}"')
            flag = True
        # count tick and/or failed tick
        if flag:
            self.consecutiveFailedTicks = 0
        else:
            self.consecutiveFailedTicks += 1
        # if over five failed ticks then restart
        if self.consecutiveFailedTicks > 5:
            self.cooking = False
            self.consecutiveFailedTicks = 0
            moveBackToFront()
