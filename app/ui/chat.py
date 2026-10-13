import time
import streamlit as st

from app.ui.components import (
    render_user_message,
    render_bot_message,
    render_thinking_message,
    render_welcome,
    render_header,
)

def render_chat_area(messages, display_name, conv_id=None, memory_mgr=None):
    render_header(conv_id=conv_id, memory_mgr=memory_mgr)

    if messages:
        st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
        for message in messages:
            role = message.get("role", "")
            if role == "user":
                render_user_message(message["content"], display_name)
            elif role == "thinking":
                render_thinking_message()
            else:
                render_bot_message(message["content"])
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        render_welcome()

def render_composer():
    st.markdown("<div class='input-container'>", unsafe_allow_html=True)

    input_col, button_col = st.columns([6, 0.8], gap="small")

    with input_col:
        user_input = st.text_input(
            "Your message",
            key="message_input",
            placeholder="Type your message here...",
            label_visibility="collapsed",
        )

    with button_col:
        send_clicked = st.button("Send", key="send_btn", use_container_width=True, type="primary")

    st.markdown("</div>", unsafe_allow_html=True)

    return user_input, send_clicked

def handle_send(user_input, send_clicked, memory_mgr, user_tone, display_name, conversation_id="default"):
    if send_clicked and user_input and user_input.strip():
        st.session_state.messages.append({
            "role": "user",
            "content": user_input.strip(),
        })
        st.session_state.messages.append({
            "role": "thinking",
            "content": "Thinking...",
        })
        st.session_state.showing_thinking = True
        st.rerun()

    if st.session_state.showing_thinking and st.session_state.messages:
        messages = st.session_state.messages

        if messages and (
            messages[-1].get("role") == "thinking"
            or (len(messages) >= 2 and messages[-2].get("role") == "user")
        ):
            user_msg_index = len(messages) - 1
            if messages[-1].get("role") == "thinking":
                user_msg_index = len(messages) - 2

            if user_msg_index >= 0 and messages[user_msg_index].get("role") == "user":
                last_user_message = messages[user_msg_index]["content"]

                hybrid_ctx = memory_mgr.get_hybrid_context(last_user_message)

                time.sleep(1.5)

                from generation.response_generator import generate_response

                bot_response = generate_response(
                    last_user_message,
                    tone=user_tone,
                    display_name=display_name,
                    hybrid_context=hybrid_ctx,
                )

                if st.session_state.messages[-1].get("role") == "thinking":
                    st.session_state.messages.pop()

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": bot_response,
                })

                memory_mgr.save_conversation(last_user_message, bot_response, conversation_id=conversation_id)

                st.session_state.showing_thinking = False
                st.rerun()
