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
    # enlarge rectangles
    new_rectangles = []
    for (x, y, w, h) in rectangles:
        new_rectangles.append([int(x - w/3), int(y - h/1.75), int(w * 1.75), int(h * 1.75)])
    return new_rectangles

def draw_rectangles(imgPath: str, rectangles, name = "item", color = (0,255,255)):
    """Draws rectangles on image"""
    logging.debug(f"Drawing rectangles on image: {imgPath}")
    img = cv2.imread(imgPath, cv2.IMREAD_UNCHANGED)
    for (x, y, w, h) in rectangles:
        cv2.putText(img, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
    cv2.imwrite(imgPath, img)
    return img