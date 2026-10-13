import os
import sys
import streamlit as st

st.set_page_config(
    page_title="MemoryAI",
    layout="wide",
    initial_sidebar_state="expanded",
)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.memory_manager import MemoryManager
from profiles.user_profile import ensure_profile_exists, get_tone, get_display_name
from app.ui.styles import inject_global_styles
from app.ui.sidebar import render_sidebar
from app.ui.chat import render_chat_area, render_composer, handle_send
from app.ui.views import (
    render_memory_explorer_view,
    render_pinned_memories_view,
    render_settings_view,
)

memory_mgr = MemoryManager()
ensure_profile_exists()

if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'memory_loaded' not in st.session_state:
    st.session_state.memory_loaded = False
if 'showing_thinking' not in st.session_state:
    st.session_state.showing_thinking = False
if 'active_view' not in st.session_state:
    st.session_state.active_view = 'chat'

if 'current_conversation_id' not in st.session_state:
    saved_convs = memory_mgr.get_conversations()
    if saved_convs:
        st.session_state.current_conversation_id = saved_convs[0]["id"]
    else:
        st.session_state.current_conversation_id = memory_mgr.create_conversation("New Chat")

def load_active_conversation_messages():
    if not st.session_state.memory_loaded:
        conv_id = st.session_state.current_conversation_id
        st.session_state.messages = memory_mgr.load_conversation_messages(conv_id)
        st.session_state.memory_loaded = True

load_active_conversation_messages()

display_name = get_display_name()
user_tone = get_tone()

inject_global_styles()

render_sidebar(
    memory_mgr=memory_mgr,
    display_name=display_name,
    user_tone=user_tone,
    current_conv_id=st.session_state.current_conversation_id,
)

active_view = st.session_state.get("active_view", "chat")

if active_view == "chat":
    render_chat_area(
        messages=st.session_state.messages,
        display_name=display_name,
        conv_id=st.session_state.current_conversation_id,
        memory_mgr=memory_mgr,
    )
    user_input, send_clicked = render_composer()
    handle_send(
        user_input=user_input,
        send_clicked=send_clicked,
        memory_mgr=memory_mgr,
        user_tone=user_tone,
        display_name=display_name,
        conversation_id=st.session_state.current_conversation_id,
    )
elif active_view == "memory_explorer":
    render_memory_explorer_view(memory_mgr)
elif active_view == "pinned_memories":
    render_pinned_memories_view(memory_mgr)
elif active_view == "settings":
    render_settings_view(memory_mgr, display_name, user_tone)