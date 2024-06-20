from telebot import types, TeleBot
from telebot.asyncio_handler_backends import StatesGroup, State
from Words import Words, AddWords
from conn import TOKEN
from model import *
from decorators import *

bot = TeleBot(TOKEN)

url_bot = 't.me/netology_translator_2_bot'


@engine_decorator
def create_db(engine):
    Base.metadata.create_all(engine)

create_db()

add_words = AddWords()
add_words.add_words()




class Command:
    ADD_WORD = 'Добавить слово ➕'
    DELETE_WORD = 'Удалить слово🔙'
    NEXT = 'Другое слово ⏭'


class MyStates(StatesGroup):
    target_word = State()
    translate_word = State()
    another_words = State()


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("👋Давай)")
    markup.add(btn1)
    bot.send_message(message.from_user.id, "👋 Привет! Давай поиграем!Угадай перевод слова!", reply_markup=markup)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == '👋Давай)' or message.text == Command.NEXT:
        id_user = message.from_user.id
        user = Words(id_user)
        user.create_start_links()
        target_rus, target_eng, other_words = user.get_words()

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn_target_eng = types.KeyboardButton(target_eng)
        btn_target_other = [types.KeyboardButton(word) for word in other_words]
        next_btn = types.KeyboardButton(Command.NEXT)
        add_word_btn = types.KeyboardButton(Command.ADD_WORD)
        delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
        markup.add(btn_target_eng, *btn_target_other, next_btn, add_word_btn, delete_word_btn)
        bot.send_message(message.from_user.id, f'Как переводится "{target_rus}"?', reply_markup=markup)
        bot.set_state(message.from_user.id, MyStates.target_word, message.chat.id)
        with bot.retrieve_data(message.from_user.id) as data:
            data['target_word'] = target_rus
            data['translate_word'] = target_eng
            data['other_words'] = other_words

        bot.register_next_step_handler(message, message_reply)

    elif message.text == Command.ADD_WORD:
        words = bot.send_message(message.from_user.id, 'Введите пару слов через запятую, например "Hello, Привет"')
        bot.register_next_step_handler(words, add_words)


    elif message.text == Command.DELETE_WORD:
        words = bot.send_message(message.from_user.id, 'Введите слово, которое хотите удалить на английском языке')
        bot.register_next_step_handler(words, delete_words)



    # elif message.text == Command.NEXT:
    #     pass


@bot.message_handler(func=lambda message: True)
def message_reply(message):
    text = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        target_eng = data['translate_word']
        other_words = data['other_words']
        if text == target_eng:
            bot.send_message(message.from_user.id, "Отлично!❤ Может выберем другое слово?",
                             reply_markup=markup)
            next_btn = types.KeyboardButton(Command.NEXT)
            add_word_btn = types.KeyboardButton(Command.ADD_WORD)
            delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
            markup.add(next_btn, add_word_btn, delete_word_btn)

        elif text in other_words:
            bot.send_message(message.from_user.id, "Не верно.Попробуешь еще раз?",
                             reply_markup=markup)
            btn_target_eng = types.KeyboardButton(target_eng)
            btn_target_other = [types.KeyboardButton(word) for word in other_words]
            next_btn = types.KeyboardButton(Command.NEXT)
            add_word_btn = types.KeyboardButton(Command.ADD_WORD)
            delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
            markup.add(btn_target_eng, *btn_target_other, next_btn, add_word_btn, delete_word_btn)

            bot.register_next_step_handler(message, message_reply)

        elif text in [Command.NEXT, Command.ADD_WORD, Command.DELETE_WORD]:
            bot.register_next_step_handler(message, get_text_messages)


def add_words(message):
    id_user = message.from_user.id
    user = Words(id_user)
    list_words = message.text.split(',')
    user.add_word(list_words[0], list_words[1])
    bot.send_message(message.chat.id, 'Слово добавлено')



def delete_words(message):
    id_user = message.from_user.id
    user = Words(id_user)
    eng_word = message.text
    result_message = user.delete_word(eng_word)
    bot.send_message(message.chat.id, result_message)

bot.polling(none_stop=False)
