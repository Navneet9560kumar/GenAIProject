import asyncio
import numpy as np
import sounddevice as sd
import speech_recognition as sr
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from graph import graph  # ✅ keep this, remove streamlit

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("❌ API key not found in .env")
    exit()

print("✅ API key loaded successfully")

messages = []
openai = AsyncOpenAI(api_key=api_key)  # Ensure API key is passed

VOICE_NAME = "shimmer"

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

            # 👋 Voice-based exit trigger
            exit_phrases = ["band kar do", "exit", "bye", "goodbye", "luna stop", "stop now", "fuck you"]
            if any(phrase in user_input.lower() for phrase in exit_phrases):
                print("👋 Exiting as per your command...")
                await tts("Aww, okay baby! Talk to you later 💖 Byeee!")
                exit()

        except sr.WaitTimeoutError:
            print("⏱️ You didn’t say anything in time.")
            return
        except sr.UnknownValueError:
            print("🤷 Could not understand.")
            return
        except sr.RequestError as e:
            print("❌ Could not request results:", e)
            return

    # ✅ Fix: Use user_input here
    messages.append({"role": "user", "content": user_input})
    print("🧠 Thinking...")

    # ✅ Fix: This loop should be inside main()
    print("📦 Graph type check:", type(graph))

    for event in graph.stream({"messages": messages}, stream_mode="values"):
        if "messages" in event:
            if not event["messages"]:
                print("⚠️ No messages returned in event — skipping.")
                continue

            ai_message = event["messages"][-1]

            # ✅ FIXED: safer way to get content
            content = getattr(ai_message, "content", "").strip()

            if content:
                print("💬 AI:", content)
                messages.append({"role": "assistant", "content": content})
                await tts(content)
            else:
                print("⚠️ Empty AI response — skipping TTS")
        else:
            print("⚠️ Event without 'messages':", event)


if __name__ == "__main__":
    try:
        while True:
            print("\n🎤 Ready for your next message (Ctrl+C to exit)...\n")
            asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bye bye, baby!\n")
