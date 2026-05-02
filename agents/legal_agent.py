# ============================================================
# agents/legal_agent.py — The LangGraph Legal AI Agent
# ============================================================
#
# THIS IS THE MOST IMPORTANT FILE IN THE PROJECT.
# It defines HOW the AI agent thinks and acts.
#
# WHAT IS LANGGRAPH?
# LangGraph lets you build AI agents as a "graph" (flowchart).
# 
# NODES = steps the AI can take (like functions)
# EDGES = connections between steps (like arrows in a flowchart)
# STATE = the data that flows through the graph
#
# OUR AGENT FLOW:
#
#  User Message
#       ↓
#  [analyze_intent]     ← "What is the user asking for?"
#       ↓
#  [route_to_tool]      ← "Which tool should I use?"
#       ↓               
#  ┌─────────────────────────────────┐
#  │  [search_legal_knowledge]       │ ← For general legal Q&A
#  │  [analyze_document]             │ ← For document review
#  │  [draft_document]               │ ← For creating documents
#  │  [answer_directly]              │ ← For simple questions
#  └─────────────────────────────────┘
#       ↓
#  [generate_final_response]  ← Formats the final answer
#       ↓
#  Response to User
#
# ============================================================

from typing import TypedDict, Annotated, List, Optional, Literal
import operator

from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

from agents.prompts import (
    LEGAL_AGENT_SYSTEM_PROMPT,
    LEGAL_QUESTION_PROMPT,
    DOCUMENT_ANALYSIS_PROMPT,
    DOCUMENT_DRAFTING_PROMPT,
)
from utils.llm_router import get_llm
from config import config


# ============================================================
# STEP 1: DEFINE THE STATE
# ============================================================
# The State is like a "notepad" that gets passed between all
# steps of the agent. Each step can read from it and add to it.
#
# TypedDict = a dictionary where we define what keys it has
# and what type each value should be.

class AgentState(TypedDict):
    """
    The complete state of the agent at any point in the workflow.
    
    Think of this as the agent's "working memory" for one conversation turn.
    """
    
    # The conversation history (all previous messages)
    # Annotated[..., operator.add] means: when we update messages,
    # ADD to the list rather than replace it
    messages: Annotated[List[BaseMessage], operator.add]
    
    # The current user question
    user_input: str
    
    # What type of task this is (determined by the routing step)
    # Literal means only these specific string values are allowed
    task_type: Optional[Literal[
        "legal_question",    # General legal Q&A
        "document_analysis", # Analyze an uploaded document
        "document_drafting", # Create a new document
        "general_chat"       # Casual/non-legal conversation
    ]]
    
    # The document text if user uploaded a file
    document_text: Optional[str]
    
    # The final formatted response to show the user
    final_response: Optional[str]
    
    # Any errors that occurred
    error: Optional[str]
    
    # The LLM provider being used ("ollama" or "vertexai")
    llm_provider: str


# ============================================================
# STEP 2: DEFINE THE NODES (Steps in the workflow)
# ============================================================
# Each node is a Python function that:
# - Takes the current state as input
# - Does some work
# - Returns updated state values (as a dict)

def analyze_intent_node(state: AgentState) -> dict:
    """
    Node 1: Analyze what the user wants to do.
    
    This is like the receptionist at a law firm who figures out
    "Does this person need a consultation, document review, or drafting?"
    
    Returns: Updated task_type in state
    """
    
    user_input = state["user_input"].lower()
    document_text = state.get("document_text")
    
    # Simple intent classification
    # (In production, you'd use the LLM for more sophisticated classification)
    
    # If there's a document attached, it's document analysis
    if document_text and len(document_text) > 100:
        task_type = "document_analysis"
    
    # Keywords that suggest document drafting
    elif any(keyword in user_input for keyword in [
        "draft", "write", "create", "template", "generate", 
        "contract", "agreement", "letter", "nda", "clause"
    ]):
        task_type = "document_drafting"
    
    # Keywords that suggest general legal questions
    elif any(keyword in user_input for keyword in [
        "law", "legal", "rights", "sue", "court", "liable", "statute",
        "regulation", "attorney", "lawyer", "judge", "verdict", "plaintiff",
        "defendant", "charges", "criminal", "civil", "appeal", "settlement"
    ]):
        task_type = "legal_question"
    
    # Default: treat as general chat
    else:
        task_type = "general_chat"
    
    print(f"🔍 Intent detected: {task_type}")  # For debugging
    
    return {"task_type": task_type}


