import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# --- CONFIG ---
TELEGRAM_TOKEN = "7427332439:AAGOjlAOaSa2lzBVhUJ4uqgO9kC7MFLlkP8"
OPENROUTER_API_KEY = "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"
OPENROUTER_MODEL = "mistralai/mistral-7b-instruct"  # or your preferred model

# --- SYSTEM PROMPT ---
SYSTEM_PROMPT = "Short answers only."

# --- LOGGING ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# --- OpenRouter API Call ---
def ask_openrouter(prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=30)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logging.error(f"OpenRouter API error: {e}")
        return "माफ़ करना, अभी मैं जवाब नहीं दे सकता।"

# --- Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("नमस्ते! मैं लोलू हूँ — आपका पर्सनल चैटबोट 🤖")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("मुझसे कुछ भी पूछिए! मैं आपकी भाषा में जवाब दूँगा।\nCommands: /weather, /joke, /shayari, /news")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.strip()
    # Command detection for custom behavior
    if user_message.lower().startswith("/weather"):
        prompt = f"Weather: {user_message}"
    elif user_message.lower().startswith("/joke"):
        prompt = f"Joke: {user_message}"
    elif user_message.lower().startswith("/shayari"):
        prompt = f"Shayari: {user_message}"
    elif user_message.lower().startswith("/news"):
        prompt = f"News: {user_message}"
    else:
        prompt = user_message
    response = ask_openrouter(prompt)
    await update.message.reply_text(response)

# --- Main ---
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main() 