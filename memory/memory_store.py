import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_connection

USER_ID = "user"
BOT_ID = "bot"

def create_conversation(title="New Chat"):
    from datetime import datetime
    conn = get_connection()
    conv_id = f"conv_{int(datetime.now().timestamp() * 1000)}"
    now = datetime.now().isoformat()
    conn.execute(
        "INSERT INTO conversations (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
        (conv_id, title, now, now),
    )
    conn.commit()
    return conv_id

def get_conversations():
    conn = get_connection()
    rows = conn.execute("""
        SELECT c.id, c.title, c.created_at, c.updated_at,
               COUNT(m.id) AS message_count
        FROM conversations c
        LEFT JOIN messages m ON m.conversation_id = c.id
        GROUP BY c.id
        ORDER BY c.updated_at DESC
    """).fetchall()
    return [
        {
            "id": row["id"],
            "title": row["title"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "message_count": row["message_count"],
        }
        for row in rows
    ]

def get_conversation(conversation_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT id, title, created_at, updated_at FROM conversations WHERE id = ?",
        (conversation_id,),
    ).fetchone()
    if not row:
        return None
    return {
        "id": row["id"],
        "title": row["title"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }

def update_conversation_title(conversation_id, title):
    conn = get_connection()
    conn.execute(
        "UPDATE conversations SET title = ? WHERE id = ?",
        (title, conversation_id),
    )
    conn.commit()

def get_conversation_messages(conversation_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, user, text, timestamp FROM messages WHERE conversation_id = ? ORDER BY id ASC",
        (conversation_id,),
    ).fetchall()
    return [{"id": row["id"], "user": row["user"], "text": row["text"], "timestamp": row["timestamp"]} for row in rows]

def clear_conversation_messages(conversation_id):
    from datetime import datetime
    conn = get_connection()
    conn.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
    now = datetime.now().isoformat()
    conn.execute("UPDATE conversations SET updated_at = ? WHERE id = ?", (now, conversation_id))
    conn.commit()

def delete_conversation(conversation_id):
    conn = get_connection()
    conn.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
    conn.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
    conn.commit()

def store_message(role, text, conversation_id="default"):
    from datetime import datetime
    conn = get_connection()
    now = datetime.now().isoformat()
    conv_id = conversation_id or "default"

    conn.execute(
        "INSERT OR IGNORE INTO conversations (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
        (conv_id, "New Chat", now, now),
    )

    cursor = conn.execute(
        "INSERT INTO messages (user, text, timestamp, conversation_id) VALUES (?, ?, ?, ?)",
        (role, text, now, conv_id),
    )

    if role == USER_ID:
        row = conn.execute("SELECT title FROM conversations WHERE id = ?", (conv_id,)).fetchone()
        if row and row["title"] in ("New Chat", "New Conversation"):
            auto_title = text[:36] + ("..." if len(text) > 36 else "")
            conn.execute(
                "UPDATE conversations SET title = ?, updated_at = ? WHERE id = ?",
                (auto_title, now, conv_id),
            )
        else:
            conn.execute(
                "UPDATE conversations SET updated_at = ? WHERE id = ?",
                (now, conv_id),
            )
    else:
        conn.execute(
            "UPDATE conversations SET updated_at = ? WHERE id = ?",
            (now, conv_id),
        )

    conn.commit()
    return cursor.lastrowid

def get_all_messages():
    conn = get_connection()
    rows = conn.execute(
        "SELECT user, text FROM messages ORDER BY id"
    ).fetchall()
    return [{"user": row["user"], "text": row["text"]} for row in rows]

def get_recent_messages(limit=20):
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, user, text FROM ("
        "  SELECT id, user, text FROM messages ORDER BY id DESC LIMIT ?"
        ") ORDER BY id ASC",
        (limit,),
    ).fetchall()
    return [{"id": row["id"], "user": row["user"], "text": row["text"]} for row in rows]

def get_message_count():
    conn = get_connection()
    row = conn.execute(
        "SELECT COUNT(*) AS cnt FROM messages WHERE user = ?", (USER_ID,)
    ).fetchone()
    return row["cnt"]

def clear_all_messages():
    conn = get_connection()
    conn.execute("DELETE FROM embeddings")
    conn.execute("DELETE FROM messages")
    conn.execute("DELETE FROM conversations")
    conn.commit()

def get_total_message_count():
    conn = get_connection()
    row = conn.execute("SELECT COUNT(*) AS cnt FROM messages").fetchone()
    return row["cnt"]

def get_oldest_messages(count):
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, user, text FROM messages ORDER BY id ASC LIMIT ?",
        (count,),
    ).fetchall()
    return [{"id": row["id"], "user": row["user"], "text": row["text"]} for row in rows]

def delete_oldest_messages(keep_recent):
    conn = get_connection()
    conn.execute(
        "DELETE FROM messages WHERE id NOT IN ("
        "  SELECT id FROM messages ORDER BY id DESC LIMIT ?"
        ")",
        (keep_recent,),
    )
    conn.commit()