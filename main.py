import telebot
from wikipediaapi import Wikipedia
from telebot import types
from config import *

bot = telebot.TeleBot(TELEGRAM_TOKEN)

wiki_ru = Wikipedia(
    language='ru',
    user_agent='https://t.me/ai_mega_multi_bot'
)
wiki_en = Wikipedia(
    language='en',
    user_agent='https://t.me/ai_mega_multi_bot'
)


# Словарь для отслеживания состояния каждого пользователя
user_states = {}


def send_long_message(chat_id, text):
    while len(text) > 4096:
        bot.send_message(chat_id, text[0:4096])
        text = text[4096::]
    bot.send_message(chat_id, text)

@bot.message_handler(commands=['start'])
def handle_command(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('Wiki')
    item2 = types.KeyboardButton('GPT')
    keyboard.add(item1, item2)
    bot.send_message(message.chat.id,   'Добро пожаловать, выберете, что вы хотите сделать \n\n\nНажмите /help чтобыузнать больше', reply_markup=keyboard)

@bot.message_handler(content_types=["text"])
def handle_message(message):
    chat_id = message.chat.id
    text = message.text

    # Если пользователь нажал на кнопку "Wiki", переводим его в состояние "wiki"
    if text == 'Wiki':
        user_states[chat_id] = 'wiki'
        bot.send_message(chat_id, 'Что бы вы хотели узнать в Википедии?')
        return

    # Если пользователь в состоянии "wiki", выполняем поиск в Википедии
    if user_states.get(chat_id) == 'wiki':
        page = wiki_ru.page(text)
        if page.exists():
            send_long_message(chat_id, page.summary)
        else:
            bot.send_message(chat_id, 'O.O\nУпс, кажется у нас ошибка, попробуйте ввести запрос по-другому')
        return
    # Если пользователь нажал на кнопку "GPT", переводим его в состояние "gpt"
    if text == 'GPT':
        user_states[chat_id] = 'gpt'
        bot.send_message(chat_id, 'Что бы вы хотели узнать в GPT?')
        return
    if user_states.get(chat_id) == 'gpt':
        bot.send_message(chat_id, 'GPT не работает, пока что')
        return

# Если пользователь нажал на кнопку "Help", переводим его в состояние "help"
@bot.message_handler(content_types=["text"])
def handle_message(message):
    chat_id = message.chat.id
    text = message.text
    if text == 'Help':
        user_states[chat_id] = 'help'
        bot.send_message(chat_id, 'Вы можете использовать бота для поиска информации в Википедии и GPT-3')
        return
# если пользователь нажал кнопку яндекс GPT, переводим его в состояние яндекс GPT
@bot.message_handler(content_types=["text"])
def handle_message(message):
    chat_id = message.chat.id
    text = message.text
    if text == 'Яндекс GPT':
        user_states[chat_id] = 'yandex_gpt'
        bot.send_message(chat_id, 'Что бы вы хотели узнать в Яндекс GPT?')
        return


if __name__ == '__main__':
    bot.polling(True)
