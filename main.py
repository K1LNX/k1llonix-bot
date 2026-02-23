import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

last_message = {}
user_orders = {}

PRICE_PER_STAR = 1.35

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

    msg = bot.send_photo(chat_id,
                         photo=open("assets/winter_menu.png", "rb"),
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

    msg = bot.send_photo(chat_id,
                         photo=open("assets/support_menu.png", "rb"),
                         caption=text,
                         reply_markup=markup)
    last_message[chat_id] = msg.message_id


# --- Универсальный показ разделов ---
def show_section(chat_id, photo_name, caption="", custom_markup=None):
    if not custom_markup:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙Назад", callback_data="back"))
    else:
        markup = custom_markup

    if chat_id in last_message:
        try: bot.delete_message(chat_id, last_message[chat_id])
        except: pass

    msg = bot.send_photo(chat_id,
                         photo=open(photo_name, "rb"),
                         caption=caption,
                         reply_markup=markup)
    last_message[chat_id] = msg.message_id


# --- Команда /start ---
@bot.message_handler(commands=['start'])
def start(message):
    main_menu(message.chat.id)


# --- Обработка текстового ввода (количество звёзд) ---
@bot.message_handler(func=lambda message: message.chat.id in user_orders and user_orders[message.chat.id].get("awaiting_amount"))
def process_amount(message):
    chat_id = message.chat.id

    try:
        amount = int(message.text)

        if amount < 50:
            bot.send_message(chat_id, "❌ Минимальное количество — 50 звёзд.")
            return

        if amount > 10000:
            bot.send_message(chat_id, "❌ Максимум за один заказ — 10.000 звёзд.")
            return

        total_price = round(amount * PRICE_PER_STAR, 2)

        user_orders[chat_id]["amount"] = amount
        user_orders[chat_id]["total"] = total_price
        user_orders[chat_id]["awaiting_amount"] = False

        text = (f"🧾 Подтверждение заказа\n\n"
                f"👤 Получатель: {user_orders[chat_id]['username']}\n"
                f"⭐ Количество: {amount} звёзд\n"
                f"💰 К оплате: {total_price} ₽\n\n"
                f"━━━━━━━━━━━━━━\n\n"
                f"⚠️ Проверьте данные перед оплатой.\n"
                f"После оплаты отмена невозможна.")

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("💳 Оплатить", callback_data="pay"))
        markup.add(InlineKeyboardButton("✏️ Изменить количество", callback_data="buy_self"))
        markup.add(InlineKeyboardButton("🔙 Отмена", callback_data="back"))

        msg = bot.send_message(chat_id, text=text, reply_markup=markup)
        last_message[chat_id] = msg.message_id

    except:
        bot.send_message(chat_id, "❌ Введите корректное число.")


# --- Callback обработка ---
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id

    try: bot.delete_message(chat_id, call.message.message_id)
    except: pass

    if call.data == "telegram":
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("⭐Telegram Stars", callback_data="stars"),
            InlineKeyboardButton("👑Premium", callback_data="premium")
        )
        markup.add(InlineKeyboardButton("🔙Назад", callback_data="back"))
        show_section(chat_id, "assets/telegram_menu.png", custom_markup=markup)

    elif call.data == "stars":
        user_mention = f"@{call.from_user.username}" if call.from_user.username else call.from_user.first_name

        user_orders[chat_id] = {
            "username": user_mention,
            "awaiting_amount": False
        }

        text = (f"⭐️ Покупка звёзд\n\n"
                f"👤 Получатель: {user_mention}\n\n"
                f"• Минимум: 50 Звёзд\n"
                f"• Максимум (за один заказ): 10.000 звёзд\n\n"
                f"ℹ️ Нажмите «Купить для себя»")

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Купить для себя", callback_data="buy_self"))
        markup.add(InlineKeyboardButton("🔙Назад", callback_data="back_to_telegram"))

        msg = bot.send_message(chat_id, text=text, reply_markup=markup)
        last_message[chat_id] = msg.message_id

    elif call.data == "buy_self":
        user_orders[chat_id]["awaiting_amount"] = True

        text = (f"⭐️ Покупка звёзд\n\n"
                f"👤 Получатель: {user_orders[chat_id]['username']}\n\n"
                f"• Минимум: 50 Звёзд\n"
                f"• Максимум (за один заказ): 10.000 звёзд\n\n"
                f"ℹ️ Введите количество звёзд для покупки —")

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙Назад", callback_data="stars"))

        msg = bot.send_message(chat_id, text=text, reply_markup=markup)
        last_message[chat_id] = msg.message_id

    elif call.data == "pay":
        bot.send_message(chat_id, "💳 Оплата скоро будет подключена.")
        main_menu(chat_id)

    elif call.data == "premium":
        bot.send_message(chat_id, "👑 Раздел Premium пока в разработке.")
        main_menu(chat_id)

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

    elif call.data == "back_to_telegram":
        callback(call)  # перезапуск раздела

    elif call.data == "back":
        main_menu(chat_id)

    bot.answer_callback_query(call.id)


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


WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

if __name__ == "__main__":
    bot.remove_webhook()
    if WEBHOOK_URL:
        bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
