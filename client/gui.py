import tkinter as tk
from tkinter import messagebox
import threading
from camera import start_camera, capture_face
from utils import send_face_to_server, save_new_face

def start_gui():
    window = tk.Tk()
    window.title("FaceNetGrid Client")
    window.geometry("400x300")

    label_result = tk.Label(window, text="Result: Not matched yet", font=("Arial", 12))
    label_result.pack(pady=10)

    def handle_start_camera():
        threading.Thread(target=start_camera).start()

    def handle_capture_match():
        encoding = capture_face()
        if encoding:
            name, distance = send_face_to_server(encoding)
            label_result.config(text=f"Result: {name} ({distance:.2f})" if name else "No face matched")
        else:
            messagebox.showerror("Error", "No face detected")

    def handle_add_face():
        name = entry_name.get()
        if not name:
            messagebox.showwarning("Input needed", "Please enter a name")
            return
        encoding = capture_face()
        if encoding:
            save_new_face(name, encoding)
            messagebox.showinfo("Saved", f"Face saved for {name}")
        else:
            messagebox.showerror("Error", "No face detected")

    # Buttons
    tk.Button(window, text="Start Camera", command=handle_start_camera).pack(pady=5)
    tk.Button(window, text="Capture and Match", command=handle_capture_match).pack(pady=5)

    entry_name = tk.Entry(window)
    entry_name.pack(pady=5)
    entry_name.insert(0, "Enter name")

    tk.Button(window, text="Add Face Info", command=handle_add_face).pack(pady=5)

    window.mainloop()
