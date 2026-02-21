import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request

# Получаем токен из переменной окружения Render
TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

# --- Хранилище ID сообщений с кнопками для удаления ---
last_markup_message_id = {}

# --- Главное меню ---
def main_menu(chat_id):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("⭐ Telegram ⭐", callback_data="telegram"),
        InlineKeyboardButton("🍯 Standoff 2 🍯", callback_data="standoff2"),
        InlineKeyboardButton("🔥 Free Fire 🔥", callback_data="freefire"),
        InlineKeyboardButton("🗡 Mobile Legends 🗡", callback_data="ml"),
        InlineKeyboardButton("😮‍💨 PUBG Mobile 😮‍💨", callback_data="pubg"),
        InlineKeyboardButton("📞 Поддержка 📞", callback_data="support")
    )
    msg = bot.send_message(chat_id, "Привет! Выбери действие ⬇️", reply_markup=markup)
    last_markup_message_id[chat_id] = msg.message_id

# --- Команда /start ---
@bot.message_handler(commands=['start'])
def start(message):
    main_menu(message.chat.id)

# --- Создаем меню с кнопкой Назад для каждого раздела ---
def section_menu(chat_id, text):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔙 Назад", callback_data="back"))
    msg = bot.send_message(chat_id, text, reply_markup=markup)
    last_markup_message_id[chat_id] = msg.message_id

# --- Обработка нажатий на инлайн-кнопки ---
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    # Удаляем старое сообщение
    try:
        bot.delete_message(chat_id, message_id)
    except:
        pass

    # Обработка каждой кнопки
    if call.data == "telegram":
        section_menu(chat_id, "⭐ Telegram ⭐")
    elif call.data == "standoff2":
        section_menu(chat_id, "🍯 Standoff 2 🍯")
    elif call.data == "freefire":
        section_menu(chat_id, "🔥 Free Fire 🔥")
    elif call.data == "ml":
        section_menu(chat_id, "🗡 Mobile Legends 🗡")
    elif call.data == "pubg":
        section_menu(chat_id, "😮‍💨 PUBG Mobile 😮‍💨")
    elif call.data == "support":
        section_menu(chat_id, "📞 Поддержка 📞")
    elif call.data == "back":
        main_menu(chat_id)

    # Подтверждаем нажатие
    bot.answer_callback_query(call.id)

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
