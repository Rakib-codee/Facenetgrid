import face_recognition
import numpy as np
import os
import json
import re
import csv
import io
from typing import List, Dict, Optional

class FaceManager:
    """
    Manages known faces: add, match, load, save, delete, and export.
    All face encodings are stored as lists for JSON compatibility.
    """
    def __init__(self, db_path: str = 'known_faces.json') -> None:
        """Initialize the FaceManager and load faces from file."""
        self.db_path = db_path
        self.known_faces: List[Dict[str, object]] = []  # List of dicts: {name, encoding}
        self.load_faces()

    def load_faces(self) -> None:
        """Load known faces from the JSON file."""
        try:
            if os.path.exists(self.db_path):
                with open(self.db_path, 'r') as f:
                    self.known_faces = json.load(f)
            else:
                self.known_faces = []
        except Exception as e:
            print(f"[ERROR] Failed to load faces: {e}")
            self.known_faces = []

    def save_faces(self) -> None:
        """Save known faces to the JSON file."""
        try:
            with open(self.db_path, 'w') as f:
                json.dump(self.known_faces, f)
        except Exception as e:
            print(f"[ERROR] Failed to save faces: {e}")

    def sanitize_name(self, name: str) -> str:
        """Sanitize the face name to prevent injection and errors."""
        return re.sub(r'[^a-zA-Z0-9_\- ]', '', name.strip())

    def add_face(self, name: str, encoding: List[float]) -> None:
        """Add a new face with the given name and encoding."""
        name = self.sanitize_name(name)
        if not name:
            raise ValueError("Name cannot be empty or invalid.")
        try:
            self.known_faces.append({'name': name, 'encoding': encoding})
            self.save_faces()
        except Exception as e:
            print(f"[ERROR] Failed to add face: {e}")
            raise

    def match_face(self, encoding: List[float], tolerance: float = 0.5) -> (str, Optional[float]):
        """
        Match a face encoding against known faces.
        Returns (name, distance) or ('Unknown', distance) or ('No known faces', None).
        """
        try:
            if not self.known_faces:
                return 'No known faces', None
            known_encodings = [np.array(f['encoding']) for f in self.known_faces]
            names = [f['name'] for f in self.known_faces]
            matches = face_recognition.compare_faces(known_encodings, np.array(encoding), tolerance)
            face_distances = face_recognition.face_distance(known_encodings, np.array(encoding))
            if len(face_distances) == 0:
                return 'No known faces', None
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                return names[best_match_index], float(face_distances[best_match_index])
            else:
                return 'Unknown', float(face_distances[best_match_index])
        except Exception as e:
            print(f"[ERROR] Failed to match face: {e}")
            return 'Error', None

    def delete_face(self, name: str) -> bool:
        """Delete a face by name. Returns True if deleted, False if not found."""
        name = self.sanitize_name(name)
        before = len(self.known_faces)
        self.known_faces = [f for f in self.known_faces if f['name'] != name]
        self.save_faces()
        return len(self.known_faces) < before

    def update_face_name(self, old_name: str, new_name: str) -> bool:
        """Update the name of a face. Returns True if updated, False if not found or invalid."""
        old_name = self.sanitize_name(old_name)
        new_name = self.sanitize_name(new_name)
        if not new_name:
            return False
        updated = False
        for f in self.known_faces:
            if f['name'] == old_name:
                f['name'] = new_name
                updated = True
        if updated:
            self.save_faces()
        return updated

    def export_faces_json(self) -> str:
        """Export known faces as a JSON string."""
        return json.dumps(self.known_faces, indent=2)

    def export_faces_csv(self) -> str:
        """Export known faces as a CSV string (name, encoding as string)."""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['name', 'encoding'])
        for f in self.known_faces:
            writer.writerow([f['name'], json.dumps(f['encoding'])])
        return output.getvalue() 