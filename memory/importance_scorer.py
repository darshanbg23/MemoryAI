import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()

_API_KEY = os.getenv("GEMINI_API_KEY", "")
_client = None

if _API_KEY:
    from google import genai
    _client = genai.Client(api_key=_API_KEY)

DEFAULT_IMPORTANCE_THRESHOLD = 0.70
DUPLICATE_SIMILARITY_THRESHOLD = 0.92

_SCORING_PROMPT = """You are a memory importance evaluator for a personal AI assistant.

Given a user message and the assistant's response, rate how important this exchange is for long-term memory on a scale of 0.0 to 1.0.

SCORE HIGH (0.7 - 1.0):
- Personal facts (name, age, location)
- Education details (degree, university, courses)
- Career information (job, company, role)
- Projects and technical work
- Skills and expertise
- Goals and aspirations
- Preferences (favorite language, tools, hobbies)
- Explicit "remember this" requests

SCORE LOW (0.0 - 0.3):
- Greetings ("Hi", "Hello", "Hey")
- Small talk ("How are you?", "What's up?")
- Acknowledgments ("Thanks", "Okay", "Got it", "Sure")
- Farewells ("Bye", "See you later")
- Generic praise ("That's great", "Nice", "Cool")
- Conversational filler

SCORE MEDIUM (0.3 - 0.7):
- General knowledge questions without personal context
- Requests for explanations of concepts
- Opinions without lasting significance

USER MESSAGE: {user_msg}
ASSISTANT RESPONSE: {bot_msg}

Respond with ONLY a single decimal number between 0.0 and 1.0. Nothing else.
Example: 0.85"""

def score_importance(user_msg, bot_msg):
    if not _client:
        return 1.0

    try:
        prompt = _SCORING_PROMPT.format(user_msg=user_msg, bot_msg=bot_msg)
        response = _client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "temperature": 0.0,
                "max_output_tokens": 256,
                "thinking_config": {"thinking_budget": 0},
            },
        )
        return _parse_score(response.text)
    except Exception as e:
        print(f"[WARN] Importance scoring failed, defaulting to 1.0: {e}")
        return 1.0

def _parse_score(raw_text):
    if not raw_text:
        return 1.0
    match = re.search(r"(0(?:\.\d+)?|1(?:\.0+)?)", raw_text.strip())
    if match:
        score = float(match.group(1))
        return max(0.0, min(1.0, score))
    return 1.0

def is_duplicate_memory(text, similarity_threshold=None):
    if similarity_threshold is None:
        similarity_threshold = DUPLICATE_SIMILARITY_THRESHOLD

    from retrieval.embedding_service import (
        generate_embedding, get_all_embeddings, cosine_similarity,
    )

    new_embedding = generate_embedding(text)
    if new_embedding is None:
        return False

    all_embeddings = get_all_embeddings()
    if not all_embeddings:
        return False

    for entry in all_embeddings:
        sim = cosine_similarity(new_embedding, entry["embedding"])
        if sim >= similarity_threshold:
            return True

    return False
