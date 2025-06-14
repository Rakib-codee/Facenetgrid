# 🧠 FaceNetGrid: Distributed Face Identity Matching Across Multiple Devices
### A Mini Cloud Simulation of Real-Time Face Recognition Using Python

---

## 📌 Summary

**FaceNetGrid** is a real-time, distributed face recognition system built in Python. It allows **multiple clients (devices)** to capture face images, encode them, and send them over a network to a **centralized server**, which matches the face against a database of known identities.

This project simulates a **cloud-based face identity system**, such as those used in **smart cities, airports, universities, and corporate buildings**, to manage identity from multiple checkpoints.

---

## 🎯 Objectives

- Simulate a cloud-based face recognition system
- Support real-time, multi-client interaction with a server
- Match face identities centrally and log all events
- Provide modern GUI-based interaction for both clients and servers
- Demonstrate a scalable and modular architecture for identity verification

---

## 🧪 Real-World Problem

In many institutions and public infrastructures, identity verification is often localized to one device. There's no shared intelligence or central record-keeping between multiple face scanning points.

**FaceNetGrid solves this by demonstrating:**

✅ How **multiple face scanners** (clients) can communicate with a **central verification system** (server)  
✅ How such a system **processes, matches, and logs** face data securely and efficiently  
✅ How to **scale face recognition** across devices without relying on commercial cloud tools

---

## 💻 Tech Stack

| Feature              | Technology                  | Reason                                  |
|----------------------|------------------------------|------------------------------------------|
| Face Recognition     | `face_recognition` (dlib)     | Fast and accurate face encoding/matching |
| GUI                  | `Tkinter` + `ttk`             | Lightweight, customizable desktop GUI    |
| Networking           | `socket`, `threading`, `json` | Real-time bidirectional communication    |
| Data Persistence     | `SQLite3`                     | Easy local storage for match logs        |
| Serialization        | `pickle`                      | Efficient data transfer between sockets  |
| Development Tools    | `PyCharm`, `VS Code`          | IDEs used for debugging and development  |

---

## 🗂️ Folder Structure
## FaceNetGrid/
├── client/
│ └── client.py # Client GUI: webcam, match, add face
│
├── server/
│ └── server_gui.py # Server GUI: logs, live history, DB
│
├── database/
│ └── match_history.db # SQLite database for face logs
│
├── known_faces/ # Stored known face encodings (.pkl)
│
├── assets/ # GUI icons or screenshots (optional)
│
├── README.md
└── requirements.txt
        
🔐 Security (Planned Features)
Add token-based authentication between client & server

Encrypt face encoding data in transfer

Use HTTPS/WebSocket for secured communication (advanced)

📃 License
MIT License © 2025 Rakib & nexgendev

# 🧠 FaceNetGrid (Streamlit Edition)

A modern, OOP-based face recognition system with a web UI using Streamlit.

## Features
- Webcam face capture and matching
- Add new faces
- View match/add results and logs
- All logic in Python (OOP)
- No JavaScript needed

## Setup
1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. Run the app:
   ```sh
   streamlit run app.py
   ```
3. Open the link in your browser (usually http://localhost:8501)

## Usage
- Use the sidebar to add faces or match faces.
- View results and match history in the main area.

## Multi-Device Usage
- Start the app with:
  ```sh
  streamlit run app.py --server.address=0.0.0.0
  ```
- Find your computer's local IP address (e.g., 192.168.1.100).
- On any device on the same network, open a browser and go to:
  ```
  http://<your-ip>:8501
  ```
- All devices will share the same face database and logs.

## Security
- Admin features (add/delete faces, download data) are password-protected.
- Change the admin password in `app.py` (`ADMIN_PASSWORD`).
- For public/internet use, add HTTPS and stronger authentication.

## Dark/Light Mode
- You can switch between dark and light mode in the Streamlit menu (top right ☰ > Settings > Theme).

## Troubleshooting
- **Camera not working:** Make sure your browser has permission to use the webcam.
- **Port in use:** Use a different port or free the port (see terminal instructions).
- **Multiple devices can't connect:** Ensure all devices are on the same WiFi/network and use the correct IP.
- **Face not detected:** Ensure your face is well-lit and clearly visible to the camera.
- **Admin features not visible:** Enter the correct admin password in the sidebar.

## Demo
- ![screenshot1](demo_screenshot1.png)
- ![screenshot2](demo_screenshot2.png)
- (Add a short demo video or GIF if possible)

---
MIT License