import streamlit as st

def render_memory_panel(memory_mgr):
    saved_memories = memory_mgr.get_memory_count()

    st.markdown("""
    <div class="memory-panel-card">
        <div class="memory-panel-header">
            <span class="memory-panel-title">Memory Summary</span>
        </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <div class="memory-panel-stat-big">{saved_memories}</div>
        <div class="memory-panel-stat-label">Total Memories</div>
    """, unsafe_allow_html=True)

    try:
        pinned_count = sum(1 for m in memory_mgr.export_memories() if m.get("pinned", False))
    except Exception:
        pinned_count = 0

    try:
        all_memories = memory_mgr.export_memories()
        categories = set(m.get("category") or "General" for m in all_memories)
        cat_count = len(categories) if all_memories else 0
    except Exception:
        cat_count = 0

    st.markdown(f"""
        <div class="memory-panel-stats-row">
            <div class="memory-panel-stat-item">
                <div class="memory-panel-stat-value">{pinned_count}</div>
                <div class="memory-panel-stat-desc">Pinned</div>
            </div>
            <div class="memory-panel-stat-item">
                <div class="memory-panel-stat-value">{cat_count}</div>
                <div class="memory-panel-stat-desc">Categories</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if saved_memories > 0:
        st.markdown("""
        <div class="memory-panel-card" style="margin-top: 16px;">
            <div class="memory-panel-header">
                <span class="memory-panel-title">Recent Memories</span>
            </div>
        """, unsafe_allow_html=True)

        try:
            recent = memory_mgr.export_memories()[-3:]
            recent.reverse()
            for mem in recent:
                text_preview = (mem.get("text", ""))[:60]
                if len(mem.get("text", "")) > 60:
                    text_preview += "..."
                cat = mem.get("category") or "General"
                st.markdown(f"""
                <div class="memory-panel-recent-item">
                    <div class="memory-panel-recent-text">{text_preview}</div>
                    <div class="memory-panel-recent-cat">{cat}</div>
                </div>
                """, unsafe_allow_html=True)
        except Exception:
            pass

        st.markdown("</div>", unsafe_allow_html=True)
