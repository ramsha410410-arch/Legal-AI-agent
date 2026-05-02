# ============================================================
# config.py — Central Configuration File
# ============================================================
#
# WHAT IS THIS FILE?
# Instead of having settings scattered everywhere in the code,
# we put ALL settings here. This is called the "Single Source
# of Truth" principle — a best practice in software engineering.
#
# Think of it like a control panel for the whole application.
# ============================================================

import os
from dotenv import load_dotenv  # Reads the .env file

# load_dotenv() reads the .env file and makes all those
# KEY=VALUE pairs available via os.getenv()
load_dotenv()


# ============================================================
# APP SETTINGS
# ============================================================
class AppConfig:
    """General application settings."""
    
    NAME: str = os.getenv("APP_NAME", "Legal AI Agent")
    VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    DEBUG: bool = os.getenv("DEBUG_MODE", "False").lower() == "true"
    
    # UI Settings
    PAGE_TITLE: str = "⚖️ Legal AI Agent"
    PAGE_ICON: str = "⚖️"
    LAYOUT: str = "wide"          # Streamlit layout: "centered" or "wide"
    
    # Legal practice areas this agent knows about
    LEGAL_DOMAINS: list = [
        "Contract Law",
        "Labor & Employment Law", 
        "Intellectual Property",
        "Criminal Law",
        "Family Law",
        "Corporate Law",
        "Real Estate Law",
        "Immigration Law",
        "Tax Law",
        "Privacy & Data Protection"
    ]


# ============================================================
# LLM (Language Model) SETTINGS
# ============================================================
class LLMConfig:
    """Settings for the AI language models."""
    
    # Which provider to use by default
    # "ollama" = runs on your computer (private, free)
    # "vertexai" = runs on Google's servers (powerful, costs $)
    DEFAULT_PROVIDER: str = os.getenv("DEFAULT_LLM_PROVIDER", "ollama")
    
    # --- Ollama (Local) Settings ---
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")
    
    # Temperature: Controls how "creative" vs "precise" the AI is
    # 0.0 = very deterministic (same answer every time, more factual)
    # 1.0 = very creative (different answers, more varied)
    # For legal work, we want LOW temperature (more precise/consistent)
    OLLAMA_TEMPERATURE: float = float(os.getenv("OLLAMA_TEMPERATURE", "0.1"))
    
    # --- Vertex AI (Google Cloud) Settings ---
    GOOGLE_PROJECT: str = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    GOOGLE_REGION: str = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")
    VERTEXAI_MODEL: str = os.getenv("VERTEXAI_MODEL", "gemini-1.5-pro")
    VERTEXAI_TEMPERATURE: float = 0.1
    
    # Context window: How much text the AI can "see" at once
    # Measured in "tokens" (~= 3/4 of a word each)
    MAX_TOKENS: int = 4096        # Max length of AI response
    CONTEXT_WINDOW: int = 8192    # Max total conversation size


# ============================================================
# DOCUMENT & FILE SETTINGS  
# ============================================================
class DocumentConfig:
    """Settings for document processing."""
    
    # Maximum file size users can upload (50 MB)
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))
    MAX_FILE_SIZE_BYTES: int = MAX_FILE_SIZE_MB * 1024 * 1024
    
    # Allowed file types
    ALLOWED_EXTENSIONS: list = [".pdf", ".docx", ".txt", ".doc"]
    
    # When processing large documents, we split them into "chunks"
    # This is because AI models can only read a limited amount at once
    CHUNK_SIZE: int = 1000        # Characters per chunk
    CHUNK_OVERLAP: int = 200      # Characters shared between chunks (for context)


# ============================================================
# VECTOR DATABASE SETTINGS
# ============================================================
class VectorDBConfig:
    """Settings for the semantic search database.
    
    WHAT IS A VECTOR DATABASE?
    Regular databases search by exact keyword matches.
    Vector databases search by MEANING.
    
    Example: "terminate employment" and "fire someone" mean the same thing.
    A regular database wouldn't connect these.
    A vector database WOULD find them as related!
    
    We use ChromaDB — it runs locally, no cloud needed.
    """
    
    CHROMA_PATH: str = os.getenv("CHROMA_DB_PATH", "./data/chroma_db")
    LEGAL_DOCS_PATH: str = os.getenv("LEGAL_DOCS_PATH", "./data/legal_knowledge")
    
    # The model that converts text to vectors (mathematical representations)
    # This runs locally too (downloads automatically)
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"  # Small, fast, good quality
    
    # How many similar documents to retrieve for each query
    TOP_K_RESULTS: int = 5


# ============================================================
# SECURITY SETTINGS
# ============================================================
class SecurityConfig:
    """Security-related settings.
    
    WHY DOES THIS MATTER FOR LEGAL AI?
    Legal documents contain highly sensitive information:
    - Client names and personal data
    - Business secrets
    - Criminal records
    - Medical information
    
    We must handle this responsibly.
    """
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-key-change-in-production")
    SESSION_TIMEOUT: int = int(os.getenv("SESSION_TIMEOUT_MINUTES", "60"))
    MAX_HISTORY: int = int(os.getenv("MAX_CONVERSATION_HISTORY", "20"))
    
    # Personal data patterns to detect and warn about
    # (We warn users when they paste sensitive data)
    SENSITIVE_PATTERNS: list = [
        r'\b\d{3}-\d{2}-\d{4}\b',          # US Social Security Numbers
        r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',  # Credit card numbers
        r'\b[A-Z]{2}\d{6,9}\b',             # Passport numbers
    ]


# ============================================================
# CONVENIENCE: Single object with all configs
# ============================================================
# Instead of importing AppConfig, LLMConfig etc. separately,
# you can just import `config` and access config.app, config.llm etc.

class Config:
    app = AppConfig()
    llm = LLMConfig()
    docs = DocumentConfig()
    vector_db = VectorDBConfig()
    security = SecurityConfig()

config = Config()
