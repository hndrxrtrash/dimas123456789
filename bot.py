from db import db, text_table
import telebot
import pdfkit
from random import randint
import os
import codecs

bot = telebot.TeleBot('378057239:AAGR5tIXwUuRJVI5iBw-YGcxMRmR-9hBwiY')


@bot.message_handler(commands=['start'])
def start(message):
    with db.connect() as conn:
        stmt = text_table.select().where(text_table.c.user == message.from_user.id)
        result = conn.execute(stmt)
        dim = False
        for i in result:
            dim = i
        if not dim:
            stmt = text_table.insert().values(user=message.from_user.id,
            text="<!doctype html> <head> " \
                 "<style> body { font-size: 20pt; } " \
                 "</style> <meta charset='utf-8'> " \
                 "</head> <body>"
            )
            conn.execute(stmt)
            print("YES")
        else:
            print('NO')
    help(message)


@bot.message_handler(commands=['help'])
def help(message):
    mess = "Send text or image to add this to your PDF file\n" \
           "Press OK if you are ready to download your file\n" \
           "Start your text with '#' (no quotes) to add header"
    bot.send_message(message.from_user.id, mess)


@bot.message_handler(content_types=['photo'])
def image_handler(message):
    file_info = bot.get_file(message.photo[2].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    chars = 'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890'
    rand_string = ''
    for i in range(0, 6):
        rand_string += chars[randint(0, len(chars) - 1)]
    filename = str(message.from_user.id) + '_' + rand_string
    with open('images/' + filename + '.jpg', 'wb') as f:
        f.write(downloaded_file)
    with db.connect() as conn:
        path = os.getcwd().encode('utf-8').decode('utf-8').replace('\\', '/')
        stmt = text_table.update().where(
            text_table.c.user == message.from_user.id
        ).values(
            text=text_table.c.text + '<img src="' + path + '/images/' + filename + '.jpg">'
        )
        conn.execute(stmt)
    markup = telebot.types.ReplyKeyboardMarkup(True, False)
    markup.row('OK')
    bot.send_message(message.from_user.id, 'Image has been saved\n', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def text_handler(message):
    if message.text == 'OK':
        html = ''
        with db.connect() as conn:
            stmt = text_table.select().where(text_table.c.user == message.from_user.id)
            result_set = conn.execute(stmt)
            for i in result_set:
                html = i[2]
            stmt = text_table.update().where(
                text_table.c.user == message.from_user.id
            ).values(text='<!doctype html> <head> <style> body { font-size: 20pt; } </style> <meta charset="utf-8"> </head> <body>')
            conn.execute(stmt)
        print(html)
        pdfkit.from_string(html, 'pdfs/' + str(message.from_user.id) + '.pdf')
        with codecs.open('pdfs/' + str(message.from_user.id) + '.pdf') as f:
            markup = telebot.types.ReplyKeyboardRemove()
            bot.send_message(message.from_user.id, "Your PDF file:", reply_markup=markup)
            bot.send_document(message.from_user.id, f)
        for filename in os.listdir('images'):
            name = filename.split('_')[0]
            if name == str(message.from_user.id):
                os.remove('images/' + filename)
        os.remove('pdfs/' + str(message.from_user.id) + '.pdf')
    elif message.text != "OK":
        if message.text[0] == '#':
            text = '<h1>' + message.text[1:] + '</h1>'
        else:
            text = '<p>' + message.text + '</p>'
        with db.connect() as conn:
            stmt = text_table.update().where(
                text_table.c.user == message.from_user.id
            ).values(
                text=text_table.c.text + text
            )
            conn.execute(stmt)
        markup = telebot.types.ReplyKeyboardMarkup(True, False)
        markup.row('OK')
        bot.send_message(
            message.from_user.id, 'Text has been added.', reply_markup=markup
        )

try:
    bot.polling(none_stop=True, interval=0)
except Exception:
    pass

