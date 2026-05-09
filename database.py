import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "york.db")


def get_conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS meals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                food TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS claimed_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT NOT NULL,
                item TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS taken_coins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT NOT NULL,
                taker_id TEXT NOT NULL,
                victim_id TEXT NOT NULL,
                amount INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def add_meal(guild_id, user_id, food):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO meals (guild_id, user_id, food) VALUES (?, ?, ?)",
            (str(guild_id), str(user_id), food),
        )
        conn.commit()


def add_claimed_item(guild_id, item):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO claimed_items (guild_id, item) VALUES (?, ?)",
            (str(guild_id), item),
        )
        conn.commit()


def get_claimed_items(guild_id, limit=10):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT item, timestamp FROM claimed_items WHERE guild_id = ? ORDER BY timestamp DESC LIMIT ?",
            (str(guild_id), limit),
        ).fetchall()
    return rows


def add_taken_coins(guild_id, taker_id, victim_id, amount):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO taken_coins (guild_id, taker_id, victim_id, amount) VALUES (?, ?, ?, ?)",
            (str(guild_id), str(taker_id), str(victim_id), amount),
        )
        conn.commit()


def get_total_taken(guild_id, taker_id):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM taken_coins WHERE guild_id = ? AND taker_id = ?",
            (str(guild_id), str(taker_id)),
        ).fetchone()
    return row[0] if row else 0


def get_recent_meals(guild_id, limit=5):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT user_id, food, timestamp FROM meals WHERE guild_id = ? ORDER BY timestamp DESC LIMIT ?",
            (str(guild_id), limit),
        ).fetchall()
    return rows
