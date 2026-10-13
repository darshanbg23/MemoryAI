import sqlite3
import threading

DB_FILE = "chatbot.db"

_local = threading.local()

def get_connection():
    conn = getattr(_local, "conn", None)
    if conn is not None:
        try:
            conn.execute("SELECT 1")
            return conn
        except Exception:
            try:
                conn.close()
            except Exception:
                pass
            _local.conn = None

    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    _local.conn = conn
    return conn

def close_connection():
    conn = getattr(_local, "conn", None)
    if conn is not None:
        try:
            conn.close()
        except Exception:
            pass
        _local.conn = None

def _init_schema(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
            text TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_profiles (
            user_id TEXT PRIMARY KEY,
            display_name TEXT NOT NULL,
            tone TEXT NOT NULL DEFAULT 'Friendly',
            preferences TEXT NOT NULL DEFAULT '{}',
            conversation_count INTEGER NOT NULL DEFAULT 0,
            first_interaction TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS embeddings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id INTEGER NOT NULL,
            user_id TEXT NOT NULL,
            text TEXT NOT NULL,
            embedding BLOB NOT NULL,
            importance_score REAL DEFAULT NULL,
            FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE CASCADE
        )
    """)
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_embeddings_user ON embeddings(user_id)"
    )
    conn.execute("""
        CREATE TABLE IF NOT EXISTS conversation_summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            summary TEXT NOT NULL,
            messages_summarized INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    _migrate_add_column(conn, "embeddings", "importance_score", "REAL DEFAULT NULL")
    _migrate_add_column(conn, "embeddings", "pinned", "INTEGER DEFAULT 0")
    _migrate_add_column(conn, "embeddings", "category", "TEXT DEFAULT NULL")
    _migrate_add_column(conn, "messages", "conversation_id", "TEXT DEFAULT 'default'")

    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_messages_user ON messages(user)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_embeddings_message_id ON embeddings(message_id)"
    )

    try:
        count_row = conn.execute("SELECT COUNT(*) FROM conversations").fetchone()
        if count_row and count_row[0] == 0:
            msg_row = conn.execute("SELECT MIN(timestamp), MAX(timestamp) FROM messages").fetchone()
            if msg_row and msg_row[0]:
                conn.execute(
                    "INSERT OR IGNORE INTO conversations (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
                    ('default', 'Initial Conversation', msg_row[0], msg_row[1] or msg_row[0])
                )
    except Exception:
        pass

    conn.commit()

def _migrate_add_column(conn, table, column, col_type):
    try:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
    except Exception:
        pass

_conn = get_connection()
_init_schema(_conn)
