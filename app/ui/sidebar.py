from datetime import datetime
import streamlit as st

from app.ui.styles import inject_sidebar_styles
from app.ui.components import section_label, divider, spacer

def render_sidebar(memory_mgr, display_name, user_tone, current_conv_id):
    with st.sidebar:
        inject_sidebar_styles()
        _brand_section()
        divider()
        _new_chat_section(memory_mgr)
        spacer(10)
        _navigation_section()
        divider()
        _conversations_section(memory_mgr, current_conv_id)

def _brand_section():
    st.markdown("""
    <div style='padding: 2px 0 6px 0;'>
        <div style='font-size: 1.25rem; font-weight: 700; color: #ffffff; letter-spacing: -0.3px;'>
            MemoryAI
        </div>
        <div style='font-size: 0.8rem; color: rgba(255, 255, 255, 0.6); margin-top: 1px;'>
            Your AI with memory
        </div>
    </div>
    """, unsafe_allow_html=True)

def _new_chat_section(memory_mgr):
    if st.button("+ New Chat", key="sb_new_chat_btn", use_container_width=True, type="primary"):
        new_conv_id = memory_mgr.create_conversation(title="New Chat")
        st.session_state.current_conversation_id = new_conv_id
        st.session_state.messages = []
        st.session_state.showing_thinking = False
        st.session_state.active_view = "chat"
        st.rerun()

def _navigation_section():
    section_label("Navigation")
    active_view = st.session_state.get("active_view", "chat")

    c1, c2 = st.columns(2)
    with c1:
        if st.button(
            "Chat",
            key="nav_chat_btn",
            use_container_width=True,
            type="primary" if active_view == "chat" else "secondary",
        ):
            st.session_state.active_view = "chat"
            st.rerun()
    with c2:
        if st.button(
            "Memory",
            key="nav_mem_btn",
            use_container_width=True,
            type="primary" if active_view == "memory_explorer" else "secondary",
        ):
            st.session_state.active_view = "memory_explorer"
            st.rerun()

    c3, c4 = st.columns(2)
    with c3:
        if st.button(
            "Pinned",
            key="nav_pinned_btn",
            use_container_width=True,
            type="primary" if active_view == "pinned_memories" else "secondary",
        ):
            st.session_state.active_view = "pinned_memories"
            st.rerun()
    with c4:
        if st.button(
            "Settings",
            key="nav_settings_btn",
            use_container_width=True,
            type="primary" if active_view == "settings" else "secondary",
        ):
            st.session_state.active_view = "settings"
            st.rerun()

def _format_time(iso_str):
    if not iso_str:
        return ""
    try:
        dt = datetime.fromisoformat(iso_str)
        now = datetime.now()
        if dt.date() == now.date():
            return dt.strftime("%I:%M %p")
        elif dt.year == now.year:
            return dt.strftime("%b %d")
        else:
            return dt.strftime("%b %d, %Y")
    except Exception:
        return ""

def _conversations_section(memory_mgr, current_conv_id):
    section_label("Recent Conversations")

    conversations = memory_mgr.get_conversations()

    if not conversations:
        st.markdown(
            "<div style='font-size: 0.78rem; color: rgba(255,255,255,0.35); font-style: italic; padding: 4px 6px;'>"
            "No conversations yet</div>",
            unsafe_allow_html=True,
        )
        return

    search_conv = ""
    if len(conversations) > 4:
        search_conv = st.text_input(
            "Filter chats",
            key="conv_search_filter",
            placeholder="Search conversations...",
            label_visibility="collapsed",
        ).strip().lower()

    filtered = [
        c for c in conversations
        if not search_conv or search_conv in c["title"].lower()
    ]

    for conv in filtered:
        cid = conv["id"]
        title = conv["title"] or "New Chat"
        time_str = _format_time(conv.get("updated_at"))
        msg_cnt = conv.get("message_count", 0)
        is_active = (cid == current_conv_id and st.session_state.get("active_view", "chat") == "chat")

        label = f"{title}"
        if time_str:
            label += f" • {time_str}"

        btn_type = "primary" if is_active else "secondary"
        if st.button(
            label,
            key=f"conv_sel_{cid}",
            use_container_width=True,
            type=btn_type,
            help=f"{title} ({msg_cnt} messages)",
        ):
            st.session_state.current_conversation_id = cid
            st.session_state.messages = memory_mgr.load_conversation_messages(cid)
            st.session_state.active_view = "chat"
            st.rerun()
