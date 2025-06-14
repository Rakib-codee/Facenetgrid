import sqlite3
import os

DB_PATH = 'data/match_logs.db'

def init_db():
    if not os.path.exists('data'):
        os.makedirs('data')
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS match_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id TEXT,
            name TEXT,
            distance REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def log_match_result(client_id, name, distance):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO match_logs (client_id, name, distance)
        VALUES (?, ?, ?)
    ''', (client_id, name, distance))
    conn.commit()
    conn.close()

# Run on import
init_db()
