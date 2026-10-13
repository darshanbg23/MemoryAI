import streamlit as st

def inject_global_styles():
    st.markdown(_GLOBAL_CSS, unsafe_allow_html=True)

def inject_sidebar_styles():
    st.markdown(_SIDEBAR_CSS, unsafe_allow_html=True)

_GLOBAL_CSS = """
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
    
    html, body, [data-testid="stAppViewContainer"] {
        background: #0e0f14 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    header[data-testid="stHeader"] {
        background: transparent !important;
        height: 2.5rem !important;
    }

    .block-container {
        padding-top: 3.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 1400px;
    }

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

    .input-area-container {
        position: relative;
        width: 100%;
        padding: 30px 0;
        margin-top: 30px;
        background: rgba(15, 15, 35, 0.95);
        backdrop-filter: blur(10px);
        border-top: 1px solid rgba(102, 126, 234, 0.2);
    }

    .stColumns {
        gap: 15px !important;
        align-items: center !important;
        padding: 0 20px !important;
    }

    [data-testid="stTextInput"] {
        flex: 1 !important;
        margin: 0 !important;
    }

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

    [data-testid="stColumns"] > div:last-child {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

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

    [data-testid="stVerticalBlock"] > div:has([data-testid="stTextInput"]) {
        padding: 0 !important;
        margin: 0 !important;
    }

    .footer-text {
        text-align: center;
        padding: 20px;
        color: rgba(255, 255, 255, 0.6);
        font-size: 14px;
        background: rgba(15, 15, 35, 0.8);
    }

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

    [data-testid="stSelectbox"] select {
        background: rgba(26, 26, 46, 0.8) !important;
        color: white !important;
        border: 1px solid rgba(102, 126, 234, 0.3) !important;
        border-radius: 10px !important;
        padding: 10px 15px !important;
    }

    .element-container {
        margin-bottom: 0 !important;
    }

    .stTextInput > div {
        overflow: visible !important;
    }

    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(to right, transparent, rgba(102, 126, 234, 0.3), transparent) !important;
        margin: 20px 0 !important;
    }

    h1, h2, h3 {
        background: linear-gradient(135deg, #00f5ff, #ff006e, #8338ec);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: fadeIn 0.6s ease-out;
    }

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

    .chat-container {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    * {
        scroll-behavior: smooth;
    }

    .memory-panel-card {
        background: rgba(12, 12, 24, 0.85);
        border: 1px solid rgba(102, 126, 234, 0.15);
        border-radius: 16px;
        padding: 20px;
        backdrop-filter: blur(10px);
        animation: fadeIn 0.5s ease-out;
    }

    .memory-panel-header {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 16px;
    }

    .memory-panel-icon {
        font-size: 1.2rem;
    }

    .memory-panel-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: 0.3px;
    }

    .memory-panel-stat-big {
        font-size: 2.4rem;
        font-weight: 800;
        color: #ffffff;
        line-height: 1;
        margin-bottom: 4px;
    }

    .memory-panel-stat-label {
        font-size: 0.78rem;
        color: rgba(255, 255, 255, 0.45);
        margin-bottom: 16px;
    }

    .memory-panel-stats-row {
        display: flex;
        gap: 20px;
        padding-top: 12px;
        border-top: 1px solid rgba(255, 255, 255, 0.06);
    }

    .memory-panel-stat-item {
        flex: 1;
    }

    .memory-panel-stat-value {
        font-size: 1.3rem;
        font-weight: 700;
        color: #ffffff;
    }

    .memory-panel-stat-desc {
        font-size: 0.7rem;
        color: rgba(255, 255, 255, 0.40);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .memory-panel-recent-item {
        padding: 10px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    }

    .memory-panel-recent-item:last-child {
        border-bottom: none;
    }

    .memory-panel-recent-text {
        font-size: 0.82rem;
        color: rgba(255, 255, 255, 0.70);
        line-height: 1.4;
        margin-bottom: 3px;
    }

    .memory-panel-recent-cat {
        font-size: 0.68rem;
        color: rgba(255, 255, 255, 0.35);
    }

    .right-panel-col [data-testid="stVerticalBlock"] {
        position: sticky;
        top: 2rem;
    }

    @media (max-width: 1024px) {
        .block-container {
            max-width: 100% !important;
        }
    }

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
"""

