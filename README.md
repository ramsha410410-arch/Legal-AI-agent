# ⚖️ Legal AI Agent — Complete Beginner's Guide

**Built with:** Python · LangGraph · Ollama (Local LLM) · Vertex AI (Google Cloud) · Streamlit

---

## 🎓 What is this project?

This is a **Legal AI Assistant** that can:
- Answer legal questions (contracts, labor law, IP, criminal, family law)
- Summarize legal documents you upload
- Draft basic legal letters/templates
- Cite relevant laws and explain them in plain English
- Run **100% locally** (no data leaves your computer) using Ollama
- OR use **Google Vertex AI** for more powerful cloud responses

---

## 🧠 Key Concepts Explained (Zero Knowledge Assumed)

### What is an AI Agent?
An AI Agent is NOT just a chatbot. A chatbot only answers one question at a time.
An **Agent** can:
1. Think: "What do I need to do?"
2. Plan: "I'll break this into steps"
3. Use Tools: Search a database, read a file, call an API
4. Reflect: "Was that answer good enough?"
5. Iterate: Try again if needed

Think of it like hiring a lawyer vs. asking a friend:
- Friend (chatbot) = answers off the top of their head
- Lawyer (agent) = researches, checks references, drafts properly

### What is LangGraph?
LangGraph is a framework (a ready-made toolkit) for building AI agents.
It lets you define a **graph** (flowchart) of steps the AI takes.
Each "node" in the graph is a step (e.g., "analyze question", "search law database", "format answer").

### What is Ollama?
Ollama lets you run AI models **on your own computer** — no internet needed.
Your data NEVER leaves your machine. Perfect for confidential legal documents.
We use **Llama 3** or **Mistral** models through Ollama.

### What is Vertex AI?
Google's cloud AI platform. More powerful than local models.
Use this when you need better quality and don't mind data going to Google's secure servers.

### What is Streamlit?
A Python library that turns your Python code into a beautiful web app.
No HTML/CSS/JavaScript needed — pure Python!

---

## 📁 Project Structure

```
legal_ai_agent/
│
├── app.py                  ← Main entry point (run this!)
├── config.py               ← All settings in one place
├── requirements.txt        ← Python packages needed
├── .env.example            ← Template for your secret keys
│
├── agents/
│   ├── __init__.py
│   ├── legal_agent.py      ← The brain: LangGraph agent definition
│   └── prompts.py          ← All AI instructions/prompts
│
├── tools/
│   ├── __init__.py
│   ├── legal_search.py     ← Tool: Search legal knowledge base
│   ├── document_analyzer.py← Tool: Analyze uploaded PDFs
│   └── draft_generator.py  ← Tool: Generate legal document drafts
│
├── utils/
│   ├── __init__.py
│   ├── llm_router.py       ← Switches between Ollama and Vertex AI
│   ├── memory.py           ← Conversation memory/history
│   └── security.py         ← Data sanitization and security helpers
│
└── pages/
    ├── chat.py             ← Chat interface page
    ├── document_review.py  ← Document upload & analysis page
    └── settings.py         ← User settings page
```

---

## 🚀 Setup Instructions (Step by Step)

### Step 1: Install Python
Download Python 3.11+ from https://python.org

### Step 2: Install Ollama
Download from https://ollama.ai
Then run in terminal:
```bash
ollama pull llama3          # Downloads the Llama 3 model (~4GB)
ollama pull mistral         # Alternative smaller model (~4GB)
```

### Step 3: Clone/Download this project
```bash
cd Desktop
# If using git:
git clone <your-repo-url>
cd legal_ai_agent

# Or just download and extract the ZIP
```

### Step 4: Create a virtual environment
```bash
# This creates an isolated Python environment (best practice!)
python -m venv venv

# Activate it:
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### Step 5: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 6: Set up environment variables
```bash
cp .env.example .env
# Now edit .env with your actual values
```

### Step 7: Run the app!
```bash
streamlit run app.py
```
Open your browser to: http://localhost:8501

---

## 🔐 Security Notes for Legal Data
- All Ollama processing = LOCAL ONLY (zero data leaves your machine)
- Vertex AI = encrypted in transit + Google's enterprise security
- No conversation logs are stored permanently by default
- Uploaded documents are processed in memory, not saved to disk

---

## 📚 Learning Resources
- LangGraph docs: https://langchain-ai.github.io/langgraph/
- Ollama: https://ollama.ai
- Streamlit: https://docs.streamlit.io
- Vertex AI: https://cloud.google.com/vertex-ai/docs
