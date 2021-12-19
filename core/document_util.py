from typing import Optional

import numpy
from PIL import Image

from transform.four_point_transform import four_point_transform
import cv2
import imutils


def get_cropped_document(image_path: str) -> Optional[numpy.ndarray]:
    # load the image and compute the ratio of the old height
    # to the new height, clone it, and resize it
    image: numpy.ndarray = cv2.imread(image_path)
    ratio: float = image.shape[0] / 500.0
    orig: numpy.ndarray = image.copy()
    image = imutils.resize(image, height=500)
    # convert the image to grayscale, blur it, and find edges
    # in the image
    gray: numpy.ndarray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edged: numpy.ndarray = cv2.Canny(gray, 75, 200)

    # find the contours in the edged image, keeping only the
    # largest ones, and initialize the screen contour
    cnts: tuple[tuple[numpy.ndarray]] = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
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


def stitch_images(image: numpy.ndarray, *other_images: numpy.ndarray) -> Image:
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
