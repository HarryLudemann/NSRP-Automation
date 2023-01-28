import cv2
import numpy as np
import logging

def find_matches(imgPath: str, template: np.ndarray) -> list:
    """Finds matches of template within image"""
    logging.debug(f"Finding matches of template within image: {imgPath}")
    img = cv2.imread(imgPath, cv2.IMREAD_UNCHANGED)
    result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    threshold = .80
    yloc, xloc = np.where(result >= threshold)
    rectangles = []
    for (x, y) in zip(xloc, yloc):
        rectangles.append([int(x), int(y), int(template.shape[1]), int(template.shape[0])])
        logging.debug(f"Found match at: {x}, {y}")
    rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)
    return rectangles

def draw_rectangles(imgPath, rectangles):
    """Draws rectangles on image"""
    logging.debug(f"Drawing rectangles on image: {imgPath}")
    img = cv2.imread(imgPath, cv2.IMREAD_UNCHANGED)
    for (x, y, w, h) in rectangles:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0,255,255), 2)
    cv2.imwrite(imgPath, img)
    return img
