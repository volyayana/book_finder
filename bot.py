import telebot
from telebot import types

from telegram import tkey
from chitayGorod import ChitaiGorod as CG


bot = telebot.TeleBot(tkey)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text.lower() == '/help':
        bot.send_message(message.from_user.id, "Напиши текст для поиска книги. Используй команду /find")
    elif message.text.lower() == '/start':
        bot.send_message(message.from_user.id, "Привет! Я помогу тебе найти самую дешевую книгу по названию, автору и "
                                               "т.д. Пока ищу только в Читай городе :)")
    elif message.text.lower() == '/find':
        bot.send_message(message.from_user.id, "Введи параметы для поиска книги. Например, 'цитадель кронин'")
        bot.register_next_step_handler(message, get_search_query)
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")


def get_search_query(message):
    search_query = message.text
    cg = CG(search_query)

    @bot.callback_query_handler(func=lambda call: True)
    def callback_worker(call):
        if call.data == "yes":  # call.data это callback_data, которую мы указали при объявлении кнопки
            bot.send_message(call.message.chat.id, 'Ура! Давай попробуем найти еще одну книгу? :)')
        elif call.data == "no":
            bot.send_message(call.message.chat.id, 'Возможно, тебе подходит что-то из этого:')
            for book in cg.books[1:6]:
                bot.send_message(message.from_user.id,
                                 f"{book['name']}\n"
                                 f"Автор: {book['author']}\n"
                                 f"Стоимость: {book['price']}\n"
                                 f"{book['link']}\n")

    if cg.cheepest_book is not None:

        keyboard = types.InlineKeyboardMarkup()
        key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')
        keyboard.add(key_yes)
        key_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
        keyboard.add(key_no)

        bot.send_photo(message.chat.id, cg.cheepest_book['image_url'])  # возможно, картинку лучше не отправлять

        bot.send_message(message.from_user.id,
                         f"Самая дешевая книга по запросу:\n"
                         f"{cg.cheepest_book['name']}\n"
                         f"Автор: {cg.cheepest_book['author']}\n"
                         f"Стоимость: {cg.cheepest_book['price']}\n"
                         f"{cg.cheepest_book['link']}\n"
                         f"Это то, что ты искал?",
                         reply_markup=keyboard)
    else:
        bot.send_message(message.from_user.id,
                         "К сожалению, у меня не получилось ничего найти. Давай попробуем еще раз?")







bot.polling(none_stop=True, interval=0)