# main.py
import asyncio
import numpy as np
import sounddevice as sd
import speech_recognition as sr
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from graph import graph

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("❌ API key not found in .env")
    exit()

print("✅ API key loaded successfully")

messages = []
openai = AsyncOpenAI(api_key=api_key)  # Ensure API key is passed

# List of supported voices
VOICE_NAME = "shimmer"  # alloy, shimmer, echo, fable, onyx, nova

async def tts(text: str):
    try:
        print(f"🔊 Speaking as {VOICE_NAME}...")
        async with openai.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice=VOICE_NAME,
            input=text,
            response_format="pcm"
        ) as response:
            audio_chunks = []
            async for chunk in response.iter_bytes():
                audio_chunks.append(chunk)

            audio_bytes = b"".join(audio_chunks)
            audio_array = np.frombuffer(audio_bytes, dtype=np.int16)

            sd.play(audio_array, samplerate=24000)
            sd.wait()
            print("✅ Done speaking")
    except Exception as e:
        print("❌ Error in TTS:", e)

async def main():
    global messages
    r = sr.Recognizer()

    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        print("🎤 Speak something...")

        try:
            audio = r.listen(source, timeout=5)
            print("✅ Audio captured")
            user_input = r.recognize_google(audio)
            print("🗣️ You said:", user_input)

        except sr.WaitTimeoutError:
            print("⏱️ You didn’t say anything in time.")
            return
        except sr.UnknownValueError:
            print("🤷 Could not understand.")
            return
        except sr.RequestError as e:
            print("❌ Could not request results:", e)
            return

    messages.append({"role": "user", "content": user_input})
    print("🧠 Thinking...")

    for event in graph.stream({"messages": messages}, stream_mode="values"):
        if "messages" in event:
            ai_message = event["messages"][-1]
            print("💬 AI:", ai_message["content"])
            messages.append({"role": "assistant", "content": ai_message["content"]})
            await tts(ai_message["content"])

if __name__ == "__main__":
    try:
        while True:
            print("\n🎤 Ready for your next message (Ctrl+C to exit)...\n")
            asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bye bye, baby!\n")
