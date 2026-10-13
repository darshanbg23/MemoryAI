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

VALID_CATEGORIES = [
    "Personal",
    "Education",
    "Career",
    "Projects",
    "Programming",
    "Preferences",
]

DEFAULT_CATEGORY = "General"
ALL_CATEGORIES = VALID_CATEGORIES + [DEFAULT_CATEGORY]

_CATEGORIZATION_PROMPT = """You are a memory categorizer for a personal AI assistant.

Given a user message, classify it into exactly ONE of these categories:

- Personal: Name, age, location, family, relationships, hobbies, daily life
- Education: Degree, university, school, courses, studying, academic work
- Career: Job, company, role, work experience, interviews, placements
- Projects: Technical projects, side projects, assignments, research work
- Programming: Languages, frameworks, libraries, code, tools, debugging
- Preferences: Likes, dislikes, favorites, preferred tone, style choices

USER MESSAGE: {text}

Respond with ONLY the category name. Nothing else.
Example: Personal"""

def categorize_memory(text):
    if not _client or not text or not text.strip():
        return DEFAULT_CATEGORY

    try:
        prompt = _CATEGORIZATION_PROMPT.format(text=text)
        response = _client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "temperature": 0.0,
                "max_output_tokens": 256,
                "thinking_config": {"thinking_budget": 0},
            },
        )
        return _parse_category(response.text)
    except Exception as e:
        print(f"[WARN] Memory categorization failed, defaulting to '{DEFAULT_CATEGORY}': {e}")
        return DEFAULT_CATEGORY

def _parse_category(raw_text):
    if not raw_text:
        return DEFAULT_CATEGORY

    cleaned = raw_text.strip().strip(".")

    for cat in VALID_CATEGORIES:
        if cleaned.lower() == cat.lower():
            return cat

    for cat in VALID_CATEGORIES:
        if re.search(rf'\b{re.escape(cat)}\b', cleaned, re.IGNORECASE):
            return cat

    return DEFAULT_CATEGORY
