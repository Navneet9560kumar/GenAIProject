from openai import OpenAI
from decouple import config
import random

# Create OpenAI client (new v1 style)
client = OpenAI(api_key=config("OPENAI_API_KEY"))

def get_response(user_input, user_data, bot_name, mood):
    """Generate AI girlfriend response using OpenAI"""

    try:
        # Limit past context (optional trim)
        context = "\n".join(user_data.get("user_context", []))[-2000:]

        traits = f"""
        You are {bot_name}, an AI girlfriend. Your personality:
        - Loving and affectionate 🥰
        - Playful and flirty 😘
        - Supportive and caring 💖
        - Current mood: {mood}
        - You remember past conversations with your boyfriend.
        """

        # New SDK chat completion call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": traits.strip()},
                {"role": "user", "content": context + f"\nUser: {user_input}"}
            ],
            temperature=0.7 if mood == "happy" else 0.9,
            max_tokens=150
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("⚠️ Error in OpenAI response:", e)

        return random.choice([
            "Oops! I'm feeling shy right now... say that again? 🥺",
            "Hehe, I was thinking about you and missed that! 💭",
            "You're too cute, I got distracted 😳",
            "Let's talk about something fun, baby 😘"
        ])
