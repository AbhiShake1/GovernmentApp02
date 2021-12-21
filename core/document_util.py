import base64
import io
from typing import Optional

import numpy as np
from PIL import Image

from core.transform.four_point_transform import four_point_transform
import cv2
import imutils


def get_cropped_document(base64_str: str) -> Optional[np.ndarray]:
    # load the image from base64 and compute the ratio of the old height
    # to the new height, clone it, and resize it
    base64_bytes = base64.urlsafe_b64decode(base64_str)
    image: np.ndarray = np.array(Image.open(io.BytesIO(base64_bytes)))
    ratio: float = image.shape[0] / 500.0
    orig: np.ndarray = image.copy()
    image = imutils.resize(image, height=500)
    # convert the image to grayscale, blur it, and find edges
    # in the image
    gray: np.ndarray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edged: np.ndarray = cv2.Canny(gray, 75, 200)

    # find the contours in the edged image, keeping only the
    # largest ones, and initialize the screen contour
    cnts: tuple[tuple[np.ndarray]] = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = tuple(sorted(cnts, key=cv2.contourArea, reverse=True)[:5])
    screenCnt = None
    # loop over the contours
    for c in cnts:
        # approximate the contour
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        # if our approximated contour has four points, then we
        # can assume that we have found our screen
        if len(approx) == 4:
            screenCnt = approx
            break
    if screenCnt is None:
        return

    # apply the four point transform to obtain a top-down
    # view of the original image
    warped = four_point_transform(orig, screenCnt.reshape(4, 2) * ratio)
    return imutils.resize(warped, height=650)


'''
def stitch_images(image: np.ndarray, *other_images: np.ndarray) -> Image:
    data = Image.fromarray(image)
    # since first image is mandatory and others are optional
    new_image = Image.new('RGB', ((len(other_images) + 1) * data.width, data.height), (250, 250, 250))
    new_image.paste(data, (0, 0))
    for index, image in enumerate(other_images):
        new_image.paste(Image.fromarray(image), (data.width * (index + 1), 0))
        new_image.paste(data, (0, 0))
    return new_image
    # new_image.save("merged_image.jpg", "JPEG")
    # new_image.show()
'''


def stitch_images_to_pdf(image: np.ndarray, *other_images: np.ndarray):
    data = Image.fromarray(image)
    other_data = [Image.fromarray(i) for i in other_images]
    buff = io.BytesIO()
    data.save(buff, 'PDF', save_all=True, append_images=other_data[0:])
    base64_pdf = base64.b64encode(buff.getvalue())
    return base64_pdf
