import os
from dotenv import load_dotenv
from google import genai
import re

# Load environment variables from .env file
load_dotenv()

# Configure Gemini API with the new google-genai library
API_KEY = os.getenv("GEMINI_API_KEY", "")

# Initialize the client
if API_KEY:
    client = genai.Client(api_key=API_KEY)
else:
    client = None


def get_tone_instructions(tone):
    """Get specific instructions based on user's tone preference"""
    tone_map = {
        "Friendly": "Your tone should be warm, approachable, and conversational. Use friendly language and emojis where appropriate. Be encouraging and supportive. Use simple explanations. Be like talking to a helpful friend. Examples: 'Hey! I\'d love to help with that! 😊' or 'Great question!'",
        
        "Technical": "Your tone should be professional, precise, and detail-oriented. Use technical terminology correctly. Focus on accuracy and depth. Provide code examples when relevant. Explain the 'why' behind concepts. Be direct and efficient. Examples: 'This implementation leverages...' or 'The underlying mechanism is...'",
        
        "Casual": "Your tone should be relaxed, informal, and laid-back. Use conversational language. Keep it light and not overly formal. Use contractions (I'd, you're, etc.). Be straightforward and unpretentious. Examples: 'So basically...' or 'Here's the deal...'"
    }
    
    return tone_map.get(tone, tone_map["Friendly"])


def detect_tone_mismatch(query, user_tone):
    """Detect if query doesn't match the user's tone preference"""
    query_lower = query.lower()
    
    # Patterns that suggest non-technical questions
    casual_patterns = [
        r'\bjoke|funny|laugh|humorous',
        r'\bstory|tell me about',
        r'\bchat|how are you|how\'s it going',
        r'\bfeel|emotional|personal',
        r'\bcreative|poem|story',
        r'\b😊|😂|🎉|❤️|\blol\b'
    ]
    
    # Patterns that suggest technical questions
    technical_patterns = [
        r'\bcode|algorithm|data structure|api',
        r'\bfunction|variable|syntax|debug',
        r'\boptimize|performance|architecture',
        r'\btechn|system design|database',
        r'\bquery|loop|recursion|python'
    ]
    
    is_casual_query = any(re.search(pattern, query_lower) for pattern in casual_patterns)
    is_technical_query = any(re.search(pattern, query_lower) for pattern in technical_patterns)
    
    # Check for mismatches
    if user_tone == "Technical" and is_casual_query:
        return "technical_user_casual_query"
    elif user_tone == "Friendly" and is_technical_query:
        return "friendly_user_technical_query"
    elif user_tone == "Casual" and is_technical_query:
        return "casual_user_technical_query"
    
    return None


def get_cross_tone_prefix(mismatch_type):
    """Get a prefix comment for cross-tone interactions"""
    prefixes = {
        "technical_user_casual_query": "I notice you're asking something more casual! While I usually focus on technical details, let me respond in a friendly way... 😊\n\n",
        "friendly_user_technical_query": "Thanks for the question! While I usually keep things friendly and simple, let me dive into the technical details for you...\n\n",
        "casual_user_technical_query": "So you're asking something pretty technical! Let me break this down in a casual way that makes sense...\n\n"
    }
    return prefixes.get(mismatch_type, "")


def build_full_conversation_history(memory, user_name):
    """
    Build COMPLETE conversation history from ALL user messages
    Every single message included - nothing left out
    """
    if not memory or len(memory) == 0:
        return None
    
    conversation_text = ""
    
    for msg in memory:
        msg_user = msg.get("user", "")
        msg_text = msg.get("text", "")
        
        if not msg_text:
            continue
        
        # Format clearly for Gemini
        if msg_user == user_name:
            conversation_text += f"USER ({user_name}): {msg_text}\n\n"
        elif msg_user.startswith("bot_"):
            conversation_text += f"ASSISTANT: {msg_text}\n\n"
    
    return conversation_text.strip() if conversation_text.strip() else None

