import os
import telebot
import os

from dotenv import load_dotenv
load_dotenv()

bot = telebot.TeleBot(os.environ['BOT_TOKEN'])



waiting_users = []
active_chats = {}  # user_id: partner_id

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    if user_id in active_chats:
        bot.send_message(user_id, "Ты уже в чате.")
        return

    if waiting_users:
        partner_id = waiting_users.pop(0)
        active_chats[user_id] = partner_id
        active_chats[partner_id] = user_id
        bot.send_message(user_id, "🔗 Вы подключены к собеседнику.")
        bot.send_message(partner_id, "🔗 Вы подключены к собеседнику.")
    else:
        waiting_users.append(user_id)
        bot.send_message(user_id, "⏳ Ожидание собеседника...")

@bot.message_handler(commands=['stop'])
def stop(message):
    user_id = message.chat.id
    partner_id = active_chats.pop(user_id, None)
    if partner_id:
        active_chats.pop(partner_id, None)
        bot.send_message(partner_id, "❌ Собеседник покинул чат.")
        bot.send_message(user_id, "❌ Вы покинули чат.")
    elif user_id in waiting_users:
        waiting_users.remove(user_id)
        bot.send_message(user_id, "⛔ Вы вышли из очереди.")
    else:
        bot.send_message(user_id, "❗ Вы не в чате и не в очереди.")

@bot.message_handler(func=lambda m: True)
def relay(message):
    user_id = message.chat.id
    partner_id = active_chats.get(user_id)
    if partner_id:
        bot.send_message(partner_id, message.text)
    else:
        bot.send_message(user_id, "💬 Напишите /start чтобы найти собеседника.")

bot.polling()
