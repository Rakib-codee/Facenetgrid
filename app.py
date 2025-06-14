import streamlit as st
import numpy as np
import face_recognition
from face_manager import FaceManager
from db_manager import DBManager
from PIL import Image
import io
import cv2

st.set_page_config(
    page_title="FaceNetGrid: Smart Multi-Device Face Recognition",
    page_icon="🧠"
)

# --- Beautiful Project Header ---
st.markdown(
    '''
    <div style="display:flex;align-items:center;gap:16px;margin-bottom:10px;">
        <img src="https://img.icons8.com/ios-filled/100/000000/face-id.png" width="60"/>
        <div>
            <h1 style="margin-bottom:0;font-size:2.5rem;">FaceNetGrid</h1>
            <h4 style="margin-top:0;color:#4F8BF9;font-weight:normal;">Distributed, Secure, Real-Time Face Recognition for Any Device</h4>
        </div>
    </div>
    ''',
    unsafe_allow_html=True
)

face_manager = FaceManager()
db_manager = DBManager()

# --- Admin Password Protection ---
ADMIN_PASSWORD = "facenet2025"  # Change this to your desired password
if 'admin_authenticated' not in st.session_state:
    st.session_state['admin_authenticated'] = False

with st.sidebar:
    st.markdown("---")
    st.subheader("Admin Login")
    if not st.session_state['admin_authenticated']:
        admin_pw = st.text_input("Enter admin password to unlock admin features:", type="password", help="Required for adding/deleting faces and downloading data.")
        if st.button("Login", key="admin_login_btn"):
            if admin_pw == ADMIN_PASSWORD:
                st.session_state['admin_authenticated'] = True
                st.success("Admin mode enabled!")
            else:
                st.error("Incorrect password. Try again.")
    else:
        st.success("Admin mode enabled!")
        if st.button("Logout", key="admin_logout_btn"):
            st.session_state['admin_authenticated'] = False

# --- Sidebar ---
st.sidebar.header("Actions")
mode = st.sidebar.radio("Choose action:", ["Match Face", "Add Face Info", "View History"], help="Select what you want to do.")

# Show known faces in sidebar
with st.sidebar.expander("Known Faces", expanded=False):
    if face_manager.known_faces:
        for f in face_manager.known_faces:
            st.write(f"- {f['name']}")
        if st.session_state['admin_authenticated']:
            # --- Update Name Feature (admin only) ---
            st.markdown("---")
            st.subheader("Update Face Name")
            upd_name = st.selectbox("Select face to update", [f['name'] for f in face_manager.known_faces], key="upd_name_select", help="Choose a face to rename.")
            new_name = st.text_input("Enter new name", key="upd_name_input", help="Type the new name for the selected face.")
            if st.button("Update Name", key="update_name_btn", help="Update the selected face's name."):
                if new_name.strip():
                    updated = face_manager.update_face_name(upd_name, new_name)
                    if updated:
                        st.success(f"✅ Updated name from '{upd_name}' to '{new_name}'. Please refresh to see changes.")
                    else:
                        st.error("❌ Failed to update name. Name may be invalid or not found.")
                else:
                    st.warning("Please enter a valid new name.")
            # --- Delete Face Feature (admin only) ---
            st.markdown("---")
            st.subheader("Delete a Face")
            del_name = st.selectbox("Select face to delete", [f['name'] for f in face_manager.known_faces], key="del_name_select", help="Choose a face to remove from the database.")
            confirm_delete = st.checkbox(f"Are you sure you want to delete '{del_name}'? This cannot be undone.", key="confirm_delete")
            if confirm_delete:
                if st.button("Delete Face", key="delete_face_btn", help="Remove the selected face from the database."):
                    deleted = face_manager.delete_face(del_name)
                    if deleted:
                        st.success(f"🗑️ Deleted face '{del_name}'. Please refresh to see changes.")
                    else:
                        st.error(f"❌ Could not delete face '{del_name}'.")
            # --- Download Known Faces (admin only) ---
            st.download_button("⬇️ Download Faces (JSON)", face_manager.export_faces_json(), file_name="known_faces.json", mime="application/json", help="Download all known faces as a JSON file.")
            st.download_button("⬇️ Download Faces (CSV)", face_manager.export_faces_csv(), file_name="known_faces.csv", mime="text/csv", help="Download all known faces as a CSV file.")
    else:
        st.write("No faces added yet.")

