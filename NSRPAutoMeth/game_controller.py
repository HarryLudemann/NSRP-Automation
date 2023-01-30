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
        self.open_close_glovebox = parser.get('Keys', 'inventory')
        self.open_close_inventory = parser.get('Keys', 'glovebox')
        self.inventory_quick_move = parser.get('Keys', 'inventory_quick_move')

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

    def openCloseInventory(self):
        """ Opens or closes inventory. """
        self.__pressKey(self.open_close_inventory)

    def openCloseGloveBox(self):
        """ Opens or closes inventory. """
        self.__pressKey(self.open_close_glovebox)

    def moveBackToFront(self):
        """ Moves back to front of vehicle. """
        self.enterExitVehicle()
        self.lockUnlockVehicle()
        time.sleep(1)
        self.enterExitVehicle()
        time.sleep(1)
        self.lockUnlockVehicle()

    def holdInventoryQuickMove(self):
        """ Holds inventory quick move key. """
        pydirectinput.keyDown(self.inventory_quick_move)

    def releaseInventoryQuickMove(self):
        """ Releases inventory quick move key. """
        pydirectinput.keyUp(self.inventory_quick_move)

    def click(self, x, y):
        """ Clicks at given coordinates. """
        pydirectinput.click(x, y)

    def set_move_count(self, number: int, center: tuple):
        """Sets the inventory move count to a given number"""
        # click the point
        self.click(center[0], center[1])
        # press right arrow twice
        self.press("right")*2
        # press backspace twice
        self.press("backspace")*2
        # press number
        self.press(str(number))
