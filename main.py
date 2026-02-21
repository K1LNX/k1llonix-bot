import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request

# Получаем токен из переменной окружения
TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

# --- Команда /start ---
@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("💰 Пополнить", callback_data="pay"),
        InlineKeyboardButton("👤 Профиль", callback_data="profile")
    )
    bot.send_message(message.chat.id, "Выбери действие:", reply_markup=markup)

# --- Обработка inline кнопок ---
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "pay":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id,
