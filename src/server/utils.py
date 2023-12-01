import urllib

import numpy as np
import cv2


def url_to_img(url: str) -> np.array:
    """
    Download an image from the given URL and convert it to a NumPy array.

    :param url: The URL of the image to download.
    :type url: str

    :return: If the image is successfully downloaded and decoded, returns the NumPy array
             representing the image; otherwise, returns None.
    :rtype: np.array
    """
    req = urllib.urlopen(url)
    arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
    img = cv2.imdecode(arr, -1)
    return img
