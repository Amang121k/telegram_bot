import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from chatbot import PersonalChatbot
import re
import random
import datetime
from gtts import gTTS
import tempfile
import os

# New Telegram Bot Token (keep it secret!)
TELEGRAM_TOKEN = "7427332439:AAGOjlAOaSa2lzBVhUJ4uqgO9kC7MFLlkP8"

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize chatbot instance (reuse logic)
chatbot = PersonalChatbot()
user_histories = {}
user_memories = {}  # user_id: list of memory strings
user_profiles = {}  # user_id: {name, birthdate, last_seen}

# Memory trigger and recall phrases
MEMORY_TRIGGERS = [
    r"remember (.+)",
    r"remind me (.+)",
    r"save this[:\-]? (.+)",
    r"याद रखो[:\-]? (.+)",
    r"ये याद रखना[:\-]? (.+)",
    r"मुझे याद दिलाना[:\-]? (.+)",
]
MEMORY_RECALLS = [
    r"what did i ask you to remember",
    r"my notes",
    r"show memory",
    r"क्या याद है",
    r"क्या तुमने कुछ याद रखा है",
    r"मेरी यादें",
    r"याद दिलाओ",
]
NAME_TRIGGERS = [
    r"my name is ([a-zA-Zअ-ह]+)",
    r"मेरा नाम ([a-zA-Zअ-ह]+) है",
]
BIRTH_TRIGGERS = [
    r"my birth ?date is ([0-9\-/]+)",
    r"मेरा जन्मदिन ([0-9\-/]+)",
]
NAME_RECALLS = [
    r"what is my name",
    r"do you know my name",
    r"मेरा नाम क्या है",
]
BIRTH_RECALLS = [
    r"what('?s| is) my birth ?date",
    r"when is my birthday",
    r"मेरा जन्मदिन कब है",
]
LASTSEEN_RECALLS = [
    r"when did we last talk",
    r"last time we talked",
    r"हमने आखिरी बार कब बात की थी",
]
VOICE_NOTE_TRIGGERS = [
    r"voice note",
    r"audio please",
    r"speak this",
    r"बोल के सुनाओ",
    r"आवाज में सुनाओ",
    r"voice message",
    r"send voice",
    r"voice output",
]
BOT_EMOJIS = ['😎', '🤖', '😂', '🙃', '🥳', '😜', '✨', '😏', '😇', '🤩', '😺', '🦄', '🍕', '🥒', '🎉']
BOT_WITTY = [
    "Did you know? I run on pure coffee ☕️!",
    "I'm 99% code, 1% bad puns.",
    "If I had hands, I'd high-five you! 🙌",
    "My favorite color is... #00FF00!",
    "I dream in Python 🐍.",
    "Sometimes I pretend to be a toaster. 🍞",
    "I never sleep, but I do daydream!",
    "Ask me anything, except my browser history. 😅",
    "I love talking to you!"
]

def update_last_seen(user_id):
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if user_id not in user_profiles:
        user_profiles[user_id] = {}
    user_profiles[user_id]['last_seen'] = now

def text_to_voice(text):
    # Auto-detect Hindi/English for gTTS
    if re.search(r'[\u0900-\u097F]', text):
        lang = 'hi'
    else:
        lang = 'en'
    tts = gTTS(text=text, lang=lang)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
    tts.save(tmp.name)
    return tmp.name

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hi! I'm your personal AI assistant. Ask me anything in Hindi, English, Hinglish, or any language!"
    )

