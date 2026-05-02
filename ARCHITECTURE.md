# ============================================================
# ARCHITECTURE.md — Visual Project Architecture Guide
# ============================================================

# Legal AI Agent — Architecture Deep Dive

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    USER'S BROWSER                            │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │              STREAMLIT WEB APP (app.py)             │   │
│   │                                                     │   │
│   │  ┌─────────────┐ ┌──────────────┐ ┌─────────────┐  │   │
│   │  │  Chat Page  │ │  Doc Review  │ │  Settings   │  │   │
│   │  │ (chat.py)   │ │(doc_review)  │ │(settings.py)│  │   │
│   │  └──────┬──────┘ └──────┬───────┘ └─────────────┘  │   │
│   └─────────┼───────────────┼─────────────────────────--┘   │
└─────────────┼───────────────┼──────────────────────────-----┘
              │               │
              ▼               ▼
┌─────────────────────────────────────────────────────────────┐
│                  LANGGRAPH AGENT ENGINE                      │
│                  (agents/legal_agent.py)                     │
│                                                             │
│   Input → analyze_intent → route → handler → response      │
│                                                             │
│   ┌──────────────────────────────────────────────────────┐  │
│   │                  AGENT STATE                         │  │
│   │  {messages, user_input, task_type, document_text,   │  │
│   │   final_response, error, llm_provider}              │  │
│   └──────────────────────────────────────────────────────┘  │
└──────────────────────────────┬──────────────────────────────┘
                               │
              ┌────────────────┼───────────────────┐
              │                │                   │
              ▼                ▼                   ▼
┌─────────────────┐  ┌──────────────────┐  ┌─────────────────┐
│   LLM ROUTER    │  │  TOOLS           │  │  UTILITIES      │
│(llm_router.py)  │  │                  │  │                 │
│                 │  │ • doc_analyzer   │  │ • memory.py     │
│  ┌───────────┐  │  │ • legal_search   │  │ • security.py   │
│  │  Ollama   │  │  │ • draft_gen      │  │                 │
│  │ (Local)   │  │  └──────────────────┘  └─────────────────┘
│  └─────┬─────┘  │
│        OR       │
│  ┌─────▼─────┐  │
│  │ Vertex AI │  │
│  │ (Google)  │  │
│  └───────────┘  │
└─────────────────┘
```

## Data Flow (Step by Step)

```
1. USER TYPES: "Is my NDA enforceable?"
   └─→ Streamlit chat_input captures it
   
2. SECURITY CHECK (utils/security.py)
   └─→ Scan for PII, prompt injection
   └─→ Sanitize input
   
3. AGENT INVOKED (agents/legal_agent.py)
   └─→ Initial state created with user_input
   
4. INTENT ANALYSIS (analyze_intent_node)
   └─→ "nda", "enforceable" → task_type = "legal_question"
   
5. ROUTING (route_task)
   └─→ "legal_question" → handle_legal_question_node
   
6. LLM CALL (via llm_router.py)
   └─→ Provider = "ollama"
   └─→ Get ChatOllama instance
   └─→ Build messages:
       [SystemMessage(LEGAL_AGENT_SYSTEM_PROMPT),
        HumanMessage("previous question"),
        AIMessage("previous answer"),
        HumanMessage("Is my NDA enforceable?")]
   └─→ llm.invoke(messages) → AIMessage(response)
   
7. RESPONSE RETURNED
   └─→ final_response = "An NDA is enforceable when..."
   └─→ Stored in session_state.chat_history
   
8. UI UPDATES
   └─→ Streamlit re-runs (triggered by state change)
   └─→ Chat history displayed with new message
```

## LangGraph State Machine

```
        ┌──────────────┐
        │  Entry Point │
        └──────┬───────┘
               │
    ┌──────────▼──────────┐
    │   analyze_intent    │ ← Node 1
    │  (classify query)   │
    └──────────┬──────────┘
               │ Conditional Edge
               │ (route_task function decides)
    ┌──────────▼──────────────────────────────────────┐
    │         ROUTING DECISION                         │
    │  "legal_question"  → handle_legal_question       │
    │  "document_analysis" → handle_document_analysis  │
    │  "document_drafting" → handle_document_drafting  │
    │  "general_chat"    → handle_general_chat         │
    └──────────┬──────────────────────────────────────┘
               │
    ┌──────────▼──────────┐
    │   Handler Node      │ ← Node 2 (one of 4)
    │  (call LLM, format) │
    └──────────┬──────────┘
               │ Edge to END
    ┌──────────▼──────────┐
    │        END          │
    └─────────────────────┘
```

## File Dependency Map

```
app.py
  ├── config.py
  ├── pages/chat.py
  │     ├── agents/legal_agent.py
  │     │     ├── agents/prompts.py
  │     │     └── utils/llm_router.py
  │     │           ├── langchain_ollama
  │     │           └── langchain_google_vertexai
  │     └── utils/security.py
  ├── pages/document_review.py
  │     ├── tools/document_analyzer.py
  │     │     ├── PyPDF2
  │     │     └── python-docx
  │     └── agents/legal_agent.py
  └── pages/settings.py
        └── utils/llm_router.py
```

## Key Design Patterns Used

### 1. Strategy Pattern (LLM Router)
```python
# The router abstracts WHICH AI is used
# Code calling get_llm() doesn't need to know if it's Ollama or Vertex AI
llm = get_llm("ollama")   # Returns ChatOllama
llm = get_llm("vertexai") # Returns ChatVertexAI
response = llm.invoke(messages)  # Same interface!
```

### 2. State Machine Pattern (LangGraph)
```python
# Data flows through nodes as "state"
# Each node reads state, does work, returns updates
def my_node(state: AgentState) -> dict:
    # Read from state
    user_input = state["user_input"]
    # Do work
    result = process(user_input)
    # Return updates (merged into state)
    return {"final_response": result}
```

### 3. Repository Pattern (Knowledge Base)
```python
# LegalKnowledgeBase abstracts storage details
kb = LegalKnowledgeBase()
results = kb.search("contract breach")  # Don't need to know HOW it searches
```

### 4. Singleton Pattern (Security Manager)
```python
# Only one instance needed — created once, reused everywhere
security_manager = SecurityManager()  # Created at module load
# Then imported and used anywhere:
from utils.security import security_manager
```
