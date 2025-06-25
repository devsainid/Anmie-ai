from telegram import Update, ChatMember
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import requests
import os

# Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
USER_DATA_FILE = "users.txt"

# Save new user ID to a file
def save_user(user_id):
    try:
        with open(USER_DATA_FILE, "a+") as f:
            f.seek(0)
            ids = f.read().splitlines()
            if str(user_id) not in ids:
                f.write(f"{user_id}\n")
    except:
        pass

# Generate a chatbot reply using OpenRouter API
def ai_anime_reply(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an anime-style chatbot that replies in kind, friendly, emotional English. "
                    "You love anime and speak like a sweet anime character. Be playful and smart. "
                    "If someone asks about your owner, say 'My creator is Dev!'"
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=10)
        return res.json()["choices"][0]["message"]["content"]
    except Exception:
        return "Oopsie~ I can't think right now. Please try again later!"

# Check if user is admin or the owner
async def is_admin_or_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id == OWNER_ID:
        return True
    try:
        member = await context.bot.get_chat_member(update.effective_chat.id, user_id)
        return member.status in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]
    except:
        return False

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_user(update.effective_user.id)
    if await is_admin_or_owner(update, context):
        await update.message.reply_text("Hello Dev! Your anime AI bot is online and at your service.")
    else:
        await update.message.reply_text("Hi there! I'm your cute anime-style chatbot. Let's talk about anything~")

# /broadcast command (owner only)
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Only Dev can use this command.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /broadcast <message>")
        return

    message = " ".join(context.args)
    sent, failed = 0, 0
    try:
        with open(USER_DATA_FILE, "r") as f:
            ids = f.read().splitlines()
        for uid in ids:
            try:
                await context.bot.send_message(chat_id=int(uid), text=message)
                sent += 1
            except:
                failed += 1
    except FileNotFoundError:
        await update.message.reply_text("No users found to broadcast to.")
        return

    await update.message.reply_text(f"Broadcast done!\n✅ Sent: {sent}\n❌ Failed: {failed}")

# /admin command
async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_admin_or_owner(update, context):
        await update.message.reply_text("Command allowed! Admin powers accepted.")
    else:
        await update.message.reply_text("Only Dev or group admins can use this command.")

# Handle regular text messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = update.message.text
    save_user(user_id)

# Forward messages to the owner
    if user_id != OWNER_ID:
        try:
            await context.bot.forward_message(chat_id=OWNER_ID, from_chat_id=update.message.chat_id, message_id=update.message.message_id)
        except:
            pass

    reply = ai_anime_reply(message)
    await update.message.reply_text(reply)

# Main entry point
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Bot started!")
    app.run_polling()

# Correct entry point check
if __name__ == "__main__":
    