# --- Download Logs (admin only) ---
if st.session_state['admin_authenticated']:
    st.sidebar.markdown("---")
    st.sidebar.subheader("Download Logs")
    st.sidebar.download_button("⬇️ Download History (CSV)", db_manager.export_history_csv(), file_name="match_history.csv", mime="text/csv", help="Download the match/add history as a CSV file.")

st.markdown("---")

if mode == "Match Face":
    st.header("🔍 Match Face")
    st.info("Use your webcam to take a photo and match against known faces.")
    img_file = st.camera_input("Take a photo to match", help="Click to open your webcam and capture a photo.")
    if img_file is not None:
        with st.spinner("🔎 Processing faces..."):
            img = Image.open(img_file)
            img_np = np.array(img)
            rgb_img = img_np[:, :, :3]
            # --- Performance: Resize for detection ---
            scale = 0.5 if max(rgb_img.shape[0], rgb_img.shape[1]) > 800 else 1.0
            small_img = cv2.resize(rgb_img, (0, 0), fx=scale, fy=scale) if scale < 1.0 else rgb_img
            face_locations = face_recognition.face_locations(small_img)
            face_encodings = face_recognition.face_encodings(small_img, face_locations)
            num_faces = len(face_encodings)
            st.info(f"🧑‍🤝‍🧑 {num_faces} face(s) detected.")
            if num_faces > 10:
                st.warning("⚠️ More than 10 faces detected! Please reduce the number of faces in the frame for best performance.")
            # Scale back locations to original image size
            face_locations = [(
                int(top/scale), int(right/scale), int(bottom/scale), int(left/scale)
            ) for (top, right, bottom, left) in face_locations]
            if not face_encodings:
                st.warning("😕 No face detected. Please try again.")
            else:
                # --- Show thumbnails of all detected faces ---
                st.subheader("Detected Face Thumbnails")
                thumb_cols = st.columns(min(num_faces, 5))
                for i, ((top, right, bottom, left), encoding) in enumerate(zip(face_locations, face_encodings)):
                    face_img = img_np[top:bottom, left:right, :]
                    if face_img.size > 0:
                        thumb = Image.fromarray(face_img).resize((80, 80))
                        thumb_cols[i % len(thumb_cols)].image(thumb, caption=f"Face {i+1}", use_column_width=False)
                # --- Visual Polish: Summary Bar ---
                match_results = []
                for (top, right, bottom, left), encoding in zip(face_locations, face_encodings):
                    name, distance = face_manager.match_face(encoding)
                    match_results.append((name, distance, (top, right, bottom, left), encoding))
                matched = sum(1 for n, _, _, _ in match_results if n not in ["Unknown", "No known faces", "Error"])
                unknown = sum(1 for n, _, _, _ in match_results if n == "Unknown")
                errors = sum(1 for n, _, _, _ in match_results if n in ["No known faces", "Error"])
                st.markdown(f"<div style='background-color:#f0f2f6;padding:10px;border-radius:8px;font-size:18px;'>"
                            f"<b>Summary:</b> {num_faces} detected &mdash; "
                            f"<span style='color:green;'>{matched} matched</span>, "
                            f"<span style='color:red;'>{unknown} unknown</span>, "
                            f"<span style='color:orange;'>{errors} error/no known faces</span>"
                            f"</div>", unsafe_allow_html=True)
                st.caption("<span style='color:green;'>🟩</span> Matched &nbsp; <span style='color:red;'>🟥</span> Unknown &nbsp; <span style='color:orange;'>🟧</span> Error/No known faces", unsafe_allow_html=True)
                st.divider()
                # --- Show results for each face ---
                for idx, (name, distance, (top, right, bottom, left), encoding) in enumerate(match_results):
                    db_manager.log_match(name, "Matched" if name != "Unknown" else "Unmatched")
                    # Visual Polish: Color rectangles
                    if name not in ["Unknown", "No known faces", "Error"]:
                        color = (0, 200, 0)  # Green for matched
                    elif name == "Unknown":
                        color = (220, 0, 0)  # Red for unknown
                    else:
                        color = (255, 140, 0)  # Orange for error/no known faces
                    img_draw = img.copy()
                    np_img = np.array(img_draw)
                    np_img = np.ascontiguousarray(np_img)
                    cv2.rectangle(np_img, (left, top), (right, bottom), color, 2)
                    img_draw = Image.fromarray(np_img)
                    dist_str = f"{distance:.2f}" if distance is not None else "N/A"
                    c1, c2 = st.columns([2, 3])
                    with c1:
                        st.image(img_draw, caption=f"Result: {name}", use_column_width=True)
                    with c2:
                        if name == "Unknown":
                            st.error(f"❌ No match found. (distance: {dist_str})")
                        elif name == "No known faces":
                            st.warning("ℹ️ No known faces in the database.")
                        elif name == "Error":
                            st.error("⚠️ Error during matching.")
                        else:
                            st.success(f"✅ Matched: {name} (distance: {dist_str})")
                        # Visual Polish: Progress bar for confidence
                        if distance is not None:
                            conf = max(0, min(1, 1 - distance))
                            st.progress(conf, text=f"Match confidence: {conf*100:.0f}%")
                st.divider()