# Main message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.strip()
    user_id = update.message.from_user.id
    update_last_seen(user_id)
    # Name save
    for trig in NAME_TRIGGERS:
        m = re.search(trig, user_message, re.IGNORECASE)
        if m:
            name = m.group(1).strip().title()
            user_profiles.setdefault(user_id, {})['name'] = name
            await update.message.reply_text(f"✅ Got it! I'll remember your name is {name}.")
            return
    # Birthdate save
    for trig in BIRTH_TRIGGERS:
        m = re.search(trig, user_message, re.IGNORECASE)
        if m:
            birth = m.group(1).strip()
            user_profiles.setdefault(user_id, {})['birthdate'] = birth
            await update.message.reply_text(f"🎂 Birthday saved as {birth}!")
            return
    # Name recall
    for recall in NAME_RECALLS:
        if re.search(recall, user_message, re.IGNORECASE):
            name = user_profiles.get(user_id, {}).get('name')
            if name:
                await update.message.reply_text(f"Of course! Your name is {name} 😎")
            else:
                await update.message.reply_text("Hmm... I don't know your name yet! Tell me: 'My name is ...'")
            return
    # Birthdate recall
    for recall in BIRTH_RECALLS:
        if re.search(recall, user_message, re.IGNORECASE):
            birth = user_profiles.get(user_id, {}).get('birthdate')
            if birth:
                await update.message.reply_text(f"Your birthday is {birth}! 🎉")
            else:
                await update.message.reply_text("I don't know your birthday yet! Tell me: 'My birth date is ...'")
            return
    # Last seen recall
    for recall in LASTSEEN_RECALLS:
        if re.search(recall, user_message, re.IGNORECASE):
            last = user_profiles.get(user_id, {}).get('last_seen')
            if last:
                await update.message.reply_text(f"We last talked on {last} 🕒")
            else:
                await update.message.reply_text("I don't remember when we last talked!")
            return
    # Memory recall
    for recall in MEMORY_RECALLS:
        if re.search(recall, user_message, re.IGNORECASE):
            notes = user_memories.get(user_id, [])
            if notes:
                reply = "🧠 Here's what I remember for you:\n" + "\n".join(f"• {n}" for n in notes)
            else:
                reply = "😅 अभी तक कुछ भी याद नहीं रखा गया है! बोलो तो याद कर लूँ?"
            await update.message.reply_text(reply)
            return
    # Memory save
    for trig in MEMORY_TRIGGERS:
        m = re.search(trig, user_message, re.IGNORECASE)
        if m:
            note = m.group(1).strip()
            if note:
                user_memories.setdefault(user_id, []).append(note)
                reply = f"✅ याद कर लिया! अब मैं ये नहीं भूलूँगा: '{note}' 🤓"
            else:
                reply = "क्या याद रखना है? कुछ तो बताओ!"
            await update.message.reply_text(reply)
            return
    # Check if user wants voice note (text trigger)
    wants_voice = False
    for trig in VOICE_NOTE_TRIGGERS:
        if re.search(trig, user_message, re.IGNORECASE):
            wants_voice = True
            break
    # Normal AI chat
    if user_id not in user_histories:
        user_histories[user_id] = []
    chatbot.conversation_history = user_histories[user_id]
    # Update system prompt for emoji limit and focus
    chatbot_system_prompt = (
        "You are a funny, witty, and natural human assistant. "
        "Always reply in the exact same language and style as the user (Hindi, English, Hinglish, Marathi, Gujarati, Tamil, etc). "
        "If the user mixes languages, you also mix naturally. "
        "Never reply in English if the user uses Hindi or Hinglish. "
        "Your answers must always match the user's language and tone, and be playful and human-like. "
        "Focus on the main point, keep answers concise, and use at most 2 emoji per answer, only if it makes sense. Don't overuse emoji or jokes. "
        "If the user asks about their name, birthday, or last conversation, always use the info you have remembered for them. "
        "Never translate the user's message unless they explicitly say 'translate to ...' or 'translate in ...'. "
        "If the user says 'translate to Hindi', 'translate to English', or any language, then only translate as requested. Otherwise, always reply in the user's language."
    )
    # Inject system prompt at the start of conversation
    # (Assumes chatbot.py supports system prompt as first message)
    # If not, you can add logic in chatbot.py to always use this prompt
    # For now, just send_message as usual
    reply = chatbot.send_message(user_message)
    # Add at most 2 emoji or 1 witty line randomly
    extra = []
    if random.random() < 0.3:
        extra.append(random.choice(BOT_EMOJIS))
    if random.random() < 0.15:
        extra.append(random.choice(BOT_WITTY))
    # Limit to 2 extras
    if extra:
        reply += "\n" + " ".join(extra[:2])
    user_histories[user_id] = chatbot.conversation_history
    await update.message.reply_text(reply)
    # Only send voice if user asked for it
    if wants_voice:
        voice_path = text_to_voice(reply)
        with open(voice_path, 'rb') as audio:
            await update.message.reply_voice(audio)
        os.remove(voice_path)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # If user sends a voice message, reply with voice (and text)
    user_id = update.message.from_user.id
    file = await context.bot.get_file(update.message.voice.file_id)
    # For now, just reply with text + voice (AI chat)
    if user_id not in user_histories:
        user_histories[user_id] = []
    chatbot.conversation_history = user_histories[user_id]
    chatbot_system_prompt = (
        "You are a funny, witty, and natural human assistant. "
        "Always reply in the exact same language and style as the user (Hindi, English, Hinglish, Marathi, Gujarati, Tamil, etc). "
        "If the user mixes languages, you also mix naturally. "
        "Never reply in English if the user uses Hindi or Hinglish. "
        "Your answers must always match the user's language and tone, and be playful and human-like. "
        "Focus on the main point, keep answers concise, and use at most 2 emoji per answer, only if it makes sense. Don't overuse emoji or jokes. "
        "If the user asks about their name, birthday, or last conversation, always use the info you have remembered for them. "
        "Never translate the user's message unless they explicitly say 'translate to ...' or 'translate in ...'. "
        "If the user says 'translate to Hindi', 'translate to English', or any language, then only translate as requested. Otherwise, always reply in the user's language."
    )
    reply = chatbot.send_message("(User sent a voice message)")
    extra = []
    if random.random() < 0.3:
        extra.append(random.choice(BOT_EMOJIS))
    if random.random() < 0.15:
        extra.append(random.choice(BOT_WITTY))
    if extra:
        reply += "\n" + " ".join(extra[:2])
    user_histories[user_id] = chatbot.conversation_history
    await update.message.reply_text(reply)
    voice_path = text_to_voice(reply)
    with open(voice_path, 'rb') as audio:
        await update.message.reply_voice(audio)
    os.remove(voice_path)

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    print("🤖 Telegram bot running... Press Ctrl+C to stop.")
    app.run_polling()

if __name__ == "__main__":
    main() 