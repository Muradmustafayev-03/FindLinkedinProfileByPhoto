import dlib
import cv2

from .CustomLinkedin import CustomLinkedin
from .PhotoParser import PhotoParser
from src.server.common import url_to_img


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

        self.root_url = 'https://www.linkedin.com'
        self.offset = 0

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

    def search(self, chunk_size: int = 100, **kwargs):
        """
                Search for LinkedIn profiles based on specified criteria.

                :param chunk_size: Number of profiles to fetch in each iteration. Defaults to 100.
                :type chunk_size: int

                :param kwargs: Additional search criteria as key-value pairs.
                :type kwargs: dict

                :return: Generator that yields profiles with photo URLs.
                :rtype: Interator[dict]
                """
        for profile in self.linkedin.search_people(kwargs, limit=chunk_size, offset=self.offset):
            profile_id = profile['public_id']
            profile_url = f'{self.root_url}/in/{profile_id}'
            photo_url = self.photo_parser.get_photo(profile_url)

            if photo_url and self.is_a_face(photo_url):
                profile['url'] = profile_url
                profile['photo'] = photo_url
                yield profile
            else:
                print(f"Couldn't distinguish {profile['name']}'s from their profile photo: {photo_url}")

            self.offset += 1
