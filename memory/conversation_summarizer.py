import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()

_API_KEY = os.getenv("GEMINI_API_KEY", "")
_client = None

if _API_KEY:
    from google import genai
    _client = genai.Client(api_key=_API_KEY)

SUMMARIZATION_THRESHOLD = 100
MESSAGES_TO_KEEP = 20

_SUMMARY_PROMPT = """You are a conversation summarizer for a personal AI assistant.

Summarize the following conversation into a concise paragraph that captures:
- Key facts about the user (name, background, preferences, goals)
- Important topics discussed
- Decisions made or conclusions reached
- Any commitments or follow-ups mentioned

Keep the summary factual, concise, and in third person (e.g., "The user...").
Do NOT include greetings, small talk, or trivial exchanges.
Maximum 300 words.

{existing_section}CONVERSATION TO SUMMARIZE:
{conversation}

SUMMARY:"""

_EXISTING_SUMMARY_SECTION = """EXISTING SUMMARY (incorporate and update with new information):
{existing_summary}

"""

def should_summarize(total_messages, recent_limit=None):
    if recent_limit is None:
        recent_limit = MESSAGES_TO_KEEP
    return total_messages > SUMMARIZATION_THRESHOLD

def summarize_messages(messages, existing_summary=None):
    if not _client:
        return None

    if not messages:
        return existing_summary

    conversation_lines = []
    for msg in messages:
        role = msg.get("user", "")
        text = msg.get("text", "")
        if not text:
            continue
        label = "USER" if role == "user" else "ASSISTANT"
        conversation_lines.append(f"{label}: {text}")

    conversation_text = "\n".join(conversation_lines)

    existing_section = ""
    if existing_summary:
        existing_section = _EXISTING_SUMMARY_SECTION.format(
            existing_summary=existing_summary,
        )

    prompt = _SUMMARY_PROMPT.format(
        existing_section=existing_section,
        conversation=conversation_text,
    )

    try:
        response = _client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "temperature": 0.3,
                "max_output_tokens": 1024,
                "thinking_config": {"thinking_budget": 0},
            },
        )
        summary = response.text.strip()
        return summary if summary else None
    except Exception as e:
        print(f"[WARN] Conversation summarization failed: {e}")
        return None

def get_current_summary():
    from database import get_connection
    conn = get_connection()
    row = conn.execute(
        "SELECT summary FROM conversation_summaries ORDER BY id DESC LIMIT 1"
    ).fetchone()
    return row["summary"] if row else None

def store_summary(summary_text, messages_summarized):
    from database import get_connection
    conn = get_connection()
    conn.execute(
        "INSERT INTO conversation_summaries (summary, messages_summarized, created_at) "
        "VALUES (?, ?, ?)",
        (summary_text, messages_summarized, datetime.now().isoformat()),
    )
    conn.commit()

def clear_all_summaries():
    from database import get_connection
    conn = get_connection()
    conn.execute("DELETE FROM conversation_summaries")
    conn.commit()
