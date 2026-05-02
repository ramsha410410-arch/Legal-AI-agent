# ============================================================
# pages/settings.py — Application Settings Page
# ============================================================

import streamlit as st
from utils.llm_router import check_ollama_status
from config import config


def render_settings():
    """Render the settings page."""
    
    st.markdown("""
    <div class="app-header">
        <div class="app-title">⚙️ Settings</div>
        <div class="app-subtitle">Configure your Legal AI Agent</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs for different setting categories
    tab1, tab2, tab3, tab4 = st.tabs([
        "🤖 AI Models", 
        "🔒 Security", 
        "📊 System Status",
        "📖 About & Help"
    ])
    
    with tab1:
        render_model_settings()
    
    with tab2:
        render_security_settings()
    
    with tab3:
        render_system_status()
    
    with tab4:
        render_about()


def render_model_settings():
    """AI model configuration settings."""
    
    st.markdown("### 🤖 AI Model Settings")
    
    st.info(
        "These settings control which AI model processes your legal questions. "
        "Ollama runs locally (private), Vertex AI uses Google's cloud (more powerful)."
    )
    
    # Ollama settings
    st.markdown("#### 🔒 Ollama (Local) Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        ollama_model = st.text_input(
            "Ollama Model Name",
            value=config.llm.OLLAMA_MODEL,
            help="Model to use. Options: llama3, mistral, mixtral, codellama"
        )
        st.caption("Download a model: `ollama pull llama3`")
    
    with col2:
        ollama_temp = st.slider(
            "Temperature (Creativity)",
            min_value=0.0,
            max_value=1.0,
            value=config.llm.OLLAMA_TEMPERATURE,
            step=0.05,
            help="0 = very precise/deterministic. 1 = creative/varied. For legal work, keep low (0.0-0.2)."
        )
        st.caption(f"Current: {ollama_temp:.2f} — {'Precise' if ollama_temp < 0.3 else 'Balanced' if ollama_temp < 0.7 else 'Creative'}")
    
    st.markdown("---")
    
    # Vertex AI settings
    st.markdown("#### ☁️ Vertex AI (Google Cloud) Settings")
    
    gcp_project = st.text_input(
        "Google Cloud Project ID",
        value=config.llm.GOOGLE_PROJECT or "",
        type="default",
        help="Your GCP project ID. Find it at console.cloud.google.com",
        placeholder="my-project-id"
    )
    
    col3, col4 = st.columns(2)
    with col3:
        gcp_region = st.selectbox(
            "GCP Region",
            options=["us-central1", "us-east1", "europe-west1", "asia-southeast1"],
            index=0
        )
    
    with col4:
        vertex_model = st.selectbox(
            "Vertex AI Model",
            options=["gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.0-pro"],
            index=0,
            help="gemini-1.5-pro = most capable. gemini-1.5-flash = faster/cheaper."
        )
    
    st.markdown("""
    **To set up Vertex AI:**
    1. Create a Google Cloud account at cloud.google.com
    2. Create a new project
    3. Enable the Vertex AI API
    4. Create a Service Account with Vertex AI permissions
    5. Download the JSON key file
    6. Set `GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json` in your .env file
    """)


def render_security_settings():
    """Security and privacy settings."""
    
    st.markdown("### 🔒 Security & Privacy Settings")
    
    st.success("✅ Using Ollama means your data never leaves your machine.")
    
    # Data handling info
    st.markdown("#### Data Handling Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🔒 Ollama (Local) Mode:**
        - ✅ All processing on YOUR computer
        - ✅ No internet connection needed
        - ✅ Zero data sent externally
        - ✅ Conversation history in memory only
        - ✅ Documents processed in RAM, not saved
        """)
    
    with col2:
        st.markdown("""
        **☁️ Vertex AI (Cloud) Mode:**
        - ⚠️ Queries sent to Google's servers
        - ✅ Encrypted in transit (HTTPS)
        - ✅ Google's enterprise security
        - ✅ Google doesn't train on your data (enterprise terms)
        - ✅ Compliant with GDPR, HIPAA (with BAA)
        """)
    
    st.markdown("---")
    
    # PII Detection
    st.markdown("#### PII Detection Settings")
    st.markdown(
        "The app automatically scans for Personal Identifiable Information (PII) "
        "and warns you before it's sent to the AI."
    )
    
    pii_warning = st.toggle(
        "Enable PII Detection Warnings",
        value=True,
        help="Shows a warning when your message contains SSNs, credit cards, etc."
    )
    
    st.session_state["pii_warning_enabled"] = pii_warning
    
    # Session settings
    st.markdown("#### Session Settings")
    
    max_history = st.number_input(
        "Maximum Conversation History",
        min_value=5,
        max_value=100,
        value=config.security.MAX_HISTORY,
        step=5,
        help="Older messages are dropped when this limit is reached."
    )


