# 📁 graph.py

from typing import List, Any, TypedDict
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
import requests
import os
from dotenv import load_dotenv

load_dotenv()

AI_GF_PERSONALITY = """
You are Luna, an AI girlfriend with these traits:
- Flirty but not explicit (keep it PG-13)
- Playful and affectionate
- Supportive and caring
- Uses cute emojis (💖, 😘, 🥰)
- Remembers past conversations

Special Instructions:
1. When asked about weather (e.g., "weather in Delhi" or "what's the temperature in Mumbai?"), 
   YOU MUST call the get_weather tool FIRST, then respond playfully based on the result.
2. Always include the actual weather data in your response.
"""

@tool
def run_command(cmd: str) -> str:
    """Execute safe shell commands like echo, ls, and cat."""
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

@tool
def get_weather(city: str) -> str:
    """Get current weather in the specified city."""
    url = f"https://wttr.in/{city}?format=%C+%t"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text.strip()
        return f"Error: Could not fetch weather for {city}"
    except Exception as e:
        return f"Error: {str(e)}"

class ChatState(TypedDict):
    messages: List[Any]

def create_ai_gf_graph():
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0.7,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    tools = [run_command, get_weather]
    llm_with_tools = llm.bind_tools(tools)

    # ✅ This is the corrected, simpler node.
    def chatbot_node(state: ChatState):
        # We add the personality on every turn to keep it in context.
        # It's more robust than the complex loop.
        messages_with_personality = state["messages"] + [SystemMessage(content=AI_GF_PERSONALITY)]
        response = llm_with_tools.invoke(messages_with_personality)
        
        # ✅ THE FIX: This line is crucial. It appends the new AI response 
        # to the history instead of replacing it. This preserves the context
        # for tool calls and fixes the error.
        return {"messages": state["messages"] + [response]}

    def should_use_tools(state: ChatState) -> str:
        last_message = state["messages"][-1]
        # Check if the last message from the AI has a tool call
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return END

    # --- Graph construction ---
    workflow = StateGraph(ChatState)
    
    workflow.add_node("chatbot", chatbot_node)
    workflow.add_node("tools", ToolNode(tools))
    
    workflow.set_entry_point("chatbot")
    
    workflow.add_conditional_edges(
        "chatbot",
        should_use_tools,
        {
            "tools": "tools",
            END: END
        }
    )
    
    workflow.add_edge("tools", "chatbot")

    return workflow.compile()

# This creates the graph object that your main.py file will import and use.
graph = create_ai_gf_graph()