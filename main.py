import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request

# Получаем токен из переменной окружения Render
TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

last_markup_message_id = {}

# --- Главное меню ---
def main_menu(chat_id):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("⭐Telegram", callback_data="telegram"),
        InlineKeyboardButton("🍯Standoff 2", callback_data="standoff2"),
        InlineKeyboardButton("🔥Free Fire", callback_data="freefire"),
        InlineKeyboardButton("🗡Mobile Legends", callback_data="ml"),
        InlineKeyboardButton("😮‍💨PUBG Mobile", callback_data="pubg"),
        InlineKeyboardButton("📞Поддержка", callback_data="support")
    )

    if chat_id in last_markup_message_id:
        try:
            bot.delete_message(chat_id, last_markup_message_id[chat_id])
        except:
            pass

    photo_path = "assets/winter_menu.png"
    msg = bot.send_photo(chat_id, photo=open(photo_path, "rb"),
                         caption="Привет! Выбери действие ⬇️",
                         reply_markup=markup)
    last_markup_message_id[chat_id] = msg.message_id

@bot.message_handler(commands=['start'])
def start(message):
    main_menu(message.chat.id)

# --- Раздел с текстом и кнопками поддержки ---
def support_section(chat_id):
    text = ("✅ Привет, ты в разделе поддержки.\n\n"
            "❗️ Если у тебя есть вопросы по покупкам или работе бота, нажми кнопку ниже, чтобы связаться со мной напрямую.\n\n"
            "⚠️ Старайся описать свою проблему максимально подробно.")
    markup = InlineKeyboardMarkup()
    # кнопка Связаться слева, Назад справа
    markup.row(InlineKeyboardButton("✅Связаться", url="https://t.me/m/_guuyZcWOTUy"),
               InlineKeyboardButton("🔙Назад", callback_data="back"))

    photo_path = "assets/support_menu.png"
    msg = bot.send_photo(chat_id, photo=open(photo_path, "rb"),
                         caption=text,
                         reply_markup=markup)
    last_markup_message_id[chat_id] = msg.message_id

# --- Обработка нажатий кнопок ---
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    try:
        bot.delete_message(chat_id, message_id)
    except:
        pass

    if call.data == "telegram":
        bot.send_message(chat_id, "⭐Telegram")
    elif call.data == "standoff2":
        bot.send_message(chat_id, "🍯Standoff 2")
    elif call.data == "freefire":
        bot.send_message(chat_id, "🔥Free Fire")
    elif call.data == "ml":
        bot.send_message(chat_id, "🗡Mobile Legends")
    elif call.data == "pubg":
        bot.send_message(chat_id, "😮‍💨PUBG Mobile")
    elif call.data == "support":
        support_section(chat_id)
    elif call.data == "back":
        main_menu(chat_id)

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

WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

if __name__ == "__main__":
    bot.remove_webhook()
    if WEBHOOK_URL:
        bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
