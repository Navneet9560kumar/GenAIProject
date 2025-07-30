from typing import List, Dict, Any, TypedDict
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
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

    def chatbot_node(state: ChatState):
        messages = state["messages"]
        lc_messages = []

        for msg in messages:
            if isinstance(msg, dict) and msg.get("role") == "user":
                lc_messages.append(HumanMessage(content=msg["content"]))
            elif isinstance(msg, dict) and msg.get("role") == "assistant":
                if "content" in msg:
                    lc_messages.append(AIMessage(content=msg["content"]))
                if "tool_calls" in msg:
                    lc_messages.append(AIMessage(
                        content="",
                        additional_kwargs={"tool_calls": msg["tool_calls"]}
                    ))
            elif isinstance(msg, ToolMessage):
                lc_messages.append(msg)
            elif isinstance(msg, AIMessage):
                lc_messages.append(msg)

        lc_messages.insert(0, SystemMessage(content=AI_GF_PERSONALITY))
        response = llm_with_tools.invoke(lc_messages)

        if hasattr(response, "tool_calls") and response.tool_calls:
            tool_calls = [
                {
                    "name": tc["name"],
                    "args": tc["args"],
                    "id": tc["id"],
                    "type": "function"
                }
                for tc in response.tool_calls
            ]
            return {
                "messages": messages + [
                    AIMessage(content="", additional_kwargs={"tool_calls": tool_calls})
                ]
            }

        return {
            "messages": messages + [
                {"role": "assistant", "content": response.content}
            ]
        }

    def should_use_tools(state: ChatState):
        for msg in reversed(state["messages"]):
            if isinstance(msg, AIMessage):
                if msg.additional_kwargs.get("tool_calls"):
                    return "tools"
            elif isinstance(msg, dict) and msg.get("role") == "assistant":
                if msg.get("tool_calls"):
                    return "tools"
        return END

    workflow = StateGraph(ChatState)
    workflow.add_node("chatbot", chatbot_node)
    workflow.add_node("tools", ToolNode(tools))
    workflow.add_edge(START, "chatbot")
    workflow.add_conditional_edges("chatbot", should_use_tools)
    workflow.add_edge("tools", "chatbot")

    return workflow.compile()

graph = create_ai_gf_graph()
