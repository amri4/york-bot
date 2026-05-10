import sqlite3

conn = sqlite3.connect("punk.db")
cur = conn.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    bounty INTEGER DEFAULT 0
)
''')

conn.commit()