elif mode == "Add Face Info":
    if st.session_state['admin_authenticated']:
        st.header("➕ Add Face Info")
        st.info("Take a photo and enter a name to add a new face to the database.")
        name = st.text_input("Enter person's name:", help="This will be used as the label for the face.")
        img_file = st.camera_input("Take a photo to add", help="Click to open your webcam and capture a photo.")
        if img_file is not None and name:
            with st.spinner("📝 Processing faces..."):
                img = Image.open(img_file)
                img_np = np.array(img)
                rgb_img = img_np[:, :, :3]
                # --- Performance: Resize for detection ---
                scale = 0.5 if max(rgb_img.shape[0], rgb_img.shape[1]) > 800 else 1.0
                small_img = cv2.resize(rgb_img, (0, 0), fx=scale, fy=scale) if scale < 1.0 else rgb_img
                face_locations = face_recognition.face_locations(small_img)
                face_encodings = face_recognition.face_encodings(small_img, face_locations)
                num_faces = len(face_encodings)
                st.info(f"🧑‍🤝‍🧑 {num_faces} face(s) detected.")
                if num_faces > 1:
                    st.error("❌ Exactly one face must be visible. Please retake the photo.")
                elif num_faces == 1:
                    # Scale back location to original image size
                    (top, right, bottom, left) = face_locations[0]
                    top = int(top/scale)
                    right = int(right/scale)
                    bottom = int(bottom/scale)
                    left = int(left/scale)
                    try:
                        face_manager.add_face(name, face_encodings[0].tolist())
                        db_manager.log_match(name, "Added")
                        st.success(f"✅ Face for '{name}' added.")
                        st.balloons()
                    except Exception as e:
                        st.error(f"❌ Failed to add face: {e}")
                else:
                    st.error("😕 No face detected. Please try again.")
    else:
        st.warning("🔒 Admin login required to add new faces.")

elif mode == "View History":
    st.header("📋 Match/Add History")
    st.info("See the last 50 match/add events.")
    rows = db_manager.get_history()
    if rows:
        st.dataframe(
            {"Name": [r[0] for r in rows], "Status": [r[1] for r in rows], "Time": [r[2] for r in rows]},
            use_container_width=True
        )
    else:
        st.write("No history yet.") 