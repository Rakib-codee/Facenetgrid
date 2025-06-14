try:
    import tkinter as tk
    from tkinter import ttk, scrolledtext
except ModuleNotFoundError:
    raise ImportError("Tkinter is not installed in your Python environment. Please install or use a Python distribution that includes tkinter.")

import socket
import threading
import sqlite3
import datetime
import json
import pickle
import struct
import sys
import os
import face_recognition
import numpy as np

# Dynamically add project root to sys.path if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import init_db, add_known_face, load_known_faces

HOST = '127.0.0.1'
PORT = 5000

class ServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("FaceNetGrid Server")

        self.server_socket = None
        self.is_running = False

        self.known_face_encodings, self.known_face_names = load_known_faces()

        self.setup_ui()

    def setup_ui(self):
        self.status_label = ttk.Label(self.root, text="🔴 Server Status: Stopped", font=('Helvetica', 12))
        self.status_label.pack(pady=10)

        self.control_frame = ttk.Frame(self.root)
        self.control_frame.pack()

        ttk.Label(self.control_frame, text="Host:").grid(row=0, column=0)
        self.host_entry = ttk.Entry(self.control_frame, width=15)
        self.host_entry.insert(0, HOST)
        self.host_entry.grid(row=0, column=1, padx=5)

        ttk.Label(self.control_frame, text="Port:").grid(row=0, column=2)
        self.port_entry = ttk.Entry(self.control_frame, width=6)
        self.port_entry.insert(0, str(PORT))
        self.port_entry.grid(row=0, column=3, padx=5)

        self.start_button = ttk.Button(self.control_frame, text="Start Server", command=self.start_server)
        self.start_button.grid(row=0, column=4, padx=5)

        self.check_port_button = ttk.Button(self.control_frame, text="Check Port", command=self.check_port)
        self.check_port_button.grid(row=0, column=6, padx=5)

        self.stop_button = ttk.Button(self.control_frame, text="Stop Server", command=self.stop_server, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=5, padx=5)

        ttk.Label(self.root, text="📋 Match History:").pack()

        self.tree = ttk.Treeview(self.root, columns=("Name", "Status", "Time"), show='headings')
        self.tree.heading("Name", text="Name")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Time", text="Time")
        self.tree.pack(padx=10, pady=10)

        ttk.Label(self.root, text="🔄 Live Log:").pack()
        self.log_area = scrolledtext.ScrolledText(self.root, height=10, state='disabled')
        self.log_area.pack(fill=tk.BOTH, padx=10, pady=5)

        # Instruction label
        ttk.Label(self.root, text="Run server and client in separate windows.", foreground="blue", font=('Helvetica', 10, 'italic')).pack(pady=2)

        self.refresh_history()

    def log(self, message):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, f"{message}\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')

    def refresh_history(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = sqlite3.connect('match_history.db')
        c = conn.cursor()
        try:
            c.execute("CREATE TABLE IF NOT EXISTS matches (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, status TEXT, timestamp TEXT)")
            c.execute("SELECT name, status, timestamp FROM matches ORDER BY id DESC LIMIT 50")
            rows = c.fetchall()
            for row in rows:
                self.tree.insert("", tk.END, values=row)
        except sqlite3.OperationalError as e:
            self.log(f"[ERROR] Database error: {e}")
        conn.close()

    def start_server(self):
        try:
            host = self.host_entry.get()
            port = int(self.port_entry.get())
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.server_socket.bind((host, port))
            except OSError as e:
                if e.errno == 48 or e.errno == 98:  # Address already in use (macOS/Linux)
                    self.log(f"[ERROR] Port {port} is already in use. Please free the port and try again.")
                    self.status_label.config(text=f"🔴 Port {port} in use!", foreground="red")
                    return
                else:
                    raise
            self.server_socket.listen(5)
            self.is_running = True
            self.status_label.config(text=f"🟢 Server Running on {host}:{port}")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            threading.Thread(target=self.accept_clients, daemon=True).start()
            self.log(f"[INFO] Server started at {host}:{port}")
        except Exception as e:
            self.log(f"[ERROR] Failed to start server: {e}")

    def stop_server(self):
        self.is_running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        self.status_label.config(text="🔴 Server Status: Stopped")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.log("[INFO] Server stopped.")

    def accept_clients(self):
        while self.is_running:
            try:
                client_socket, addr = self.server_socket.accept()
                self.log(f"[Client Connected] {addr}")
                threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()
            except:
                break

    def handle_client(self, client_socket):
        try:
            data = self.receive_data(client_socket)
            if data and 'type' in data:
                if data['type'] == 'match':
                    encoding = np.array(data['encoding'], dtype=np.float64)
                    name, status = self.compare_faces(encoding)
                    self.save_match(name, status)
                    self.send_data(client_socket, {"name": name, "status": status})
                    self.refresh_history()
                    self.log(f"[MATCH] {name} - {status}")

                elif data['type'] == 'add':
                    name = data['name']
                    encoding = np.array(data['encoding'], dtype=np.float64)
                    add_known_face(name, encoding)
                    self.known_face_encodings, self.known_face_names = load_known_faces()
                    self.send_data(client_socket, {"status": "success"})
                    self.log(f"[INFO] Added new face: {name}")
            else:
                self.send_data(client_socket, {"status": "error", "message": "Invalid data or missing type."})
                self.log("[ERROR] Received invalid data or missing type.")
        except Exception as e:
            self.send_data(client_socket, {"status": "error", "message": str(e)})
            self.log(f"[ERROR] {str(e)}")
        finally:
            client_socket.close()

    def compare_faces(self, encoding):
        # Safety: make sure all encodings are float64 numpy arrays
        self.known_face_encodings = [np.array(e, dtype=np.float64) for e in self.known_face_encodings]
        if not self.known_face_encodings:
            return ("Unknown", "Unmatched")
        matches = face_recognition.compare_faces(self.known_face_encodings, encoding)
        face_distances = face_recognition.face_distance(self.known_face_encodings, encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            return (self.known_face_names[best_match_index], "Matched")
        else:
            return ("Unknown", "Unmatched")

    def save_match(self, name, status):
        conn = sqlite3.connect('match_history.db')
        c = conn.cursor()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("CREATE TABLE IF NOT EXISTS matches (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, status TEXT, timestamp TEXT)")
        c.execute("INSERT INTO matches (name, status, timestamp) VALUES (?, ?, ?)", (name, status, timestamp))
        conn.commit()
        conn.close()

    def send_data(self, sock, data):
        serialized = json.dumps(data).encode('utf-8')
        sock.sendall(serialized)

    def receive_data(self, sock):
        try:
            data = sock.recv(4096)
            if not data:
                print("[ERROR] No data received.")
                return None
            return json.loads(data.decode('utf-8'))
        except Exception as e:
            print("[ERROR] JSON decode failed:", str(e))
            return None

    def recvall(self, sock, n):
        data = bytearray()
        while len(data) < n:
            packet = sock.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return data

    def check_port(self):
        import socket
        host = self.host_entry.get()
        port = int(self.port_entry.get())
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind((host, port))
            s.close()
            self.log(f"[INFO] Port {port} is free.")
            self.status_label.config(text=f"🟢 Port {port} is free.", foreground="green")
        except OSError as e:
            if e.errno == 48 or e.errno == 98:
                self.log(f"[ERROR] Port {port} is already in use. Please free the port and try again.")
                self.status_label.config(text=f"🔴 Port {port} in use!", foreground="red")
            else:
                self.log(f"[ERROR] Could not check port: {e}")
                self.status_label.config(text=f"🔴 Error checking port.", foreground="red")

if __name__ == '__main__':
    init_db()
    root = tk.Tk()
    app = ServerGUI(root)
    root.mainloop()
