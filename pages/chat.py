# ============================================================
# pages/chat.py — The Main Chat Interface
# ============================================================
#
# This is the primary user interface for chatting with the
# Legal AI Agent. It handles:
# - Displaying the conversation history
# - Accepting user input
# - Calling the agent
# - Showing responses with nice formatting
# ============================================================

import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

from agents.legal_agent import run_legal_agent
from utils.security import security_manager
from config import config


def render_chat():
    """Render the complete chat interface."""
    
    # Page header
    st.markdown("""
    <div class="app-header">
        <div class="app-title">⚖️ Legal AI Assistant</div>
        <div class="app-subtitle">Powered by LangGraph · Ask me anything about law</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Legal domains chips (quick filters)
    render_domain_chips()
    
    # Conversation area
    render_conversation_history()
    
    # Input area
    render_input_area()


def render_domain_chips():
    """Show clickable domain tags to start conversations quickly."""
    
    st.markdown("**Quick Start — Click a legal area:**")
    
    cols = st.columns(5)
    
    quick_topics = [
        ("📋 Contracts", "Explain the key elements of a valid contract"),
        ("👔 Employment", "What are my rights as an employee?"),
        ("💡 IP Rights", "What is intellectual property and how do I protect it?"),
        ("🏠 Real Estate", "What should I check before signing a lease?"),
        ("🔒 Privacy", "What are GDPR data protection requirements?"),
    ]
    
    for i, (label, prompt) in enumerate(quick_topics):
        with cols[i]:
            if st.button(label, use_container_width=True, key=f"quick_{i}"):
                # When clicked, send this as a message
                process_user_message(prompt)
                st.rerun()
    
    st.markdown("---")


def render_conversation_history():
    """Display all previous messages in the conversation."""
    
    chat_history = st.session_state.get("chat_history", [])
    
    if not chat_history:
        # Show welcome message when no conversation yet
        st.markdown("""
        <div class="info-box">
            <div style="color: #e2c88a; font-size: 1.1rem; margin-bottom: 0.5rem;">
                👋 Welcome to Legal AI Assistant
            </div>
            <div style="color: #94a3b8; font-size: 0.9rem;">
                I can help you with:<br>
                • <strong style="color: #cbd5e1;">Understanding legal concepts</strong> — contracts, rights, regulations<br>
                • <strong style="color: #cbd5e1;">Document analysis</strong> — upload a PDF and I'll review it<br>
                • <strong style="color: #cbd5e1;">Document drafting</strong> — ask me to create templates<br>
                • <strong style="color: #cbd5e1;">General legal questions</strong> — across 10+ practice areas<br><br>
                Try: "What makes a contract legally binding?" or click a topic above.
            </div>
        </div>
        <br>
        """, unsafe_allow_html=True)
        return
    
    # Display each message
    for message in chat_history:
        role = message["role"]
        content = message["content"]
        
        if role == "user":
            # User message — right-aligned feel with blue accent
            with st.chat_message("user", avatar="👤"):
                st.markdown(content)
        
        elif role == "assistant":
            # AI message — with scales of justice avatar
            with st.chat_message("assistant", avatar="⚖️"):
                st.markdown(content)
                
                # Show task type badge if available
                if "task_type" in message:
                    task_labels = {
                        "legal_question": "📚 Legal Q&A",
                        "document_analysis": "📄 Document Analysis",
                        "document_drafting": "✍️ Document Drafting",
                        "general_chat": "💬 General"
                    }
                    label = task_labels.get(message["task_type"], "")
                    if label:
                        st.caption(f"*{label}*")


def render_input_area():
    """Render the message input area at the bottom."""
    
    # Show if a document is loaded
    if st.session_state.get("document_name"):
        st.info(
            f"📎 Document loaded: **{st.session_state.document_name}** "
            f"— Ask me to analyze it!",
            icon="📄"
        )
    
    # Chat input using Streamlit's built-in chat_input
    # This automatically appears at the bottom of the page
    user_input = st.chat_input(
        placeholder="Ask a legal question... (e.g., 'What is the statute of limitations?')",
    )
    
    if user_input:
        # Security checks
        is_injection, matched = security_manager.check_prompt_injection(user_input)
        if is_injection:
            st.error(
                f"⚠️ Your message was flagged for a potential prompt injection attempt. "
                f"Please rephrase your question."
            )
            return
        
        # Warn about sensitive data (but don't block)
        has_pii, pii_types = security_manager.scan_for_sensitive_data(user_input)
        if has_pii:
            st.warning(
                f"⚠️ Your message may contain sensitive information "
                f"({', '.join(pii_types)}). "
                f"Consider removing personal details for privacy."
            )
        
        # Process the message
        process_user_message(user_input)
        st.rerun()  # Re-run to display the new messages


def process_user_message(user_input: str):
    """
    Process a user message through the agent and store the response.
    
    Args:
        user_input: The text the user sent
    """
    
    # Sanitize input
    clean_input = security_manager.sanitize_input(user_input)
    
    if not clean_input:
        return
    
    # Add user message to display history
    st.session_state.chat_history.append({
        "role": "user",
        "content": clean_input
    })
    
    # Build LangChain message history for context
    # (Convert our dict history to LangChain message objects)
    lc_history = []
    for msg in st.session_state.chat_history[:-1]:  # All but the last (just added)
        if msg["role"] == "user":
            lc_history.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            lc_history.append(AIMessage(content=msg["content"]))
    
    # Show a loading spinner while the AI thinks
    with st.spinner("⚖️ Analyzing your question..."):
        result = run_legal_agent(
            user_input=clean_input,
            conversation_history=lc_history,
            document_text=st.session_state.get("document_text"),
            llm_provider=st.session_state.get("llm_provider", "ollama")
        )
    
    # Add AI response to display history
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": result["response"],
        "task_type": result.get("task_type")
    })
    
    # Increment query counter
    st.session_state.total_queries = st.session_state.get("total_queries", 0) + 1
