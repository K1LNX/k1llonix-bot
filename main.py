import os  
import telebot  
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto  
from flask import Flask, request  
import threading  
import time  
  
TOKEN = os.environ.get("BOT_TOKEN")  
bot = telebot.TeleBot(TOKEN)  
app = Flask(__name__)  
  
ADMIN_ID = 8488495908  
  
last_message = {}  
user_state = {}  
order_data = {}  
orders = {}  
order_counter = 1  # нумерация заказов  
COURSE = 1.35  # курс за 1 звезду  
  
# --- Главное меню ---  
def main_menu(chat_id):  
    markup = InlineKeyboardMarkup(row_width=2)  
    markup.add(  
        InlineKeyboardButton("⭐Telegram Stars", callback_data="stars"),  
        InlineKeyboardButton("👑Premium", callback_data="premium"),  
        InlineKeyboardButton("🍯Standoff 2", callback_data="standoff2"),  
        InlineKeyboardButton("🔥Free Fire", callback_data="freefire"),  
        InlineKeyboardButton("🗡Mobile Legends", callback_data="ml"),  
        InlineKeyboardButton("😮‍💨PUBG Mobile", callback_data="pubg"),  
    )  
    markup.add(InlineKeyboardButton("📞 Поддержка", callback_data="support"))  
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
    order_id = order_counter  
    order_counter += 1  
  
    order_data[chat_id] = {"username": username, "order_id": order_id, "status": "Ввод количества"}  
    user_state[chat_id] = "waiting_amount"  
  
    text = (f"⭐️ Покупка звёзд\n\n"  
            f"👤 Получатель: {username}\n"  
            f"• Минимум: 50 Звёзд\n"  
            f"• Максимум (за один заказ): 10.000 звёзд\n"  
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
  
    order_data[chat_id].update({"amount": amount, "total": total, "status": "Ожидает чек"})  
    if chat_id not in orders:  
        orders[chat_id] = []  
    orders[chat_id].append(order_data[chat_id])  
  
    user_state[chat_id] = None  
  
    text = (f"⭐️ Заказ #{order_id}\n\n"  
            f"👤 Получатель: {username}\n"  
            f"⭐ Количество: {amount}\n"  
            f"💰 Сумма к оплате: {total} ₽\n\n"  
            f"Номер карты: 2204120133449765\n"  
            f"📎 После оплаты прикрепите скрин/файл о переводе.\n"  
            f"❗ Чек обязателен для быстрой обработки заказа.")  
  
    markup = InlineKeyboardMarkup()  
    markup.add(InlineKeyboardButton("✅ Оплатил", callback_data=f"paid_{order_id}"))  
    markup.add(InlineKeyboardButton("❌ Отменить", callback_data=f"cancel_{order_id}"))  
    markup.add(InlineKeyboardButton("📦 Мой заказ", callback_data="my_orders"))  
    markup.add(InlineKeyboardButton("🔙 Назад", callback_data="stars"))  
  
    bot.send_message(chat_id, text=text, reply_markup=markup)  
  
    threading.Thread(target=reminder_timer, args=(chat_id, order_id), daemon=True).start()  
  
def reminder_timer(chat_id, order_id):  
    time.sleep(15 * 60)  
    for order in orders.get(chat_id, []):  
        if order["order_id"] == order_id and order["status"] == "Ожидает чек":  
            bot.send_message(chat_id, f"⏳ Ваш заказ #{order_id} ждёт прикрепления чека.\n"  
                                      "📝 Пожалуйста, прикрепите файл для ускоренной обработки.")  
  
# --- Админ-панель ---  
def show_admin_orders(chat_id, page=1):  
    if chat_id != ADMIN_ID:  
        bot.send_message(chat_id, "❌ Доступ запрещён.")  
        return  
  
    all_orders = []  
    for user_orders in orders.values():  
        all_orders.extend(user_orders)  
      
    if not all_orders:  
        bot.send_message(chat_id, "📦 Заказов пока нет.")  
        return  
  
    per_page = 5  
    total_pages = (len(all_orders) + per_page - 1) // per_page  
    start = (page - 1) * per_page  
    end = start + per_page  
    current_orders = all_orders[start:end]  
  
    for o in current_orders:  
        text = (f"⭐️ Заказ #{o['order_id']}\n"  
                f"👤 Пользователь: {o['username']}\n"  
                f"⭐ Количество: {o.get('amount','—')}\n"  
                f"💰 Сумма: {o.get('total','—')} ₽\n"  
                f"Статус: {o['status']}")  
        markup = InlineKeyboardMarkup()  
        markup.add(  
            InlineKeyboardButton("В обработке", callback_data=f"admin_status_{o['order_id']}_processing"),  
            InlineKeyboardButton("Зачислено", callback_data=f"admin_status_{o['order_id']}_credited"),  
            InlineKeyboardButton("Удалить", callback_data=f"admin_delete_{o['order_id']}")  
        )  
        bot.send_message(chat_id, text, reply_markup=markup)  
  
    nav_markup = InlineKeyboardMarkup()  
    if page > 1:  
        nav_markup.add(InlineKeyboardButton("⬅️ Назад", callback_data=f"admin_page_{page-1}"))  
    if page < total_pages:  
        nav_markup.add(InlineKeyboardButton("➡️ Далее", callback_data=f"admin_page_{page+1}"))  
    nav_markup.add(InlineKeyboardButton("🔙 Назад", callback_data="back"))  
    bot.send_message(chat_id, "Навигация по страницам:", reply_markup=nav_markup)  
  
# --- Обработка кнопок ---  
@bot.callback_query_handler(func=lambda call: True)  
def callback(call):  
    chat_id = call.message.chat.id  
    try: bot.delete_message(chat_id, call.message.message_id)  
    except: pass  
  
    if call.data == "stars":  
        user_state[chat_id] = "waiting_username"  
        user_mention = f"@{call.from_user.username}" if call.from_user.username else call.from_user.first_name  
        text = (f"⭐️ Покупка звёзд\n\n"  
                f"🔎 Введите юзернейм пользователя, которому будем дарить звёзды:\n"  
                f"— Пример: {user_mention}")  
        markup = InlineKeyboardMarkup()  
        markup.add(InlineKeyboardButton("Купить для себя", callback_data="buy_self"))  
        markup.add(InlineKeyboardButton("🔙Назад", callback_data="back_to_telegram"))  
        msg = bot.send_photo(chat_id, photo="https://t.me/Kill_Onix/3", caption=text, reply_markup=markup)  
        last_message[chat_id] = msg.message_id  
  
    elif call.data == "buy_self":  
        username = f"@{call.from_user.username}" if call.from_user.username else call.from_user.first_name  
        global order_counter  
        order_id = order_counter  
        order_counter += 1  
        order_data[chat_id] = {"username": username, "order_id": order_id, "status": "Ввод количества"}  
        user_state[chat_id] = "waiting_amount"  
  
        text = (f"⭐️ Покупка звёзд\n\n"  
                f"👤 Получатель: {username}\n"  
                f"• Минимум: 50 Звёзд\n"  
                f"• Максимум (за один заказ): 10.000 звёзд\n"  
                f"💱 Курс: {COURSE} ₽ за звезду\n\n"  
                f"ℹ️ Введите количество звёзд для покупки —")  
        markup = InlineKeyboardMarkup()  
        markup.add(InlineKeyboardButton("🔙Назад", callback_data="stars"))  
        bot.send_message(chat_id, text, reply_markup=markup)  
  
    elif call.data.startswith("paid_"):  
        order_id = int(call.data.split("_")[1])  
        for order in orders.get(chat_id, []):  
            if order["order_id"] == order_id:  
                order["status"] = "В обработке"  
                bot.send_message(chat_id, f"✅ Заказ #{order_id} принят в обработку. После зачисления вы получите уведомление.\n"  
                                          "Если есть вопросы, пишите в поддержку.")  
  
    elif call.data.startswith("cancel_"):  
        order_id = int(call.data.split("_")[1])  
        orders[chat_id] = [o for o in orders.get(chat_id, []) if o["order_id"] != order_id]  
        bot.send_message(chat_id, f"❌ Заказ #{order_id} отменён.")  
  
    elif call.data == "my_orders":  
        show_orders(chat_id, page=1)  
  
    elif call.data.startswith("page_"):  
        _, page = call.data.split("_")  
        show_orders(chat_id, int(page))  
  
    elif call.data.startswith("admin_status_"):  
        if call.from_user.id != ADMIN_ID:  
            bot.answer_callback_query(call.id, "❌ Доступ запрещён")  
            return  
        parts = call.data.split("_")  
        order_id = int(parts[2])  
        new_status = "В обработке" if parts[3] == "processing" else "Зачислено"  
        for user_id, user_orders in orders.items():  
            for o in user_orders:  
                if o["order_id"] == order_id:  
                    o["status"] = new_status  
                    bot.send_message(user_id, f"ℹ️ Статус вашего заказа #{order_id} изменён на: {new_status}")  
                    bot.answer_callback_query(call.id, f"Статус заказа #{order_id} обновлён")  
                    break  
  
    elif call.data.startswith("admin_delete_"):  
        if call.from_user.id != ADMIN_ID:  
            bot.answer_callback_query(call.id, "❌ Доступ запрещён")  
            return  
        order_id = int(call.data.split("_")[2])  
        for user_id, user_orders in orders.items():  
            for o in user_orders:  
                if o["order_id"] == order_id:  
                    user_orders.remove(o)  
                    bot.send_message(user_id, f"❌ Ваш заказ #{order_id} был удалён администратором")  
                    bot.answer_callback_query(call.id, f"Заказ #{order_id} удалён")  
                    break  
  
    elif call.data == "back_to_telegram":  
        callback_fake = type('', (), {})()  
        callback_fake.data = "stars"  
        callback_fake.message = call.message  
        callback(callback_fake)  
        return  
  
    elif call.data == "back":  
        main_menu(chat_id)  
  
    elif call.data.startswith("admin_page_"):  
        if chat_id != ADMIN_ID:  
            bot.answer_callback_query(call.id, "❌ Доступ запрещён")  
            return  
        _, page = call.data.split("_")  
        show_admin_orders(chat_id, int(page))  
  
    bot.answer_callback_query(call.id)  
  
# --- Показ заказов пользователя с постраничкой ---  
def show_orders(chat_id, page=1):  
    user_orders = orders.get(chat_id, [])  
    if not user_orders:  
        bot.send_message(chat_id, "📦 У вас нет заказов.")  
        return  
  
    per_page = 5  
    total_pages = (len(user_orders) + per_page - 1) // per_page  
    start = (page - 1) * per_page  
    end = start + per_page  
    current_orders = user_orders[start:end]  
  
    text = ""  
    for o in current_orders:  
        text += (f"⭐️ Заказ #{o['order_id']}\n"  
                 f"👤 Получатель: {o['username']}\n"  
                 f"⭐ Количество: {o.get('amount', '—')}\n"  
                 f"💰 Сумма к оплате: {o.get('total', '—')} ₽\n"  
                 f"Статус: {o['status']}\n\n")  
  
    markup = InlineKeyboardMarkup()  
    if page > 1:  
        markup.add(InlineKeyboardButton("⬅️ Назад", callback_data=f"page_{page-1}"))  
    if end < len(user_orders):  
        markup.add(InlineKeyboardButton("➡️ Далее", callback_data=f"page_{page+1}"))  
    markup.add(InlineKeyboardButton("🔙 Назад", callback_data="back"))  
  
    bot.send_message(chat_id, text, reply_markup=markup)  
  
# --- Команда /admin для вызова админ-панели ---  
@bot.message_handler(commands=['admin'])  
def admin_panel(message):  
    if message.from_user.id != ADMIN_ID:  
        bot.send_message(message.chat.id, "❌ Доступ запрещён.")  
        return  
    show_admin_orders(message.chat.id, page=1)  
  
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
