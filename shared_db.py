import sqlite3
import os


def get_db_path():
    return os.getenv("SHAKA_DB_PATH", "shaka.db")


def get_conn():
    return sqlite3.connect(get_db_path())


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id   TEXT NOT NULL,
                guild_id  TEXT NOT NULL,
                berries   INTEGER DEFAULT 500,
                trust     INTEGER DEFAULT 0,
                last_daily TEXT,
                PRIMARY KEY (user_id, guild_id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS warnings (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id     TEXT NOT NULL,
                user_id      TEXT NOT NULL,
                moderator_id TEXT NOT NULL,
                reason       TEXT NOT NULL,
                timestamp    DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id     TEXT NOT NULL,
                from_user_id TEXT,
                to_user_id   TEXT,
                amount       INTEGER NOT NULL,
                reason       TEXT,
                timestamp    DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS york_feeds (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id     TEXT NOT NULL,
                feeder_id    TEXT NOT NULL,
                trust_gained INTEGER DEFAULT 20,
                berries_spent INTEGER DEFAULT 50,
                timestamp    DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS york_state (
                guild_id          TEXT PRIMARY KEY,
                hunger_level      INTEGER DEFAULT 100,
                last_fed          DATETIME DEFAULT CURRENT_TIMESTAMP,
                hunger_channel_id TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS trivia_scores (
                user_id  TEXT NOT NULL,
                guild_id TEXT NOT NULL,
                score    INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, guild_id)
            )
        """)
        conn.commit()


# ── User helpers ──────────────────────────────────────────────────────────────

def ensure_user(user_id, guild_id):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO users (user_id, guild_id) VALUES (?, ?)",
            (str(user_id), str(guild_id)),
        )
        conn.commit()


def get_user(user_id, guild_id):
    ensure_user(user_id, guild_id)
    with get_conn() as conn:
        return conn.execute(
            "SELECT berries, trust, last_daily FROM users WHERE user_id = ? AND guild_id = ?",
            (str(user_id), str(guild_id)),
        ).fetchone()


def get_berries(user_id, guild_id):
    return get_user(user_id, guild_id)[0]


def add_berries(user_id, guild_id, amount, reason=None):
    ensure_user(user_id, guild_id)
    with get_conn() as conn:
        conn.execute(
            "UPDATE users SET berries = MAX(0, berries + ?) WHERE user_id = ? AND guild_id = ?",
            (amount, str(user_id), str(guild_id)),
        )
        if reason:
            col = "to_user_id" if amount > 0 else "from_user_id"
            conn.execute(
                f"INSERT INTO transactions (guild_id, {col}, amount, reason) VALUES (?, ?, ?, ?)",
                (str(guild_id), str(user_id), abs(amount), reason),
            )
        conn.commit()


def transfer_berries(from_id, to_id, guild_id, amount, reason=None):
    ensure_user(from_id, guild_id)
    ensure_user(to_id, guild_id)
    with get_conn() as conn:
        bal = conn.execute(
            "SELECT berries FROM users WHERE user_id = ? AND guild_id = ?",
            (str(from_id), str(guild_id)),
        ).fetchone()[0]
        if bal < amount:
            return False
        conn.execute(
            "UPDATE users SET berries = berries - ? WHERE user_id = ? AND guild_id = ?",
            (amount, str(from_id), str(guild_id)),
        )
        conn.execute(
            "UPDATE users SET berries = berries + ? WHERE user_id = ? AND guild_id = ?",
            (amount, str(to_id), str(guild_id)),
        )
        conn.execute(
            "INSERT INTO transactions (guild_id, from_user_id, to_user_id, amount, reason) VALUES (?,?,?,?,?)",
            (str(guild_id), str(from_id), str(to_id), amount, reason),
        )
        conn.commit()
        return True


def get_trust(user_id, guild_id):
    return get_user(user_id, guild_id)[1]


def add_trust(user_id, guild_id, amount):
    ensure_user(user_id, guild_id)
    with get_conn() as conn:
        conn.execute(
            "UPDATE users SET trust = trust + ? WHERE user_id = ? AND guild_id = ?",
            (amount, str(user_id), str(guild_id)),
        )
        conn.commit()


def get_trust_level(trust):
    if trust >= 1500:
        return 4, "Trusted", 1.5
    elif trust >= 700:
        return 3, "Close Friend", 1.3
    elif trust >= 300:
        return 2, "Friend", 1.2
    elif trust >= 100:
        return 1, "Acquaintance", 1.1
    else:
        return 0, "Stranger", 1.0


def set_last_daily(user_id, guild_id, date_str):
    with get_conn() as conn:
        conn.execute(
            "UPDATE users SET last_daily = ? WHERE user_id = ? AND guild_id = ?",
            (date_str, str(user_id), str(guild_id)),
        )
        conn.commit()


def get_leaderboard(guild_id, by="berries", limit=10):
    col = "berries" if by == "berries" else "trust"
    with get_conn() as conn:
        return conn.execute(
            f"SELECT user_id, berries, trust FROM users WHERE guild_id = ? ORDER BY {col} DESC LIMIT ?",
            (str(guild_id), limit),
        ).fetchall()


def get_recent_transactions(guild_id, limit=8):
    with get_conn() as conn:
        return conn.execute(
            "SELECT from_user_id, to_user_id, amount, reason, timestamp FROM transactions WHERE guild_id = ? ORDER BY timestamp DESC LIMIT ?",
            (str(guild_id), limit),
        ).fetchall()


# ── Warnings ──────────────────────────────────────────────────────────────────

def add_warning(guild_id, user_id, moderator_id, reason):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO warnings (guild_id, user_id, moderator_id, reason) VALUES (?,?,?,?)",
            (str(guild_id), str(user_id), str(moderator_id), reason),
        )
        conn.commit()


def get_warnings(user_id, guild_id):
    with get_conn() as conn:
        return conn.execute(
            "SELECT id, moderator_id, reason, timestamp FROM warnings WHERE user_id = ? AND guild_id = ? ORDER BY timestamp DESC",
            (str(user_id), str(guild_id)),
        ).fetchall()


def clear_warnings(user_id, guild_id):
    with get_conn() as conn:
        conn.execute(
            "DELETE FROM warnings WHERE user_id = ? AND guild_id = ?",
            (str(user_id), str(guild_id)),
        )
        conn.commit()


# ── York state ────────────────────────────────────────────────────────────────

def ensure_york_state(guild_id):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO york_state (guild_id) VALUES (?)",
            (str(guild_id),),
        )
        conn.commit()


def get_york_state(guild_id):
    ensure_york_state(guild_id)
    with get_conn() as conn:
        return conn.execute(
            "SELECT hunger_level, last_fed, hunger_channel_id FROM york_state WHERE guild_id = ?",
            (str(guild_id),),
        ).fetchone()


def update_york_hunger(guild_id, hunger_level):
    ensure_york_state(guild_id)
    with get_conn() as conn:
        conn.execute(
            "UPDATE york_state SET hunger_level = ? WHERE guild_id = ?",
            (max(0, min(100, hunger_level)), str(guild_id)),
        )
        conn.commit()


def feed_york(guild_id, feeder_id, berries_spent=50, trust_gained=20):
    ensure_york_state(guild_id)
    with get_conn() as conn:
        conn.execute(
            "UPDATE york_state SET hunger_level = MIN(100, hunger_level + 30), last_fed = CURRENT_TIMESTAMP WHERE guild_id = ?",
            (str(guild_id),),
        )
        conn.execute(
            "INSERT INTO york_feeds (guild_id, feeder_id, trust_gained, berries_spent) VALUES (?,?,?,?)",
            (str(guild_id), str(feeder_id), trust_gained, berries_spent),
        )
        conn.commit()


def set_york_channel(guild_id, channel_id):
    ensure_york_state(guild_id)
    with get_conn() as conn:
        conn.execute(
            "UPDATE york_state SET hunger_channel_id = ? WHERE guild_id = ?",
            (str(channel_id), str(guild_id)),
        )
        conn.commit()


# ── Trivia ────────────────────────────────────────────────────────────────────

def add_trivia_score(user_id, guild_id, amount=1):
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO trivia_scores (user_id, guild_id, score) VALUES (?,?,?)
               ON CONFLICT(user_id, guild_id) DO UPDATE SET score = score + ?""",
            (str(user_id), str(guild_id), amount, amount),
        )
        conn.commit()


def get_trivia_score(user_id, guild_id):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT score FROM trivia_scores WHERE user_id = ? AND guild_id = ?",
            (str(user_id), str(guild_id)),
        ).fetchone()
    return row[0] if row else 0


def get_trivia_leaderboard(guild_id, limit=10):
    with get_conn() as conn:
        return conn.execute(
            "SELECT user_id, score FROM trivia_scores WHERE guild_id = ? ORDER BY score DESC LIMIT ?",
            (str(guild_id), limit),
        ).fetchall()


# ── Server stats (for Edison) ─────────────────────────────────────────────────

def get_server_stats(guild_id):
    with get_conn() as conn:
        total_users = conn.execute(
            "SELECT COUNT(*) FROM users WHERE guild_id = ?", (str(guild_id),)
        ).fetchone()[0]
        total_berries = conn.execute(
            "SELECT COALESCE(SUM(berries),0) FROM users WHERE guild_id = ?", (str(guild_id),)
        ).fetchone()[0]
        total_warnings = conn.execute(
            "SELECT COUNT(*) FROM warnings WHERE guild_id = ?", (str(guild_id),)
        ).fetchone()[0]
        total_feeds = conn.execute(
            "SELECT COUNT(*) FROM york_feeds WHERE guild_id = ?", (str(guild_id),)
        ).fetchone()[0]
        avg_trust = conn.execute(
            "SELECT COALESCE(AVG(trust),0) FROM users WHERE guild_id = ?", (str(guild_id),)
        ).fetchone()[0]
    return {
        "total_users": total_users,
        "total_berries": total_berries,
        "total_warnings": total_warnings,
        "total_feeds": total_feeds,
        "avg_trust": round(avg_trust, 1),
    }
