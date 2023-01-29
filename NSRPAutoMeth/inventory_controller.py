import cv2
import numpy as np
import logging
if __name__ != "__main__":
    from NSRPAutoMeth.constants import LITHIUM_IMG, ACETONE_IMG, CENTER_INVENTORY_IMG

def __clean_lithium_img(rectangles) -> np.ndarray:
    """Cleans the lithium image"""
    new_rectangles = []
    for (x, y, w, h) in rectangles:
        new_rectangles.append([int(x - w/3), int(y - h/1.75), int(w * 1.75), int(h * 1.75)])
    return new_rectangles

def __clean_acetone_img(rectangles) -> np.ndarray:
    """Cleans the acetone image"""
    new_rectangles = []
    for (x, y, w, h) in rectangles:
        new_rectangles.append([int(x - w/2), int(y - h/3.25), int(w * 2), int(h * 1.75)])
    return new_rectangles

def __clean_center_inventory_img(rectangles) -> np.ndarray:
    """Cleans the center inventory image"""
    new_rectangles = []
    for (x, y, w, h) in rectangles:
        # reduce width to center 10th and reduce height to center 2 times
        new_rectangles.append([int(x + w/2), int(y + h/3.35), int(w * .2), int(h * .05)])
    return new_rectangles

def find_matches(imgPath: str, template: np.ndarray, threshold: int = .80, results = -1) -> list:
    """Finds matches of template within image"""
    logging.debug(f"Finding matches of template within image: {imgPath}")
    img = cv2.imread(imgPath, cv2.IMREAD_UNCHANGED)
    result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    yloc, xloc = np.where(result >= threshold)
    rectangles = []
    for (x, y) in zip(xloc, yloc):
        rectangles.append([int(x), int(y), int(template.shape[1]), int(template.shape[0])])
        logging.debug(f"Found match at: {x}, {y}")
    rectangles, weight = cv2.groupRectangles(rectangles, 1, 0.2)
    if results != -1:
        # order by weight
        rectangles = sorted(rectangles, key=lambda x: x[2], reverse=True)
        rectangles = rectangles[:results]
    # clean img if certain templates
    if template is LITHIUM_IMG:
        return __clean_lithium_img(rectangles)
    elif template is ACETONE_IMG:
        return __clean_acetone_img(rectangles)
    elif template is CENTER_INVENTORY_IMG:
        return __clean_center_inventory_img(rectangles)
    else:
        return rectangles

def draw_rectangles(imgPath: str, rectangles, name = "item", color = (0,255,255)):
    """Draws rectangles on image"""
    logging.debug(f"Drawing rectangles on image: {imgPath}")
    img = cv2.imread(imgPath, cv2.IMREAD_UNCHANGED)
    for (x, y, w, h) in rectangles:
        cv2.putText(img, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
    cv2.imwrite(imgPath, img)
    return img

def draw_point(imgPath: str, point, name = "", color = (0,255,255)):
    """Draws point on image"""
    logging.debug(f"Drawing point on image: {imgPath}")
    img = cv2.imread(imgPath, cv2.IMREAD_UNCHANGED)
    cv2.putText(img, name, (point[0], point[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    cv2.circle(img, (point[0], point[1]), 10, color, 2)
    cv2.imwrite(imgPath, img)
    return img