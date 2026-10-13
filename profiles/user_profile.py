import json
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_connection

USER_ID = "user"
AVAILABLE_TONES = ["Friendly", "Technical", "Casual"]

def ensure_profile_exists():
    conn = get_connection()
    row = conn.execute(
        "SELECT 1 FROM user_profiles WHERE user_id = ?", (USER_ID,)
    ).fetchone()
    if row is None:
        conn.execute(
            """INSERT INTO user_profiles
               (user_id, display_name, tone, preferences, conversation_count, first_interaction)
               VALUES (?, ?, ?, ?, 0, ?)""",
            (USER_ID, "User", "Friendly", json.dumps({}), datetime.now().isoformat()),
        )
        conn.commit()

def get_profile():
    ensure_profile_exists()
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM user_profiles WHERE user_id = ?", (USER_ID,)
    ).fetchone()
    return {
        "user_id": row["user_id"],
        "display_name": row["display_name"],
        "tone": row["tone"],
        "preferences": json.loads(row["preferences"]),
        "conversation_count": row["conversation_count"],
        "first_interaction": row["first_interaction"],
    }

def get_tone():
    ensure_profile_exists()
    conn = get_connection()
    row = conn.execute(
        "SELECT tone FROM user_profiles WHERE user_id = ?", (USER_ID,)
    ).fetchone()
    return row["tone"] if row else "Friendly"

def get_display_name():
    ensure_profile_exists()
    conn = get_connection()
    row = conn.execute(
        "SELECT display_name FROM user_profiles WHERE user_id = ?", (USER_ID,)
    ).fetchone()
    return row["display_name"] if row else "User"

def update_profile(display_name=None, tone=None):
    ensure_profile_exists()
    conn = get_connection()
    if display_name:
        conn.execute(
            "UPDATE user_profiles SET display_name = ? WHERE user_id = ?",
            (display_name, USER_ID),
        )
    if tone and tone in AVAILABLE_TONES:
        conn.execute(
            "UPDATE user_profiles SET tone = ? WHERE user_id = ?",
            (tone, USER_ID),
        )
    conn.commit()
    return True

def update_preferences(new_preferences):
    ensure_profile_exists()
    conn = get_connection()
    row = conn.execute(
        "SELECT preferences FROM user_profiles WHERE user_id = ?", (USER_ID,)
    ).fetchone()
    current = json.loads(row["preferences"]) if row else {}
    current.update(new_preferences)
    conn.execute(
        "UPDATE user_profiles SET preferences = ? WHERE user_id = ?",
        (json.dumps(current), USER_ID),
    )
    conn.commit()
    return True