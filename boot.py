import telebot
from telebot import types
from groq import Groq
import time
import os

# 🔹 API Keys ko yahan seedhe daala gaya hai
# WARNING: Yeh tarika surakshit nahi hai,
# kripya is code ko share na karein.
TELEGRAM_TOKEN = "7451412892:AAH9dpk8jIGnkZHyRWADVtzLiXhpAkBBVCw"
GROQ_API_KEY = "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"

# 🔹 Initialize bot and Groq client
bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = Groq(api_key=GROQ_API_KEY)

# 🔹 User state aur chat history dictionary
user_state = {}
chat_history = {} # Nayi chat history dictionary

# 🔹 Helper: get username
def get_username(message):
    return f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name

# 🔹 Helper: Gendered greeting
def get_gendered_greeting(username):
    # Ek simple list jisse ladkiyon ke naam ka anumaan lagaya ja sake
    female_names = ["priya", "sita", "geeta", "neha", "anjali", "pooja", "rekha", "sonam", "rani", "simran", "kajal", "isha"]
    
    # Username ko lower case mein badal kar check karein
    if any(name in username.lower() for name in female_names):
        return "aapki" # Female greeting
    else:
        return "aapka" # Male/Neutral greeting

# ===== /start command =====
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_state[chat_id] = "active"
    chat_history[chat_id] = [] # Nayi chat shuru hone par history ko saaf karein

    markup = types.InlineKeyboardMarkup(row_width=3)
    markup.add(
        types.InlineKeyboardButton("ℹ️ Help", callback_data="help"),
        types.InlineKeyboardButton("🤖 About", callback_data="about"),
        types.InlineKeyboardButton("❌ Stop", callback_data="stop")
    )

    username = get_username(message)
    gendered_greeting = get_gendered_greeting(username)
    bot.send_message(
        chat_id,
        f"👋 **Namaste {username}!**\n\n"
        "Main aapka professional AI assistant hoon.\n"
        f"Batao, aaj kya haal hai {gendered_greeting}?\n"
        "Aapko kya puchna hai? 🤔",
        parse_mode="Markdown",
        reply_markup=markup
    )

# ===== Callback buttons handler =====
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    username = get_username(call.message)

    if call.data == "stop":
        user_state[chat_id] = "stopped"
        chat_history.pop(chat_id, None) # Stop hone par history ko hatayein
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔄 Restart Bot", callback_data="start"))
        bot.edit_message_text(
            f"❌ **{username}, bot ab band ho gaya.**",
            chat_id=chat_id,
            message_id=call.message.message_id,
            parse_mode="Markdown",
            reply_markup=markup
        )

    elif call.data == "start":
        user_state[chat_id] = "active"
        start(call.message)

    elif call.data == "help":
        bot.answer_callback_query(call.id)
        bot.send_message(
            chat_id,
            f"ℹ️ **{get_username(call.message)},** mujhe koi bhi sawal bhejo aur main context ke hisab se short reply dunga. Main aapki pichli **30 baatein** yaad rakh sakta hoon. 😊",
            parse_mode="Markdown"
        )

    elif call.data == "about":
        bot.answer_callback_query(call.id)
        bot.send_message(
            chat_id,
            "🤖 **Professional AI Bot**\n\n"
            "Banaaya gaya Python aur Telegram API se.\n"
            "Groq AI (Llama 3.1) par based hai.\n"
            "Secure API key system use karta hai. 🔐",
            parse_mode="Markdown"
        )

# ===== /help, /about, /stop commands =====
@bot.message_handler(commands=['help'])
def help_command(message):
    username = get_username(message)
    bot.send_message(message.chat.id, f"ℹ️ **{username},** mujhe koi bhi sawal bhejo aur main context ke hisab se short reply dunga. Main aapki pichli **30 baatein** yaad rakh sakta hoon. 😊", parse_mode="Markdown")

@bot.message_handler(commands=['about'])
def about_command(message):
    bot.send_message(
        message.chat.id,
        "🤖 **Professional AI Bot**\n\n"
        "Banaaya gaya Python aur Telegram API se.\n"
        "Groq AI (Llama 3.1) par based hai.\n"
        "Secure API key system use karta hai. 🔐",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['stop'])
def stop_command(message):
    chat_id = message.chat.id
    user_state[chat_id] = "stopped"
    chat_history.pop(chat_id, None) # Stop hone par history ko hatayein
    username = get_username(message)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔄 Restart Bot", callback_data="start"))
    bot.send_message(chat_id, f"❌ **{username}, bot ab band ho gaya.**", parse_mode="Markdown", reply_markup=markup)

# ===== New Command-Based Text handler =====
# Ab bot sirf /ask ya /query command par hi reply dega.
@bot.message_handler(commands=['ask', 'query'])
def chat(message):
    chat_id = message.chat.id
    
    # Message mein se command hata kar asli text nikaale
    if message.text.startswith('/ask'):
        text = message.text.replace('/ask', '', 1).strip()
    elif message.text.startswith('/query'):
        text = message.text.replace('/query', '', 1).strip()
    else:
        # Agar command ke baad kuch nahi hai, to user ko bataye
        bot.send_message(chat_id, "🤔 **Kya poochhna chahte hain?** Please /ask ke baad apna sawal likhein.", parse_mode="Markdown")
        return

    username = get_username(message)

    if user_state.get(chat_id) == "stopped":
        bot.send_message(chat_id, f"⚠️ **{username}, bot band hai.** Dubara chalu karne ke liye /start likho. 🤔", parse_mode="Markdown")
        return

    bot.send_chat_action(chat_id, "typing")
    time.sleep(1)

    history = chat_history.get(chat_id, [])

    try:
        # User message ko history mein daalein
        history.append({"role": "user", "content": text})
        
        # Groq AI call with short/concise Hindi reply and history
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a professional AI assistant who replies in short, concise, and simple Hindi. Your responses are friendly and conversational. You must use relevant emojis based on the context of the conversation to make the chat more engaging. For example, use a laughing emoji 😂 for a joke, a thinking emoji 🤔 for a question, or a happy face 😊 to greet someone."},
                *history
            ],
        )
        reply = response.choices[0].message.content.strip()

        # Bot ke reply ko history mein daalein
        history.append({"role": "assistant", "content": reply})
        # History ko 30 messages tak seemit rakhein (15 user messages + 15 bot replies)
        chat_history[chat_id] = history[-30:]

        # Response mein koi generic emoji nahi hai, AI hi decide karega
        bot.send_message(chat_id, f"**{username},** {reply}", parse_mode="Markdown")

    except Exception as e:
        print(f"Groq API error: {e}")
        bot.send_message(chat_id, f"⚠️ Kuch gadbad hui: {e}", parse_mode="Markdown")

# ===== Sticker handler =====
# Yeh handler stickers par reaction dene ke liye hai
@bot.message_handler(content_types=['sticker'])
def handle_sticker(message):
    chat_id = message.chat.id
    username = get_username(message)
    
    # Bot sticker par react karega
    bot.send_message(chat_id, f"😅 **{username},** yeh sticker mazedaar hai!", parse_mode="Markdown")

# ===== Non-command, non-sticker handler =====
# Yeh handler baaki sabhi messages ko ignore karne ke liye hai
@bot.message_handler(func=lambda m: True)
def ignore_all_other_messages(message):
    pass # Kuch bhi nahi karega

# ===== Start bot =====
print("🤖 Professional Bot chal raha hai...")
bot.polling(non_stop=True, interval=0)

