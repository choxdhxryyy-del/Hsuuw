import telebot
from telebot import types
from groq import Groq
import time
import os

TELEGRAM_TOKEN = "7451412892:AAH9dpk8jIGnkZHyRWADVtzLiXhpAkBBVCw"
GROQ_API_KEY = "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"

try:
    bot = telebot.TeleBot(TELEGRAM_TOKEN)
    client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    print(f"Error: Bot ya Groq client ko initialize nahi kiya ja saka. Please check your API keys. Error: {e}")
    exit()

user_state = {}
chat_history = {}

def get_username(message):
    return f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name

def get_gendered_greeting(username):
    female_names = ["priya", "sita", "geeta", "neha", "anjali", "pooja", "rekha", "sonam", "rani", "simran", "kajal", "isha"]
    
    if any(name in username.lower() for name in female_names):
        return "aapki"
    else:
        return "aapka"

# ===== /start command =====
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_state[chat_id] = "active"
    chat_history[chat_id] = []

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
        chat_history.pop(chat_id, None)
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
    chat_history.pop(chat_id, None)
    username = get_username(message)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔄 Restart Bot", callback_data="start"))
    bot.send_message(chat_id, f"❌ **{username}, bot ab band ho gaya.**", parse_mode="Markdown", reply_markup=markup)

# ===== Reply handler =====
# Naya handler jo sirf tab kaam karega jab koi bot ke message ko reply kare
@bot.message_handler(content_types=['text'], func=lambda message: message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id)
def chat_reply_handler(message):
    chat_id = message.chat.id
    text = message.text.strip()
    username = get_username(message)

    if user_state.get(chat_id) == "stopped":
        bot.send_message(chat_id, f"⚠️ **{username}, bot band hai.** Dubara chalu karne ke liye /start likho. 🤔", parse_mode="Markdown")
        return

    bot.send_chat_action(chat_id, "typing")
    time.sleep(1)

    history = chat_history.get(chat_id, [])

    try:
        history.append({"role": "user", "content": text})
        
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a professional AI assistant who replies in short, concise, and simple Hindi. Your responses are friendly and conversational. You must use relevant emojis based on the context of the conversation to make the chat more engaging. For example, use a laughing emoji 😂 for a joke, a thinking emoji 🤔 for a question, or a happy face 😊 to greet someone."},
                *history
            ],
        )
        reply = response.choices[0].message.content.strip()

        history.append({"role": "assistant", "content": reply})
        chat_history[chat_id] = history[-30:]

        bot.send_message(chat_id, f"**{username},** {reply}", parse_mode="Markdown")

    except Exception as e:
        print(f"Groq API error: {e}")
        bot.send_message(chat_id, f"⚠️ Kuch gadbad hui: {e}", parse_mode="Markdown")

# ===== Sticker handler =====
@bot.message_handler(content_types=['sticker'])
def handle_sticker(message):
    chat_id = message.chat.id
    username = get_username(message)
    bot.send_message(chat_id, f"😅 **{username},** yeh sticker mazedaar hai!", parse_mode="Markdown")

# ===== Fallback handler =====
# Yah handler baaki sabhi messages ko ignore karne ke liye hai
@bot.message_handler(func=lambda m: True)
def ignore_all_other_messages(message):
    pass

# ===== Start bot in a secure polling loop =====
def main():
    print("🤖 Professional Bot chal raha hai...")
    while True:
        try:
            bot.polling(non_stop=True, interval=0, timeout=120)
        except Exception as e:
            print(f"Polling error: {e}")
            time.sleep(15)

if __name__ == "__main__":
    main()
