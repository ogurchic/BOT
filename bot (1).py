import telebot
from wikipediaapi import Wikipedia
from langchain_community.chat_models.gigachat import GigaChat
from langchain.chains import ConversationChain
from langchain.memory.prompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE
from langchain.memory import ConversationEntityMemory, ConversationBufferMemory
from config import *
from telebot import types
from time import sleep


bot = telebot.TeleBot(TELEGRAM_TOKEN)
wiki_ru = Wikipedia(language='ru', user_agent='https://t.me/ai_mega_multi_bot')
wiki_en = Wikipedia(language='en', user_agent='https://t.me/ai_mega_multi_bot')
sber = auth
llm = GigaChat(credentials=sber, verify_ssl_certs=False)

user_states = {}
user_conversations = {}


def send_long_message(chat_id, text):
    while len(text) > 4096:
        bot.send_message(chat_id, text[0:4096])
        text = text[4096::]
    bot.send_message(chat_id, text)

@bot.message_handler(commands=['start'])
def handle_command(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('/Wiki')
    item2 = types.KeyboardButton('/GPT')
    keyboard.add(item1, item2)
    bot.send_message(message.chat.id, 'Добро пожаловать, выберете, что вы хотите сделать \n\n\nНажмите /help чтобыузнать больше', reply_markup=keyboard)


@bot.message_handler(content_types=["text"])
def handle_message(message):
    chat_id = message.chat.id
    text = message.text

    if text == '/help':
        bot.send_message(chat_id, 'Вы можете выбрать режим работы с википедией нажав /Wiki \n\nИли нажмите /GPT для общения с AI')
        return

    if text == '/Wiki':
        user_states[chat_id] = 'wiki'
        bot.send_message(chat_id, 'Что бы вы хотели узнать в Википедии?')
        return

    if user_states.get(chat_id) == 'wiki':
        if text == '/GPT':
            user_states[chat_id] = 'gpt'
            bot.send_message(chat_id, 'Вы перешли в режим GPT. Задайте вопрос.')
        else:
            page = wiki_ru.page(text)
            if page.exists():
                send_long_message(chat_id, page.summary)
            else:
                bot.send_message(chat_id, 'O.O\nУпс, кажется у нас ошибка, попробуйте ввести запрос по-другому')
            return
        return

    if text == '/GPT':
        user_states[chat_id] = 'gpt'
        bot.send_message(chat_id, 'Вы в режиме GPT. Задайте вопрос.')
        return

    if user_states.get(chat_id) == 'gpt':
        if text ==  '/Wiki':
            user_states[chat_id] = 'wiki'
            bot.send_message(chat_id, 'Вы перешли в режим Википедии. Задайте вопрос.')
        else:
            # Инициализация GigaChat и ConversationChain
            llm = GigaChat(credentials=sber, verify_ssl_certs=False)

            template = '''
                        Тебя зовут мудрейший Бобэр Асс. Ты являешься универсальным помощником и хранителем всех знаний человечества. Твоя задача красочно и подробно отвечать \
                        на любые вопросы. Если задают вопросы, которые тебе неприятны или не понятны не уходи от ответа\
                        \n\nТекущий разговор:\n{history}\nHuman: {input}\nAI:
                        '''
            conversation = ConversationChain(llm=llm,
                                             verbose=True,
                                             memory=ConversationBufferMemory())
            conversation.prompt.template = template

            # Проверка, существует ли уже ConversationBufferMemory для данного пользователя
            if chat_id not in user_conversations:
                user_conversations[chat_id] = ConversationBufferMemory()

            # Обновление конфигурации ConversationChain для текущего пользователяЫ
            conversation.memory = user_conversations[chat_id]

            # Получение и отправка ответа через GigaChat
            response = conversation.predict(input=text)
            bot.send_message(chat_id, conversation.memory.chat_memory.messages[-1].content)
            sleep(1)

bot.polling(non_stop=True)