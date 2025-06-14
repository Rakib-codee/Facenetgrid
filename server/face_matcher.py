import os
import face_recognition
import numpy as np
import pickle

KNOWN_FACES_DIR = 'data/known_faces'


def load_known_faces():
    known_encodings = []
    known_names = []

    for file in os.listdir(KNOWN_FACES_DIR):
        if file.endswith('.pkl'):
            path = os.path.join(KNOWN_FACES_DIR, file)
            with open(path, 'rb') as f:
                data = pickle.load(f)
                known_encodings.append(data['encoding'])
                known_names.append(data['name'])

    return known_encodings, known_names


def match_face(incoming_encoding):
    known_encodings, known_names = load_known_faces()

    incoming_np = np.array(incoming_encoding)
    distances = face_recognition.face_distance(known_encodings, incoming_np)

    if len(distances) == 0:
        return "No known faces", None

    min_distance = min(distances)
    index = distances.tolist().index(min_distance)

    if min_distance < 0.5:
        return known_names[index], float(min_distance)
    else:
        return "Unknown", float(min_distance)
