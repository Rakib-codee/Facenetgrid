import socket
import threading
from server_manager import handle_client

HOST = '0.0.0.0'  # Accept connections on all interfaces
PORT = 9999       # Change this if needed

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"[SERVER STARTED] Listening on {HOST}:{PORT}")

    while True:
        client_socket, addr = server.accept()
        print(f"[NEW CONNECTION] {addr} connected.")
        thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        thread.start()

if __name__ == "__main__":
    start_server()
