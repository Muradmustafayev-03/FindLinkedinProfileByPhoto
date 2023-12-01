import dlib
import cv2

from .CustomLinkedin import CustomLinkedin
from .PhotoParser import PhotoParser
from ..utils import url_to_img


class DataCollector:
    """
    A class to collect  and combine the data about LinkedIn users.

    :param username: Username of LinkedIn account.
    :type username: str
    :param password: Password of LinkedIn account.
    :type password: str
    """
    def __init__(self, username, password):
        self.linkedin = CustomLinkedin(username, password)
        self.photo_parser = PhotoParser(username, password)
        self.face_detector = dlib.get_frontal_face_detector()

    def is_a_face(self, photo_url) -> bool:
        """
        Check if a given photo URL contains exactly one face.

        :param photo_url: The URL of the photo to analyze.
        :type photo_url: str

        :return: True if the photo contains exactly one face, False otherwise.
        :rtype: bool
        """
        img = url_to_img(photo_url)

        # Convert the image to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Return True if there is exactly one face on the photo
        return len(self.face_detector(gray)) == 1
