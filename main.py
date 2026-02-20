import telebot
from telebot import types
import os

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

# Главное меню
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Telegram Premium")
    btn2 = types.KeyboardButton("Telegram Stars")
    btn3 = types.KeyboardButton("Standoff 2")
    btn4 = types.KeyboardButton("Mobile Legends")
    btn5 = types.KeyboardButton("Free Fire")
    btn6 = types.KeyboardButton("PUBG Mobile")

    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    markup.add(btn5, btn6)

    bot.send_message(message.chat.id, "💎 Выберите товар:", reply_markup=markup)


@bot.message_handler(func=lambda message: True)
def menu(message):

    if message.text == "Telegram Premium":
        bot.send_message(message.chat.id,
        "🔵 Telegram Premium\n\n"
        "3 мес — 1.100₽\n"
        "6 мес — 1.450₽\n"
        "1 год — 2.550₽")

    elif message.text == "Telegram Stars":
        bot.send_message(message.chat.id,
        "⭐ Telegram Stars\n\n"
        "1 — 1.3₽\n"
        "100 — 130₽\n"
        "250 — 325₽\n"
        "500 — 650₽\n"
        "1000 — 1300₽\n"
        "2500 — 3250₽\n"
        "5000 — 6500₽\n"
        "10000 — 13000₽")

    elif message.text == "Standoff 2":
        bot.send_message(message.chat.id,
        "💎 Standoff 2\n\n"
        "Global:\n"
        "100 — 135₽\n"
        "500 — 545₽\n"
        "1000 — 985₽\n"
        "3000 — 2180₽\n\n"
        "RU:\n"
        "1 — 0.63₽\n"
        "1000 — 630₽\n"
        "3000 — 1890₽\n"
        "5000 — 3150₽\n"
        "10000 — 6300₽")

    elif message.text == "Mobile Legends":
        bot.send_message(message.chat.id,
        "💎 Mobile Legends\n\n"
        "35 — 58₽\n"
        "55 — 92₽\n"
        "165 — 268₽\n"
        "275 — 460₽\n"
        "565 — 850₽\n"
        "1155 — 1850₽\n"
        "1765 — 2405₽\n"
        "2975 — 4000₽\n"
        "6000 — 8000₽")

    elif message.text == "Free Fire":
        bot.send_message(message.chat.id,
        "🎮 Free Fire Max\n\n"
        "105 — 67₽\n"
        "326 — 213₽\n"
        "546 — 350₽\n"
        "1113 — 700₽\n"
        "2398 — 1370₽\n"
        "6160 — 3350₽")

    elif message.text == "PUBG Mobile":
        bot.send_message(message.chat.id,
        "🏆 PUBG Mobile\n\n"
        "60 — 80₽\n"
        "325 — 400₽\n"
        "660 — 800₽\n"
        "1800 — 2000₽\n"
        "3850 — 3950₽\n"
        "8100 — 7900₽")

print("Bot started...")
bot.infinity_polling()
