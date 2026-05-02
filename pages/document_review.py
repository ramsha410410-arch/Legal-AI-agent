# ============================================================
# pages/document_review.py — Document Upload & Analysis Page
# ============================================================
#
# This page lets users:
# 1. Upload a legal document (PDF, DOCX, TXT)
# 2. See document stats (pages, word count)
# 3. Get an automatic AI analysis
# 4. Ask specific questions about the document
# ============================================================

import streamlit as st

from tools.document_analyzer import (
    extract_document_text,
    get_document_stats
)
from agents.legal_agent import run_legal_agent
from utils.security import security_manager
from config import config


def render_document_review():
    """Render the document review page."""
    
    # Page header
    st.markdown("""
    <div class="app-header">
        <div class="app-title">📄 Document Review</div>
        <div class="app-subtitle">Upload legal documents for AI-powered analysis</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Two-column layout
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        render_upload_section()
    
    with col2:
        render_analysis_section()


def render_upload_section():
    """Left column: File upload and document preview."""
    
    st.markdown("### 📁 Upload Document")
    
    # File uploader
    # accept_multiple_files=False means only one file at a time
    uploaded_file = st.file_uploader(
        "Choose a legal document",
        type=["pdf", "docx", "txt"],
        help="Supported formats: PDF, Word (.docx), Plain Text (.txt). Max 50MB.",
        accept_multiple_files=False
    )
    
    if uploaded_file is not None:
        # Validate the file
        is_valid, error_msg = security_manager.validate_file_upload(uploaded_file)
        
        if not is_valid:
            st.error(f"❌ {error_msg}")
            return
        
        # Show file info
        file_size_mb = uploaded_file.size / (1024 * 1024)
        
        st.success(f"✅ File uploaded: **{uploaded_file.name}**")
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("File Size", f"{file_size_mb:.2f} MB")
        with col_b:
            st.metric("File Type", uploaded_file.name.split('.')[-1].upper())
        
        # Extract text button
        if st.button("🔍 Process Document", type="primary", use_container_width=True):
            with st.spinner("📖 Extracting text from document..."):
                text, error = extract_document_text(uploaded_file)
            
            if error:
                st.error(f"❌ Extraction error: {error}")
            elif not text:
                st.warning("⚠️ No text could be extracted from this document.")
            else:
                # Store in session state for use in chat
                st.session_state.document_text = text
                st.session_state.document_name = uploaded_file.name
                
                # Get stats
                stats = get_document_stats(text)
                
                st.success("✅ Document processed successfully!")
                
                # Show stats
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Words", f"{stats['word_count']:,}")
                with col2:
                    st.metric("Est. Pages", stats['estimated_pages'])
                with col3:
                    st.metric("Tokens ~", f"{stats['token_estimate']:,}")
                
                # Preview first 500 characters
                with st.expander("📝 Document Preview (first 500 characters)"):
                    st.text(text[:500] + "..." if len(text) > 500 else text)
        
        # If document already processed, show status
        elif st.session_state.get("document_name") == uploaded_file.name:
            st.info("✅ This document is already loaded and ready for analysis!")
    
    # Show currently loaded document
    if st.session_state.get("document_name") and (
        not uploaded_file or 
        st.session_state.document_name != (uploaded_file.name if uploaded_file else "")
    ):
        st.markdown("---")
        st.markdown("**Currently Loaded Document:**")
        st.markdown(f"📎 `{st.session_state.document_name}`")
        
        if st.button("🗑️ Remove Document", use_container_width=True):
            st.session_state.document_text = None
            st.session_state.document_name = None
            st.rerun()
    
    # Privacy notice
    st.markdown("""
    <div class="disclaimer-box">
        🔒 <strong>Privacy Notice:</strong> Documents are processed in memory only.
        They are NOT saved to disk or sent to external servers when using Ollama (local mode).
        When using Vertex AI, documents are sent to Google's encrypted servers.
    </div>
    """, unsafe_allow_html=True)


def render_analysis_section():
    """Right column: Analysis options and results."""
    
    st.markdown("### 🔬 Analysis")
    
    if not st.session_state.get("document_text"):
        st.markdown("""
        <div class="info-box">
            <div style="color: #94a3b8; text-align: center; padding: 2rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📄</div>
                <div>Upload and process a document to begin analysis</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Example analyses to show what's possible
        st.markdown("---")
        st.markdown("**What I can analyze:**")
        
        analysis_types = [
            ("🔍 Full Review", "Complete document analysis with key terms, parties, and red flags"),
            ("⚠️ Risk Assessment", "Identify potentially problematic clauses and unfair terms"),
            ("📋 Summary", "Plain-English summary of what the document says"),
            ("📅 Key Dates", "Extract all important dates and deadlines"),
            ("❓ Custom Question", "Ask any specific question about the document"),
        ]
        
        for name, desc in analysis_types:
            st.markdown(f"**{name}** — *{desc}*")
        
        return
    
    # Analysis options
    analysis_type = st.selectbox(
        "Choose analysis type:",
        options=[
            "Full Document Review",
            "Risk Assessment",
            "Plain English Summary",
            "Extract Key Dates & Deadlines",
            "Identify Parties & Their Obligations",
            "Custom Question"
        ],
        index=0
    )
    
    # Custom question input (only shown when Custom Question selected)
    custom_question = ""
    if analysis_type == "Custom Question":
        custom_question = st.text_area(
            "Your question about the document:",
            placeholder="e.g., 'Does this contract have a non-compete clause? What are its terms?'",
            height=80
        )
    
    # Run analysis button
    if st.button("🚀 Run Analysis", type="primary", use_container_width=True):
        
        # Build the query based on selection
        queries = {
            "Full Document Review": (
                "Please perform a comprehensive legal review of this document. "
                "Cover: document type, all parties, key terms and conditions, "
                "any red flags or concerning clauses, and overall assessment."
            ),
            "Risk Assessment": (
                "Perform a risk assessment of this document. "
                "Focus on: one-sided terms, missing standard protections, "
                "ambiguous language, unusual clauses, and potential disputes. "
                "Rate the overall risk level."
            ),
            "Plain English Summary": (
                "Summarize this document in plain English that a non-lawyer can understand. "
                "Focus on what it means practically for the parties involved."
            ),
            "Extract Key Dates & Deadlines": (
                "Extract ALL dates, deadlines, time limits, and time-sensitive provisions "
                "from this document. Present them in chronological order."
            ),
            "Identify Parties & Their Obligations": (
                "Identify all parties in this document and list their specific "
                "rights, obligations, and responsibilities."
            ),
            "Custom Question": custom_question or "Please analyze this document."
        }
        
        query = queries.get(analysis_type, "Please analyze this document.")
        
        if analysis_type == "Custom Question" and not custom_question.strip():
            st.warning("Please enter your question before running analysis.")
            return
        
        with st.spinner(f"🔬 Running {analysis_type}..."):
            result = run_legal_agent(
                user_input=query,
                document_text=st.session_state.document_text,
                llm_provider=st.session_state.get("llm_provider", "ollama")
            )
        
        st.markdown("---")
        st.markdown(f"### 📋 Analysis Results")
        st.markdown(f"*Analysis type: {analysis_type}*")
        st.markdown("---")
        
        if result.get("error"):
            st.error(f"Analysis error: {result['error']}")
        else:
            st.markdown(result["response"])
        
        # Option to copy to clipboard (opens in expandable text area)
        with st.expander("📋 Copy Results"):
            st.text_area(
                "Select all and copy:",
                value=result["response"],
                height=200,
                key="copy_results"
            )
        
        # Button to send to chat for follow-up questions
        if st.button("💬 Continue in Chat", use_container_width=True):
            # Add the analysis to chat history so user can follow up
            st.session_state.chat_history.append({
                "role": "user",
                "content": f"[Document Analysis: {analysis_type}] {query}"
            })
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": result["response"],
                "task_type": "document_analysis"
            })
            st.session_state.current_page = "chat"
            st.rerun()
