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
PAYMENT_CARD = "2204120133449765"  # Твоя карта для оплат

# --- Состояния ---
last_message = {}
user_state = {}
orders = {}
order_counter = 1

# --- Каталог товаров ---
catalog = [
    {"name": "⭐Telegram Stars", "min": 50, "max": 10000, "course": 1.35, "id": "stars", "image": "assets/stars.png"},
    {"name": "👑Premium", "min": 1, "max": 100, "course": 100, "id": "premium", "image": "assets/premium.png"},
    {"name": "🍯Standoff 2", "min": 10, "max": 10000, "course": 0.5, "id": "standoff2", "image": "assets/standoff2.png"},
    {"name": "🔥Free Fire", "min": 10, "max": 10000, "course": 0.5, "id": "freefire", "image": "assets/freefire.png"},
    {"name": "🗡Mobile Legends", "min": 10, "max": 10000, "course": 0.5, "id": "ml", "image": "assets/ml.png"},
    {"name": "😮‍💨PUBG Mobile", "min": 10, "max": 10000, "course": 0.5, "id": "pubg", "image": "assets/pubg.png"}
]

# --- Главное меню ---
def main_menu(chat_id):
    markup = InlineKeyboardMarkup(row_width=2)
    for item in catalog:
        markup.add(InlineKeyboardButton(item["name"], callback_data=f"buy_{item['id']}"))
    markup.add(InlineKeyboardButton("📦 Мои заказы", callback_data="my_orders"))
    markup.add(InlineKeyboardButton("📞 Поддержка", callback_data="support"))

    if chat_id in last_message:
        try: bot.delete_message(chat_id, last_message[chat_id])
        except: pass

    msg = bot.send_photo(chat_id, photo=open("assets/winter_menu.png", "rb"), caption="Выберите товар:", reply_markup=markup)
    last_message[chat_id] = msg.message_id

# --- /start ---
@bot.message_handler(commands=['start'])
def start(message):
    main_menu(message.chat.id)

# --- Выбор товара ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def buy_item(call):
    chat_id = call.message.chat.id
    item_id = call.data.split("_")[1]
    item = next((x for x in catalog if x["id"] == item_id), None)
    if not item:
        bot.send_message(chat_id, "❌ Товар не найден.")
        return

    user_state[chat_id] = {"step": "waiting_username", "item": item}
    bot.send_message(chat_id, f"🔎 Введите юзернейм получателя (начинается с @):")

# --- Ввод юзернейма ---
@bot.message_handler(func=lambda m: user_state.get(m.chat.id, {}).get("step") == "waiting_username")
def username_input(message):
    chat_id = message.chat.id
    username = message.text.strip()
    if not username.startswith("@"):
        bot.send_message(chat_id, "❌ Юзернейм должен начинаться с @")
        return

    item = user_state[chat_id]["item"]
    user_state[chat_id] = {"step": "waiting_amount", "item": item, "username": username}
    bot.send_message(chat_id, f"ℹ️ Введите количество ({item['min']}–{item['max']}):")

# --- Ввод количества ---
@bot.message_handler(func=lambda m: user_state.get(m.chat.id, {}).get("step") == "waiting_amount")
def amount_input(message):
    chat_id = message.chat.id
    state = user_state[chat_id]
    item = state["item"]
    username = state["username"]

    if not message.text.isdigit():
        bot.send_message(chat_id, "❌ Введите число")
        return
    amount = int(message.text)
    if amount < item["min"] or amount > item["max"]:
        bot.send_message(chat_id, f"❌ Минимум {item['min']}, максимум {item['max']}")
        return

    global order_counter
    order_id = order_counter
    order_counter += 1

    total = round(amount * item["course"], 2)
    order = {
        "order_id": order_id,
        "username": username,
        "item": item["name"],
        "amount": amount,
        "total": total,
        "status": "Ожидает чек"
    }
    if chat_id not in orders:
        orders[chat_id] = []
    orders[chat_id].append(order)

    user_state[chat_id] = None

    text = (f"⭐️ Заказ #{order_id}\n"
            f"👤 Получатель: {username}\n"
            f"📦 Товар: {item['name']}\n"
            f"⭐ Количество: {amount}\n"
            f"💰 Сумма: {total} ₽\n\n"
            f"Номер карты: {PAYMENT_CARD}\n"
            f"📎 Прикрепите скрин или файл чека оплаты.\n"
            f"❗ После отправки чек автоматически формирует заказ.")

    bot.send_message(chat_id, text)

# --- Обработка чеков (файлы) ---
@bot.message_handler(content_types=['photo', 'document'])
def handle_receipt(message):
    chat_id = message.chat.id
    if chat_id not in orders or not orders[chat_id]:
        bot.send_message(chat_id, "❌ Нет активного заказа.")
        return
    last_order = orders[chat_id][-1]
    if last_order["status"] != "Ожидает чек":
        bot.send_message(chat_id, "❌ Заказ уже обработан.")
        return

    last_order["status"] = "В обработке"
    bot.send_message(chat_id, f"✅ Заказ #{last_order['order_id']} принят в обработку. Администратор скоро его обработает.")

    # Уведомление админу
    bot.send_message(ADMIN_ID,
                     f"📌 Новый заказ #{last_order['order_id']} от {last_order['username']}\n"
                     f"Товар: {last_order['item']}\n"
                     f"Количество: {last_order['amount']}\n"
                     f"Сумма: {last_order['total']} ₽\n\n"
                     f"Статус: {last_order['status']}")

# --- Показ заказов пользователя ---
def show_user_orders(chat_id, page=1):
    user_orders = orders.get(chat_id, [])
    if not user_orders:
        bot.send_message(chat_id, "📦 У вас нет заказов.")
        return

    per_page = 5
    total_pages = (len(user_orders)+per_page-1)//per_page
    start = (page-1)*per_page
    end = start+per_page
    markup = InlineKeyboardMarkup()
    text = ""
    for o in user_orders[start:end]:
        text += f"⭐️ Заказ #{o['order_id']}\nТовар: {o['item']}\nКоличество: {o['amount']}\nСумма: {o['total']} ₽\nСтатус: {o['status']}\n\n"

    if page>1:
        markup.add(InlineKeyboardButton("⬅️ Назад", callback_data=f"user_page_{page-1}"))
    if end < len(user_orders):
        markup.add(InlineKeyboardButton("➡️ Далее", callback_data=f"user_page_{page+1}"))
    bot.send_message(chat_id, text=text, reply_markup=markup)

# --- Админ панель ---
def show_admin_panel(chat_id, page=1):
    all_orders = []
    for u_orders in orders.values():
        all_orders.extend(u_orders)
    if not all_orders:
        bot.send_message(chat_id, "📦 Заказов нет")
        return
    per_page = 5
    total_pages = (len(all_orders)+per_page-1)//per_page
    start = (page-1)*per_page
    end = start+per_page

    for o in all_orders[start:end]:
        text = f"⭐️ Заказ #{o['order_id']}\nПользователь: {o['username']}\nТовар: {o['item']}\nКоличество: {o['amount']}\nСумма: {o['total']} ₽\nСтатус: {o['status']}"
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("В обработке", callback_data=f"admin_status_{o['order_id']}_processing"),
            InlineKeyboardButton("Зачислено", callback_data=f"admin_status_{o['order_id']}_credited"),
            InlineKeyboardButton("Удалить", callback_data=f"admin_delete_{o['order_id']}")
        )
        bot.send_message(chat_id, text, reply_markup=markup)

    nav_markup = InlineKeyboardMarkup()
    if page>1:
        nav_markup.add(InlineKeyboardButton("⬅️ Назад", callback_data=f"admin_page_{page-1}"))
    if end < len(all_orders):
        nav_markup.add(InlineKeyboardButton("➡️ Далее", callback_data=f"admin_page_{page+1}"))
    nav_markup.add(InlineKeyboardButton("🔙 Назад", callback_data="back"))
    bot.send_message(chat_id, "Навигация по страницам:", reply_markup=nav_markup)

# --- /admin ---
@bot.message_handler(commands=['admin'])
def admin_command(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ Доступ запрещён")
        return
    show_admin_panel(message.chat.id)

# --- Callback ---
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    try: bot.delete_message(chat_id, call.message.message_id)
    except: pass

    # Пользовательские страницы
    if call.data=="my_orders":
        show_user_orders(chat_id, page=1)
    elif call.data.startswith("user_page_"):
        page = int(call.data.split("_")[2])
        show_user_orders(chat_id, page)
    # Админ
    elif call.data.startswith("admin_page_"):
        if chat_id!=ADMIN_ID:
            bot.answer_callback_query(call.id,"❌ Доступ запрещён")
            return
        page = int(call.data.split("_")[2])
        show_admin_panel(chat_id,page)
    elif call.data.startswith("admin_status_"):
        if call.from_user.id != ADMIN_ID:
            bot.answer_callback_query(call.id,"❌ Доступ запрещён")
            return
        parts = call.data.split("_")
        order_id = int(parts[2])
        new_status = "В обработке" if parts[3]=="processing" else "Зачислено"
        for u_id,u_orders in orders.items():
            for o in u_orders:
                if o['order_id']==order_id:
                    o['status']=new_status
                    bot.send_message(u_id,f"ℹ️ Статус вашего заказа #{order_id} изменён: {new_status}")
                    bot.answer_callback_query(call.id,"Статус обновлён")
                    break
    elif call.data.startswith("admin_delete_"):
        if call.from_user.id != ADMIN_ID:
            bot.answer_callback_query(call.id,"❌ Доступ запрещён")
            return
        order_id = int(call.data.split("_")[2])
        for u_id,u_orders in orders.items():
            for o in u_orders:
                if o['order_id']==order_id:
                    u_orders.remove(o)
                    bot.send_message(u_id,f"❌ Ваш заказ #{order_id} удалён администратором")
                    bot.answer_callback_query(call.id,"Заказ удалён")
                    break
    elif call.data=="back":
        main_menu(chat_id)

# --- Webhook ---
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK",200

@app.route("/")
def index():
    return "Bot is running!"

WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
if __name__=="__main__":
    bot.remove_webhook()
    if WEBHOOK_URL:
        bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)))
