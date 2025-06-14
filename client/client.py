import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import socket
import cv2
import face_recognition
import numpy as np
import threading
import json
import os
from PIL import Image, ImageTk

# === Configuration ===
SERVER_IP = '127.0.0.1'  # Change to your server IP (for LAN or WAN)
SERVER_PORT = 5000      # Make sure this matches server's port

# === Networking ===
def send_data_to_server(data):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.settimeout(3)
            client_socket.connect((SERVER_IP, SERVER_PORT))
            client_socket.sendall(json.dumps(data).encode())
            response = client_socket.recv(4096)
        return json.loads(response.decode())
    except ConnectionRefusedError:
        print("[CLIENT ERROR] Server is not running or port is not open.")
        return None
    except Exception as e:
        print("[CLIENT ERROR]", e)
        return None

# === GUI & App ===
class FaceNetGridClient:
    def __init__(self, root):
        self.root = root
        self.root.title("FaceNetGrid Client")
        self.root.geometry("600x600")
        self.root.minsize(500, 500)
        self.root.resizable(True, True)

        self.cap = None
        self.frame = None
        self.camera_running = False
        self.photo = None
        self.connected = False
        self.match_history = []

        # --- Instruction Label ---
        ttk.Label(root, text="Run server and client in separate windows.", foreground="blue", font=('Helvetica', 10, 'italic')).pack(pady=2)

        # --- Connection Section ---
        conn_frame = ttk.LabelFrame(root, text="Server Connection", padding=(10, 5))
        conn_frame.pack(fill='x', padx=10, pady=8)
        ttk.Label(conn_frame, text="Server IP:").grid(row=0, column=0, sticky='e')
        self.entry_ip = ttk.Entry(conn_frame, width=15)
        self.entry_ip.insert(0, SERVER_IP)
        self.entry_ip.grid(row=0, column=1, padx=5)
        ttk.Label(conn_frame, text="Port:").grid(row=0, column=2, sticky='e')
        self.entry_port = ttk.Entry(conn_frame, width=8)
        self.entry_port.insert(0, str(SERVER_PORT))
        self.entry_port.grid(row=0, column=3, padx=5)
        self.btn_connect = ttk.Button(conn_frame, text="Connect", command=self.try_connect)
        self.btn_connect.grid(row=0, column=4, padx=10)
        self.btn_check_port = ttk.Button(conn_frame, text="Check Port", command=self.check_port)
        self.btn_check_port.grid(row=0, column=5, padx=5)
        self.conn_status = ttk.Label(conn_frame, text="Disconnected", foreground="red")
        self.conn_status.grid(row=0, column=6, padx=5)

        # --- Camera Section ---
        cam_frame = ttk.LabelFrame(root, text="Camera", padding=(10, 5))
        cam_frame.pack(fill='x', padx=10, pady=8)
        self.btn_start = ttk.Button(cam_frame, text="Start Camera", command=self.start_camera)
        self.btn_stop = ttk.Button(cam_frame, text="Stop Camera", command=self.stop_camera, state=tk.DISABLED)
        self.btn_popout = ttk.Button(cam_frame, text="Pop Out Preview", command=self.popout_preview, state=tk.DISABLED)
        self.btn_start.grid(row=0, column=0, padx=5, pady=5)
        self.btn_stop.grid(row=0, column=1, padx=5, pady=5)
        self.btn_popout.grid(row=0, column=2, padx=5, pady=5)
        self.camera_status = ttk.Label(cam_frame, text="Camera stopped", foreground="blue")
        self.camera_status.grid(row=0, column=3, padx=10)

        # --- Camera Preview ---
        self.camera_label = tk.Label(root, bg='black', width=480, height=320)
        self.camera_label.pack(pady=5, fill='both', expand=True)

        # --- Face Actions Section ---
        action_frame = ttk.LabelFrame(root, text="Face Actions", padding=(10, 5))
        action_frame.pack(fill='x', padx=10, pady=8)
        self.btn_capture = ttk.Button(action_frame, text="Capture and Match", command=self.capture_and_match, state=tk.DISABLED)
        self.btn_add = ttk.Button(action_frame, text="Add Face Info", command=self.add_face_info, state=tk.DISABLED)
        self.btn_capture.grid(row=0, column=0, padx=5, pady=5)
        self.btn_add.grid(row=0, column=1, padx=5, pady=5)

        # --- Results Section ---
        result_frame = ttk.LabelFrame(root, text="Results & History", padding=(10, 5))
        result_frame.pack(fill='both', padx=10, pady=8, expand=True)
        self.result_text = tk.Text(result_frame, height=6, state='disabled', bg='#f7f7f7')
        self.result_text.pack(fill='both', expand=True)

    def get_server_config(self):
        ip = self.entry_ip.get().strip()
        try:
            port = int(self.entry_port.get().strip())
        except ValueError:
            port = SERVER_PORT
        return ip, port

    def try_connect(self):
        ip, port = self.get_server_config()
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2)
                s.connect((ip, port))
            self.connected = True
            self.conn_status.config(text="Connected", foreground="green")
            self.btn_capture.config(state=tk.NORMAL)
            self.btn_add.config(state=tk.NORMAL)
            self.btn_popout.config(state=tk.NORMAL)
            self.append_result(f"[INFO] Connected to {ip}:{port}")
        except Exception as e:
            self.connected = False
            self.conn_status.config(text="Disconnected", foreground="red")
            self.btn_capture.config(state=tk.DISABLED)
            self.btn_add.config(state=tk.DISABLED)
            self.btn_popout.config(state=tk.DISABLED)
            if 'Connection refused' in str(e) or 'actively refused' in str(e) or 'timed out' in str(e):
                self.append_result(f"[ERROR] Could not connect: Port {port} is not open or server is not running.")
            else:
                self.append_result(f"[ERROR] Could not connect: {e}")

    def start_camera(self):
        if self.cap is None or not self.cap.isOpened():
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                self.camera_status.config(text="Cannot open webcam", foreground="red")
                messagebox.showerror("Camera Error", "Cannot open webcam.")
                return
            self.camera_running = True
            self.camera_status.config(text="Camera running", foreground="green")
            self.btn_start.config(state=tk.DISABLED)
            self.btn_stop.config(state=tk.NORMAL)
            self.btn_popout.config(state=tk.NORMAL)
            self.update_camera()

    def stop_camera(self):
        self.camera_running = False
        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.cap = None
        self.camera_label.config(image='')
        self.camera_status.config(text="Camera stopped", foreground="blue")
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)

    def update_camera(self):
        if self.cap and self.cap.isOpened() and self.camera_running:
            ret, frame = self.cap.read()
            if ret:
                self.frame = frame.copy()
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(rgb)
                img = img.resize((480, 320))
                self.photo = ImageTk.PhotoImage(img)
                self.camera_label.config(image=self.photo)
            self.root.after(15, self.update_camera)
        else:
            self.stop_camera()

    def send_data_to_server(self, data):
        ip, port = self.get_server_config()
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.settimeout(3)
                client_socket.connect((ip, port))
                client_socket.sendall(json.dumps(data).encode())
                response = client_socket.recv(4096)
            return json.loads(response.decode())
        except Exception as e:
            self.append_result(f"[ERROR] Server communication failed: {e}")
            return None

    def capture_and_match(self):
        if self.frame is None:
            messagebox.showwarning("Warning", "Start the camera first.")
            return
        rgb_frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        if not face_encodings:
            self.append_result("[INFO] No face detected.")
            messagebox.showinfo("Match Result", "No face detected.")
            return
        draw_frame = self.frame.copy()
        for (top, right, bottom, left), encoding in zip(face_locations, face_encodings):
            data = {
                'type': 'match',
                'encoding': encoding.tolist()
            }
            result = self.send_data_to_server(data)
            name = result.get('name', 'Unknown') if result else 'Unknown'
            color = (0, 255, 0) if name != 'Unknown' else (0, 0, 255)
            cv2.rectangle(draw_frame, (left, top), (right, bottom), color, 2)
            cv2.putText(draw_frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)
            self.append_result(f"[MATCH] {name}")
            self.match_history.append(name)
        # Show result in the Tkinter label
        rgb = cv2.cvtColor(draw_frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb)
        img = img.resize((480, 320))
        self.photo = ImageTk.PhotoImage(img)
        self.camera_label.config(image=self.photo)

    def add_face_info(self):
        if self.frame is None:
            messagebox.showwarning("Warning", "Start the camera first.")
            return
        name = simpledialog.askstring("Add Person", "Enter person's name:")
        if not name:
            return
        rgb_frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        if len(face_encodings) != 1:
            self.append_result("[ERROR] Exactly one face must be visible.")
            messagebox.showerror("Error", "Exactly one face must be visible.")
            return
        data = {
            'type': 'add',
            'name': name,
            'encoding': face_encodings[0].tolist()
        }
        result = self.send_data_to_server(data)
        if result and (result.get('status') == 'success' or 'Added' in str(result)):
            self.append_result(f"[SUCCESS] Face for '{name}' added.")
            messagebox.showinfo("Success", f"Face for '{name}' added.")
        elif result is None:
            self.append_result("[ERROR] Could not connect to server. Is it running?")
            messagebox.showerror("Failed", "Could not connect to server. Is it running?")
        else:
            self.append_result("[ERROR] Could not add face to server.")
            messagebox.showerror("Failed", "Could not add face to server.")

    def popout_preview(self):
        if self.frame is not None:
            frame = self.frame.copy()
            cv2.imshow("Camera Pop Out Preview (press 'q' to close)", frame)
            while True:
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            cv2.destroyWindow("Camera Pop Out Preview (press 'q' to close)")
        else:
            messagebox.showinfo("No Frame", "No camera frame available. Start the camera first.")

    def append_result(self, text):
        self.result_text.config(state='normal')
        self.result_text.insert('end', text + '\n')
        self.result_text.see('end')
        self.result_text.config(state='disabled')

    def check_port(self):
        ip, port = self.get_server_config()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind((ip, port))
            s.close()
            self.append_result(f"[INFO] Port {port} is free.")
            self.conn_status.config(text=f"🟢 Port {port} is free.", foreground="green")
        except OSError as e:
            if e.errno == 48 or e.errno == 98:
                self.append_result(f"[ERROR] Port {port} is already in use. Please free the port and try again.")
                self.conn_status.config(text=f"🔴 Port {port} in use!", foreground="red")
            else:
                self.append_result(f"[ERROR] Could not check port: {e}")
                self.conn_status.config(text=f"🔴 Error checking port.", foreground="red")

# === Start App ===
if __name__ == '__main__':
    os.environ["QT_MAC_WANTS_LAYER"] = "1"
    root = tk.Tk()
    app = FaceNetGridClient(root)
    root.mainloop()
