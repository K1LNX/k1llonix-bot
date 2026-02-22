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

    # --- Telegram раздел ---
    if call.data == "telegram":
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("⭐Telegram Stars", callback_data="stars"),
            InlineKeyboardButton("👑Premium", callback_data="premium")
        )
        markup.add(InlineKeyboardButton("🔙Назад", callback_data="back"))
        show_section(chat_id, "assets/telegram_menu.png", custom_markup=markup)

    # --- Stars раздел ---
    elif call.data == "stars":
        user_mention = f"@{call.from_user.username}" if call.from_user.username else call.from_user.first_name
        text = (f"⭐️ Покупка звёзд\n\n"
                f"🔎 Введите юзернейм пользователя, которому будем дарить звёзды:\n"
                f"— Пример: {user_mention}")
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("Купить для себя", callback_data="buy_self"),
            InlineKeyboardButton("🔙Назад", callback_data="back_to_stars")
        )
        if chat_id in last_message:
            try: bot.delete_message(chat_id, last_message[chat_id])
            except: pass
        msg = bot.send_photo(chat_id,
                             photo="https://t.me/Kill_Onix/3",
                             caption=text,
                             reply_markup=markup)
        last_message[chat_id] = msg.message_id

    # --- Купить для себя ---
    elif call.data == "buy_self":
        user_mention = f"@{call.from_user.username}" if call.from_user.username else call.from_user.first_name
        text = (f"⭐️ Покупка звёзд\n\n"
                f"👤 Получатель: {user_mention}\n\n"
                f"• Минимум: 50 Звёзд\n"
                f"• Максимум (за один заказ): 10.000 звёзд\n\n"
                f"ℹ️ Введите количество звёзд для покупки —")
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("🔙Назад", callback_data="back_to_stars")
        )
        if chat_id in last_message:
            try: bot.delete_message(chat_id, last_message[chat_id])
            except: pass
        msg = bot.send_message(chat_id, text=text, reply_markup=markup)
        last_message[chat_id] = msg.message_id

    # --- Назад в Stars раздел ---
    elif call.data == "back_to_stars":
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("⭐Telegram Stars", callback_data="stars"),
            InlineKeyboardButton("👑Premium", callback_data="premium")
        )
        markup.add(InlineKeyboardButton("🔙Назад", callback_data="back"))
        show_section(chat_id, "assets/telegram_menu.png", custom_markup=markup)

    # --- Premium раздел ---
    elif call.data == "premium":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙Назад", callback_data="back_to_telegram"))
        if chat_id in last_message:
            try: bot.delete_message(chat_id, last_message[chat_id])
            except: pass
        msg = bot.send_message(chat_id,
                               text="👑 Раздел Premium пока в разработке.",
                               reply_markup=markup)
        last_message[chat_id] = msg.message_id

    # --- Назад из Telegram раздела ---
    elif call.data == "back_to_telegram":
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("⭐Telegram Stars", callback_data="stars"),
            InlineKeyboardButton("👑Premium", callback_data="premium")
        )
        markup.add(InlineKeyboardButton("🔙Назад", callback_data="back"))
        show_section(chat_id, "assets/telegram_menu.png", custom_markup=markup)

    # --- Другие разделы ---
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
