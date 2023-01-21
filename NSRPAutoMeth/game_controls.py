from pyautogui import press
from time import sleep

def startCook():
    """ Starts cooking process. """
    print("Starting cooking process...")
    press('g')

def enterExitVehicle():
    """ Enters or exits vehicle. """
    press('f')

def lockUnlockVehicle():
    """ Locks or unlocks vehicle. """
    press('pagedown')

def moveBackToFront():
    """ Moves back to front of vehicle. """
    press('f')
    sleep(1)
    press('f')
    sleep(1)