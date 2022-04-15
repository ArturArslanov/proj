import logging
import random
import config
from telegram import Update, ForceReply, ReplyKeyboardRemove, ReplyKeyboardMarkup, \
    InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, \
    CallbackQueryHandler
from datetime import datetime
from requests import get, post, put

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)


def close_keyboard(update, context):
    update.message.reply_text(
        "Ok",
        reply_markup=ReplyKeyboardRemove()
    )


def bot_started(update: Update, context: CallbackContext):
    agree = KeyboardButton("отправить номер", request_contact=True)
    s1 = [[agree]]
    markup = ReplyKeyboardMarkup(s1)
    update.message.reply_text(f"""чтобы создать или привязать аккаунт на сайте ARZETEL разрешите 
    использовать ваш номер""", reply_markup=markup)


def take_nomer(update: Update, context: CallbackContext):
    contact = update.message.contact
    name = contact.first_name
    nomer = contact.phone_number
    request = 'api/user_add'
    res = post(config.address + request, json={'name': name, 'nomer': nomer,
                                               'tele_id': update.effective_user.id})
    update.message.reply_text(name + ' ' + nomer)


def set_name(update: Update, context: CallbackContext):
    message = ' '.join(update.message.text.split()[1:])
    requset = 'api/user_set_name'
    res = post(config.address + requset, json={'new_name': message,
                                               'id': update.effective_user.id})
    update.message.reply_text(f'имя измененно на {message}')


def get_themes(update: Update, context: CallbackContext):
    id = update.effective_user.id
    req = f'api/user_get_themes/{id}'
    res = get(config.address + req).json()['answer']
    s = ''
    for i in range(len(res)):
        req2 = f'api/theme_header/{res[i]}'
        s += get(config.address + req2).json()['answer'] + '\n'
    update.message.reply_text(f"""{s}""")


def add_theme(update: Update, context: CallbackContext):
    id = update.effective_user.id
    message = ' '.join(update.message.text.split()[1:])
    req = f'api/theme_add/'
    res = post(config.address + req, json={'header': message, 'user_id': id})
    update.message.reply_text(f'добавлена тема {message}')


def rename_theme(update: Update, context: CallbackContext):
    id = update.effective_user.id
    message = ' '.join(update.message.text.split()[1:])
    req = f'api/user_get_themes/{id}'
    res = get(config.address + req).json()['answer']
    reply = [['отменить']]
    for i in range(len(res)):
        req2 = f'api/theme_header/{res[i]}'
        bt_text = get(config.address + req2).json()['answer']
        reply.append([KeyboardButton(f'/retheme {bt_text} && {message}')])
    markup = ReplyKeyboardMarkup(reply)
    update.message.reply_text('переназвать', reply_markup=markup)


def retheme(update: Update, context: CallbackContext):
    id = update.effective_user.id
    old, new = ' '.join(update.message.text.split()[1:]).split('& ')
    old = old[:-2]
    req = 'api/id_from_header/'
    id = str(get(config.address + req + f'/{id}/{old}').json()['answer'])
    if not id.isdigit():
        raise AttributeError("LOH")
    req2 = 'api/set_theme_header'
    res = put(config.address + req2, json={'id': id, 'header': new})
    update.message.reply_text(res.json()['answer'])


def any_text(update: Update, context: CallbackContext):
    message = update.message.text
    if message == 'отменить':
        close_keyboard(update, context)


def delete_theme(update: Update, context: CallbackContext):
    id = update.effective_user.id
    req = f'api/user_get_themes/{id}'
    res = get(config.address + req).json()['answer']
    reply = [['отменить']]
    for i in range(len(res)):
        req2 = f'api/theme_header/{res[i]}'
        bt_text = get(config.address + req2).json()['answer']
        reply.append([KeyboardButton(f'/delete_theme {bt_text}')])
    markup = ReplyKeyboardMarkup(reply)
    update.message.reply_text('удалить', reply_markup=markup)


