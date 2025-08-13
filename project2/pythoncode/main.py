# 📁 main.py

import asyncio
import numpy as np
import sounddevice as sd
import speech_recognition as sr
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from langchain_core.messages import AIMessage, HumanMessage
from graph import graph # This is correct

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("❌ API key not found in .env")
    exit()

print("✅ API key loaded successfully")

openai = AsyncOpenAI(api_key=api_key)
VOICE_NAME = "shimmer"

async def tts(text: str):
    if not text:
        print("⚠️ Empty text, skipping TTS.")
        return
    try:
        print(f"🔊 Speaking as {VOICE_NAME}...")
        with sd.OutputStream(samplerate=24000, channels=1, dtype='int16') as stream:
            async with openai.audio.speech.with_streaming_response.create(
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

async def main(messages: list):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        print("🎤 Speak something...")
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
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

    final_state = await graph.ainvoke({"messages": messages})
    
    # ✅ THE FIX: Replace the old message history with the complete,
    # updated history from the graph's final state.
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
    messages = []
    while True:
        should_continue, messages = await main(messages)
        if not should_continue:
            break
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    try:
        print("\n🎤 Ready for your first message (Ctrl+C to exit)...\n")
        asyncio.run(run_conversation())
    except KeyboardInterrupt:
        print("\n👋 Bye bye, baby!\n")