def render_system_status():
    """System status and diagnostics."""
    
    st.markdown("### 📊 System Status")
    
    # Ollama Status
    st.markdown("#### Ollama Status")
    
    with st.spinner("Checking Ollama..."):
        status = check_ollama_status()
    
    if status['running']:
        st.success(f"✅ Ollama is running at {config.llm.OLLAMA_BASE_URL}")
        
        if status['models']:
            st.markdown("**Available Models:**")
            for model in status['models']:
                current = "← Currently selected" if model.startswith(config.llm.OLLAMA_MODEL) else ""
                st.markdown(f"- `{model}` {current}")
        else:
            st.warning(
                "Ollama is running but no models are downloaded. "
                "Run: `ollama pull llama3`"
            )
    else:
        st.error(f"❌ Ollama is not running: {status['error']}")
        
        st.markdown("""
        **To start Ollama:**
        1. Download Ollama from https://ollama.ai
        2. Open a terminal
        3. Run: `ollama serve`
        4. In a new terminal: `ollama pull llama3`
        5. Refresh this page
        """)
    
    # Python packages status
    st.markdown("---")
    st.markdown("#### Package Status")
    
    packages = [
        ("langgraph", "LangGraph"),
        ("langchain", "LangChain"),
        ("streamlit", "Streamlit"),
        ("PyPDF2", "PDF Processing"),
        ("docx", "Word Documents"),
        ("chromadb", "Vector Database"),
    ]
    
    cols = st.columns(3)
    for i, (pkg_name, display_name) in enumerate(packages):
        with cols[i % 3]:
            try:
                __import__(pkg_name)
                st.markdown(f"✅ {display_name}")
            except ImportError:
                st.markdown(f"❌ {display_name}")
    
    # Session stats
    st.markdown("---")
    st.markdown("#### Session Statistics")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Queries", st.session_state.get("total_queries", 0))
    with col2:
        chat_history = st.session_state.get("chat_history", [])
        st.metric("Messages", len(chat_history))
    with col3:
        doc = st.session_state.get("document_text", "")
        doc_words = len(doc.split()) if doc else 0
        st.metric("Document Words", f"{doc_words:,}")


def render_about():
    """About page and learning resources."""
    
    st.markdown("### 📖 About This Project")
    
    st.markdown("""
    This **Legal AI Agent** is a teaching project demonstrating how to build 
    a production-quality AI application using modern Python tools.
    
    ---
    
    #### 🏗️ Architecture Overview
    
    ```
    User Input
        ↓
    Streamlit UI  (app.py, pages/)
        ↓
    LangGraph Agent  (agents/legal_agent.py)
        ↓
    LLM Router  (utils/llm_router.py)
        ↓
    ┌─────────────┐     ┌──────────────┐
    │ Ollama      │     │ Vertex AI    │
    │ (Local)     │ OR  │ (Google)     │
    └─────────────┘     └──────────────┘
    ```
    
    #### 🧰 Technologies Used
    
    | Technology | Purpose | Why We Chose It |
    |-----------|---------|-----------------|
    | **LangGraph** | Agent workflow | Visual, debuggable, production-ready |
    | **Ollama** | Local LLM | Privacy, no cost, no internet needed |
    | **Vertex AI** | Cloud LLM | Power, Gemini models, enterprise compliance |
    | **Streamlit** | Web UI | Rapid Python-native development |
    | **ChromaDB** | Vector search | Local semantic search, no cloud needed |
    | **PyPDF2** | PDF parsing | Extract text from legal PDFs |
    
    ---
    
    #### 📚 Key Concepts to Learn
    
    1. **AI Agents vs Chatbots** — Agents plan, use tools, and iterate
    2. **LangGraph State Machine** — Directed graphs for AI workflows  
    3. **Prompt Engineering** — Writing effective AI instructions
    4. **Vector Embeddings** — How semantic search works
    5. **LLM Routing** — Switching between AI providers
    6. **Streamlit Session State** — Persisting data in web apps
    
    ---
    
    #### 🔗 Resources
    - [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
    - [Ollama Models Library](https://ollama.ai/library)
    - [Vertex AI Quickstart](https://cloud.google.com/vertex-ai/docs/start/introduction-unified-platform)
    - [Streamlit Documentation](https://docs.streamlit.io)
    - [Prompt Engineering Guide](https://www.promptingguide.ai)
    """)
