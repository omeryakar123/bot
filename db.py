import sqlite3
from pathlib import Path

DB_PATH = Path("scores.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        last_name TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS scores(
        user_id INTEGER PRIMARY KEY,
        score INTEGER DEFAULT 0,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )
    """)
    conn.commit()
    conn.close()

def upsert_user(uid, username, first_name, last_name):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO users(user_id, username, first_name, last_name)
    VALUES (?, ?, ?, ?)
    ON CONFLICT(user_id) DO UPDATE SET
        username=excluded.username,
        first_name=excluded.first_name,
        last_name=excluded.last_name
    """, (uid, username, first_name, last_name))
    conn.commit()
    conn.close()

def submit_score(uid, score):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT score FROM scores WHERE user_id = ?", (uid,))
    row = cur.fetchone()
    if row is None or score > (row[0] or 0):
        cur.execute("""
        INSERT INTO scores(user_id, score) VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            score=excluded.score,
            updated_at=CURRENT_TIMESTAMP
        """, (uid, score))
        conn.commit()
    conn.close()

def get_user_score(uid):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT score FROM scores WHERE user_id = ?", (uid,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else 0

def get_leaderboard(limit: int = 10):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    SELECT u.user_id,
           COALESCE(u.username, u.first_name || ' ' || COALESCE(u.last_name, '')) AS name,
           s.score
    FROM scores s
    JOIN users u ON u.user_id = s.user_id
    ORDER BY s.score DESC, s.updated_at ASC
    LIMIT ?
    """, (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows
