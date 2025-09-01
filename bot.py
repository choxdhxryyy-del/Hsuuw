import telebot
from telebot import types
from groq import Groq
import time
import os
import random

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
            f"ℹ️ **@choxdhxry,** mujhe koi bhi sawal bhejo aur main context ke hisab se short reply dunga. Main aapki pichli **30 baatein** yaad rakh sakta hoon. 😊",
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
    if username == "@choxdhxry":
        bot.send_message(message.chat.id, f"ℹ️ **@choxdhxry,** mujhe koi bhi sawal bhejo aur main context ke hisab se short reply dunga. Main aapki pichli **30 baatein** yaad rakh sakta hoon. 😊", parse_mode="Markdown")
    else:
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

# ===== Weather Handler =====
@bot.message_handler(commands=['weather'])
def get_location_for_weather(message):
    chat_id = message.chat.id
    user_state[chat_id] = "waiting_for_location"
    bot.send_message(chat_id, "🌧️ Achcha, kis jagah ka mausam jaanna chahte ho? Location ka naam batao.")
    time.sleep(1)

# ===== Text handler =====
@bot.message_handler(func=lambda message: user_state.get(message.chat.id) != "waiting_for_location" and not message.text.startswith('/') and message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id)
def chat(message):
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
                {"role": "system", "content": "You are an AI assistant who talks like a gangster or a 'don.' Your replies are short, confident, and direct. You don't use many emojis and your tone is serious and commanding. You speak in simple, slightly arrogant Hindi. Example replies: 'Bol, kya kaam hai?' 'Sawal seedha kar.' 'Pata hai, main kaun hoon?'"},
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

# ===== Location Handler for Weather =====
@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == "waiting_for_location")
def handle_location(message):
    chat_id = message.chat.id
    location = message.text.strip()
    username = get_username(message)
    
    weather_info = "Saaf hai, aur 25°C temperature hai."
    if "delhi" in location.lower():
        weather_info = "Thoda sa pollution hai, halki dhundh bhi hai. 28°C temperature hai. 💨"
    elif "mumbai" in location.lower():
        weather_info = "Mausam bahut mast hai, halki-halki hawa chal rahi hai. 30°C temperature hai. 🌊"
    
    bot.send_message(chat_id, f"**{username},** {location} mein mausam: {weather_info} 😊", parse_mode="Markdown")
    user_state[chat_id] = "active"

# ===== Sticker handler =====
@bot.message_handler(content_types=['sticker'])
def handle_sticker(message):
    chat_id = message.chat.id
    
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a professional AI assistant who replies to stickers in a very short, funny, and friendly way. Use simple, colloquial Hindi with emojis. Make sure your replies are varied and creative, for example: 'Haha, bahut sahi sticker! 😂', 'Ekdum mast! 🤩', 'Kamaal kar diya! 👏', 'Bahut hi badhiya! 🤣', 'Arey, waah! Maza aa gaya! 😊', 'Nice one! 💯', 'Sahi hai boss! 😎'"},
                {"role": "user", "content": "User sent a sticker. Give a reaction."}
            ],
        )
        ai_reaction = response.choices[0].message.content.strip()
        bot.reply_to(message, ai_reaction)
    except Exception as e:
        print(f"Groq API error: {e}")
        bot.reply_to(message, "😅 **Oops,** kuch gadbad ho gayi.")


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
