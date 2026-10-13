import streamlit as st

CAT_COLORS = {
    "Personal":    ("#ec4899", "rgba(236,72,153,0.15)"),
    "Education":   ("#3b82f6", "rgba(59,130,246,0.15)"),
    "Career":      ("#f59e0b", "rgba(245,158,11,0.15)"),
    "Projects":    ("#10b981", "rgba(16,185,129,0.15)"),
    "Programming": ("#8b5cf6", "rgba(139,92,246,0.15)"),
    "Preferences": ("#06b6d4", "rgba(6,182,212,0.15)"),
    "General":     ("#6b7280", "rgba(107,114,128,0.15)"),
}

def section_label(text):
    st.markdown(f"<span class='sb-label'>{text}</span>", unsafe_allow_html=True)

def divider():
    st.markdown("<div class='sb-divider'></div>", unsafe_allow_html=True)

def spacer(px=16):
    st.markdown(f"<div style='margin-top: {px}px;'></div>", unsafe_allow_html=True)

def category_badge_html(category):
    cat = category or "General"
    fg, bg = CAT_COLORS.get(cat, CAT_COLORS["General"])
    return (
        f"<span style='display:inline-block; font-size:0.62rem; "
        f"padding:1px 6px; border-radius:4px; margin-bottom:3px; margin-right:4px; "
        f"background:{bg}; color:{fg}; font-weight:600;'>"
        f"{cat}</span>"
    )

def render_memory_item(entry, search_mode="Keyword", search_q=""):
    text = entry.get("text", "")
    is_pinned = entry.get("pinned", False)
    cat = entry.get("category") or "General"

    pin_class = " sb-memory-item-pinned" if is_pinned else ""
    pin_badge = "<div class='sb-memory-pin-badge'>Pinned</div>" if is_pinned else ""

    cat_badge = category_badge_html(cat)

    sim_badge = ""
    if search_mode == "Semantic" and search_q and search_q.strip() and "similarity" in entry:
        sim_pct = int(entry["similarity"] * 100)
        sim_badge = (
            f"<span style='display:inline-block; font-size:0.65rem; "
            f"padding:2px 6px; border-radius:4px; margin-bottom:4px; "
            f"background:rgba(99,102,241,0.20); color:rgba(165,180,252,0.90);'>"
            f"{sim_pct}% match</span> "
        )

    preview = text[:200] + ("..." if len(text) > 200 else "")
    st.markdown(
        f"<div class='sb-memory-item{pin_class}'>"
        f"{pin_badge}{cat_badge}{sim_badge}{preview}</div>",
        unsafe_allow_html=True,
    )

def render_user_message(content, display_name="User"):
    st.markdown(f"""
    <div class="user-message">
        <div class="message-label">{display_name}</div>
        <div>{content}</div>
    </div>
    """, unsafe_allow_html=True)

def render_bot_message(content):
    st.markdown(f"""
    <div class="bot-message">
        <div class="message-label">Assistant</div>
        <div>{content}</div>
    </div>
    """, unsafe_allow_html=True)

def render_thinking_message():
    st.markdown("""
    <div class="thinking-message">
        <div class="message-label" style="margin: 0;">Assistant</div>
        <span>Thinking</span>
        <div class="thinking-dots" style="margin-left: auto;">
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_header(conv_id=None, memory_mgr=None):
    h_col1, h_col2 = st.columns([5, 1])
    with h_col1:
        st.markdown("""
        <div style='padding: 2px 0;'>
            <div style='font-size: 1.45rem; font-weight: 700; color: #ffffff; letter-spacing: -0.3px; line-height: 1.2;'>
                MemoryAI
            </div>
            <div style='font-size: 0.82rem; color: rgba(255, 255, 255, 0.6); margin-top: 2px;'>
                Your AI with memory
            </div>
        </div>
        """, unsafe_allow_html=True)
    with h_col2:
        if st.button("Clear Chat", key="hdr_clear_chat", use_container_width=True, type="secondary"):
            if memory_mgr and conv_id:
                memory_mgr.clear_conversation(conv_id)
            st.session_state.messages = []
            st.session_state.showing_thinking = False
            st.rerun()

    st.divider()

def render_welcome():
    st.markdown("""
    <div style='text-align: center; padding: 48px 20px 24px 20px;'>
        <div style='font-size: 1.35rem; font-weight: 700; color: #ffffff;'>
            Welcome to MemoryAI
        </div>
        <div style='font-size: 0.88rem; color: rgba(255, 255, 255, 0.55); margin-top: 6px; max-width: 480px; margin-left: auto; margin-right: auto; line-height: 1.5;'>
            Your AI assistant with persistent memory. Ask a question or share details to remember across conversations.
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_footer():
    pass
