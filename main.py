import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request

# Получаем токен из переменной окружения Render
TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

# --- Хранилище ID сообщений с кнопками для обновления ---
last_markup_message_id = {}

# --- Команда /start ---
@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("⭐️ Telegram", callback_data="telegram"),
        InlineKeyboardButton("🎯 Standoff 2", callback_data="standoff2"),
        InlineKeyboardButton("🔥 Free Fire", callback_data="freefire"),
        InlineKeyboardButton("🗡 Mobile Legends", callback_data="ml"),
        InlineKeyboardButton("😮‍💨 PUBG Mobile", callback_data="pubg"),
        InlineKeyboardButton("📞 Поддержка", callback_data="support")
    )

    # Если есть старое сообщение с кнопками — редактируем
    if message.chat.id in last_markup_message_id:
        try:
            bot.edit_message_reply_markup(chat_id=message.chat.id,
                                          message_id=last_markup_message_id[message.chat.id],
                                          reply_markup=markup)
            return
        except:
            pass

    # Иначе отправляем новое сообщение с кнопками
    msg = bot.send_message(message.chat.id, "Привет! Выбери действие ⬇️", reply_markup=markup)
    last_markup_message_id[message.chat.id] = msg.message_id

# --- Обработка нажатий на инлайн-кнопки ---
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "telegram":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "⭐️ Telegram")
    elif call.data == "standoff2":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "🎯 Standoff 2")
    elif call.data == "freefire":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "🔥 Free Fire")
    elif call.data == "ml":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "🗡 Mobile Legends")
    elif call.data == "pubg":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "😮‍💨 PUBG Mobile")
    elif call.data == "support":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "📞 Поддержка")

# --- Webhook для Render ---
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/")
def index():
    return "Bot is running!"

# --- Настройка webhook через переменную окружения ---
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

if __name__ == "__main__":
    bot.remove_webhook()
    if WEBHOOK_URL:
        bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
