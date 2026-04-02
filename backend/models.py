"""
SQLite table definitions for Weekly Highlights system.
Run once to initialize the database schema.
"""
import sqlite3
import os
from datetime import datetime

DB_PATH = "/home/node/.openclaw/workspace-main/本周高光/data/本周高光.db"
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

SCHEMA = """
CREATE TABLE IF NOT EXISTS records (
    id TEXT PRIMARY KEY,
    agent TEXT NOT NULL,
    score INTEGER NOT NULL,
    reason TEXT NOT NULL,
    category TEXT NOT NULL,
    recorder TEXT NOT NULL,
    date TEXT NOT NULL,
    summary TEXT,
    remark TEXT,
    week TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dashboard (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    week TEXT UNIQUE NOT NULL,
    total_score INTEGER DEFAULT 0,
    record_count INTEGER DEFAULT 0,
    top_agent TEXT,
    last_updated TEXT
);

CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    week TEXT UNIQUE NOT NULL,
    total_score INTEGER DEFAULT 0,
    record_count INTEGER DEFAULT 0,
    top_agent TEXT,
    summary TEXT,
    archived_at TEXT
);
"""

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

def init_current_week():
    """Insert empty dashboard for current week if not exists."""
    from datetime import date
    today = date.today()
    # ISO week: YYYY-Www
    week = today.isocalendar()[:2]
    current_week = f"{week[0]}-W{week[1]:02d}"
    now = datetime.utcnow().isoformat()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO dashboard (week, total_score, record_count, last_updated) VALUES (?, 0, 0, ?)",
        (current_week, now)
    )
    conn.commit()
    conn.close()
    print(f"Current week {current_week} dashboard initialized")

if __name__ == "__main__":
    init_db()
    init_current_week()
