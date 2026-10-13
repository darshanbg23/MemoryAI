import json
import streamlit as st
from app.ui.components import render_memory_item, spacer
from memory.memory_categorizer import ALL_CATEGORIES
from profiles.user_profile import AVAILABLE_TONES, update_profile
from retrieval.embedding_service import get_pinned_embeddings

def render_memory_explorer_view(memory_mgr):
    top_col1, top_col2 = st.columns([5, 1])
    with top_col1:
        st.markdown("""
        <div style='padding: 2px 0;'>
            <div style='font-size: 1.45rem; font-weight: 700; color: #ffffff;'>Memory Explorer</div>
            <div style='font-size: 0.82rem; color: rgba(255, 255, 255, 0.6);'>
                Search, filter, edit, pin, and export your stored long-term memories.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with top_col2:
        if st.button("← Back to Chat", key="back_from_mem_exp", use_container_width=True):
            st.session_state.active_view = "chat"
            st.rerun()

    st.divider()

    saved_memories = memory_mgr.get_memory_count()
    if saved_memories == 0:
        st.info("No saved memories yet. Important facts from your conversations will automatically be stored here.")
        return

    col_mode, col_cat = st.columns([1, 1])
    with col_mode:
        search_mode = st.radio(
            "Search mode",
            ["Keyword", "Semantic"],
            key="view_mem_search_mode",
            horizontal=True,
        )
    with col_cat:
        cat_options = ["All"] + ALL_CATEGORIES
        selected_category = st.selectbox(
            "Filter by category",
            cat_options,
            key="view_mem_cat_filter",
        )

    search_q = st.text_input(
        "Search memories",
        key="view_mem_search",
        placeholder="Type to search..." if search_mode == "Keyword" else "Describe what you're looking for...",
    )

    if search_mode == "Semantic":
        displayed_memories = memory_mgr.semantic_search_memories(search_q)
    else:
        displayed_memories = memory_mgr.search_memories(search_q)

    if selected_category != "All":
        displayed_memories = [
            m for m in displayed_memories
            if (m.get("category") or "General") == selected_category
        ]

    st.caption(f"Showing {len(displayed_memories)} of {saved_memories} memories")

    if displayed_memories:
        for entry in displayed_memories:
            eid = entry["id"]
            text = entry.get("text", "")
            is_pinned = entry.get("pinned", False)

            render_memory_item(entry, search_mode, search_q)

            c1, c2, c3 = st.columns([1, 1, 1])
            with c1:
                pin_label = "Unpin" if is_pinned else "Pin"
                if st.button(pin_label, key=f"view_pin_{eid}", use_container_width=True):
                    memory_mgr.toggle_memory_pin(eid, not is_pinned)
                    st.rerun()
            with c2:
                if st.button("Edit", key=f"view_edit_{eid}", use_container_width=True):
                    st.session_state["view_mem_editing"] = eid
            with c3:
                if st.session_state.get("view_mem_confirm_delete") == eid:
                    if st.button("Confirm Delete", key=f"view_cdel_{eid}", use_container_width=True, type="primary"):
                        memory_mgr.delete_memory(eid)
                        st.session_state.pop("view_mem_confirm_delete", None)
                        st.rerun()
                else:
                    if st.button("Delete", key=f"view_del_{eid}", use_container_width=True):
                        st.session_state["view_mem_confirm_delete"] = eid
                        st.rerun()

            if st.session_state.get("view_mem_editing") == eid:
                new_text = st.text_area("Edit memory content", value=text, key=f"view_edt_txt_{eid}")
                ec1, ec2 = st.columns(2)
                with ec1:
                    if st.button("Save Changes", key=f"view_esave_{eid}", use_container_width=True, type="primary"):
                        if new_text and new_text.strip():
                            if memory_mgr.edit_memory(eid, new_text.strip()):
                                st.session_state.pop("view_mem_editing", None)
                                st.rerun()
                            else:
                                st.error("Failed to re-embed memory. Check API key.")
                with ec2:
                    if st.button("Cancel", key=f"view_ecancel_{eid}", use_container_width=True):
                        st.session_state.pop("view_mem_editing", None)
                        st.rerun()

            st.write("")
    else:
        st.write("No memories matched your query.")

    spacer(12)
    export_data = json.dumps(memory_mgr.export_memories(), indent=2)
    st.download_button(
        "Export All Memories (JSON)",
        data=export_data,
        file_name="memories_export.json",
        mime="application/json",
        key="view_export_btn",
    )

def render_pinned_memories_view(memory_mgr):
    top_col1, top_col2 = st.columns([5, 1])
    with top_col1:
        st.markdown("""
        <div style='padding: 2px 0;'>
            <div style='font-size: 1.45rem; font-weight: 700; color: #ffffff;'>Pinned Memories</div>
            <div style='font-size: 0.82rem; color: rgba(255, 255, 255, 0.6);'>
                Pinned memories are permanently prioritized and injected into all prompt contexts.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with top_col2:
        if st.button("← Back to Chat", key="back_from_pinned", use_container_width=True):
            st.session_state.active_view = "chat"
            st.rerun()

    st.divider()

    pinned = get_pinned_embeddings()
    if not pinned:
        st.info("No pinned memories yet. You can pin important memories from the Memory Explorer.")
        return

    st.write(f"You have **{len(pinned)}** pinned memories:")
    for p in pinned:
        with st.container():
            p_col1, p_col2 = st.columns([5, 1])
            with p_col1:
                st.markdown(
                    f"<div class='sb-memory-item sb-memory-item-pinned' style='font-size: 0.9rem; padding: 12px; margin-bottom: 8px;'>"
                    f"{p['text']}</div>",
                    unsafe_allow_html=True,
                )
            with p_col2:
                if st.button("Unpin", key=f"view_unpin_{p['id']}", use_container_width=True):
                    memory_mgr.toggle_memory_pin(p['id'], False)
                    st.rerun()

def render_settings_view(memory_mgr, display_name, user_tone):
    top_col1, top_col2 = st.columns([5, 1])
    with top_col1:
        st.markdown("""
        <div style='padding: 2px 0;'>
            <div style='font-size: 1.45rem; font-weight: 700; color: #ffffff;'>Settings</div>
            <div style='font-size: 0.82rem; color: rgba(255, 255, 255, 0.6);'>
                Manage your user profile, response style, and data storage.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with top_col2:
        if st.button("← Back to Chat", key="back_from_settings", use_container_width=True):
            st.session_state.active_view = "chat"
            st.rerun()

    st.divider()

    st.subheader("Profile & Conversation Preferences")
    col1, col2 = st.columns(2)
    with col1:
        new_name = st.text_input("Display Name", value=display_name, key="set_display_name")
    with col2:
        new_tone = st.selectbox(
            "Default Response Tone",
            AVAILABLE_TONES,
            index=AVAILABLE_TONES.index(user_tone) if user_tone in AVAILABLE_TONES else 0,
            key="set_response_tone",
        )

    if st.button("Save Preferences", key="save_settings_btn", type="primary"):
        if update_profile(new_name, new_tone):
            st.success("Preferences saved successfully!")
            st.rerun()

    spacer(24)
    st.divider()

    st.subheader("Data Management")
    st.markdown(
        "<p style='color: rgba(255,255,255,0.6); font-size: 0.88rem;'>"
        "Manage your persistent SQLite database, conversation history, and long-term memory embeddings."
        "</p>",
        unsafe_allow_html=True,
    )

    if not st.session_state.get("show_clear_all_confirm", False):
        if st.button("Clear All Memory", key="trigger_clear_all_btn", type="secondary"):
            st.session_state.show_clear_all_confirm = True
            st.rerun()
    else:
        st.warning("**Danger Zone:** This will permanently delete all messages, conversations, and long-term memory embeddings. This action cannot be undone.")
        confirm_check = st.checkbox("I understand that all memory data will be permanently erased", key="clear_all_ack")
        c_del, c_cancel = st.columns([1, 1])
        with c_del:
            if st.button("Confirm Delete All", key="execute_clear_all_btn", type="primary", disabled=not confirm_check):
                memory_mgr.delete_conversations()
                st.session_state.messages = []
                st.session_state.memory_loaded = False
                st.session_state.show_clear_all_confirm = False
                st.session_state.active_view = "chat"
                st.success("All memory data has been cleared.")
                st.rerun()
        with c_cancel:
            if st.button("Cancel", key="cancel_clear_all_btn"):
                st.session_state.show_clear_all_confirm = False
                st.rerun()
