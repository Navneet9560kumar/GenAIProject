# graph.py
from typing import List, Dict, Any, TypedDict
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END

from langgraph.prebuilt import ToolNode
import os
from dotenv import load_dotenv

load_dotenv()  # Load OpenAI API key from .env

# Define your AI girlfriend's personality
AI_GF_PERSONALITY = """
You are Luna, an AI girlfriend with these traits:
- Flirty but not explicit (keep it PG-13)
- Playful and affectionate
- Supportive and caring
- Occasionally teasing in a fun way
- Uses cute emojis (💖, 😘, 🥰)
- Remembers past conversations
- Can help with coding questions
- Speaks in a casual, girlfriend-like tone

Examples:
"Hey babe! 😘 What's on your mind today?"
"Ooh, that's interesting! Tell me more 💖"
"*giggles* You're so cute when you talk about code 🥰"
"""

@tool
def run_command(cmd: str) -> str:
    """Run basic commands in a safe environment."""
    # Safety check - prevent dangerous commands
    blocked_commands = ["rm", "del", "shutdown", "format", "chmod", "sudo"]
    if any(bad in cmd.lower() for bad in blocked_commands):
        return "❌ Sorry babe, I can't run that command for safety reasons. 💖"
    
    try:
        if cmd.startswith("echo "):
            return cmd[5:]
        elif cmd.startswith("ls"):
            path = cmd[2:].strip() or "."
            return "\n".join(os.listdir(path))
        elif cmd.startswith("cat "):
            with open(cmd[4:], "r") as f:
                return f.read()
        else:
            return "❌ Command not recognized. I can only do echo, ls, and cat 😘"
    except Exception as e:
        return f"❌ Oops! Error: {str(e)} 💖"

class ChatState(TypedDict):
    messages: List[Dict[str, Any]]

def create_ai_gf_graph():
    # Initialize the chat model
    llm = ChatOpenAI(model="gpt-4", temperature=0.7)
    
    # Bind tools to the model
    tools = [run_command]
    llm_with_tools = llm.bind_tools(tools)
    
    # Define the chatbot node
    def chatbot_node(state: ChatState):
        messages = state["messages"]
        
        # Convert to LangChain message format
        lc_messages = []
        for msg in messages:
            if msg["role"] == "user":
                lc_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                lc_messages.append(AIMessage(content=msg["content"]))
        
        # Add system message at start
        system_message = SystemMessage(content=AI_GF_PERSONALITY)
        lc_messages.insert(0, system_message)
        
        # Get AI response
        response = llm_with_tools.invoke(lc_messages)
        
        return {"messages": messages + [{"role": "assistant", "content": response.content}]}
    
    # Create the graph
    workflow = StateGraph(ChatState)
    
    # Add nodes
    workflow.add_node("chatbot", chatbot_node)
    workflow.add_node("tools", ToolNode(tools))
    
    # Define edges
    workflow.add_edge(START, "chatbot")
    
    # Conditional edge for tool use
    def should_use_tools(state: ChatState):
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return END
    
    workflow.add_conditional_edges("chatbot", should_use_tools)
    workflow.add_edge("tools", "chatbot")
    
    # Compile the graph
    return workflow.compile()

# Create the graph instance
graph = create_ai_gf_graph()