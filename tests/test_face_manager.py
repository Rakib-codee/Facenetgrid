import os
import json
from face_manager import FaceManager

def test_add_and_match_face():
    fm = FaceManager(db_path='test_faces.json')
    fm.known_faces = []
    fm.save_faces()
    # Add a face
    encoding = [0.1] * 128
    fm.add_face('TestUser', encoding)
    assert len(fm.known_faces) == 1
    # Match the same face
    name, dist = fm.match_face(encoding)
    assert name == 'TestUser'
    # Clean up
    os.remove('test_faces.json')

def test_delete_face():
    fm = FaceManager(db_path='test_faces.json')
    fm.known_faces = []
    fm.save_faces()
    encoding = [0.2] * 128
    fm.add_face('DeleteMe', encoding)
    assert fm.delete_face('DeleteMe')
    assert len(fm.known_faces) == 0
    os.remove('test_faces.json')

def test_export_faces():
    fm = FaceManager(db_path='test_faces.json')
    fm.known_faces = []
    fm.save_faces()
    encoding = [0.3] * 128
    fm.add_face('ExportUser', encoding)
    json_str = fm.export_faces_json()
    csv_str = fm.export_faces_csv()
    assert 'ExportUser' in json_str
    assert 'ExportUser' in csv_str
    os.remove('test_faces.json')

if __name__ == '__main__':
    test_add_and_match_face()
    test_delete_face()
    test_export_faces()
    print('All FaceManager tests passed!') 