import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

last_message = {}

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

    if chat_id in last_message:
        try: bot.delete_message(chat_id, last_message[chat_id])
        except: pass

    msg = bot.send_photo(chat_id, photo=open("assets/winter_menu.png", "rb"),
                         caption="",
                         reply_markup=markup)
    last_message[chat_id] = msg.message_id

# --- Поддержка ---
def support_section(chat_id):
    text = ("✅ Привет, ты в разделе поддержки.\n\n"
            "❗️ Если у тебя есть вопросы по покупкам или работе бота, нажми кнопку ниже, чтобы связаться со мной напрямую.\n\n"
            "⚠️ Старайся описать свою проблему максимально подробно.")
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("✅Связаться", url="https://t.me/m/_guuyZcWOTUy"),
        InlineKeyboardButton("🔙Назад", callback_data="back")
    )
    if chat_id in last_message:
        try: bot.delete_message(chat_id, last_message[chat_id])
        except: pass
    msg = bot.send_photo(chat_id, photo=open("assets/support_menu.png", "rb"),
                         caption=text,
                         reply_markup=markup)
    last_message[chat_id] = msg.message_id

# --- Разделы с картинками и кнопкой назад или кастомной разметкой ---
def show_section(chat_id, photo_name, caption="", custom_markup=None):
    if not custom_markup:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙Назад", callback_data="back"))
    else:
        markup = custom_markup

    if chat_id in last_message:
        try: bot.delete_message(chat_id, last_message[chat_id])
        except: pass
    msg = bot.send_photo(chat_id, photo=open(photo_name, "rb"),
                         caption=caption,
                         reply_markup=markup)
    last_message[chat_id] = msg.message_id

# --- Команда /start ---
@bot.message_handler(commands=['start'])
def start(message):
    main_menu(message.chat.id)

# --- Обработка кнопок ---
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id
    try: bot.delete_message(chat_id, call.message.message_id)
    except: pass

    if call.data == "telegram":
        # Кастомные кнопки для Telegram
        markup = InlineKeyboardMarkup(row_width=2)
        # Звёзды
        markup.add(
            InlineKeyboardButton("⭐️100🟰130₽", url="https://t.me/m/UFaea8-mOWY6"),
            InlineKeyboardButton("⭐️250🟰325₽", url="https://t.me/m/H0ugOYhKZGQy"),
            InlineKeyboardButton("⭐️500🟰650₽", url="https://t.me/m/bIQ0lKCWNzRi"),
            InlineKeyboardButton("⭐️1.000🟰1.300₽", url="https://t.me/m/m8mDWX3bN2Iy"),
            InlineKeyboardButton("⭐️2.500🟰3.250₽", url="https://t.me/m/4KkuPRgtOWUy"),
            InlineKeyboardButton("⭐️5.000🟰6.500₽", url="https://t.me/m/RhA9T-4FY2Fi"),
            InlineKeyboardButton("⭐️10.000🟰13.000₽", url="https://t.me/m/BUCEaewgZWQy"),
            InlineKeyboardButton("⭐️20.000🟰26.000₽", url="https://t.me/m/ZYG6py3wNzA6"),
        )
        # Premium пакеты
        markup.add(
            InlineKeyboardButton("🎁3месяца🟰1.100₽", url="https://t.me/m/AE7KCdkoZTgy"),
            InlineKeyboardButton("🎁6месяцев🟰1.450₽", url="https://t.me/m/82ISweV3NDYy"),
            InlineKeyboardButton("🎁1год🟰2.550₽", url="https://t.me/m/9DWFyVUYODky"),
            InlineKeyboardButton("🔙Назад", callback_data="back")  # кнопка справа
        )
        show_section(chat_id, "assets/telegram_menu.png", custom_markup=markup)

    elif call.data == "standoff2":
        show_section(chat_id, "assets/standoff2_menu.png", "🍯Standoff 2")
    elif call.data == "freefire":
        show_section(chat_id, "assets/freefire_menu.png", "🔥Free Fire")
    elif call.data == "ml":
        show_section(chat_id, "assets/ml_menu.png", "🗡Mobile Legends")
    elif call.data == "pubg":
        show_section(chat_id, "assets/pubg_menu.png", "😮‍💨PUBG Mobile")
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
