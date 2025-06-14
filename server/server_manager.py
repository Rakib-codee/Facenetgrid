import json
from face_matcher import match_face
from db_manager import log_match_result

def handle_client(client_socket, addr):
    try:
        while True:
            data = client_socket.recv(4096)
            if not data:
                break

            payload = json.loads(data.decode())
            face_encoding = payload.get('face_encoding')
            client_id = payload.get('client_id', 'Unknown')

            if face_encoding:
                name, distance = match_face(face_encoding)
                result = {
                    "name": name,
                    "distance": distance
                }
                log_match_result(client_id, name, distance)
                client_socket.send(json.dumps(result).encode())
            else:
                client_socket.send(json.dumps({"error": "No face encoding received"}).encode())

    except Exception as e:
        print(f"[ERROR] Client {addr}: {e}")
    finally:
        client_socket.close()
        print(f"[DISCONNECTED] {addr}")