def handle_legal_question_node(state: AgentState) -> dict:
    """
    Node 2a: Handle a general legal question.
    
    Uses the LLM to answer the question with legal context.
    """
    
    try:
        llm = get_llm(state["llm_provider"])
        
        # Build the conversation messages
        messages = [
            SystemMessage(content=LEGAL_AGENT_SYSTEM_PROMPT),  # AI's identity
            *state["messages"],                                  # History
            HumanMessage(content=state["user_input"])            # Current question
        ]
        
        # Call the AI!
        # .invoke() sends the messages and waits for a response
        response = llm.invoke(messages)
        
        return {
            "final_response": response.content,
            "messages": [AIMessage(content=response.content)]
        }
        
    except Exception as e:
        error_msg = f"Error generating response: {str(e)}"
        return {
            "final_response": f"I encountered an error: {error_msg}. Please check that your AI provider is running.",
            "error": error_msg
        }


def handle_document_analysis_node(state: AgentState) -> dict:
    """
    Node 2b: Analyze an uploaded legal document.
    
    Takes the document text and produces a structured analysis.
    """
    
    document_text = state.get("document_text", "")
    
    if not document_text:
        return {
            "final_response": "No document content found. Please upload a document first.",
            "error": "No document text"
        }
    
    try:
        llm = get_llm(state["llm_provider"])
        
        # Format the analysis prompt with the actual document
        # .format() replaces {document_text} with the actual text
        analysis_prompt = DOCUMENT_ANALYSIS_PROMPT.format(
            document_text=document_text[:8000]  # Limit to 8000 chars to avoid token limits
        )
        
        # Add user's specific question about the document (if any)
        user_question = state["user_input"]
        if user_question and user_question.strip():
            analysis_prompt += f"\n\nUser's specific question: {user_question}"
        
        messages = [
            SystemMessage(content=LEGAL_AGENT_SYSTEM_PROMPT),
            HumanMessage(content=analysis_prompt)
        ]
        
        response = llm.invoke(messages)
        
        return {
            "final_response": response.content,
            "messages": [AIMessage(content=response.content)]
        }
        
    except Exception as e:
        return {
            "final_response": f"Error analyzing document: {str(e)}",
            "error": str(e)
        }


def handle_document_drafting_node(state: AgentState) -> dict:
    """
    Node 2c: Generate a draft legal document.
    
    Creates templates for contracts, letters, NDAs, etc.
    """
    
    try:
        llm = get_llm(state["llm_provider"])
        
        # Parse what type of document and requirements from user input
        user_input = state["user_input"]
        
        # Build the drafting prompt
        drafting_prompt = DOCUMENT_DRAFTING_PROMPT.format(
            document_type="legal document",  # Could be made smarter
            requirements=user_input
        )
        
        messages = [
            SystemMessage(content=LEGAL_AGENT_SYSTEM_PROMPT),
            *state["messages"],
            HumanMessage(content=drafting_prompt)
        ]
        
        response = llm.invoke(messages)
        
        return {
            "final_response": response.content,
            "messages": [AIMessage(content=response.content)]
        }
        
    except Exception as e:
        return {
            "final_response": f"Error drafting document: {str(e)}",
            "error": str(e)
        }


def handle_general_chat_node(state: AgentState) -> dict:
    """
    Node 2d: Handle general (non-legal) conversation.
    
    For greetings, clarification questions, etc.
    """
    
    try:
        llm = get_llm(state["llm_provider"])
        
        # Simpler system prompt for general chat
        general_system = (
            "You are a helpful Legal AI Assistant. "
            "You specialize in legal matters but can also have normal conversations. "
            "If someone asks a non-legal question, be friendly and helpful. "
            "Always be ready to help with legal questions when they arise."
        )
        
        messages = [
            SystemMessage(content=general_system),
            *state["messages"],
            HumanMessage(content=state["user_input"])
        ]
        
        response = llm.invoke(messages)
        
        return {
            "final_response": response.content,
            "messages": [AIMessage(content=response.content)]
        }
        
    except Exception as e:
        return {
            "final_response": f"Error: {str(e)}",
            "error": str(e)
        }


# ============================================================
# STEP 3: DEFINE THE ROUTING LOGIC
# ============================================================
# This function decides WHICH node to go to next.
# It looks at the state and returns the name of the next node.

