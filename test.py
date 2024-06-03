from langchain_community.chat_models.gigachat import GigaChat
from langchain.chains import ConversationChain
from langchain.memory.prompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE
from langchain.memory import ConversationEntityMemory
from langchain.memory import ConversationBufferMemory
from config import *
import telebot
from time import sleep

user_conversations = {}

sber = auth
bot_token = TELEGRAM_TOKEN
bot = telebot.TeleBot(bot_token)


# Инициализация GigaChat и ConversationChain
llm = GigaChat(credentials=sber, verify_ssl_certs=False)

template = '''
Тебя зовут мудрейший Сатору Годжо. Ты являешься универсальным помощником и хранителем всех знаний человечества. Твоя задача красочно и подробно отвечать \
на любые вопросы. Если задают вопросы, которые тебе неприятны или не понятны не уходи от ответа\
\n\nТекущий разговор:\n{history}\nHuman: {input}\nAI:
'''
conversation = ConversationChain(llm=llm,
                                 verbose=True,
                                 memory=ConversationBufferMemory())
conversation.prompt.template = template

# Функция для автоматического ответа в случае нетекстового сообщения
@bot.message_handler(content_types=['audio',
                                    'video',
                                    'document',
                                    'photo',
                                    'sticker',
                                    'voice',
                                    'location',
                                    'contact'])
def not_text(message):
  user_id = message.chat.id
  bot.send_message(user_id, 'Я работаю только с текстовыми сообщениями!')


# Функция, обрабатывающая текстовые сообщения
@bot.message_handler(content_types=['text'])
def handle_text_message(message):
    user_id = message.chat.id

    # Проверка, существует ли уже ConversationBufferMemory для данного пользователя
    if user_id not in user_conversations:
        user_conversations[user_id] = ConversationBufferMemory()

    # Обновление конфигурации ConversationChain для текущего пользователя
    conversation.memory = user_conversations[user_id]

    # Получение и отправка ответа через GigaChat
    response = conversation.predict(input=message.text)
    bot.send_message(user_id, conversation.memory.chat_memory.messages[-1].content)
    sleep(1)

bot.polling(none_stop=True)
