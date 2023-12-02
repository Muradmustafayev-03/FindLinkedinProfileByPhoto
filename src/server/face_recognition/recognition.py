import face_recognition
import numpy as np


def face_matching_probability(target_face: np.array, photo: np.array) -> float:
    """
    Calculate the probability of a given face being present in a photo.

    :param target_face: The face for which the probability is calculated.
    :type target_face: np.array

    :param photo: The photo in which the presence of the face is checked.
    :type photo: np.array

    :return: The probability of the face being present in the photo.
    :rtype: float
    """
    # Find face locations in the target face and the photo
    extracted_face = face_recognition.face_locations(target_face)
    faces_on_photo = face_recognition.face_locations(photo)

    # If no faces are found in either the target face or the photo, return 0.0
    if not extracted_face or not faces_on_photo:
        return 0.0

    # Encode the target face and all faces in the photo
    face_encoding = face_recognition.face_encodings(target_face, extracted_face)[0]
    photo_encodings = face_recognition.face_encodings(photo, faces_on_photo)

    # Calculate distances between the target face and all faces in the photo
    distances = face_recognition.face_distance(photo_encodings, face_encoding)

    # Calculate similarities by subtracting distances from 1
    similarities = [1 - dist for dist in distances]

    # Return the maximum similarity as the probability of the face being present
    return max(similarities)
