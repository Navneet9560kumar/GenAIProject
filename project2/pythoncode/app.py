# 📁 app.py (The only file you need)

import asyncio
import os
from typing import List, Any, TypedDict

import numpy as np
import requests
import sounddevice as sd
import speech_recognition as sr
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode
from openai import AsyncOpenAI

# --- Setup and API Keys ---
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("❌ API key not found in .env")
    exit()
print("✅ API key loaded successfully")

# ==============================================================================
# 🧠 AI BRAIN LOGIC (This was your graph.py file)
# ==============================================================================

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
def get_weather(city: str) -> str:
    """Get current weather in the specified city."""
    url = f"https://wttr.in/{city}?format=%C+%t"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text.strip()
    except requests.exceptions.RequestException as e:
        return f"Error: Could not fetch weather. Reason: {e}"

class ChatState(TypedDict):
    messages: List[HumanMessage | AIMessage]

def create_ai_gf_graph():
    llm = ChatOpenAI(model="gpt-4", temperature=0.7, api_key=api_key)
    tools = [get_weather] # Simplified to one tool for clarity
    llm_with_tools = llm.bind_tools(tools)

    def chatbot_node(state: ChatState):
        messages_with_personality = state["messages"] + [SystemMessage(content=AI_GF_PERSONALITY)]
        response = llm_with_tools.invoke(messages_with_personality)
        return {"messages": state["messages"] + [response]}

    def should_use_tools(state: ChatState) -> str:
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return END

    workflow = StateGraph(ChatState)
    workflow.add_node("chatbot", chatbot_node)
    workflow.add_node("tools", ToolNode(tools))
    workflow.set_entry_point("chatbot")
    workflow.add_conditional_edges("chatbot", should_use_tools, {"tools": "tools", END: END})
    workflow.add_edge("tools", "chatbot")
    return workflow.compile()

# Create the graph instance right here in the same file
graph = create_ai_gf_graph()

# ==============================================================================
# 🎤 VOICE AND MAIN LOOP (This was your main.py file)
# ==============================================================================

openai_client = AsyncOpenAI(api_key=api_key)
VOICE_NAME = "shimmer"

async def tts(text: str):
    if not text:
        print("⚠️ Empty text, skipping TTS.")
        return
    try:
        print(f"🔊 Speaking as {VOICE_NAME}...")
        with sd.OutputStream(samplerate=24000, channels=1, dtype='int16') as stream:
            async with openai_client.audio.speech.with_streaming_response.create(
                model="tts-1",
                voice=VOICE_NAME,
                input=text,
                response_format="pcm"
            ) as response:
                async for chunk in response.iter_bytes(chunk_size=1024):
                    stream.write(np.frombuffer(chunk, dtype=np.int16))
        print("✅ Done speaking")
    except Exception as e:
        print(f"❌ Error in TTS: {e}")

async def main_turn(messages: list):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        print("🎤 Speak something...")
        try:
            audio = r.listen(source, timeout=10, phrase_time_limit=15)
            print("✅ Audio captured")
            user_input = r.recognize_google(audio)
            print(f"🗣️ You said: {user_input}")

            exit_phrases = ["band kar do", "exit", "bye", "goodbye", "luna stop", "stop now"]
            if any(phrase in user_input.lower() for phrase in exit_phrases):
                print("👋 Exiting as per your command...")
                await tts("Aww, okay baby! Talk to you later 💖 Byeee!")
                return False, messages

        except sr.WaitTimeoutError:
            print("⏱️ You didn’t say anything in time.")
            return True, messages
        except sr.UnknownValueError:
            print("🤷 Could not understand.")
            return True, messages
        except sr.RequestError as e:
            print(f"❌ Could not request results: {e}")
            return True, messages

    messages.append(HumanMessage(content=user_input))
    print("🧠 Thinking...")

    # Invoke the graph, which is now in the same file
    final_state = await graph.ainvoke({"messages": messages})
    
    # Replace our old history with the complete, updated history from the graph
    messages = final_state["messages"]
    final_response = messages[-1]

    if isinstance(final_response, AIMessage) and final_response.content:
        ai_content = final_response.content.strip()
        print(f"💬 AI: {ai_content}")
        await tts(ai_content)
    else:
        print("✅ Tool call finished. Ready for your next message.")

    return True, messages

async def run_conversation():
    # This list will now correctly remember the entire conversation
    messages = []
    while True:
        should_continue, messages = await main_turn(messages)
        if not should_continue:
            break
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    try:
        print("\n💕 Luna is ready for you (Ctrl+C to exit)...\n")
        asyncio.run(run_conversation())
    except KeyboardInterrupt:
        print("\n👋 Bye bye, baby!\n")