_SIDEBAR_CSS = """
<style>
    [data-testid="stSidebar"] {
        background: #0c0c18 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
    }

    [data-testid="stSidebarContent"],
    [data-testid="stSidebarUserContent"] {
        padding-top: 1.8rem !important;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdown"] h1,
    [data-testid="stSidebar"] [data-testid="stMarkdown"] h2,
    [data-testid="stSidebar"] [data-testid="stMarkdown"] h3 {
        background: none !important;
        -webkit-background-clip: unset !important;
        -webkit-text-fill-color: unset !important;
        background-clip: unset !important;
    }

    .sb-divider {
        height: 1px;
        background: rgba(255, 255, 255, 0.06);
        margin: 16px 0;
    }

    .sb-label {
        font-size: 0.68rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        color: rgba(255, 255, 255, 0.35);
        margin-bottom: 10px;
        display: block;
    }

    .sb-conv-group {
        font-size: 0.72rem;
        font-weight: 500;
        color: rgba(255, 255, 255, 0.30);
        margin-bottom: 4px;
        margin-top: 8px;
    }
    .sb-conv-item {
        font-size: 0.85rem;
        color: rgba(255, 255, 255, 0.75);
        padding: 8px 12px;
        border-radius: 8px;
        cursor: default;
        transition: background 0.2s;
    }
    .sb-conv-item-active {
        background: rgba(255, 255, 255, 0.06);
        color: #ffffff;
    }

    .sb-memory-count {
        font-size: 0.82rem;
        color: rgba(255, 255, 255, 0.50);
        margin-bottom: 10px;
    }

    .sb-profile-name {
        font-size: 0.95rem;
        font-weight: 600;
        color: #ffffff;
        margin: 0;
    }
    .sb-profile-tone {
        font-size: 0.78rem;
        color: rgba(255, 255, 255, 0.45);
        margin: 2px 0 0 0;
    }

    [data-testid="stSidebar"] button[kind="primary"],
    [data-testid="stSidebar"] [data-testid="baseButton-primary"] {
        background: rgba(255, 255, 255, 0.06) !important;
        border: 1px solid rgba(255, 255, 255, 0.10) !important;
        border-radius: 8px !important;
        color: rgba(255, 255, 255, 0.75) !important;
        font-weight: 500 !important;
        font-size: 0.82rem !important;
        padding: 8px 14px !important;
        box-shadow: none !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stSidebar"] button[kind="primary"]:hover,
    [data-testid="stSidebar"] [data-testid="baseButton-primary"]:hover {
        background: rgba(255, 255, 255, 0.10) !important;
        border-color: rgba(255, 255, 255, 0.18) !important;
        transform: none !important;
        color: #ffffff !important;
    }

    [data-testid="stSidebar"] [data-testid="baseButton-secondary"] {
        background: transparent !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 8px !important;
        color: rgba(255, 255, 255, 0.55) !important;
        font-weight: 500 !important;
        font-size: 0.82rem !important;
        padding: 8px 14px !important;
        box-shadow: none !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stSidebar"] [data-testid="baseButton-secondary"]:hover {
        background: rgba(255, 255, 255, 0.04) !important;
        border-color: rgba(255, 255, 255, 0.12) !important;
        transform: none !important;
    }

    .sb-new-chat-btn button {
        background: rgba(99, 102, 241, 0.12) !important;
        border: 1px solid rgba(99, 102, 241, 0.25) !important;
        color: #818cf8 !important;
        font-weight: 600 !important;
    }
    .sb-new-chat-btn button:hover {
        background: rgba(99, 102, 241, 0.20) !important;
        border-color: rgba(99, 102, 241, 0.40) !important;
        color: #a5b4fc !important;
    }

    .sb-danger-btn button {
        border-color: rgba(239, 68, 68, 0.25) !important;
        color: rgba(239, 68, 68, 0.70) !important;
    }
    .sb-danger-btn button:hover {
        background: rgba(239, 68, 68, 0.08) !important;
        border-color: rgba(239, 68, 68, 0.40) !important;
        color: #ef4444 !important;
    }

    [data-testid="stSidebar"] [data-testid="stTextInput"] input {
        height: 40px !important;
        min-height: 40px !important;
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.10) !important;
        border-radius: 8px !important;
        padding: 0 12px !important;
        font-size: 0.85rem !important;
        line-height: 40px !important;
        box-shadow: none !important;
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] [data-testid="stTextInput"] input:focus {
        border-color: rgba(99, 102, 241, 0.40) !important;
        box-shadow: none !important;
    }

    [data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.10) !important;
        border-radius: 8px !important;
    }

    .sb-memory-item {
        font-size: 0.80rem;
        color: rgba(255, 255, 255, 0.65);
        padding: 8px 12px;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 6px;
        margin-bottom: 6px;
        border-left: 2px solid rgba(99, 102, 241, 0.30);
        line-height: 1.4;
        word-wrap: break-word;
    }
    .sb-memory-item-pinned {
        border-left-color: rgba(250, 204, 21, 0.60) !important;
        background: rgba(250, 204, 21, 0.04) !important;
    }
    .sb-memory-pin-badge {
        display: inline-block;
        font-size: 0.68rem;
        color: rgba(250, 204, 21, 0.80);
        margin-bottom: 2px;
    }

    [data-testid="stSidebar"] [data-testid="stExpander"] {
        background: transparent !important;
        border: none !important;
        border-radius: 0 !important;
    }
</style>
"""
