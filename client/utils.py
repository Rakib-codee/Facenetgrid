import json
import socket
import os
import pickle

SERVER_IP = '127.0.0.1'
SERVER_PORT = 5000

def send_face_to_server(encoding):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((SERVER_IP, SERVER_PORT))

        payload = {
            "type": "match",
            "encoding": encoding
        }
        sock.send(json.dumps(payload).encode())

        response = sock.recv(4096).decode()
        data = json.loads(response)
        sock.close()
        return data.get("name"), data.get("distance")
    except Exception as e:
        print("[CLIENT ERROR]", e)
        return None, None

def save_new_face(name, encoding):
    if not os.path.exists("data/known_faces"):
        os.makedirs("data/known_faces")

    file_path = f"data/known_faces/{name}.pkl"
    with open(file_path, 'wb') as f:
        pickle.dump({"name": name, "encoding": encoding}, f)
