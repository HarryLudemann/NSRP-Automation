import cv2

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
