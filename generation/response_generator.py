import os
import re
from dotenv import load_dotenv
from google import genai

from generation.prompt_builder import (
    PromptBuilder,
    detect_tone_mismatch,
    get_cross_tone_prefix,
)

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY", "")

if API_KEY:
    client = genai.Client(api_key=API_KEY)
else:
    client = None

_prompt_builder = PromptBuilder()

def generate_response(query, context=None, memory=None, tone="Friendly",
                      display_name="User", hybrid_context=None):
    if not client or not API_KEY:
        return (
            f"**Gemini API not configured**\n\n"
            f"To enable intelligent responses:\n\n"
            f"1. Get your free API key from: https://makersuite.google.com/app/apikey\n"
            f"2. Set environment variable: `$env:GEMINI_API_KEY = 'your_key_here'`\n"
            f"3. Restart the application\n\n"
            f"Your question: '{query}' will be answered once API is configured!"
        )

    try:
        mismatch = detect_tone_mismatch(query, tone)
        cross_tone_prefix = get_cross_tone_prefix(mismatch) if mismatch else ""

        prompt = _prompt_builder.build(
            query,
            display_name=display_name,
            tone=tone,
            hybrid_context=hybrid_context,
            context=context,
            memory=memory,
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "temperature": 0.7,
                "max_output_tokens": 2500,
            }
        )

        generated_text = response.text.strip()

        if cross_tone_prefix:
            generated_text = cross_tone_prefix + generated_text

        ctx_for_fix = (
            hybrid_context.get("recent_conversation", "")
            if hybrid_context else context
        )
        generated_text = fix_pronoun_confusion(generated_text, ctx_for_fix, display_name)

        return generated_text

    except Exception as e:
        error_msg = str(e)
        error_lower = error_msg.lower()

        if "429" in error_msg or "rate_limit" in error_lower or "too many requests" in error_lower or "quota" in error_lower:
            return "**Request limit reached. Please wait a moment and try again.**\n\nOur service has temporarily reached its request limit. This is usually a brief pause. Feel free to try your question again in a few seconds!"
        elif "api_key" in error_lower or "authentication" in error_lower or "permission" in error_lower:
            return "**Authentication Error**\n\nThere's an issue with the API key. Please check if it's set correctly and try again."
        elif "model" in error_lower and ("not found" in error_lower or "not available" in error_lower):
            return "**Model Unavailable**\n\nThe AI model is temporarily unavailable. This usually resolves quickly. Please try again in a moment."
        elif "connection" in error_lower or "timeout" in error_lower or "network" in error_lower:
            return "**Connection Issue**\n\nThere's a network connectivity problem. Please check your internet connection and try again."
        elif "invalid" in error_lower and "request" in error_lower:
            return "**Invalid Request**\n\nThere was an issue with the request. Please try rephrasing your question and try again."
        else:
            return "**Service Temporarily Unavailable**\n\nWe encountered an issue processing your request. Please try again in a moment. If the problem persists, please try later."

def fix_pronoun_confusion(response_text, context, display_name="User"):
    if not context:
        return response_text

    name_patterns = [
        r"(?:my name is|i'm|i am|call me)\s+([A-Z][a-z]+)",
        r"name[:\s]+([A-Z][a-z]+)",
    ]

    actual_name = None
    for pattern in name_patterns:
        match = re.search(pattern, context, re.IGNORECASE)
        if match:
            actual_name = match.group(1)
            break

    if actual_name:
        response_text = re.sub(
            rf"\bI'm {re.escape(actual_name)}\b",
            f"You're {actual_name}",
            response_text,
            flags=re.IGNORECASE
        )
        response_text = re.sub(
            rf"\bI am {re.escape(actual_name)}\b",
            f"You are {actual_name}",
            response_text,
            flags=re.IGNORECASE
        )

    return response_text
