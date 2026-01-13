import streamlit as st
import sys
import os
import time
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.memory_store import store_message, get_memory, clear_memory, get_user_memory, clear_user_memory
from retrieval.context_retriever import retrieve_context, retrieve_full_context
from generation.response_generator import generate_response
from profiles.user_profile import (
    get_all_users, get_user_profile, get_user_tone, get_user_display_name,
    create_user_profile, update_user_profile, delete_user_profile, AVAILABLE_TONES,
    get_profile_count, get_max_profile_limit
)

# MUST be first Streamlit command
st.set_page_config(
    page_title="AI Chatbot with Long Term Memory",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'current_user' not in st.session_state:
    st.session_state.current_user = "user1"
if 'user_messages' not in st.session_state:
    st.session_state.user_messages = {}  # Separate messages per user
if 'memory_loaded' not in st.session_state:
    st.session_state.memory_loaded = {}  # Track if memory loaded per user
if 'show_profile_form' not in st.session_state:
    st.session_state.show_profile_form = False
if 'show_edit_form' not in st.session_state:
    st.session_state.show_edit_form = False
if 'message_input_cleared' not in st.session_state:
    st.session_state.message_input_cleared = False
if 'showing_thinking' not in st.session_state:
    st.session_state.showing_thinking = False

def load_user_messages(user_id):
    """Load messages for specific user from long-term memory"""
    if user_id not in st.session_state.memory_loaded:
        # Get only this user's messages from persistent storage
        user_memory = get_user_memory(user_id)
        
        # Initialize user's message list if not exists
        if user_id not in st.session_state.user_messages:
            st.session_state.user_messages[user_id] = []
        
        # Load last 20 messages from this user's history
        loaded_messages = []
        i = 0
        while i < len(user_memory):
            msg = user_memory[i]
            
            # User message
            if msg.get("user") == user_id:
                loaded_messages.append({
                    "role": "user",
                    "content": msg.get("text", "")
                })
                
                # Check if next message is bot response
                if i + 1 < len(user_memory) and user_memory[i + 1].get("user") == f"bot_{user_id}":
                    loaded_messages.append({
                        "role": "assistant",
                        "content": user_memory[i + 1].get("text", "")
                    })
                    i += 2
                else:
                    i += 1
            else:
                i += 1
        
        # Load only last 20 messages to avoid clutter
        st.session_state.user_messages[user_id] = loaded_messages[-20:]
        st.session_state.memory_loaded[user_id] = True

def switch_user(new_user):
    """Switch to different user and load their messages"""
    st.session_state.current_user = new_user
    load_user_messages(new_user)

# Load current user's messages
load_user_messages(st.session_state.current_user)

# Get current user's messages
current_messages = st.session_state.user_messages.get(st.session_state.current_user, [])

# Modern CSS with animations and glassmorphism
st.markdown("""
<style>
    :root {
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --bot-gradient: linear-gradient(135deg, #30cfd0 0%, #330867 100%);
        --bg-dark: #0e0f14;
        --bg-darker: #0a0a15;
        --accent-1: #00f5ff;
        --accent-2: #ff006e;
        --accent-3: #8338ec;
    }
    
    /* Root styling */
    html, body, [data-testid="stAppViewContainer"] {
        # background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 100%);
        background: #0e0f14 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Sidebar glassmorphism effect */
    [data-testid="stSidebar"] {
        background: rgba(10, 10, 21, 0.8) !important;
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(0, 245, 255, 0.1);
    }
    
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Keyframe animations */
    @keyframes slideInRight {
        from {
            transform: translateX(100px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideInLeft {
        from {
            transform: translateX(-100px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes bounce {
        0%, 80%, 100% {
            transform: translateY(0);
        }
        40% {
            transform: translateY(-10px);
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.5;
        }
    }
    
    @keyframes glow {
        0%, 100% {
            box-shadow: 0 0 10px rgba(102, 126, 234, 0.5), 0 4px 15px rgba(0, 0, 0, 0.2);
        }
        50% {
            box-shadow: 0 0 20px rgba(102, 126, 234, 0.8), 0 8px 25px rgba(0, 0, 0, 0.3);
        }
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }
    
    @keyframes scaleIn {
        from {
            transform: scale(0.95);
            opacity: 0;
        }
        to {
            transform: scale(1);
            opacity: 1;
        }
    }
    
    @keyframes dotBounce {
        0%, 60%, 100% {
            animation-timing-function: cubic-bezier(0.5, 0, 0.5, 1);
            opacity: 0.3;
            transform: translateY(0);
        }
        30% {
            animation-timing-function: cubic-bezier(0.5, 0, 0.5, 1);
            opacity: 1;
            transform: translateY(-10px);
        }
    }
    
    /* User message styling */
    .user-message {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        color: white;
        padding: 16px 24px;
        border-radius: 20px;
        margin: 12px 0;
        margin-left: 20%;
        text-align: left;
        box-shadow: 0 4px 15px rgba(79, 70, 229, 0.4), 0 8px 25px rgba(0, 0, 0, 0.15);
        animation: slideInRight 0.4s ease-out;
        transition: all 0.3s ease;
        line-height: 1.6;
        word-wrap: break-word;
    }
    
    .user-message:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 20px rgba(79, 70, 229, 0.6), 0 10px 30px rgba(0, 0, 0, 0.2);
    }
    
    /* Bot message styling */
    .bot-message {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: #ffffff;
        padding: 16px 24px;
        border-radius: 20px;
        margin: 12px 0;
        margin-right: 20%;
        text-align: left;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4), 0 8px 25px rgba(0, 0, 0, 0.15);
        animation: slideInLeft 0.4s ease-out;
        transition: all 0.3s ease;
        line-height: 1.6;
        word-wrap: break-word;
    }
    
    .bot-message:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.6), 0 10px 30px rgba(0, 0, 0, 0.2);
    }        
            
    .message-label {
        font-size: 0.75rem;
        font-weight: 700;
        margin-bottom: 8px;
        opacity: 0.95;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Thinking indicator styling */
    .thinking-message {
        background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
        color: #ffffff;
        padding: 16px 24px;
        border-radius: 20px;
        margin: 12px 0;
        margin-right: 20%;
        text-align: left;
        box-shadow: 0 4px 15px rgba(6, 182, 212, 0.4), 0 8px 25px rgba(0, 0, 0, 0.15);
        animation: slideInLeft 0.4s ease-out;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        gap: 10px;
        line-height: 1.6;
    }
    
    .thinking-message:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 20px rgba(6, 182, 212, 0.6), 0 10px 30px rgba(0, 0, 0, 0.2);
    }
    
    .thinking-dots {
        display: flex;
        gap: 4px;
        align-items: center;
    }
    
    .dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #ffffff;
        animation: dotBounce 1.4s infinite;
    }
    
    .dot:nth-child(2) {
        animation-delay: 0.2s;
    }
    
    .dot:nth-child(3) {
        animation-delay: 0.4s;
    }
    
    /* Text styling in messages */
    .bot-message, .bot-message p, .bot-message div, .bot-message span {
        color: #ffffff !important;
    }
    
    .bot-message strong, .bot-message b {
        color: #ffd700 !important;
        font-weight: 700;
    }
    
    .bot-message a {
        color: #00f5ff !important;
        text-decoration: underline;
        font-weight: 500;
    }
    
    .user-message strong, .user-message b {
        color: #ffd700 !important;
        font-weight: 700;
    }
    
    /* Input area container - Fixed positioning and visibility */
    .input-area-container {
        position: relative;
        width: 100%;
        padding: 30px 0;
        margin-top: 30px;
        background: rgba(15, 15, 35, 0.95);
        backdrop-filter: blur(10px);
        border-top: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    /* Fix Streamlit's column layout for input */
    .stColumns {
        gap: 15px !important;
        align-items: center !important;
        padding: 0 20px !important;
    }
    
    /* Text input container */
    [data-testid="stTextInput"] {
        flex: 1 !important;
        margin: 0 !important;
    }
    
    /* Text input field - Fully visible with proper height */
    [data-testid="stTextInput"] > div {
        margin: 0 !important;
    }
    
    [data-testid="stTextInput"] input {
        height: 60px !important;
        min-height: 60px !important;
        background: #1a1a2e !important;
        border: 2px solid #667eea !important;
        color: #ffffff !important;
        border-radius: 30px !important;
        padding: 0 30px !important;
        font-size: 16px !important;
        line-height: 60px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3), inset 0 2px 4px rgba(0, 0, 0, 0.2) !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }
    
    [data-testid="stTextInput"] input:focus {
        border-color: #764ba2 !important;
        box-shadow: 0 0 25px rgba(118, 75, 162, 0.6), inset 0 2px 4px rgba(0, 0, 0, 0.2) !important;
        background: #1a1a2e !important;
        outline: none !important;
    }
    
    [data-testid="stTextInput"] input::placeholder {
        color: rgba(255, 255, 255, 0.4) !important;
        font-size: 15px !important;
    }
    
    /* Send button container */
    [data-testid="stColumns"] > div:last-child {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    /* Send button - Match input box height exactly */
    [data-testid="stColumns"] > div:last-child button {
        width: 75px !important;
        height: 75px !important;
        min-width: 75px !important;
        min-height: 75px !important;
        max-width: 75px !important;
        max-height: 75px !important;
        padding: 0 !important;
        border-radius: 50% !important;
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%) !important;
        border: none !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 4px 20px rgba(255, 107, 107, 0.5) !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        font-size: 28px !important;
        flex-shrink: 0 !important;
    }
    
    [data-testid="stColumns"] > div:last-child button:hover {
        transform: scale(1.15) !important;
        box-shadow: 0 8px 30px rgba(255, 107, 107, 0.7) !important;
    }
    
    [data-testid="stColumns"] > div:last-child button:active {
        transform: scale(0.95) !important;
    }
    
    [data-testid="stColumns"] > div:last-child button p {
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1 !important;
        font-size: 28px !important;
    }
    
    /* Remove any extra spacing/margins from Streamlit defaults */
    [data-testid="stVerticalBlock"] > div:has([data-testid="stTextInput"]) {
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* Footer text styling */
    .footer-text {
        text-align: center;
        padding: 20px;
        color: rgba(255, 255, 255, 0.6);
        font-size: 14px;
        background: rgba(15, 15, 35, 0.8);
    }
    
    /* General button styling for other buttons */
    [data-testid="baseButton-primary"]:not([data-testid="stColumns"] > div:last-child button) {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        padding: 10px 24px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
    }
    
    [data-testid="baseButton-primary"]:not([data-testid="stColumns"] > div:last-child button):hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5) !important;
    }
    
    [data-testid="baseButton-secondary"] {
        background: rgba(255, 0, 110, 0.1) !important;
        border: 1px solid #ff006e !important;
        color: #ff006e !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 10px 24px !important;
        transition: all 0.3s ease !important;
    }
    
    [data-testid="baseButton-secondary"]:hover {
        background: rgba(255, 0, 110, 0.2) !important;
        transform: translateY(-1px) !important;
    }
    
    /* Selectbox styling */
    [data-testid="stSelectbox"] select {
        background: rgba(26, 26, 46, 0.8) !important;
        color: white !important;
        border: 1px solid rgba(102, 126, 234, 0.3) !important;
        border-radius: 10px !important;
        padding: 10px 15px !important;
    }
    
    /* Remove default Streamlit spacing that causes cut-off */
    .element-container {
        margin-bottom: 0 !important;
    }
    
    /* Ensure input container doesn't overflow */
    .stTextInput > div {
        overflow: visible !important;
    }

    /* Divider styling */
    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(to right, transparent, rgba(102, 126, 234, 0.3), transparent) !important;
        margin: 20px 0 !important;
    }
    
    /* Header styling */
    h1, h2, h3 {
        background: linear-gradient(135deg, #00f5ff, #ff006e, #8338ec);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: fadeIn 0.6s ease-out;
    }
    
    /* Welcome message styling */
    .welcome-container {
        text-align: center;
        padding: 60px 20px;
        animation: fadeIn 0.8s ease-out;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(48, 207, 208, 0.05));
        border-radius: 20px;
        border: 1px solid rgba(102, 126, 234, 0.1);
    }
    
    .welcome-container h3 {
        font-size: 2rem;
        margin-bottom: 15px;
    }
    
    .welcome-container p {
        color: rgba(255, 255, 255, 0.7);
        font-size: 1.1rem;
        margin: 10px 0;
    }
    
    /* Info message styling */
    [data-testid="stInfo"] {
        background: rgba(48, 207, 208, 0.1) !important;
        border-left: 4px solid #30cfd0 !important;
        border-radius: 8px !important;
        animation: slideInLeft 0.4s ease-out !important;
    }
    
    [data-testid="stSuccess"] {
        background: rgba(48, 207, 208, 0.1) !important;
        border-left: 4px solid #00ff88 !important;
        border-radius: 8px !important;
    }
    
    [data-testid="stWarning"] {
        background: rgba(255, 0, 110, 0.1) !important;
        border-left: 4px solid #ff006e !important;
        border-radius: 8px !important;
    }
    
    [data-testid="stError"] {
        background: rgba(255, 0, 110, 0.1) !important;
        border-left: 4px solid #ff0040 !important;
        border-radius: 8px !important;
    }
    
    #MainMenu {
        visibility: hidden;
    }
    footer {
        visibility: hidden;
    }
    
    /* Metric styling */
    [data-testid="metric-container"] {
        background: rgba(102, 126, 234, 0.1) !important;
        border: 1px solid rgba(102, 126, 234, 0.2) !important;
        border-radius: 12px !important;
        padding: 16px !important;
        transition: all 0.3s ease !important;
    }
    
    [data-testid="metric-container"]:hover {
        background: rgba(102, 126, 234, 0.15) !important;
        border-color: rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Expander styling */
    [data-testid="stExpander"] {
        background: rgba(26, 26, 46, 0.6) !important;
        border: 1px solid rgba(102, 126, 234, 0.2) !important;
        border-radius: 12px !important;
    }
    
    /* Chat container */
    .chat-container {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }
    
    /* Smooth scrolling */
    * {
        scroll-behavior: smooth;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .user-message {
            margin-left: 0;
            margin-right: 10%;
        }
        
        .bot-message {
            margin-right: 0;
            margin-left: 10%;
        }
        
        .thinking-message {
            margin-right: 0;
            margin-left: 10%;
        }
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; margin-bottom: 25px;'>
        <h1 style='margin: 0; font-size: 2.5rem;'>👤</h1>
        <h2 style='margin-top: 10px; font-size: 1.3rem;'>User Profile</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Get all available users
    all_users = get_all_users()
    
    # User selection dropdown with custom styling
    st.markdown("""
    <style>
        .sidebar-section-title {
            font-size: 0.9rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #00f5ff;
            margin-top: 20px;
            margin-bottom: 12px;
            display: block;
        }
    </style>
    <span class='sidebar-section-title'>👥 Switch User</span>
    """, unsafe_allow_html=True)
    
    selected_user = st.selectbox(
        "Select User",
        all_users,
        key="user_select",
        index=all_users.index(st.session_state.current_user) if st.session_state.current_user in all_users else 0,
        label_visibility="collapsed"
    )
    
    # If user changed, switch to new user
    if selected_user != st.session_state.current_user:
        switch_user(selected_user)
        st.rerun()
    
    # Get current user info
    user_profile = get_user_profile(st.session_state.current_user)
    user_display_name = get_user_display_name(st.session_state.current_user)
    user_tone = get_user_tone(st.session_state.current_user)
    
    # Display current user info in modern card style
    st.markdown(f"""
    <div style='background: rgba(102, 126, 234, 0.1); border: 1px solid rgba(102, 126, 234, 0.2); border-radius: 12px; padding: 16px; margin: 20px 0; transition: all 0.3s ease;'>
        <div style='margin-bottom: 12px;'>
            <span style='color: #00f5ff; font-size: 0.8rem; font-weight: 700; text-transform: uppercase;'>Display Name</span>
            <p style='margin: 8px 0 0 0; color: #ffffff; font-size: 1.1rem; font-weight: 600;'>{user_display_name}</p>
        </div>
        <div>
            <span style='color: #00f5ff; font-size: 0.8rem; font-weight: 700; text-transform: uppercase;'>Tone</span>
            <p style='margin: 8px 0 0 0; color: #ffd700; font-size: 1rem; font-weight: 600;'>🎨 {user_tone}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Create new user section
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Create New", use_container_width=True):
            st.session_state.show_profile_form = not st.session_state.show_profile_form
    with col2:
        if st.button("✏️ Edit Profile", use_container_width=True):
            st.session_state.show_edit_form = not st.session_state.show_edit_form
    
    if st.session_state.show_profile_form:
        st.subheader("Create New User Profile")
        
        # Display current profile count and limit
        current_count = get_profile_count()
        max_limit = get_max_profile_limit()
        st.info(f"📊 Current profiles: {current_count}/{max_limit}")
        
        new_user_id = st.text_input(
            "User ID (e.g., alex_tech)",
            key="new_user_id",
            placeholder="unique_identifier"
        )
        
        new_display_name = st.text_input(
            "Display Name (e.g., Alex Johnson)",
            key="new_display_name",
            placeholder="Your real name"
        )
        
        new_tone = st.selectbox(
            "Preferred Tone",
            AVAILABLE_TONES,
            key="new_user_tone"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ Create", key="create_user_btn", use_container_width=True, type="primary"):
                if new_user_id and new_display_name:
                    success, message = create_user_profile(new_user_id, new_display_name, new_tone)
                    if success:
                        st.success(message)
                        st.session_state.show_profile_form = False
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Please fill in all fields!")
        
        with col2:
            if st.button("❌ Cancel", key="cancel_create_btn", use_container_width=True, type="secondary"):
                st.session_state.show_profile_form = False
                st.rerun()
    
    if st.session_state.show_edit_form:
        st.subheader("Edit Profile")
        
        edit_display_name = st.text_input(
            "Display Name",
            value=user_display_name,
            key="edit_display_name"
        )
        
        edit_tone = st.selectbox(
            "Preferred Tone",
            AVAILABLE_TONES,
            index=AVAILABLE_TONES.index(user_tone),
            key="edit_user_tone"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ Save", key="save_edit_btn", use_container_width=True, type="primary"):
                if update_user_profile(st.session_state.current_user, edit_display_name, edit_tone):
                    st.success("✅ Profile updated!")
                    st.session_state.show_edit_form = False
                    st.rerun()
        
        with col2:
            if st.button("❌ Cancel", key="cancel_edit_btn", use_container_width=True, type="secondary"):
                st.session_state.show_edit_form = False
                st.rerun()
    
    st.divider()
    
    # Statistics section
    st.markdown("""<span class='sidebar-section-title'>📊 Statistics</span>""", unsafe_allow_html=True)
    
    user_specific_memory = get_user_memory(st.session_state.current_user)
    user_msg_count = len([m for m in user_specific_memory if m.get("user") == st.session_state.current_user])
    current_messages = st.session_state.user_messages.get(st.session_state.current_user, [])
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Messages", user_msg_count)
    with col2:
        st.metric("Session Messages", len(current_messages))
    
    st.divider()
    
    # Actions section
    st.markdown("""<span class='sidebar-section-title'>⚙️ Actions</span>""", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.user_messages[st.session_state.current_user] = []
            st.success("✅ Chat cleared!")
            st.rerun()
    
    with col2:
        if st.button("🧠 Clear Memory", use_container_width=True, type="secondary"):
            clear_user_memory(st.session_state.current_user)
            st.session_state.user_messages[st.session_state.current_user] = []
            st.session_state.memory_loaded[st.session_state.current_user] = False
            st.warning("⚠️ Memory deleted!")
            st.rerun()
    
    st.divider()
    
    # Delete user profile option (only if not the last user)
    if len(all_users) > 1:
        if st.button("❌ Delete Profile", use_container_width=True, type="secondary"):
            delete_user_profile(st.session_state.current_user)
            clear_user_memory(st.session_state.current_user)
            st.session_state.current_user = all_users[0] if all_users[0] != st.session_state.current_user else all_users[1]
            st.session_state.user_messages = {}
            st.session_state.memory_loaded = {}
            st.warning("❌ Profile deleted!")
            st.rerun()
    
    st.divider()
    
    # Memory explorer
    if st.button("📜 View Memory", use_container_width=True):
        st.session_state.show_memory = not st.session_state.get('show_memory', False)
    
    if st.session_state.get('show_memory', False):
        with st.expander("🧠 Memory Store - All Your Memories", expanded=True):
            my_memory = get_user_memory(st.session_state.current_user)
            if my_memory:
                st.markdown(f"**Total memories stored: {len(my_memory)}**")
                st.json(my_memory)  # Show ALL memories for this user
            else:
                st.info("No memory stored yet for your account")

# Main header with modern styling
st.markdown(f"""
<div style='animation: fadeIn 0.6s ease-out;'>
    <h1 style='margin-bottom: 15px; margin-top: 0;'>🤖 AI Chatbot with Long Term Memory</h1>
</div>
""", unsafe_allow_html=True)

# Memory indicator for current user ONLY
if user_msg_count > 0:
    st.markdown("""<div style='margin-top: 20px;'></div>""", unsafe_allow_html=True)
    st.info(f"💾 **Your Memory Active:** {user_msg_count} previous messages from your account")

st.divider()

# Get current user's messages
current_messages = st.session_state.user_messages.get(st.session_state.current_user, [])

# Display chat messages with animations
if current_messages and len(current_messages) > 0:
    st.markdown("""<div class='chat-container'>""", unsafe_allow_html=True)
    
    for idx, message in enumerate(current_messages):
        if message["role"] == "user":
            st.markdown(f"""
            <div class="user-message">
                <div class="message-label">👤 {user_display_name}</div>
                <div>{message["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
        elif message["role"] == "thinking":
            st.markdown(f"""
            <div class="thinking-message">
                <div class="message-label" style="margin: 0;">🤖 Assistant</div>
                <span>Thinking</span>
                <div class="thinking-dots" style="margin-left: auto;">
                    <div class="dot"></div>
                    <div class="dot"></div>
                    <div class="dot"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Log what's about to be rendered
            print("\n" + "="*80)
            print("🖼️ UI DEBUG - RENDERING ASSISTANT MESSAGE")
            print("="*80)
            print(f"Message Content Length: {len(message['content'])} characters")
            print(f"Message Content:\n{message['content']}")
            print("="*80 + "\n")
            
            st.markdown(f"""
            <div class="bot-message">
                <div class="message-label">🤖 Assistant</div>
                <div>{message["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("""</div>""", unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="welcome-container">
        <h3>👋 Welcome, {user_display_name}!</h3>
        <p>Start typing below to begin your conversation</p>
    </div>
    """, unsafe_allow_html=True)

# Input area container using HTML
st.markdown("""<div class='input-container'>""", unsafe_allow_html=True)

input_col, button_col = st.columns([6, 0.8], gap="small")

with input_col:
    user_input = st.text_input(
        "Your message",
        key=f"message_input_{st.session_state.current_user}",
        placeholder="✨ Type your message here...",
        label_visibility="collapsed"
    )

with button_col:
    send_clicked = st.button("➤", key=f"send_btn_{st.session_state.current_user}", use_container_width=True, type="primary")

st.markdown("""</div>""", unsafe_allow_html=True)

# Process message when send is clicked
if send_clicked and user_input and user_input.strip():
    
    # Initialize messages list if not exists
    if st.session_state.current_user not in st.session_state.user_messages:
        st.session_state.user_messages[st.session_state.current_user] = []
    
    # Add user message immediately for instant feedback
    st.session_state.user_messages[st.session_state.current_user].append({
        "role": "user",
        "content": user_input.strip()
    })
    
    # Add thinking message to session state (displayed in chat area)
    st.session_state.user_messages[st.session_state.current_user].append({
        "role": "thinking",
        "content": "Thinking..."
    })
    
    # Trigger thinking animation
    st.session_state.showing_thinking = True
    
    # Rerun to display user message and thinking animation
    st.rerun()

# Show thinking animation and process response
if st.session_state.showing_thinking and st.session_state.current_user in st.session_state.user_messages:
    messages = st.session_state.user_messages[st.session_state.current_user]
    # Check if last message is thinking or user message
    if messages and (messages[-1].get("role") == "thinking" or (len(messages) >= 2 and messages[-2].get("role") == "user")):
        # Get user message (could be last or second to last)
        user_msg_index = len(messages) - 1
        if messages[-1].get("role") == "thinking":
            user_msg_index = len(messages) - 2
        
        if user_msg_index >= 0 and messages[user_msg_index].get("role") == "user":
            last_user_message = messages[user_msg_index]["content"]
            
            # Get COMPLETE current user's memory for full history
            user_specific_memory = get_user_memory(st.session_state.current_user)
            
            # Retrieve FULL context - ALL messages, no truncation
            full_context = retrieve_full_context(user_specific_memory)
            
            # Simulate processing delay for realistic feel (1-2 seconds)
            time.sleep(1.5)
            
            # Generate response with COMPLETE history AND TONE PREFERENCE
            bot_response = generate_response(
                last_user_message,
                full_context,
                user_name=st.session_state.current_user,
                memory=user_specific_memory,
                tone=user_tone,
                display_name=user_display_name
            )
            
            # DEBUG: Log the response to UI
            print("\n" + "="*80)
            print("🎨 UI DEBUG - RECEIVED BOT RESPONSE")
            print("="*80)
            print(f"Response Length: {len(bot_response)} characters")
            print(f"Response Content:\n{bot_response}")
            print("="*80 + "\n")
            
            # Remove thinking message and add actual response
            if st.session_state.user_messages[st.session_state.current_user][-1].get("role") == "thinking":
                st.session_state.user_messages[st.session_state.current_user].pop()
            
            st.session_state.user_messages[st.session_state.current_user].append({
                "role": "assistant",
                "content": bot_response
            })
            
            # DEBUG: Log the stored message in session state
            stored_msg = st.session_state.user_messages[st.session_state.current_user][-1]["content"]
            print("\n" + "="*80)
            print("💾 UI DEBUG - MESSAGE STORED IN SESSION STATE")
            print("="*80)
            print(f"Stored Message Length: {len(stored_msg)} characters")
            print(f"Stored Message Content:\n{stored_msg}")
            print("="*80 + "\n")
            
            # Store in long-term memory with user-specific bot identifier
            store_message(st.session_state.current_user, last_user_message)
            store_message(f"bot_{st.session_state.current_user}", bot_response)
            
            # Stop showing thinking and rerun to display response
            st.session_state.showing_thinking = False
            st.rerun()

# Info at bottom
st.markdown("""
<div style='text-align: center; color: rgba(255, 255, 255, 0.6); font-size: 0.85rem; margin-top: 30px; padding-top: 20px; border-top: 1px solid rgba(102, 126, 234, 0.2);'>
    💬 <strong>AI Chatbot powered by Google Gemini</strong> | Built with Streamlit | Your conversation partner with memory
</div>
""", unsafe_allow_html=True)