def generate_response(query, context, user_name="User", memory=None, tone="Friendly", display_name=None):
    """
    Generate intelligent responses using Google Gemini API
    Uses COMPLETE conversation history (all messages, no truncation)
    Adapts response style based on user's tone preference
    """
    
    if not client or not API_KEY:
        return (
            f"⚠️ **Gemini API not configured**\n\n"
            f"To enable intelligent responses:\n\n"
            f"1. Get your free API key from: https://makersuite.google.com/app/apikey\n"
            f"2. Set environment variable: `$env:GEMINI_API_KEY = 'your_key_here'`\n"
            f"3. Restart the application\n\n"
            f"Your question: '{query}' will be answered once API is configured!"
        )
    
    try:
        # Check for cross-tone mismatch
        mismatch = detect_tone_mismatch(query, tone)
        cross_tone_prefix = get_cross_tone_prefix(mismatch) if mismatch else ""
        
        # Get tone-specific instructions
        tone_instructions = get_tone_instructions(tone)
        
        # Build COMPLETE history from ALL messages
        full_history = None
        if memory and len(memory) > 0:
            full_history = build_full_conversation_history(memory, user_name)
        
        # Fallback to context if no memory
        if not full_history and context:
            full_history = context
        
        # Use display_name if available, otherwise use user_name
        user_ref = display_name if display_name else user_name
        
        # Create prompt with FULL HISTORY and TONE PREFERENCE
        if full_history:
            # User has previous conversation history
            prompt = f"""You are a helpful AI assistant with perfect memory talking to {user_ref}.

TONE PREFERENCE FOR {user_ref}:
{user_ref} prefers a {tone} tone. {tone_instructions}

📜 COMPLETE CONVERSATION HISTORY WITH {user_ref}:
================================================================================
{full_history}
================================================================================

This is the ENTIRE conversation history. Use ALL of it to answer accurately.

CURRENT QUESTION FROM {user_ref}:
{query}

Extract information from the complete history above and respond in a {tone} tone.

YOUR RESPONSE:"""
        else:
            # First conversation
            prompt = f"""You are a helpful AI assistant talking to {user_ref}.

TONE PREFERENCE FOR {user_ref}:
{user_ref} prefers a {tone} tone. {tone_instructions}

This is your first conversation with {user_ref}. User says: {query}

Respond in a {tone} tone, being warm and welcoming.

YOUR RESPONSE:"""
        
        # Call Gemini API
        print("\n" + "="*80)
        print("🔍 API DEBUG - CALLING GEMINI API")
        print("="*80)
        print(f"Model: gemini-2.5-flash-lite")
        print(f"Max Output Tokens: 2500")
        print(f"Prompt Length: {len(prompt)} characters")
        print("-"*80)
        
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
            config={
                "temperature": 0.7,
                "max_output_tokens": 2500,
            }
        )
        
        # Extract the generated text
        generated_text = response.text.strip()
        
        # Log API response details
        print("\n📊 API RESPONSE RECEIVED:")
        print(f"Response Length: {len(generated_text)} characters")
        print(f"Response Preview (first 200 chars): {generated_text[:200]}...")
        print(f"Response End (last 100 chars): ...{generated_text[-100:]}")
        print(f"Full Response:\n{generated_text}")
        print("="*80 + "\n")
        
        # Add cross-tone prefix if applicable
        if cross_tone_prefix:
            generated_text = cross_tone_prefix + generated_text
        
        # Post-process to fix pronoun confusion
        generated_text = fix_pronoun_confusion(generated_text, context, user_name)
        
        return generated_text
    
    except Exception as e:
        error_msg = str(e)
        error_lower = error_msg.lower()
        
        # Check for rate limiting errors (429 or rate limit messages)
        if "429" in error_msg or "rate_limit" in error_lower or "too many requests" in error_lower or "quota" in error_lower:
            return "⏱️ **Request limit reached. Please wait a moment and try again.**\n\nOur service has temporarily reached its request limit. This is usually a brief pause. Feel free to try your question again in a few seconds!"
        
        # Helpful error messages for common issues
        elif "api_key" in error_lower or "authentication" in error_lower or "permission" in error_lower:
            return f"🔐 **Authentication Error**\n\nThere's an issue with the API key. Please check if it's set correctly and try again."
        
        elif "model" in error_lower and ("not found" in error_lower or "not available" in error_lower):
            return "❌ **Model Unavailable**\n\nThe AI model is temporarily unavailable. This usually resolves quickly. Please try again in a moment."
        
        elif "connection" in error_lower or "timeout" in error_lower or "network" in error_lower:
            return "🌐 **Connection Issue**\n\nThere's a network connectivity problem. Please check your internet connection and try again."
        
        elif "invalid" in error_lower and "request" in error_lower:
            return "⚠️ **Invalid Request**\n\nThere was an issue with the request. Please try rephrasing your question and try again."
        
        else:
            # Generic fallback error message
            return f"❌ **Service Temporarily Unavailable**\n\nWe encountered an issue processing your request. Please try again in a moment. If the problem persists, please try later."


def fix_pronoun_confusion(response_text, context, user_name="User"):
    """
    Post-process response to fix pronoun confusion
    Example: Fix "I'm Nandan" to "You're Nandan"
    """
    if not context:
        return response_text
    
    # Extract user's actual name from context
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
        # Fix "I'm [Name]" → "You're [Name]" or "Your name is [Name]"
        response_text = re.sub(
            rf"\bI'm {re.escape(actual_name)}\b",
            f"You're {actual_name}",
            response_text,
            flags=re.IGNORECASE
        )
        
        # Fix "I am [Name]" → "You are [Name]"
        response_text = re.sub(
            rf"\bI am {re.escape(actual_name)}\b",
            f"You are {actual_name}",
            response_text,
            flags=re.IGNORECASE
        )
    
    return response_text