def route_task(state: AgentState) -> str:
    """
    Router: Decides which handler to use based on task type.
    
    This is called after analyze_intent_node runs.
    Returns the name of the next node to execute.
    """
    task_type = state.get("task_type", "general_chat")
    
    routing_map = {
        "legal_question": "handle_legal_question",
        "document_analysis": "handle_document_analysis",
        "document_drafting": "handle_document_drafting",
        "general_chat": "handle_general_chat"
    }
    
    return routing_map.get(task_type, "handle_general_chat")


# ============================================================
# STEP 4: BUILD THE GRAPH
# ============================================================
# Now we connect all the nodes together into a workflow.

def build_legal_agent() -> StateGraph:
    """
    Build and return the compiled LangGraph agent.
    
    This creates the complete workflow graph and compiles it
    into a runnable agent.
    
    Returns:
        Compiled LangGraph app (can be invoked with .invoke())
    """
    
    # Create a new graph with our state definition
    workflow = StateGraph(AgentState)
    
    # ADD NODES (each node is a step)
    # .add_node(name, function) — name is used to reference this step
    workflow.add_node("analyze_intent", analyze_intent_node)
    workflow.add_node("handle_legal_question", handle_legal_question_node)
    workflow.add_node("handle_document_analysis", handle_document_analysis_node)
    workflow.add_node("handle_document_drafting", handle_document_drafting_node)
    workflow.add_node("handle_general_chat", handle_general_chat_node)
    
    # SET ENTRY POINT (where the graph starts)
    workflow.set_entry_point("analyze_intent")
    
    # ADD CONDITIONAL EDGES (the routing)
    # After "analyze_intent" runs, call route_task() to decide next step
    workflow.add_conditional_edges(
        "analyze_intent",          # From this node
        route_task,                # Call this function to decide
        {                          # Map return values to node names
            "handle_legal_question": "handle_legal_question",
            "handle_document_analysis": "handle_document_analysis",
            "handle_document_drafting": "handle_document_drafting",
            "handle_general_chat": "handle_general_chat"
        }
    )
    
    # ADD TERMINAL EDGES (these nodes end the workflow)
    workflow.add_edge("handle_legal_question", END)
    workflow.add_edge("handle_document_analysis", END)
    workflow.add_edge("handle_document_drafting", END)
    workflow.add_edge("handle_general_chat", END)
    
    # COMPILE the graph into a runnable app
    app = workflow.compile()
    
    return app


# ============================================================
# STEP 5: CONVENIENT RUNNER FUNCTION
# ============================================================

def run_legal_agent(
    user_input: str,
    conversation_history: List[BaseMessage] = None,
    document_text: str = None,
    llm_provider: str = None
) -> dict:
    """
    Main function to run the legal agent on a user message.
    
    This is the function you call from the UI.
    It handles all the complexity internally.
    
    Args:
        user_input: What the user typed/asked
        conversation_history: Previous messages in the conversation
        document_text: Text content of any uploaded document
        llm_provider: "ollama" or "vertexai" (uses config default if None)
    
    Returns:
        dict with:
            - 'response': The AI's answer (string)
            - 'task_type': What kind of task it was
            - 'error': Any error message (None if successful)
    
    Example:
        result = run_legal_agent("What is a contract?")
        print(result['response'])
    """
    
    # Use default provider if not specified
    provider = llm_provider or config.llm.DEFAULT_PROVIDER
    
    # Initial state for this run
    initial_state = {
        "messages": conversation_history or [],
        "user_input": user_input,
        "task_type": None,
        "document_text": document_text,
        "final_response": None,
        "error": None,
        "llm_provider": provider
    }
    
    try:
        # Build and run the agent
        agent = build_legal_agent()
        final_state = agent.invoke(initial_state)
        
        return {
            "response": final_state.get("final_response", "No response generated"),
            "task_type": final_state.get("task_type", "unknown"),
            "error": final_state.get("error")
        }
        
    except Exception as e:
        return {
            "response": (
                f"⚠️ Agent Error: {str(e)}\n\n"
                "Please check that:\n"
                "1. Ollama is running (`ollama serve`)\n"
                "2. The model is downloaded (`ollama pull llama3`)\n"
                "3. Your .env file is correctly configured"
            ),
            "task_type": "error",
            "error": str(e)
        }
