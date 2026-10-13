import re

_TONE_MAP = {
    "Friendly": (
        "Your tone should be warm, approachable, and conversational. "
        "Use friendly language. Be encouraging and supportive. "
        "Use simple explanations. Be like talking to a helpful friend. "
        "Examples: 'Hey! I'd love to help with that!' or 'Great question!'"
    ),
    "Technical": (
        "Your tone should be professional, precise, and detail-oriented. "
        "Use technical terminology correctly. Focus on accuracy and depth. "
        "Provide code examples when relevant. Explain the 'why' behind "
        "concepts. Be direct and efficient. Examples: 'This implementation "
        "leverages...' or 'The underlying mechanism is...'"
    ),
    "Casual": (
        "Your tone should be relaxed, informal, and laid-back. Use "
        "conversational language. Keep it light and not overly formal. Use "
        "contractions (I'd, you're, etc.). Be straightforward and "
        "unpretentious. Examples: 'So basically...' or 'Here's the deal...'"
    ),
}

_CROSS_TONE_PREFIXES = {
    "technical_user_casual_query": (
        "I notice you're asking something more casual! While I usually "
        "focus on technical details, let me respond in a friendly way...\n\n"
    ),
    "friendly_user_technical_query": (
        "Thanks for the question! While I usually keep things friendly and "
        "simple, let me dive into the technical details for you...\n\n"
    ),
    "casual_user_technical_query": (
        "So you're asking something pretty technical! Let me break this "
        "down in a casual way that makes sense...\n\n"
    ),
}

_CASUAL_PATTERNS = [
    r'\bjoke|funny|laugh|humorous',
    r'\bstory|tell me about',
    r'\bchat|how are you|how\'s it going',
    r'\bfeel|emotional|personal',
    r'\bcreative|poem|story',
    r'\b\U0001f60a|\U0001f602|\U0001f389|\u2764\ufe0f|\blol\b',
]

_TECHNICAL_PATTERNS = [
    r'\bcode|algorithm|data structure|api',
    r'\bfunction|variable|syntax|debug',
    r'\boptimize|performance|architecture',
    r'\btechn|system design|database',
    r'\bquery|loop|recursion|python',
]

_SEPARATOR = "=" * 60

def get_tone_instructions(tone):
    return _TONE_MAP.get(tone, _TONE_MAP["Friendly"])

def detect_tone_mismatch(query, user_tone):
    query_lower = query.lower()

    is_casual = any(re.search(p, query_lower) for p in _CASUAL_PATTERNS)
    is_technical = any(re.search(p, query_lower) for p in _TECHNICAL_PATTERNS)

    if user_tone == "Technical" and is_casual:
        return "technical_user_casual_query"
    elif user_tone == "Friendly" and is_technical:
        return "friendly_user_technical_query"
    elif user_tone == "Casual" and is_technical:
        return "casual_user_technical_query"
    return None

def get_cross_tone_prefix(mismatch_type):
    return _CROSS_TONE_PREFIXES.get(mismatch_type, "")

def build_full_conversation_history(memory):
    if not memory:
        return None

    parts = []
    for msg in memory:
        role = msg.get("user", "")
        text = msg.get("text", "")
        if not text:
            continue
        if role == "user":
            parts.append(f"USER: {text}")
        elif role == "bot":
            parts.append(f"ASSISTANT: {text}")

    if not parts:
        return None
    return "\n\n".join(parts)

