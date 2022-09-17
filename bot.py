import math

import telebot
from telebot import types

import config
from chitayGorod import ChitaiGorod
from Labirint import Labirint

bot = telebot.TeleBot(config.telegram_key)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text.lower() == '/help':
        bot.send_message(message.from_user.id, "Напиши текст для поиска книги. Используй команду /find")
    elif message.text.lower() == '/start':
        bot.send_message(message.from_user.id, "Привет! Я помогу тебе найти самую дешевую книгу по названию, автору и "
                                               "т.д. Пока ищу только в Читай городе и Лабиринте :)")
    elif message.text.lower() == '/find':
        bot.send_message(message.from_user.id, "Введи параметы для поиска книги. Например, 'цитадель кронин'")
        bot.register_next_step_handler(message, get_search_query)
    else:
        # bot.register_next_step_handler(message, get_search_query)
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")


def get_search_query(message):
    bot.send_message(message.from_user.id, "Уже ищу :)")
    search_query = message.text
    cg = ChitaiGorod(search_query)
    l = Labirint(search_query)
    books = sorted(cg.books + l.books, key=lambda x: x['price'])

    @bot.callback_query_handler(func=lambda call: True)
    def callback_worker(call):
        bot.edit_message_text(get_book_message(books, call.data, config.articles_per_page),
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=keyboard,
                              disable_web_page_preview=True)

    if books is not None:

        keyboard = types.InlineKeyboardMarkup()

        for i in range(0, math.ceil(len(books) / config.articles_per_page)):
            key_button = types.InlineKeyboardButton(text=str(i), callback_data=str(i))
            keyboard.add(key_button)

        bot.send_message(message.from_user.id,
                         get_book_message(books, 0, config.articles_per_page),
                         reply_markup=keyboard,
                         disable_web_page_preview=True)
    else:
        bot.send_message(message.from_user.id,
                         "К сожалению, у меня не получилось ничего найти. Давай попробуем еще раз?")


def get_book_message(books, offset, limit):
    message = ''
    first_id = int(offset) * limit

    for book in books[first_id:first_id + limit]:
        message += (
            f"{book['name']}\n"
            f"Автор: {book['author']}\n"
            f"Цена: {book['price']}\n"
            f"Магазин: {book['store']}\n"
            f"{book['link']}\n"
            f"\n"
        )
    return message


bot.polling(none_stop=True, interval=0)
