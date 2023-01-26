import pydirectinput
import time
from configparser import ConfigParser

class GameController:
    
    """
    Class contains the main bot loop and manages the bots state.

    Attributes
    -------
    parser : ConfigParser
        ConfigParser object containing the config file

    Methods
    -------
    startCook()
        Starts cooking process
    enterExitVehicle()
        Enters or exits vehicle
    lockUnlockVehicle()
        Locks or unlocks vehicle
    moveBackToFront()
        Moves back to front of vehicle, from production position
    __pressKey(key: str)
        Presses given key


    """
    def __init__(self, parser: ConfigParser):
        self.cook_key = parser.get('Keys', 'cook')
        self.enter_exit_key = parser.get('Keys', 'enter_exit')
        self.lock_unlock_key = parser.get('Keys', 'lock_unlock_door')

    def __pressKey(self, key: str):
        """ Presses key. """
        pydirectinput.keyDown(key)
        time.sleep(0.5)
        pydirectinput.keyUp(key)

    def startCook(self):
        """ Starts cooking process. """
        self.__pressKey(self.cook_key)
        self.__pressKey(self.cook_key)

    def enterExitVehicle(self):
        """ Enters or exits vehicle. """
        self.__pressKey(self.enter_exit_key)

    def lockUnlockVehicle(self):
        """ Locks or unlocks vehicle. """
        self.__pressKey(self.lock_unlock_key)

    def moveBackToFront(self):
        """ Moves back to front of vehicle. """
        self.enterExitVehicle()
        time.sleep(1)
        self.enterExitVehicle()
        time.sleep(1)