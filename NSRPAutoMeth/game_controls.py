import pydirectinput
import time
from configparser import ConfigParser

_parser = ConfigParser()
_parser.read('settings.ini')
cook_key = _parser.get('Keys', 'cook')
enter_exit_key = _parser.get('Keys', 'enter_exit')
lock_unlock_key = _parser.get('Keys', 'lock_unlock_door')

def _pressKey(key: str):
    """ Presses key. """
    pydirectinput.keyDown(key)
    time.sleep(0.5)
    pydirectinput.keyUp(key)

def startCook():
    """ Starts cooking process. """
    _pressKey(cook_key)
    _pressKey(cook_key)

def enterExitVehicle():
    """ Enters or exits vehicle. """
    _pressKey(enter_exit_key)

def lockUnlockVehicle():
    """ Locks or unlocks vehicle. """
    _pressKey(lock_unlock_key)

def moveBackToFront():
    """ Moves back to front of vehicle. """
    enterExitVehicle()
    time.sleep(1)
    enterExitVehicle()
    time.sleep(1)