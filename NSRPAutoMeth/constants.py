import cv2
import numpy as np

# key is a sentence or word that is within the question, 
# value is a word or sentence within the answer
QUESTION_ANSWERS = {
    "The filter is clogged": "Replace the filter",
    "sprinkles": "Add them now",
    "This smoke is kind": "windmill",
    "Christmas": "be a present",
    "propane": "Replace",
    "mother": "Ignore",
    "smell": "friend",
    "acetone on the ground": "Open a window",
    "take a shit": "hold it",
    "turning into crystal": "Raise the temp",
    "glass pieces": "NO",
}

# all measurements are in kg
JOURNEY_BOOT_CAPACITY = 488
JOURNEY_GLOVEBOX_CAPACITY = 88
PLAYER_CAPACITY = 30

# items
LITHIUM = 0.75
ACETONE = 0.75
CHEMICAL_KIT = 10

# images for image matching
LITHIUM_IMG = cv2.imread('images/data/lithium.jpg', cv2.IMREAD_UNCHANGED)
ACETONE_IMG = cv2.imread('images/data/acetone.jpg', cv2.IMREAD_UNCHANGED)
METH_IMG = cv2.imread('images/data/lithium.jpg', cv2.IMREAD_UNCHANGED)
CENTER_INVENTORY_IMG = cv2.imread('images/data/center_inventory.jpg', cv2.IMREAD_UNCHANGED)
CENTER_INVENTORY_IMG = cv2.cvtColor(np.array(CENTER_INVENTORY_IMG), cv2.COLOR_BGR2GRAY)
CENTER_INVENTORY_IMG = cv2.cvtColor(CENTER_INVENTORY_IMG, cv2.COLOR_GRAY2BGR)

# log images
IMAGE_PATH = "images/log/last-inventory-ss.jpg"
LEFT_IMAGE_PATH = "images/log/left-half.jpg"
RIGHT_IMAGE_PATH = "images/log/right-half.jpg"
CENTER_IMAGE_PATH = "images/log/center-half.jpg"