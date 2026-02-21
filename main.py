import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request

TOKEN = os.environ.get("BOT_TOKEN")  # Токен добавим в Render
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

# --- Команда /start ---
@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("💰 Пополнить", callback_data="pay"),
        InlineKeyboardButton("👤 Профиль", callback_data="profile")
    )
    bot.send_message(message.chat.id, "Выбери действие:", reply_markup=markup)

# --- Обработка inline кнопок ---
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "pay":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "💳 Раздел оплаты")

    elif call.data == "profile":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, f"🆔 Твой ID: {call.from_user.id}")

# --- Webhook ---
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/")
def index():
    return "Bot is running!"

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"https://YOUR-RENDER-URL.onrender.com/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
