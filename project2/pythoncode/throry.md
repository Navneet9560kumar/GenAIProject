🔄 Flow Summary Diagram:
pgsql
Copy code
🎤 User Speaks
   ↓
🎙️ main.py: Record audio → Convert to text
   ↓
🧠 graph.py (GPT-4 with LangGraph)
   - System prompt + tools check
   - Reply in Luna’s style
   ↓
🔊 main.py: Text → Voice via OpenAI TTS
   ↓
💬 Luna bolti hai: “Aww you're so cute! 🥰”