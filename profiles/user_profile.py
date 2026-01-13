import json
import os
from datetime import datetime

# Global profiles dictionary: user_id -> profile dict
profiles = {}

# File path for profiles
PROFILES_FILE = 'user_profiles.json'

# Available tone options
AVAILABLE_TONES = ["Friendly", "Technical", "Casual"]

# Maximum number of user profiles allowed
MAX_PROFILES = 10

def load_profiles():
    global profiles
    if os.path.exists(PROFILES_FILE):
        try:
            with open(PROFILES_FILE, 'r') as f:
                profiles = json.load(f)
        except Exception as e:
            print(f"Error loading profiles: {e}")
            profiles = {}

def save_profiles():
    try:
        with open(PROFILES_FILE, 'w') as f:
            json.dump(profiles, f, indent=4)
    except Exception as e:
        print(f"Error saving profiles: {e}")

# Load profiles on startup
load_profiles()

def create_user_profile(user_id, display_name, tone="Friendly", preferences=None):
    """
    Create a custom user profile with display name and tone preference
    Returns a tuple: (success: bool, message: str)
    """
    # Check if user already exists
    if user_id in profiles:
        return False, "User ID already exists!"
    
    # Check if maximum profiles limit reached
    if len(profiles) >= MAX_PROFILES:
        return False, f"Maximum limit of {MAX_PROFILES} profiles reached. Please delete an existing profile to create a new one."
    
    # Validate tone
    if tone not in AVAILABLE_TONES:
        tone = "Friendly"
    
    if preferences is None:
        preferences = {}
    
    profile = {
        "user_id": user_id,
        "display_name": display_name,
        "tone": tone,
        "preferences": preferences,
        "conversation_count": 0,
        "first_interaction": datetime.now().isoformat()
    }
    profiles[user_id] = profile
    save_profiles()
    return True, f"✅ Profile created successfully!"

def get_user_profile(user_id):
    """Get user profile by user_id"""
    return profiles.get(user_id, None)

def get_user_tone(user_id):
    """Get user's tone preference"""
    profile = profiles.get(user_id, None)
    if profile:
        return profile.get("tone", "Friendly")
    return "Friendly"

def get_user_display_name(user_id):
    """Get user's display name"""
    profile = profiles.get(user_id, None)
    if profile:
        return profile.get("display_name", user_id)
    return user_id

def get_all_users():
    """Get all available user IDs"""
    return list(profiles.keys())

def update_user_profile(user_id, display_name=None, tone=None):
    """Update user's display name and/or tone"""
    if user_id not in profiles:
        return False
    
    if display_name:
        profiles[user_id]["display_name"] = display_name
    
    if tone and tone in AVAILABLE_TONES:
        profiles[user_id]["tone"] = tone
    
    save_profiles()
    return True

def update_user_preferences(user_id, new_preferences):
    """Update user's preferences"""
    if user_id in profiles:
        profiles[user_id]["preferences"].update(new_preferences)
        save_profiles()
        return True
    return False

def delete_user_profile(user_id):
    """Delete a user profile"""
    if user_id in profiles:
        del profiles[user_id]
        save_profiles()
        return True
    return False

def get_profile_count():
    """Get the current number of user profiles"""
    return len(profiles)

def get_max_profile_limit():
    """Get the maximum number of profiles allowed"""
    return MAX_PROFILES