import os
import logging
import random
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Set up logging
logging.basicConfig(level=logging.INFO)

# Anime-style personality
greetings = ["Heya~", "Yo!", "Ohayo~", "Hi hi!", "Kon'nichiwa~", "Helloo!"]
anime_responses = [
    "Nani?! That’s interesting~",
    "Sugoi! You're pretty cool!",
    "Baka~ what are you even saying? 😂",
    "Ara ara~ that's suspicious...",
    "UwU I’m just a bot... but I have feelings too!",
    "You remind me of an anime protagonist 🐾",
]

# Handle start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Heya! I'm your anime  bot. Ask me anything or just chat with me~ 💬")

# Handle messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text.lower()

    if "who is your owner" in message:
        await update.message.reply_text("My Dev is the supreme being behind my code! 💻✨")
    elif any(greet in message for greet in ["hi", "hello", "yo", "hey", "kon", "ohayo"]):
        await update.message.reply_text(random.choice(greetings))
    else:
        # AI reply from OpenRouter
        response = await get_ai_response(update.message.text)
        await update.message.reply_text(response)

    # Forward to owner
    await context.bot.send_message(chat_id=OWNER_ID, text=f"📩 From @{update.effective_user.username} ({update.effective_user.id}):\n{update.message.text}")

# OpenRouter API call
async def get_ai_response(user_message):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    json_data = {
        "model": "openchat/openchat-7b:free",
        "messages": [
            {"role": "system", "content": "You're a friendly anime chatbot who replies in anime style."},
            {"role": "user", "content": user_message},
        ]
    }
    try:
        r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=json_data)
        reply = r.json()['choices'][0]['message']['content']
        return reply
    except Exception as e:
        return f"Oops! Something went wrong: {e}"

# Main
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Bot started!")
    app.run_polling()

if __name__ == "__main__":
    main()
