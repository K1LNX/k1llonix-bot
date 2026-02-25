import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request
import threading
import time

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

last_message = {}
user_state = {}
order_data = {}
order_counter = 1  # нумерация заказов
COURSE = 1.35  # курс за 1 звезду
ADMIN_ID = 8488495908  # твой Telegram ID для уведомлений о заказах

# --- Главное меню ---
def main_menu(chat_id):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("⭐Telegram", callback_data="telegram"),
        InlineKeyboardButton("🍯Standoff 2", callback_data="standoff2"),
        InlineKeyboardButton("🔥Free Fire", callback_data="freefire"),
        InlineKeyboardButton("🗡Mobile Legends", callback_data="ml"),
        InlineKeyboardButton("😮‍💨PUBG Mobile", callback_data="pubg"),
        InlineKeyboardButton("📞Поддержка", callback_data="support"),
    )
    markup.add(InlineKeyboardButton("📦 Мои заказы", callback_data="my_orders"))

    if chat_id in last_message:
        try: bot.delete_message(chat_id, last_message[chat_id])
        except: pass

    msg = bot.send_photo(chat_id,
                         photo=open("assets/winter_menu.png", "rb"),
                         caption="",
                         reply_markup=markup)
    last_message[chat_id] = msg.message_id

# --- Команда /start ---
@bot.message_handler(commands=['start'])
def start(message):
    main_menu(message.chat.id)

# --- Ввод юзернейма ---
@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == "waiting_username")
def get_username(message):
    chat_id = message.chat.id
    username = message.text.strip()

    if not username.startswith("@") or len(username) < 5:
        bot.send_message(chat_id, "❌ Юзернейм должен начинаться с @\nПопробуйте снова:")
        return

    global order_counter
    order_data[chat_id] = {"username": username, "order_id": order_counter}
    order_counter += 1
    user_state[chat_id] = "waiting_amount"

    text = (f"⭐️ Покупка звёзд\n\n"
            f"👤 Получатель: {username}\n\n"
            f"• Минимум: 50 Звёзд\n"
            f"• Максимум (за один заказ): 10.000 звёзд\n\n"
            f"💱 Курс: {COURSE} ₽ за звезду\n\n"
            f"ℹ️ Введите количество звёзд для покупки —")

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔙Назад", callback_data="stars"))
    bot.send_message(chat_id, text, reply_markup=markup)

# --- Ввод количества ---
@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == "waiting_amount")
def get_amount(message):
    chat_id = message.chat.id

    if not message.text.isdigit():
        bot.send_message(chat_id, "❌ Введите число от 50 до 10000")
        return

    amount = int(message.text)
    if amount < 50 or amount > 10000:
        bot.send_message(chat_id, "❌ Минимум 50, максимум 10.000")
        return

    data = order_data[chat_id]
    username = data["username"]
    order_id = data["order_id"]
    total = amount * COURSE
    user_state[chat_id] = "waiting_payment"

    # Скрытый номер карты через Telegram spoiler
    hidden_card = "||2204120133449765||"

    text = (f"⭐️ Заказ #{order_id}\n\n"
            f"👤 Получатель: {username}\n"
            f"⭐ Количество: {amount}\n"
            f"💰 Сумма к оплате: {total} ₽\n\n"
            f"Номер карты: {hidden_card}\n"
            f"📎 После оплаты прикрепите скрин/файл о переводе.\n"
            f"❗ Чек обязателен для быстрой обработки заказа.")

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✅ Подтвердить оплату", callback_data="confirm_order"))
    markup.add(InlineKeyboardButton("❌ Отменить заказ", callback_data="cancel_order"))
    markup.add(InlineKeyboardButton("🔙 Назад", callback_data="stars"))

    msg = bot.send_message(chat_id, text=text, reply_markup=markup)
    last_message[chat_id] = msg.message_id

# --- Обработка прикрепленного файла/чека ---
@bot.message_handler(content_types=['photo', 'document'])
def receive_payment_file(message):
    chat_id = message.chat.id

    if user_state.get(chat_id) != "waiting_payment":
        return  # если пользователь не в состоянии оплаты

    data = order_data[chat_id]
    order_id = data["order_id"]
    username = data["username"]

    # отправка чека в админ-чат
    caption = f"💳 Новый заказ #{order_id}\n👤 Получатель: {username}\nОтправлен файл/скрин оплаты"
    if message.photo:
        file_id = message.photo[-1].file_id
        bot.send_photo(ADMIN_ID, file_id, caption=caption)
    elif message.document:
        file_id = message.document.file_id
        bot.send_document(ADMIN_ID, file_id, caption=caption)

    # сообщение пользователю
    text_user = (f"✅ Ваш заказ #{order_id} принят и находится в обработке.\n"
                 f"📎 Ваш чек успешно получен.\n"
                 f"Если есть вопросы — пишите в поддержку, вам обязательно помогут.")

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📦 Мой заказ", callback_data="my_orders"))

    bot.send_message(chat_id, text=text_user, reply_markup=markup)
    user_state[chat_id] = None  # сброс состояния

# --- Обработка кнопок ---
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id
    try:
        bot.delete_message(chat_id, call.message.message_id)
    except: pass

    if call.data == "telegram":
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("⭐Telegram Stars", callback_data="stars"),
            InlineKeyboardButton("👑Premium", callback_data="premium")
        )
        markup.add(InlineKeyboardButton("🔙Назад", callback_data="back"))
        msg = bot.send_photo(chat_id,
                             photo=open("assets/telegram_menu.png", "rb"),
                             caption="",
                             reply_markup=markup)
        last_message[chat_id] = msg.message_id

    elif call.data == "stars":
        user_state[chat_id] = "waiting_username"
        user_mention = f"@{call.from_user.username}" if call.from_user.username else call.from_user.first_name
        text = (f"⭐️ Покупка звёзд\n\n"
                f"🔎 Введите юзернейм пользователя, которому будем дарить звёзды:\n"
                f"— Пример: {user_mention}")
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Купить для себя", callback_data="buy_self"))
        markup.add(InlineKeyboardButton("🔙Назад", callback_data="back_to_telegram"))
        msg = bot.send_photo(chat_id,
                             photo="https://t.me/Kill_Onix/3",
                             caption=text,
                             reply_markup=markup)
        last_message[chat_id] = msg.message_id

    elif call.data == "buy_self":
        username = f"@{call.from_user.username}" if call.from_user.username else call.from_user.first_name
        global order_counter
        order_data[chat_id] = {"username": username, "order_id": order_counter}
        order_counter += 1
        user_state[chat_id] = "waiting_amount"
        text = (f"⭐️ Покупка звёзд\n\n"
                f"👤 Получатель: {username}\n\n"
                f"• Минимум: 50 Звёзд\n"
                f"• Максимум (за один заказ): 10.000 звёзд\n\n"
                f"💱 Курс: {COURSE} ₽ за звезду\n\n"
                f"ℹ️ Введите количество звёзд для покупки —")
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙Назад", callback_data="stars"))
        bot.send_message(chat_id, text, reply_markup=markup)

    elif call.data == "premium":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙Назад", callback_data="back_to_telegram"))
        bot.send_message(chat_id,
                         "👑 Раздел Premium пока в разработке.",
                         reply_markup=markup)

    elif call.data == "back_to_telegram":
        user_state[chat_id] = None
        callback_fake = type('', (), {})()
        callback_fake.data = "telegram"
        callback_fake.message = call.message
        callback(callback_fake)
        return

    elif call.data == "back":
        user_state[chat_id] = None
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