class PromptBuilder:

    def build(self, query, display_name="User", tone="Friendly",
              hybrid_context=None, context=None, memory=None):
        if hybrid_context is not None:
            return self._build_hybrid_prompt(
                query, hybrid_context, display_name, tone,
            )
        return self._build_legacy_prompt(
            query, context, memory, display_name, tone,
        )

    def _build_hybrid_prompt(self, query, hybrid_context, display_name, tone):
        summary = hybrid_context.get("conversation_summary", "")
        pinned = hybrid_context.get("pinned_memories", "")
        long_term = hybrid_context.get("long_term_memories", "")
        recent = hybrid_context.get("recent_conversation", "")

        sections = [
            self._system_prompt(display_name),
            self._tone_section(display_name, tone),
        ]

        if summary:
            sections.append(self._summary_section(summary))

        if pinned:
            sections.append(self._pinned_section(pinned))

        if long_term:
            sections.append(self._long_term_section(long_term))

        if recent:
            sections.append(self._recent_section(recent))

        if not summary and not pinned and not long_term and not recent:
            sections.append(
                f"\nThis is your first conversation with {display_name}. "
                f"Be warm and welcoming."
            )

        sections.append(self._current_message_section(query, display_name, tone))

        return "\n".join(sections)

    def _build_legacy_prompt(self, query, context, memory, display_name, tone):
        tone_instructions = get_tone_instructions(tone)

        full_history = None
        if memory:
            full_history = build_full_conversation_history(memory)
        if not full_history and context:
            full_history = context

        if full_history:
            return (
                f"You are a helpful AI assistant with perfect memory talking to {display_name}.\n\n"
                f"TONE PREFERENCE FOR {display_name}:\n"
                f"{display_name} prefers a {tone} tone. {tone_instructions}\n\n"
                f"COMPLETE CONVERSATION HISTORY:\n"
                f"{'=' * 80}\n{full_history}\n{'=' * 80}\n\n"
                f"This is the ENTIRE conversation history. Use ALL of it to answer accurately.\n\n"
                f"CURRENT QUESTION FROM {display_name}:\n{query}\n\n"
                f"Extract information from the complete history above and respond in a {tone} tone.\n\n"
                f"YOUR RESPONSE:"
            )
        return (
            f"You are a helpful AI assistant talking to {display_name}.\n\n"
            f"TONE PREFERENCE FOR {display_name}:\n"
            f"{display_name} prefers a {tone} tone. {tone_instructions}\n\n"
            f"This is your first conversation with {display_name}. User says: {query}\n\n"
            f"Respond in a {tone} tone, being warm and welcoming.\n\n"
            f"YOUR RESPONSE:"
        )

    @staticmethod
    def _system_prompt(display_name):
        return f"You are a helpful AI assistant with persistent memory talking to {display_name}."

    @staticmethod
    def _tone_section(display_name, tone):
        instructions = get_tone_instructions(tone)
        return (
            f"\nTONE PREFERENCE FOR {display_name}:\n"
            f"{display_name} prefers a {tone} tone. {instructions}"
        )

    @staticmethod
    def _summary_section(summary):
        return (
            f"\nCONVERSATION SUMMARY (compressed history of earlier conversations):\n"
            f"{_SEPARATOR}\n{summary}\n{_SEPARATOR}\n"
            f"This summary covers older conversations that have been archived. "
            f"Use it for background context about the user."
        )

    @staticmethod
    def _long_term_section(memories):
        return (
            f"\nRELEVANT LONG-TERM MEMORIES (older, semantically relevant information):\n"
            f"{_SEPARATOR}\n{memories}\n{_SEPARATOR}\n"
            f"Use these memories to recall past information when relevant to the current question."
        )

    @staticmethod
    def _pinned_section(pinned):
        return (
            f"\nPINNED MEMORIES (always-active, user-prioritized information):\n"
            f"{_SEPARATOR}\n{pinned}\n{_SEPARATOR}\n"
            f"These memories have been explicitly pinned. Always consider them."
        )

    @staticmethod
    def _recent_section(recent):
        return (
            f"\nRECENT CONVERSATION (most recent messages for continuity):\n"
            f"{_SEPARATOR}\n{recent}\n{_SEPARATOR}"
        )

    @staticmethod
    def _current_message_section(query, display_name, tone):
        return (
            f"\nCURRENT QUESTION FROM {display_name}:\n{query}\n\n"
            f"Respond in a {tone} tone.\n\nYOUR RESPONSE:"
        )
