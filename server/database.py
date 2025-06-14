import sqlite3
import json
import numpy as np

def init_db():
    conn = sqlite3.connect('match_history.db')
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS matches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    status TEXT,
                    timestamp TEXT
                )""")
    c.execute("""CREATE TABLE IF NOT EXISTS known_faces (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    encoding TEXT
                )""")
    conn.commit()
    conn.close()

def add_known_face(name, encoding):
    conn = sqlite3.connect('match_history.db')
    c = conn.cursor()
    enc_str = json.dumps(encoding.tolist())
    c.execute("INSERT INTO known_faces (name, encoding) VALUES (?, ?)", (name, enc_str))
    conn.commit()
    conn.close()

def load_known_faces():
    conn = sqlite3.connect('match_history.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS known_faces (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, encoding TEXT)")
    c.execute("SELECT name, encoding FROM known_faces")
    records = c.fetchall()
    conn.close()

    names, encs = [], []
    for name, enc_str in records:
        try:
            arr = np.array(json.loads(enc_str), dtype=np.float64)
            names.append(name)
            encs.append(arr)
        except:
            continue
    return encs, names