def del_theme(update: Update, context: CallbackContext):
    message = ' '.join(update.message.text.split()[1:])
    user_id = update.effective_user.id
    req = 'api/del_theme'
    req2 = f'api/id_from_header/{user_id}/{message}'
    id = get(config.address + req2).json()['answer']
    res = post(config.address + req, json={'user_id': user_id, 'id': id})
    update.message.reply_text(res.json()['answer'])


def add_note(update: Update, context: CallbackContext):
    id = update.effective_user.id
    message = ' '.join(update.message.text.split()[1:])
    req = f'api/user_get_themes/{id}'
    res = get(config.address + req).json()['answer']
    reply = [['отменить']]
    for i in range(len(res)):
        req2 = f'api/theme_header/{res[i]}'
        bt_text = get(config.address + req2).json()['answer']
        reply.append([KeyboardButton(f'/add_note_to_theme {bt_text} && {message}')])
    markup = ReplyKeyboardMarkup(reply)
    update.message.reply_text('добавить', reply_markup=markup)


def add_note_to_theme(update: Update, context: CallbackContext):
    id = update.effective_user.id
    old, new = ' '.join(update.message.text.split()[1:]).split('& ')
    old = old[:-2]
    req = 'api/id_from_header'
    id = str(get(config.address + req + f'/{id}/{old}').json()['answer'])
    if not id.isdigit():
        print(1)
        raise AttributeError("LOH")
    req2 = 'api/add_note'
    res = post(config.address + req2, json={'theme_id': id, 'header': new})
    reply = []
    b1 = KeyboardButton(f'/add_links_to_note {new}')
    b2 = KeyboardButton(f'/add_text_to_note {new}')
    b3 = KeyboardButton(f'отменить')
    reply.append([b1])
    reply.append([b2])
    reply.append([b3])
    markup = ReplyKeyboardRemove(reply)
    update.message.reply_text(reply_markup=markup)


def get_notes_theme(update: Update, context: CallbackContext):
    id = update.effective_user.id
    message = ' '.join(update.message.text.split()[1:])
    req = f'api/user_get_themes/{id}'
    res = get(config.address + req).json()['answer']
    reply = [['отменить']]
    for i in range(len(res)):
        req2 = f'api/theme_header/{res[i]}'
        bt_text = get(config.address + req2).json()['answer']
        reply.append([KeyboardButton(f'/get_note_from_theme {bt_text}')])
    markup = ReplyKeyboardMarkup(reply)
    update.message.reply_text('выбрать', reply_markup=markup)


def get_notes(update: Update, context: CallbackContext):
    id = update.effective_user.id

    message = ' '.join(update.message.text.split()[1:])
    req = 'api/id_from_header/'
    id = str(get(config.address + req + f'/{id}/{message}').json()['answer'])
    if not id.isdigit():
        raise AttributeError("LOH")
    req2 = f'api/get_notes/{id}'
    res = get(config.address + req2).json()['answer']
    if not res:
        update.message.reply_text(f'в теме {message} нет заметок')
    return ''
    s = ''
    for i in res:
        s += str(i) + '\n'
    update.message.reply_text(s)


def main():
    updater = Updater(config.TOKEN)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", bot_started))
    dispatcher.add_handler(MessageHandler(Filters.contact, take_nomer))
    dispatcher.add_handler(CommandHandler('set_name', set_name))
    dispatcher.add_handler(CommandHandler('add_theme', add_theme))
    dispatcher.add_handler(CommandHandler('get_all_themes', get_themes))
    dispatcher.add_handler(CommandHandler('rename_theme', rename_theme))
    dispatcher.add_handler(CommandHandler('retheme', retheme))
    dispatcher.add_handler(CommandHandler('del_theme', delete_theme))
    dispatcher.add_handler(CommandHandler('delete_theme', del_theme))
    dispatcher.add_handler(CommandHandler('add_note', add_note))
    dispatcher.add_handler(CommandHandler('add_note_to_theme', add_note_to_theme))
    dispatcher.add_handler(CommandHandler('get_notes', get_notes_theme))
    dispatcher.add_handler(CommandHandler('get_note_from_theme', get_notes))
    dispatcher.add_handler(MessageHandler(Filters.text, any_text))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
