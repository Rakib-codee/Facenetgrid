# 🧠 FaceNetGrid

![FaceNetGrid Logo](assets/facenetgrid_logo.svg)

**Distributed, Secure, Real-Time Face Recognition for Any Device**

---

## 🚀 Overview
FaceNetGrid is a modern, OOP-based face recognition system with a beautiful web UI (Streamlit). It supports multi-device, real-time face matching, admin controls, and is ready for both local and public deployment—no cloud costs, no JavaScript, just Python.

---

## ✨ Features
- **Webcam face capture & matching** (multi-face, real-time)
- **Add, update, and delete faces** (admin only)
- **Update face names** (admin only)
- **View match/add history** (with export)
- **Download/export faces and logs** (JSON/CSV)
- **Admin/user roles** (password-protected features)
- **Modern, responsive Streamlit UI** (dark/light mode)
- **Multi-device support** (LAN or public via tunnel)
- **OOP, type hints, docstrings, and unit tests**
- **Beautiful branding** (custom logo, favicon, tooltips)

---

## 🖥️ Tech Stack
| Area         | Technology         |
|--------------|-------------------|
| Face Recog.  | face_recognition  |
| Web UI       | Streamlit         |
| Image Proc.  | OpenCV, Pillow    |
| Data         | JSON, CSV, SQLite |
| OOP/Quality  | Python 3, PEP8    |

---

## 📦 Setup
1. **Clone the repo:**
   ```sh
   git clone https://github.com/YOUR-USERNAME/FaceNetGrid.git
   cd FaceNetGrid
   ```
2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
3. **Run the app (local):**
   ```sh
   streamlit run app.py
   ```
4. **Run for LAN/multi-device:**
   ```sh
   streamlit run app.py --server.address=0.0.0.0
   ```

---

## 🌐 Multi-Device & Public Access
- **LAN:** Find your local IP (e.g., 192.168.1.100) and open `http://<your-ip>:8501` on any device on the same WiFi.
- **Public (free):** Use [ngrok](https://ngrok.com/) or [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/) to get a public URL. No code changes needed!

---

## 🔒 Security
- **Admin features** (add/update/delete faces, download data) are password-protected.
- Change the admin password in `app.py` (`ADMIN_PASSWORD`).
- For public use, always use a strong password and consider HTTPS/tunnel.

---

## 🛠️ Usage
- Use the sidebar to match faces, add new faces, update names, or view history.
- Admin login unlocks sensitive features.
- All devices share the same face database and logs.

---

## 🧑‍💻 Example: Update Face Name
1. Log in as admin (sidebar).
2. In "Known Faces," select a face and enter a new name.
3. Click **Update Name**—done!

---

## 🖼️ Demo
- ![screenshot1](demo_screenshot1.png)
- ![screenshot2](demo_screenshot2.png)
- (Add a short demo video or GIF if possible)

---

## 📄 License
MIT License © 2025 Rakib & nexgendev

---

**FaceNetGrid: Modern, Secure, and Ready for Real-World Use.**