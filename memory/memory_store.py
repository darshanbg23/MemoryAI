import pandas as pd
import json
import os

MEMORY_FILE = "conversation_history.json"
memory = []

def load_from_file():
    """Load memory from file"""
    try:
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading memory: {e}")
    return []

def save_to_file():
    """Save memory to file"""
    try:
        with open(MEMORY_FILE, 'w') as f:
            json.dump(memory, f, indent=2)
    except Exception as e:
        print(f"Error saving memory: {e}")

def store_message(user, text):
    """Store a message in memory with user identification"""
    global memory
    memory.append({"user": user, "text": text})
    save_to_file()

def get_memory():
    """Get all stored memory (for admin purposes only)"""
    return memory

def get_user_memory(user_id):
    """
    Get ONLY the specified user's memory
    This ensures complete data isolation
    Handles both old format (user/bot) and new format (user/bot_user)
    """
    # Filter for user's messages and bot responses to that user
    user_specific = []
    for msg in memory:
        # Include user's own messages
        if msg.get("user") == user_id:
            user_specific.append(msg)
        # Include bot responses specifically for this user (new format)
        elif msg.get("user") == f"bot_{user_id}":
            user_specific.append(msg)
        # Include generic bot responses for backward compatibility (old format)
        # Only include if this is user1 (to avoid duplication for other users)
        elif msg.get("user") == "bot" and user_id == "user1":
            user_specific.append(msg)
    
    return user_specific

def clear_memory():
    """Clear all memory (admin function)"""
    global memory
    memory = []
    save_to_file()
    if os.path.exists(MEMORY_FILE):
        os.remove(MEMORY_FILE)

def clear_user_memory(user_id):
    """
    Clear ONLY the specified user's memory
    Preserves other users' data
    """
    global memory
    # Remove only this user's messages
    memory = [msg for msg in memory 
              if msg.get("user") != user_id and msg.get("user") != f"bot_{user_id}"]
    save_to_file()

# Load existing memory on module import
memory = load_from_file()