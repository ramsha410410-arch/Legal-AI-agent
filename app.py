# ============================================================
# app.py — Main Streamlit Application Entry Point
# ============================================================
#
# HOW TO RUN THIS:
#   streamlit run app.py
#
# WHAT IS STREAMLIT?
# Streamlit is a Python library that magically turns Python scripts
# into interactive web applications.
#
# You write Python → Streamlit creates HTML/CSS/JS for you.
# No web development experience needed!
#
# HOW STREAMLIT WORKS:
# Every time a user interacts with the app (clicks a button,
# sends a message), Streamlit re-runs your entire script
# from top to bottom. This is unusual but makes state management
# simple once you understand it.
#
# st.session_state = where you store data that persists
# between these re-runs.
# ============================================================

import streamlit as st
from config import config

# ============================================================
# PAGE CONFIGURATION
# Must be the FIRST Streamlit command in your app!
# ============================================================
st.set_page_config(
    page_title=config.app.PAGE_TITLE,
    page_icon=config.app.PAGE_ICON,
    layout=config.app.LAYOUT,           # "wide" = full-width layout
    initial_sidebar_state="expanded",    # Sidebar open by default
)

# ============================================================
# CUSTOM CSS — Makes the app look professional
# ============================================================
st.markdown("""
<style>
    /* Import Google Font for a professional legal look */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600&family=Inter:wght@300;400;500&display=swap');
    
    /* Main app background */
    .main {
        background-color: #0f1117;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #1a1d23;
    }
    
    /* Header styling */
    .app-header {
        background: linear-gradient(135deg, #1a1d2e 0%, #16213e 50%, #0f3460 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        border: 1px solid #2d3748;
    }
    
    .app-title {
        font-family: 'Playfair Display', serif;
        font-size: 2.2rem;
        color: #e2c88a;
        margin: 0;
        letter-spacing: 1px;
    }
    
    .app-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        color: #8896a5;
        margin-top: 0.4rem;
        font-weight: 300;
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    
    /* Chat message styling */
    .user-message {
        background: linear-gradient(135deg, #1e3a5f, #1a3352);
        border-left: 3px solid #4a9eff;
        padding: 1rem 1.2rem;
        border-radius: 0 10px 10px 10px;
        margin: 0.5rem 0;
        font-family: 'Inter', sans-serif;
        color: #e2e8f0;
    }
    
    .ai-message {
        background: linear-gradient(135deg, #1a2535, #1e2d42);
        border-left: 3px solid #e2c88a;
        padding: 1rem 1.2rem;
        border-radius: 0 10px 10px 10px;
        margin: 0.5rem 0;
        font-family: 'Inter', sans-serif;
        color: #e2e8f0;
    }
    
    /* Status badge */
    .status-badge {
        display: inline-block;
        padding: 0.2rem 0.7rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 500;
        font-family: 'Inter', sans-serif;
    }
    
    .status-online { background: #1a3a2a; color: #4ade80; border: 1px solid #16a34a; }
    .status-offline { background: #3a1a1a; color: #f87171; border: 1px solid #dc2626; }
    
    /* Info box */
    .info-box {
        background: linear-gradient(135deg, #1a2535, #1e2d42);
        border: 1px solid #2d4a6e;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    /* Disclaimer box */
    .disclaimer-box {
        background: #2d1f0a;
        border: 1px solid #854d0e;
        border-radius: 8px;
        padding: 0.8rem 1rem;
        color: #fbbf24;
        font-size: 0.85rem;
        margin: 1rem 0;
    }
    
    /* Feature card */
    .feature-card {
        background: linear-gradient(135deg, #1a1d2e, #16213e);
        border: 1px solid #2d3748;
        border-radius: 10px;
        padding: 1.2rem;
        margin: 0.4rem 0;
        transition: border-color 0.2s;
    }
    
    .feature-card:hover { border-color: #e2c88a; }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Stacked columns gap */
    .block-container { padding-top: 1rem !important; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# INITIALIZE SESSION STATE
# ============================================================
# session_state persists between Streamlit re-runs.
# We initialize defaults here if they don't exist yet.

def initialize_session_state():
    """Set up default values for the session."""
    
    defaults = {
        "current_page": "chat",              # Which page is active
        "llm_provider": config.llm.DEFAULT_PROVIDER,  # AI provider
        "chat_history": [],                  # List of messages for display
        "conversation_messages": [],         # LangChain message objects
        "document_text": None,               # Uploaded document content
        "document_name": None,               # Uploaded document filename
        "total_queries": 0,                  # Counter for session stats
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


initialize_session_state()


# ============================================================
# SIDEBAR — Navigation and Settings
# ============================================================

def render_sidebar():
    """Render the left sidebar with navigation and settings."""
    
    with st.sidebar:
        # Logo / Title
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <div style="font-size: 2.5rem;">⚖️</div>
            <div style="font-family: 'Playfair Display', serif; 
                        color: #e2c88a; font-size: 1.1rem; 
                        letter-spacing: 1px;">
                Legal AI Agent
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Navigation
        st.markdown("**Navigation**")
        
        pages = {
            "💬 Legal Chat": "chat",
            "📄 Document Review": "document",
            "⚙️ Settings": "settings",
        }
        
        for label, page_id in pages.items():
            # Highlight current page
            is_current = st.session_state.current_page == page_id
            button_type = "primary" if is_current else "secondary"
            
            if st.button(label, use_container_width=True, type=button_type):
                st.session_state.current_page = page_id
                st.rerun()  # Re-run the app to show new page
        
        st.divider()
        
        # AI Provider Selector
        st.markdown("**AI Provider**")
        
        provider = st.radio(
            "Choose your AI model:",
            options=["ollama", "vertexai"],
            format_func=lambda x: "🔒 Ollama (Local)" if x == "ollama" else "☁️ Vertex AI (Google)",
            index=0 if st.session_state.llm_provider == "ollama" else 1,
            help="Ollama = runs on your computer (private). Vertex AI = Google Cloud (powerful)."
        )
        
        st.session_state.llm_provider = provider
        
        # Show provider status
        if provider == "ollama":
            from utils.llm_router import check_ollama_status
            status = check_ollama_status()
            
            if status['running']:
                st.markdown(
                    f'<span class="status-badge status-online">● Ollama Running</span>',
                    unsafe_allow_html=True
                )
                if status['models']:
                    st.caption(f"Models: {', '.join(status['models'][:3])}")
            else:
                st.markdown(
                    f'<span class="status-badge status-offline">● Ollama Offline</span>',
                    unsafe_allow_html=True
                )
                st.caption("Run: `ollama serve` in terminal")
        else:
            gcp_project = config.llm.GOOGLE_PROJECT
            if gcp_project:
                st.markdown(
                    '<span class="status-badge status-online">● Vertex AI Configured</span>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    '<span class="status-badge status-offline">● Not Configured</span>',
                    unsafe_allow_html=True
                )
                st.caption("Set GOOGLE_CLOUD_PROJECT in .env")
        
        st.divider()
        
        # Session stats
        st.markdown("**Session Stats**")
        st.caption(f"🔢 Queries: {st.session_state.total_queries}")
        if st.session_state.document_name:
            st.caption(f"📎 Doc: {st.session_state.document_name[:25]}...")
        
        # Clear conversation button
        if st.button("🗑️ Clear Conversation", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.conversation_messages = []
            st.session_state.document_text = None
            st.session_state.document_name = None
            st.rerun()
        
        st.divider()
        
        # Disclaimer in sidebar
        st.markdown("""
        <div style="font-size: 0.72rem; color: #6b7280; line-height: 1.4;">
        ⚠️ This AI provides general legal information, not legal advice.
        Always consult a licensed attorney for your specific situation.
        </div>
        """, unsafe_allow_html=True)


# ============================================================
# RENDER PAGES
# ============================================================

def render_chat_page():
    """Render the main chat interface."""
    from pages.chat import render_chat
    render_chat()

def render_document_page():
    """Render the document analysis page."""
    from pages.document_review import render_document_review
    render_document_review()

def render_settings_page():
    """Render the settings page."""
    from pages.settings import render_settings
    render_settings()


# ============================================================
# MAIN — Puts it all together
# ============================================================

def main():
    """
    Main function — the entry point for the app.
    
    1. Renders the sidebar
    2. Shows the appropriate page based on navigation
    """
    
    # Always render sidebar (it's on every page)
    render_sidebar()
    
    # Render the correct page based on what user selected
    page_map = {
        "chat": render_chat_page,
        "document": render_document_page,
        "settings": render_settings_page,
    }
    
    current_page = st.session_state.get("current_page", "chat")
    render_func = page_map.get(current_page, render_chat_page)
    render_func()


# ============================================================
# Python entry point
# "if __name__ == '__main__'" means:
# "Only run this code if this file is run directly"
# (not when imported by another file)
# ============================================================
if __name__ == "__main__":
    main()
