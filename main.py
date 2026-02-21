import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request

# Получаем токен из переменной окружения Render
TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

# --- Хранилище пользователей (простое, в памяти) ---
users = set()

# --- Команда /start ---
@bot.message_handler(commands=['start'])
def start(message):
    # Добавляем пользователя в счётчик
    users.add(message.from_user.id)

    # Убираем любые старые ReplyKeyboard
    bot.send_message(message.chat.id, "Привет! Выбери действие ⬇️", reply_markup=None)

    # Новое красивое инлайн-меню
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("💰 Пополнить баланс", callback_data="pay"),
        InlineKeyboardButton("👤 Профиль", callback_data="profile"),
        InlineKeyboardButton("📦 Магазин", callback_data="shop"),
        InlineKeyboardButton("🛠 Поддержка", callback_data="support")
    )
    bot.send_message(message.chat.id, "Выбери действие ⬇️", reply_markup=markup)

# --- Обработка нажатий на инлайн-кнопки ---
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "pay":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "💳 Раздел оплаты")
    elif call.data == "profile":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, f"🆔 Твой ID: {call.from_user.id}\n👥 Всего пользователей: {len(users)}")
    elif call.data == "shop":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "📦 Добро пожаловать в магазин")
    elif call.data == "support":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "🛠 Свяжитесь с поддержкой")

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
