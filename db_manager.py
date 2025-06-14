import sqlite3
import os
from datetime import datetime
import csv
import io
from typing import List, Tuple

class DBManager:
    """
    Handles match/add logs in SQLite and provides export functionality.
    """
    def __init__(self, db_path: str = 'match_history.db') -> None:
        """Initialize the DBManager and create the matches table if needed."""
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Create the matches table if it does not exist."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            status TEXT,
            timestamp TEXT
        )''')
        conn.commit()
        conn.close()

    def log_match(self, name: str, status: str) -> None:
        """Log a match or add event to the database."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        c.execute('INSERT INTO matches (name, status, timestamp) VALUES (?, ?, ?)', (name, status, timestamp))
        conn.commit()
        conn.close()

    def get_history(self, limit: int = 50) -> List[Tuple[str, str, str]]:
        """Retrieve the last `limit` match/add events from the database."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT name, status, timestamp FROM matches ORDER BY id DESC LIMIT ?', (limit,))
        rows = c.fetchall()
        conn.close()
        return rows

    def export_history_csv(self) -> str:
        """Export match/add history as a CSV string."""
        rows = self.get_history(limit=1000)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['name', 'status', 'timestamp'])
        for row in rows:
            writer.writerow(row)
        return output.getvalue() 